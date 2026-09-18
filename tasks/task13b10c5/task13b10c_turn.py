"""Task 13B10C5 per-turn glue (TEST ONLY).

Retains the Task 13B10C module path so the collector wiring is unchanged.  Two selectors
run on every turn:

  * the Task 13B10C3/C4 provenance lock, byte-identical, recorded as a shadow verdict; and
  * the Task 13B10C5 operational response layer, whose result is what the user sees.

Both must agree on the lane, and both must be non-MODEL_RAW on every operational turn, or the
run stops.  The lock therefore still independently proves the invariant it has always proven.
"""
from __future__ import annotations

import copy

import task13b10b_gate_frozen as old_detector
import task13b10c5_response as c5
from provenance_lock import select_response as locked_select
from task13b10c_gate import evaluate
from task13b10c_proposal_guard import classify_request


def collect_drafts(new_messages: list[dict], final_response: str) -> list[str]:
    drafts = [message["content"] for message in new_messages if message.get("role") == "assistant" and isinstance(message.get("content"), str) and message["content"].strip()]
    final = final_response or ""
    if not drafts or drafts[-1] != final:
        drafts.append(final)
    return drafts


def tool_events(turn_tool_ledger: list[dict]) -> list[dict]:
    return [{
        "tool": event["tool"],
        "raw_model_arguments": event.get("raw_model_arguments"),
        "canonical_arguments": event.get("canonical_arguments"),
        "result": event.get("result"),
        "proposal_guard": event.get("proposal_guard"),
        "dispatcher_called": event.get("dispatcher_called", False),
    } for event in turn_tool_ledger]


def gate_turn(ledger, turn: int, prompt: str, new_messages: list[dict], final_response: str, turn_tool_ledger: list[dict]) -> dict:
    user_facts = ledger.ingest_user(turn, prompt)
    events = tool_events(turn_tool_ledger)
    tool_provenance = ledger.ingest_tool_events(turn, events)
    drafts = collect_drafts(new_messages, final_response)
    request_class = classify_request(prompt)
    frozen_gate = evaluate(drafts, events, ledger, prompt, request_class)
    shadow_reviews = []
    for index, draft in enumerate(drafts, 1):
        proof = old_detector.evaluate([draft], [event for event in events if isinstance(event.get("result"), dict)], ledger)
        shadow_reviews.append({"draft": index, "text": draft, "decision": proof["decision"], "violations": proof["violations"]})

    # Immutable C4 provenance lock, run unchanged on every turn and kept as evidence.
    c4_shadow = locked_select(prompt, drafts, events, ledger, user_facts, frozen_gate)
    result = c5.select_response(prompt, drafts, events, ledger, user_facts, {**frozen_gate, "request_class": request_class})

    if c4_shadow["response_lane"]["lane"] != result["response_lane"]["lane"]:
        raise RuntimeError("HARD HARNESS FAILURE: C5 lane diverged from the frozen provenance lock")
    if result["response_lane"]["lane"] == "OPERATIONAL":
        if c4_shadow["final_user_visible_source"] == "MODEL_RAW":
            raise RuntimeError("HARD HARNESS FAILURE: frozen lock yielded operational MODEL_RAW")
        if result["final_user_visible_source"] == "MODEL_RAW" or result["final_user_visible_source"] not in c5.ALLOWED_OPERATIONAL_SOURCES:
            raise RuntimeError("HARD HARNESS FAILURE: operational final source is not provenance locked")

    return {
        "user_facts": user_facts,
        "tool_provenance": tool_provenance,
        "request_class": request_class,
        "proposal_decisions": [event.get("proposal_guard") for event in events],
        "drafts": drafts,
        "shadow_detector_reviews": shadow_reviews,
        "c4_lock_shadow": {"final_user_visible_source": c4_shadow["final_user_visible_source"],
                           "output_mode": c4_shadow["output_mode"],
                           "visible_text": c4_shadow["visible_text"],
                           "lane": c4_shadow["response_lane"]["lane"]},
        **result,
        "ledger_snapshot": ledger.snapshot(),
    }


def visible_history(messages: list[dict], history_len: int, gate: dict) -> tuple[list[dict], dict]:
    out = copy.deepcopy(messages)
    assistants = [index for index in range(history_len, len(out)) if out[index].get("role") == "assistant"]
    record = {"assistant_indices": assistants, "final_index": None, "blanked_interim_indices": [], "appended": False, "final_content_before": None, "final_content_changed": False}
    if not assistants:
        out.append({"role": "assistant", "content": gate["visible_text"]})
        record["appended"] = True
        return out, record
    final_index = assistants[-1]
    record["final_index"] = final_index
    if gate["final_user_visible_source"] != "MODEL_RAW":
        for index in assistants[:-1]:
            if out[index].get("content"):
                out[index]["content"] = ""
                record["blanked_interim_indices"].append(index)
    record["final_content_before"] = out[final_index].get("content")
    record["final_content_changed"] = out[final_index].get("content") != gate["visible_text"]
    out[final_index]["content"] = gate["visible_text"]
    return out, record

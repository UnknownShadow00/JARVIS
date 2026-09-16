"""Task 13B10C3 operational response provenance lock (TEST ONLY)."""
from __future__ import annotations

import re

from lane import derive_lane
from task13b10c2_classifier import classify_response_need

ALLOWED_OPERATIONAL_SOURCES = {
    "LEDGER",
    "TOOL_SUCCESS",
    "TOOL_ERROR",
    "CONFIRMATION",
    "AMBIGUITY",
    "MISSING_CONTEXT",
    "DECLARATIVE_ACK",
    "UNVERIFIED_STATUS",
    "CAPABILITY_UNAVAILABLE",
}

CONFIRMATION_TEXT = "Confirmation is required before that action can run, sir; nothing has been executed."
AMBIGUITY_TEXT = "The target is not sufficiently specified, sir."
MISSING_CONTEXT_TEXT = "That detail is not available in the current context, sir; please specify the source."
UNVERIFIED_STATUS_TEXT = "That status has not been verified, sir."
CAPABILITY_UNAVAILABLE_TEXT = "The requested action is not available through the current tools, sir."


def _trusted(events: list[dict]) -> list[dict]:
    # Frozen C2 trust rule: a structured result is trusted; blocked proposals have result=None.
    return [event for event in events if isinstance(event.get("result"), dict)]


def _prior_texts(ledger, prompt: str) -> list[str]:
    texts = list(ledger.user_texts)
    if texts and texts[-1] == prompt:
        texts = texts[:-1]
    return texts


def _ledger_value(prompt: str, ledger) -> tuple[str, str] | None:
    low = prompt.lower()
    for needle, key, label in (
        ("port", "port", "port"),
        ("environment", "active_environment", "environment"),
        ("target", "deployment_target", "deployment target"),
    ):
        value = (ledger.params.get(key) or {}).get("current")
        if needle in low and value:
            return f"The current supplied {label} is {value}, sir.", f"current_{key}"
    if "region" in low:
        for text in reversed(ledger.user_texts):
            match = re.search(r"\bpreferred\s+region\s+is\s+([a-z0-9-]+)\b", text, re.I)
            if match:
                return f"The current supplied preferred region is {match.group(1)}, sir.", "current_preferred_region"
    if "backup" in low and re.search(r"\bdid\s+i\s+say\b|\bwhat\b|\bwhich\b", low):
        for text in reversed(_prior_texts(ledger, prompt)):
            if re.search(r"\bbackup\b.*\b(?:completed|succeeded|successful)\b", text, re.I):
                return "Yes, sir; that is what you supplied about last night's backup outcome.", "current_backup_result"
    return None


def _declarative_ack(prompt: str, ledger) -> tuple[str, str]:
    low = prompt.lower()
    for key, label, needles in (
        ("port", "service port", ("port",)),
        ("active_environment", "environment", ("environment",)),
        ("deployment_target", "target", ("target", "deploy")),
    ):
        value = (ledger.params.get(key) or {}).get("current")
        if value and any(needle in low for needle in needles):
            return f"The current supplied {label} is {value}, sir.", f"declarative_{key}"
    match = re.search(r"\bpreferred\s+region\s+is\s+([a-z0-9-]+)\b", prompt, re.I)
    if match:
        return f"The current supplied preferred region is {match.group(1)}, sir.", "declarative_preferred_region"
    observation = ledger.observations[-1] if ledger.observations else None
    if observation:
        words = set(observation.get("words", []))
        latency = observation.get("latency_ms", [])
        if "passed" in words and latency:
            return f"The database check is reported as having passed at {latency[-1]} ms, sir.", "reported_measurement"
        if "deploying" in words and (ledger.params.get("deployment_target") or {}).get("current"):
            target = ledger.params["deployment_target"]["current"]
            return f"You reported that deployment to {target} is underway, sir; that state has not been independently verified.", "reported_deployment"
    return "Acknowledged, sir; I retained that as a user-supplied operational fact, not an independently verified result.", "reported_operational_fact"


def _tool_response(event: dict) -> dict | None:
    tool, result = event.get("tool"), event.get("result") or {}
    status = result.get("status")
    if status == "confirmation_required" and result.get("executed") is False:
        return _candidate("CONFIRMATION_REQUIRED_RESPONSE", "CONFIRMATION", CONFIRMATION_TEXT, "confirmation_required")
    if status == "error":
        if result.get("error") == "app_not_found":
            text = "That application could not be opened because it was not found, sir."
        else:
            detail = str(result.get("error") or "unknown error").replace("_", " ").strip()
            text = f"The requested action could not complete because {detail}, sir."
        return _candidate("TOOL_ERROR_RESPONSE", "TOOL_ERROR", text, "trusted_tool_error")
    if status == "success" and tool == "jarvis_test_open_app":
        return _candidate("TOOL_SUCCESS_RESPONSE", "TOOL_SUCCESS", "The requested application was opened successfully, sir.", "trusted_open_app_success")
    if status == "success" and tool == "jarvis_test_open_url":
        return _candidate("TOOL_SUCCESS_RESPONSE", "TOOL_SUCCESS", "The requested page was opened successfully, sir.", "trusted_open_url_success")
    if status == "success" and tool == "jarvis_test_get_database_status":
        db_status = result.get("database_status")
        latency = result.get("latency_ms")
        if db_status == "reachable" and latency is not None:
            text = f"The database is reachable at {latency} ms, sir."
        elif db_status is not None:
            text = f"The database status is {db_status}, sir."
        else:
            text = "The database check completed successfully, sir."
        return _candidate("TOOL_SUCCESS_RESPONSE", "TOOL_SUCCESS", text, "trusted_database_success")
    return None


def _candidate(kind: str, source: str, text: str, reason: str) -> dict:
    return {"class": kind, "source": source, "text": text, "reason": reason, "eligible": True}


def _operational_candidates(prompt: str, response_need: dict, events: list[dict], ledger, lane: dict) -> list[dict]:
    candidates: list[dict] = []
    trusted = _trusted(events)
    for event in trusted:
        made = _tool_response(event)
        if made:
            candidates.append(made)

    cls = response_need["class"]
    value = _ledger_value(prompt, ledger)
    if value:
        candidates.append(_candidate("LEDGER_VALUE_RESPONSE", "LEDGER", value[0], value[1]))
    if cls == "CONFIRMATION_SENSITIVE_ACTION" and not any(c["source"] == "CONFIRMATION" for c in candidates):
        candidates.append(_candidate("CONFIRMATION_REQUIRED_RESPONSE", "CONFIRMATION", CONFIRMATION_TEXT, "frozen_confirmation_policy"))
    if cls == "AMBIGUOUS_ACTION":
        candidates.append(_candidate("AMBIGUITY_RESPONSE", "AMBIGUITY", AMBIGUITY_TEXT, response_need["reason"]))
    if cls == "MISSING_CONTEXT_QUERY":
        candidates.append(_candidate("MISSING_CONTEXT_RESPONSE", "MISSING_CONTEXT", MISSING_CONTEXT_TEXT, response_need["reason"]))
    if cls == "DECLARATIVE_FACT":
        if "action_target" in lane["reasons"] and not trusted:
            candidates.append(_candidate("CAPABILITY_UNAVAILABLE_RESPONSE", "CAPABILITY_UNAVAILABLE", CAPABILITY_UNAVAILABLE_TEXT, "imperative_action_without_available_result"))
        else:
            text, reason = _declarative_ack(prompt, ledger)
            candidates.append(_candidate("DECLARATIVE_FACT_ACKNOWLEDGEMENT", "DECLARATIVE_ACK", text, reason))
    if cls == "STATUS_CHECK_REQUEST" and not trusted:
        candidates.append(_candidate("UNVERIFIED_STATUS_RESPONSE", "UNVERIFIED_STATUS", UNVERIFIED_STATUS_TEXT, "no_trusted_status_result"))
    if cls == "VALUE_QUERY" and value is None:
        candidates.append(_candidate("MISSING_CONTEXT_RESPONSE", "MISSING_CONTEXT", MISSING_CONTEXT_TEXT, "no_current_ledger_value"))
    if cls == "ACTION_REQUEST" and not trusted:
        candidates.append(_candidate("UNVERIFIED_STATUS_RESPONSE", "UNVERIFIED_STATUS", UNVERIFIED_STATUS_TEXT, "no_trusted_action_result"))
    if cls == "OTHER":
        reasons = set(lane["reasons"])
        if "external_status_claim_required" in reasons:
            candidates.append(_candidate("UNVERIFIED_STATUS_RESPONSE", "UNVERIFIED_STATUS", UNVERIFIED_STATUS_TEXT, "other_external_status"))
        elif "action_target" in reasons or "tool_proposal" in reasons:
            candidates.append(_candidate("CAPABILITY_UNAVAILABLE_RESPONSE", "CAPABILITY_UNAVAILABLE", CAPABILITY_UNAVAILABLE_TEXT, "other_action_without_trusted_result"))
        else:
            candidates.append(_candidate("MISSING_CONTEXT_RESPONSE", "MISSING_CONTEXT", MISSING_CONTEXT_TEXT, "other_operational_context"))
    return candidates


def select_response(
    prompt: str,
    drafts: list[str],
    events: list[dict],
    ledger,
    current_user_facts: list[dict],
    frozen_gate: dict,
) -> dict:
    response_need = classify_response_need(prompt)
    lane = derive_lane(prompt, response_need, events, ledger, current_user_facts)
    candidates: list[dict] = []

    if lane["lane"] == "CONVERSATIONAL":
        if frozen_gate.get("draft_gate_decision") == "ALLOW" and drafts:
            candidates.append(_candidate("GENERAL_EXPLANATION_RAW" if response_need["class"] == "GENERAL_EXPLANATION" else "SAFE_RAW", "MODEL_RAW", drafts[-1], "shadow_detector_allow"))
        candidates.append(_candidate("MISSING_CONTEXT_RESPONSE", "MISSING_CONTEXT", MISSING_CONTEXT_TEXT, "conversational_raw_blocked_fallback"))
    else:
        candidates = _operational_candidates(prompt, response_need, events, ledger, lane)

    def first_source(*sources: str) -> dict | None:
        return next((candidate for candidate in candidates if candidate["source"] in sources), None)

    if lane["lane"] == "CONVERSATIONAL":
        selected = first_source("MODEL_RAW") or first_source("MISSING_CONTEXT")
    else:
        # Preserve C2 deterministic ordering.  This intentionally does not tune G07.
        selected = first_source("CONFIRMATION", "TOOL_SUCCESS", "TOOL_ERROR", "AMBIGUITY", "MISSING_CONTEXT")
        if selected is None and response_need["class"] == "VALUE_QUERY":
            selected = first_source("LEDGER")
        if selected is None and response_need["class"] == "DECLARATIVE_FACT":
            selected = first_source("DECLARATIVE_ACK") or first_source("LEDGER")
        if selected is None:
            selected = first_source("UNVERIFIED_STATUS", "CAPABILITY_UNAVAILABLE", "LEDGER", "DECLARATIVE_ACK")
    if selected is None:
        raise RuntimeError("no response candidate")

    if lane["lane"] == "OPERATIONAL":
        if selected["source"] == "MODEL_RAW" or selected["source"] not in ALLOWED_OPERATIONAL_SOURCES:
            raise RuntimeError("HARD HARNESS FAILURE: operational final source is not provenance locked")

    return {
        **frozen_gate,
        "response_need_class": response_need,
        "response_lane": lane,
        "response_candidates": candidates,
        "selected_candidate": selected,
        "final_user_visible_source": selected["source"],
        "output_mode": selected["class"],
        "visible_text": selected["text"],
        "fallback": None if selected["source"] == "MODEL_RAW" else selected["source"],
        "grounded_reason": selected["reason"],
    }

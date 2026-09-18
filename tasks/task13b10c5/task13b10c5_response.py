"""Task 13B10C5 TEST-ONLY deterministic operational response layer.

Changes exactly one family: operational response-obligation derivation, candidate
construction, source selection and templates.  It changes nothing about the
provenance lock, the action router, the request classifiers, the proposal guard,
canonicalization, the dispatcher, the confirmation policy or the trust rules.

The Task 13B10C3/C4 provenance lock file is imported unchanged and its allowed-source
set is the authority here; ``MULTI_ACTION_UNSUPPORTED`` is the one source this task is
authorized to add (spec section 10).  The lock's rule is re-applied verbatim to the
response this layer emits: for every OPERATIONAL turn the final source may never be
``MODEL_RAW`` and must be in the allowed set, or the run stops with a hard error.

Every component of every response is derived from one of:
  A user intent   B current ledger value   C trusted tool result   D confirmation state
  E router result   F capability availability   G ambiguity / missing target
Nothing else may appear in an operational response.
"""
from __future__ import annotations

import re

import provenance_lock as lock
from lane import derive_lane
from task13b10c2_classifier import classify_response_need
from task13b10c_provenance import ACTION_WORDS, EVENT_WORDS, PRESENT_STATE_WORDS

# Spec section 10: the C4 allowed set plus the one authorized addition.
ALLOWED_OPERATIONAL_SOURCES = set(lock.ALLOWED_OPERATIONAL_SOURCES) | {"MULTI_ACTION_UNSUPPORTED"}

OBLIGATIONS = (
    "ACKNOWLEDGE_FACT", "ANSWER_LEDGER_VALUE", "REPORT_TOOL_SUCCESS", "REPORT_TOOL_ERROR",
    "REQUEST_CONFIRMATION", "REQUEST_TARGET", "REPORT_CAPABILITY_UNAVAILABLE",
    "REPORT_UNVERIFIED_STATUS", "REPORT_MULTI_ACTION_LIMIT",
    "ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION", "MISSING_CONTEXT",
)
OBLIGATION_SOURCE = {
    "REQUEST_CONFIRMATION": "CONFIRMATION",
    "REPORT_TOOL_ERROR": "TOOL_ERROR",
    "REPORT_TOOL_SUCCESS": "TOOL_SUCCESS",
    "REQUEST_TARGET": "AMBIGUITY",
    "REPORT_MULTI_ACTION_LIMIT": "MULTI_ACTION_UNSUPPORTED",
    "REPORT_CAPABILITY_UNAVAILABLE": "CAPABILITY_UNAVAILABLE",
    "ANSWER_LEDGER_VALUE": "LEDGER",
    "ACKNOWLEDGE_FACT": "DECLARATIVE_ACK",
    "REPORT_UNVERIFIED_STATUS": "UNVERIFIED_STATUS",
    "ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION": "DECLARATIVE_ACK",
    "MISSING_CONTEXT": "MISSING_CONTEXT",
}

# ---- frozen templates ------------------------------------------------------------------------------------------
CONFIRMATION_TEXT = lock.CONFIRMATION_TEXT
MISSING_CONTEXT_TEXT = "That detail is not available in the current context, sir; please provide the source."
AMBIGUITY_TEXT = lock.AMBIGUITY_TEXT
CAPABILITY_TEXT = "That action is not available through the current tools, sir."
MULTI_ACTION_TEXT = "That request contains multiple actions, sir; please send them one at a time."
UNVERIFIED_TEXT = "That status has not been verified, sir."
INTENT_ONLY_TEXT = "That request was understood, sir, but no result is available and nothing has been executed."
GENERIC_FACT_TEXT = ("Acknowledged, sir; I retained that as a user-supplied operational fact, "
                     "not an independently verified result.")

TARGET_QUESTION = {
    "OPEN_APP": "Which application should be opened, sir?",
    "OPEN_URL": "Which URL should be opened, sir?",
    "DELETE_PATH": "Which exact path should be deleted, sir?",
    "DEPLOY": "Which environment should be deployed to, sir?",
}
# Progressive/past action words -> the neutral noun used in an attributed progress acknowledgement.
ACTION_NOUN = {
    "deploying": "deployment", "deployed": "deployment", "restarting": "restart", "restarted": "restart",
    "deleting": "deletion", "deleted": "deletion", "opening": "open", "opened": "open",
    "launching": "launch", "launched": "launch", "starting": "start", "started": "start",
    "stopping": "stop", "stopped": "stop", "switching": "switch", "switched": "switch",
    "checking": "check", "checked": "check",
}
# Frozen display nouns for explicitly requested operations that have no tool.
VERB_NOUN = {"verify": "verification", "check": "check", "inspect": "inspection", "get": "retrieval",
             "restart": "restart", "reboot": "reboot", "change": "change", "update": "update",
             "modify": "modification", "install": "installation", "set": "change", "start": "start",
             "stop": "stop", "scale": "scaling", "reset": "reset", "rollback": "rollback"}
PARAM_LABEL = (("port", "port", ("port",)),
               ("active_environment", "environment", ("environment",)),
               ("deployment_target", "target", ("target", "deploy")))
_VERIFICATION_QUESTION = re.compile(r"\b(?:verif(?:y|ied|ication)|independently)\b", re.I)
_YES_NO = re.compile(r"^\s*(?:did|was|were|is|are|has|have|does|do)\b", re.I)
_STATE_WORDS = set(PRESENT_STATE_WORDS) | set(EVENT_WORDS)


def _trusted(events: list[dict]) -> list[dict]:
    return [event for event in events if isinstance(event.get("result"), dict)]


def _status(event: dict) -> str | None:
    return (event.get("result") or {}).get("status")


def _latest_observation(ledger) -> dict | None:
    return ledger.observations[-1] if ledger.observations else None


def _asserted_observation(ledger, prompt: str) -> dict | None:
    """Latest observation the user actually asserted, never one parsed out of their own question.

    A state word inside a question ("Is the database down?") is the user asking, not reporting, so
    it must never be echoed back as something they reported.
    """
    for record in reversed(ledger.observations):
        text = str((record.get("value") or {}).get("text") or record.get("text") or "").strip()
        if not text or text.endswith("?") or text == (prompt or "").strip():
            continue
        return record
    return None


def _param_for_prompt(prompt: str, ledger) -> tuple[str, str] | None:
    """Current ledger value whose label the user's own wording refers to."""
    low = prompt.lower()
    for key, label, needles in PARAM_LABEL:
        value = (ledger.params.get(key) or {}).get("current")
        if value and any(needle in low for needle in needles):
            return label, value
    return None


# ---- obligation derivation (spec sections 13 and 14) ---------------------------------------------------------------
def derive_obligation(prompt: str, request_class: dict, response_need: dict, events: list[dict], ledger, lane: dict) -> dict:
    """Exactly one obligation per operational turn, from frozen inputs only.  No model inference."""
    trusted = _trusted(events)
    need = response_need["class"]
    intent = request_class.get("intent")
    reasons = set(lane.get("reasons") or [])

    if any(_status(event) == "confirmation_required" for event in trusted) or need == "CONFIRMATION_SENSITIVE_ACTION":
        return {"obligation": "REQUEST_CONFIRMATION", "priority": 1, "reason": "confirmation_required_state"}
    if any(_status(event) == "error" for event in trusted):
        return {"obligation": "REPORT_TOOL_ERROR", "priority": 2, "reason": "trusted_tool_error"}
    if any(_status(event) == "success" for event in trusted):
        return {"obligation": "REPORT_TOOL_SUCCESS", "priority": 3, "reason": "trusted_tool_success"}
    if intent == "AMBIGUOUS_ACTION" or need == "AMBIGUOUS_ACTION":
        return {"obligation": "REQUEST_TARGET", "priority": 4, "reason": request_class.get("reason", "target_unresolved")}
    if intent == "MULTI_ACTION_UNSUPPORTED":
        return {"obligation": "REPORT_MULTI_ACTION_LIMIT", "priority": 5, "reason": "multiple_supported_actions"}
    if intent in ("UNKNOWN_ACTION", "UNSUPPORTED_ACTION") or (
            need == "MISSING_CONTEXT_QUERY" and response_need.get("reason") == "requested_capability_unavailable"):
        return {"obligation": "REPORT_CAPABILITY_UNAVAILABLE", "priority": 6, "reason": "explicit_action_without_tool"}
    if need == "VALUE_QUERY" and lock._ledger_value(prompt, ledger) is not None:
        return {"obligation": "ANSWER_LEDGER_VALUE", "priority": 7, "reason": "direct_ledger_value_question"}
    if need == "DECLARATIVE_FACT":
        return {"obligation": "ACKNOWLEDGE_FACT", "priority": 8, "reason": "user_supplied_operational_fact"}
    if need == "STATUS_CHECK_REQUEST":
        return {"obligation": "REPORT_UNVERIFIED_STATUS", "priority": 9, "reason": "status_question_without_trusted_result"}
    if "external_status_claim_required" in reasons:
        return {"obligation": "REPORT_UNVERIFIED_STATUS", "priority": 9, "reason": "external_status_claim_without_trusted_result"}
    if need == "ACTION_REQUEST" or intent == "EXPLICIT_ACTION" or "action_target" in reasons or "tool_proposal" in reasons:
        return {"obligation": "ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION", "priority": 10, "reason": "action_intent_without_result"}
    if lock._ledger_value(prompt, ledger) is not None:
        return {"obligation": "ANSWER_LEDGER_VALUE", "priority": 7, "reason": "ledger_value_available"}
    if need == "MISSING_CONTEXT_QUERY":
        return {"obligation": "MISSING_CONTEXT", "priority": 11, "reason": response_need.get("reason", "missing_context")}
    return {"obligation": "MISSING_CONTEXT", "priority": 11, "reason": "no_grounded_source_available"}


# ---- renderers -----------------------------------------------------------------------------------------------------
def _render_tool_error(event: dict) -> str:
    result = event.get("result") or {}
    error = result.get("error")
    if error == "app_not_found":
        return "The requested application was not found, sir."
    if error == "url_not_in_test_fixture":
        return "The requested page was not found, sir."
    detail = str(error or "unknown error").replace("_", " ").strip()
    return f"The requested action could not complete because {detail}, sir."


def _render_tool_success(event: dict) -> str:
    tool, result = event.get("tool"), event.get("result") or {}
    if tool == "jarvis_test_open_app":
        return "The requested application was opened successfully, sir."
    if tool == "jarvis_test_open_url":
        return "The requested page was opened successfully, sir."
    if tool == "jarvis_test_get_database_status":
        status, latency = result.get("database_status"), result.get("latency_ms")
        if status == "reachable" and latency is not None:
            return f"The database is reachable at {latency} ms, sir."
        if status is not None:
            return f"The database status is {status}, sir."
    return "The requested action completed successfully, sir."


def _render_capability(prompt: str, request_class: dict, ledger) -> str:
    """Capability limit, carrying a grounded value when provenance already holds one."""
    param = _param_for_prompt(prompt, ledger)
    if param is not None:
        label, value = param
        return (f"The requested {label} is {value}, sir, but applying that change is not available "
                "through the current tools.")
    verb = None
    for row in request_class.get("clause_analysis") or []:
        if row.get("primary_action") == "UNKNOWN_ACTION" and row.get("verb"):
            verb = row["verb"]
            break
    if verb:
        text = f"The requested {VERB_NOUN.get(verb, verb)} is not available through the current tools, sir"
        if request_class.get("reporting_intent") in ("REPORT_STATUS", "REPORT_COMPLETION", "REPORT_SUCCESS", "REPORT_FAILURE"):
            return text + ", so its outcome cannot be verified from that action."
        return text + "."
    return CAPABILITY_TEXT


def _render_acknowledge_fact(prompt: str, ledger) -> str:
    low = prompt.lower()
    observation = _latest_observation(ledger)
    words = list(observation.get("words") or []) if observation else []
    latency = list(observation.get("latency_ms") or []) if observation else []
    param = _param_for_prompt(prompt, ledger)

    action_words = [w for w in words if w in ACTION_NOUN]
    state_words = [w for w in words if w in _STATE_WORDS]

    if param is not None and action_words:
        label, value = param
        noun = ACTION_NOUN[action_words[-1]]
        return (f"A {noun} to {value} is reported in progress, sir; that has not been "
                "independently verified.")
    if param is not None and state_words:
        label, value = param
        # Only treat the state word as a reported state when the user wrote it after the value.
        if low.rfind(state_words[-1]) > low.rfind(str(value).lower()):
            return f"{label.capitalize()} {value} is reported as {state_words[-1]}, sir."
    if param is not None:
        label, value = param
        return f"The current supplied {label} is {value}, sir."
    # Any value the frozen provenance layer can already name is rendered by the frozen lookup itself,
    # so this layer never introduces a second, competing way of recognising a value.
    frozen_value = lock._ledger_value(prompt, ledger)
    if frozen_value is not None:
        return frozen_value[0]
    if state_words and latency:
        return f"That is reported as {state_words[-1]} at {latency[-1]} ms, sir; that has not been independently verified."
    if state_words:
        joined = state_words[0] if len(state_words) == 1 else " and ".join((", ".join(state_words[:-1]), state_words[-1]))
        return f"That is reported as {joined}, sir; that has not been independently verified."
    if latency:
        return (f"That is reported as {latency[-1]} ms of latency, sir; that has not been "
                "independently verified.")
    if action_words:
        return f"A {ACTION_NOUN[action_words[-1]]} is reported in progress, sir; that has not been independently verified."
    return GENERIC_FACT_TEXT


def _render_unverified(prompt: str, ledger) -> str:
    observation = _asserted_observation(ledger, prompt)
    words = [w for w in ((observation or {}).get("value") or {}).get("words", []) if w in _STATE_WORDS]
    asks_about_verification = bool(_VERIFICATION_QUESTION.search(prompt)) and bool(_YES_NO.match(prompt.strip()))
    if asks_about_verification:
        if words:
            return (f"No, sir; that has not been independently verified and remains reported as "
                    f"{words[-1]} only.")
        return "No, sir; that has not been independently verified."
    if words:
        return f"That has not been independently verified, sir; it remains reported as {words[-1]} only."
    return UNVERIFIED_TEXT


def _render_request_target(request_class: dict) -> str:
    action = request_class.get("primary_action")
    return TARGET_QUESTION.get(action, AMBIGUITY_TEXT)


def build_candidates(prompt: str, request_class: dict, response_need: dict, events: list[dict], ledger, lane: dict) -> list[dict]:
    """One candidate per obligation that the frozen state actually supports."""
    trusted = _trusted(events)
    candidates: list[dict] = []

    def add(obligation: str, text: str, reason: str) -> None:
        candidates.append({"obligation": obligation, "source": OBLIGATION_SOURCE[obligation],
                           "text": text, "reason": reason, "eligible": True})

    for event in trusted:
        if _status(event) == "confirmation_required" and (event.get("result") or {}).get("executed") is False:
            add("REQUEST_CONFIRMATION", CONFIRMATION_TEXT, "trusted_confirmation_required")
    if response_need["class"] == "CONFIRMATION_SENSITIVE_ACTION":
        add("REQUEST_CONFIRMATION", CONFIRMATION_TEXT, "frozen_confirmation_policy")
    for event in trusted:
        if _status(event) == "error":
            add("REPORT_TOOL_ERROR", _render_tool_error(event), "trusted_tool_error")
    for event in trusted:
        if _status(event) == "success":
            add("REPORT_TOOL_SUCCESS", _render_tool_success(event), "trusted_tool_success")
    if request_class.get("intent") == "AMBIGUOUS_ACTION" or response_need["class"] == "AMBIGUOUS_ACTION":
        add("REQUEST_TARGET", _render_request_target(request_class), "target_unresolved")
    if request_class.get("intent") == "MULTI_ACTION_UNSUPPORTED":
        add("REPORT_MULTI_ACTION_LIMIT", MULTI_ACTION_TEXT, "multiple_supported_actions")
    if request_class.get("intent") in ("UNKNOWN_ACTION", "UNSUPPORTED_ACTION") or (
            response_need["class"] == "MISSING_CONTEXT_QUERY"
            and response_need.get("reason") == "requested_capability_unavailable"):
        add("REPORT_CAPABILITY_UNAVAILABLE", _render_capability(prompt, request_class, ledger), "explicit_action_without_tool")
    value = lock._ledger_value(prompt, ledger)
    if value is not None:
        add("ANSWER_LEDGER_VALUE", value[0], value[1])
    if response_need["class"] == "DECLARATIVE_FACT":
        add("ACKNOWLEDGE_FACT", _render_acknowledge_fact(prompt, ledger), "user_supplied_operational_fact")
    if response_need["class"] == "STATUS_CHECK_REQUEST" or "external_status_claim_required" in set(lane.get("reasons") or []):
        add("REPORT_UNVERIFIED_STATUS", _render_unverified(prompt, ledger), "no_trusted_status_result")
    if not trusted:
        add("ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION", INTENT_ONLY_TEXT, "action_intent_without_result")
    add("MISSING_CONTEXT", MISSING_CONTEXT_TEXT, "no_higher_priority_grounded_source")
    return candidates


def select_response(prompt, drafts, events, ledger, current_user_facts, frozen_gate):
    """Same contract as the frozen lock's selector; operational composition is the C5 layer's."""
    response_need = classify_response_need(prompt)
    lane = derive_lane(prompt, response_need, events, ledger, current_user_facts)
    request_class = frozen_gate["request_class"]

    if lane["lane"] == "CONVERSATIONAL":
        # Conversational-lane policy is unchanged (spec section 26): the frozen lock decides it.
        chosen = lock.select_response(prompt, drafts, events, ledger, current_user_facts,
                                      {k: v for k, v in frozen_gate.items() if k != "request_class"})
        obligation = "CONVERSATIONAL_RAW" if chosen["final_user_visible_source"] == "MODEL_RAW" else "MISSING_CONTEXT"
        return {**chosen, "response_obligation": {"obligation": obligation, "priority": None,
                                                  "reason": "conversational_lane_policy_unchanged"}}

    obligation = derive_obligation(prompt, request_class, response_need, events, ledger, lane)
    candidates = build_candidates(prompt, request_class, response_need, events, ledger, lane)
    selected = next((c for c in candidates if c["obligation"] == obligation["obligation"]), None)
    if selected is None:
        selected = candidates[-1]
        obligation = {**obligation, "obligation": selected["obligation"], "reason": "obligation_candidate_unavailable"}

    # The frozen provenance-lock rule, re-applied verbatim to what this layer emits.
    if selected["source"] == "MODEL_RAW" or selected["source"] not in ALLOWED_OPERATIONAL_SOURCES:
        raise RuntimeError("HARD HARNESS FAILURE: operational final source is not provenance locked")

    return {
        **{k: v for k, v in frozen_gate.items() if k != "request_class"},
        "response_need_class": response_need,
        "response_lane": lane,
        "response_obligation": obligation,
        "response_candidates": candidates,
        "selected_candidate": selected,
        "final_user_visible_source": selected["source"],
        "output_mode": selected["obligation"],
        "visible_text": selected["text"],
        "fallback": selected["source"],
        "grounded_reason": selected["reason"],
    }

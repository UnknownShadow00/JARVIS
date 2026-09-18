"""Task 13B10C4 TEST-ONLY deterministic pre-dispatch proposal guard.

This module keeps the Task 13B10C module path so that every other frozen component
(classifier, lane, gate, turn glue, control plane, provenance, dispatcher, schemas and
the Task 13B10C3 provenance lock) stays byte-identical.  Its content is the authorized
Task 13B10C4 guard: explicit-action recognition is delegated to the deterministic
``task13b10c4_action_router`` so a trailing report/verify/notify clause no longer erases
the primary action, while every non-action fallback branch below is the verbatim Task
13B10C chain.

It uses only explicit lexical/syntactic cues and exact target comparison.  It does not call a model.
Anything not classified as an explicit supported action/read request has an empty allow-list.  A blocked proposal
never reaches the inert dispatcher and cannot create TOOL_SUCCESS, TOOL_ERROR, or CONFIRMATION_REQUIRED provenance.
"""
from __future__ import annotations

import re

import task13b10c4_action_router as router
from task13b10c_provenance import canonicalize

OPEN_APP = router.OPEN_APP
OPEN_URL = router.OPEN_URL
DEPLOY = router.DEPLOY
DELETE = router.DELETE
DB = router.DB


def _fallback(text: str) -> dict:
    """Verbatim Task 13B10C non-action classification chain (unchanged)."""
    low = text.lower()
    if re.search(r"\b(?:what\s+does|what\s+did|what\s+is|why\s+might|tell\s+me\s+what\s+that\s+means|mean\s+by)\b", low):
        return {"intent": "EXPLANATION", "allowed_tool": None, "expected": None, "reason": "explanation_request"}
    if re.search(r"\b(?:which|what)\s+(?:deployment\s+)?(?:target|port|environment)\b", low):
        return {"intent": "LEDGER_QUESTION", "allowed_tool": None, "expected": None, "reason": "ledger_question"}
    if re.search(r"^\s*(?:correction\s*:|the\s+|looks\s+like\b|we(?:'re|\s+are)\b)", low):
        return {"intent": "DECLARATIVE_USER_FACT", "allowed_tool": None, "expected": None, "reason": "declarative_or_correction"}
    if re.search(r"\b(?:obviously|because)\b", low) and not re.search(r"\b(?:check|verify)\b", low):
        return {"intent": "UNSUPPORTED_CONCLUSION", "allowed_tool": None, "expected": None, "reason": "unsupported_conclusion_no_check"}
    if re.search(r"\brestart\b", low):
        return {"intent": "UNSUPPORTED_ACTION", "allowed_tool": None, "expected": None, "reason": "no_restart_tool"}
    return {"intent": "CONVERSATIONAL_OR_UNKNOWN", "allowed_tool": None, "expected": None, "reason": "no_explicit_supported_request"}


def classify_request(prompt: str) -> dict:
    """Return a frozen intent class, the only permitted tool, and exact expected target where applicable."""
    text = prompt or ""
    route = router.parse(text)
    routing = {
        "primary_action": route["primary_action"],
        "reporting_intent": route["reporting_intent"],
        "reporting_clause": route["reporting_clause"],
        "routing_target": route["target"],
        "target_resolved": route["target_resolved"],
        "clauses": route["clauses"],
        "connectors_present": route["connectors_present"],
        "selected_clause": route["selected_clause"],
        "multi_action": route["multi_action"],
        "clause_analysis": route["clause_analysis"],
        "routing_reason": route["reason"],
    }
    action = route["primary_action"]

    if action == "MULTI_ACTION":
        return {"intent": "MULTI_ACTION_UNSUPPORTED", "allowed_tool": None, "expected": None,
                "reason": route["reason"], **routing}
    if action in router.SUPPORTED_ACTIONS:
        if not route["target_resolved"]:
            return {"intent": "AMBIGUOUS_ACTION", "allowed_tool": None, "expected": None,
                    "reason": route["reason"], **routing}
        intent = "EXPLICIT_READ" if action == "GET_DATABASE_STATUS" else "EXPLICIT_ACTION"
        return {"intent": intent, "allowed_tool": route["allowed_tool"], "expected": route["expected"],
                "reason": route["reason"], **routing}
    if action == "UNKNOWN_ACTION":
        return {"intent": "UNKNOWN_ACTION", "allowed_tool": None, "expected": None,
                "reason": route["reason"], **routing}
    return {**_fallback(text), **routing}


def decide(prompt: str, tool: str, raw_args: dict) -> dict:
    classification = classify_request(prompt)
    canonical, _ = canonicalize(tool, raw_args if isinstance(raw_args, dict) else {})
    allowed = classification["allowed_tool"] == tool and canonical == classification["expected"]
    if allowed:
        reason = "explicit_request_and_exact_target"
    elif classification["allowed_tool"] is None:
        reason = classification["reason"]
    elif classification["allowed_tool"] != tool:
        reason = "tool_does_not_match_request"
    else:
        reason = "arguments_do_not_match_user_target"
    return {**classification, "proposal_tool": tool, "raw_arguments": dict(raw_args) if isinstance(raw_args, dict) else {},
            "canonical_arguments": canonical, "decision": "ALLOW" if allowed else "BLOCK", "decision_reason": reason}

"""Task 13B10C3 deterministic response-lane derivation (TEST ONLY).

The frozen 13B10C2 response classifier remains authoritative.  This module
adds only the response-source lane required by C3; it does not authorize or
dispatch tools.
"""
from __future__ import annotations

import re


ALWAYS_OPERATIONAL = {
    "VALUE_QUERY",
    "ACTION_REQUEST",
    "STATUS_CHECK_REQUEST",
    "DECLARATIVE_FACT",
    "AMBIGUOUS_ACTION",
    "MISSING_CONTEXT_QUERY",
    "CONFIRMATION_SENSITIVE_ACTION",
}

_ACTION_TARGET = re.compile(
    r"^\s*(?:please\s+)?(?:open|deploy|delete|remove|restart|change|update|check|verify)\b", re.I
)
_EXTERNAL_STATUS = re.compile(
    r"\b(?:database|query|service|application|app|port|deployment|backup)\b.*"
    r"\b(?:status|state|error|fail(?:ed|ing)?|down|healthy|worked|complete(?:d)?)\b"
    r"|\b(?:what error|did .* fail|is .* down|is .* healthy)\b",
    re.I,
)


def derive_lane(
    prompt: str,
    response_need: dict,
    events: list[dict],
    ledger,
    current_user_facts: list[dict],
) -> dict:
    """Return OPERATIONAL or CONVERSATIONAL without an LLM decision."""
    cls = response_need["class"]
    if cls == "GENERAL_EXPLANATION":
        return {"lane": "CONVERSATIONAL", "reasons": ["general_explanation_class"]}
    reasons: list[str] = [f"always_operational:{cls}"] if cls in ALWAYS_OPERATIONAL else []
    if events:
        reasons.append("tool_proposal")
    if any(isinstance(event.get("result"), dict) for event in events):
        reasons.append("tool_result")
    if any((event.get("result") or {}).get("status") == "confirmation_required" for event in events):
        reasons.append("confirmation_required")
    if ledger.params or any(fact.get("kind") in {"param", "observation", "target"} for fact in current_user_facts):
        reasons.append("active_operational_provenance")
    if any(fact.get("supersedes") for fact in current_user_facts) or re.search(r"\bcorrection\b", prompt, re.I):
        reasons.append("operational_correction")
    if _ACTION_TARGET.search(prompt):
        reasons.append("action_target")
    if _EXTERNAL_STATUS.search(prompt):
        reasons.append("external_status_claim_required")
    return {"lane": "OPERATIONAL" if reasons else "CONVERSATIONAL", "reasons": reasons or ["other_non_operational"]}

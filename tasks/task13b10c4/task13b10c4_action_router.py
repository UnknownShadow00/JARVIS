"""Task 13B10C4 TEST-ONLY deterministic action router.

Frozen before scored collection.  Pure lexical grammar: ``re`` only, no model, no
embedding, no fuzzy similarity, no runtime learning, and no benchmark-specific
string matching.  The router answers three separate questions for one request:

  1. PRIMARY_ACTION   — the first explicit supported operation the user asked for.
  2. REPORTING_INTENT — what the user wants told back afterwards.  It never
                        creates an executable action.
  3. TARGET           — the exact operand the user wrote.  Never invented.

A compound request is segmented on frozen connectors first, so a trailing
report/verify/notify clause can no longer erase the primary action that precedes
it.  Two or more distinct supported executable actions are refused outright
(``MULTI_ACTION_UNSUPPORTED``) rather than silently reduced to one.
"""
from __future__ import annotations

import re

from task13b10c_provenance import PATH_RE, URL_RE, canonicalize

OPEN_APP = "jarvis_test_open_app"
OPEN_URL = "jarvis_test_open_url"
DEPLOY = "jarvis_test_deploy"
DELETE = "jarvis_test_delete_path"
DB = "jarvis_test_get_database_status"

PRIMARY_ACTIONS = ("OPEN_APP", "OPEN_URL", "DEPLOY", "DELETE_PATH", "GET_DATABASE_STATUS", "NONE", "UNKNOWN_ACTION")
REPORTING_INTENTS = ("REPORT_RESULT", "REPORT_SUCCESS", "REPORT_FAILURE", "REPORT_COMPLETION", "REPORT_STATUS", "NONE")
SUPPORTED_ACTIONS = ("OPEN_APP", "OPEN_URL", "DEPLOY", "DELETE_PATH", "GET_DATABASE_STATUS")

# ---- frozen action lexicon (spec section 13) ---------------------------------------------------------------------
OPEN_VERBS = ("open", "launch")
DEPLOY_VERBS = ("deploy",)
DELETE_VERBS = ("delete", "remove")
DB_VERBS = ("check", "verify", "inspect", "get")
# Explicit operations for which this diagnostic has no tool at all (spec section 16).
UNSUPPORTED_VERBS = (
    "restart", "reboot", "start", "stop", "shutdown", "install", "uninstall", "upgrade", "update", "change",
    "modify", "rollback", "roll", "scale", "reset", "kill", "enable", "disable", "create", "rename", "move",
    "copy", "run", "execute", "build", "push", "pull", "commit", "merge", "revert", "fix", "send", "email",
    "download", "upload", "backup", "restore", "clear", "flush", "rotate", "patch",
)

# ---- frozen connector grammar (spec section 12) -------------------------------------------------------------------
CONNECTOR_WORDS = ("and then", "after that", "and", "then", "once", "when", "if", "but", "so")
_SPLIT = re.compile(r"(?:\s*[;,\n]+\s*|\s+(?:and\s+then|after\s+that|and|then|once|when|if|but|so)\s+)", re.I)
_CONNECTOR_FOUND = re.compile(r"[;,\n]|\b(?:and\s+then|after\s+that|and|then|once|when|if|but|so)\b", re.I)

# Clause-initial reporting/notification markers.  These describe what to say, never what to do.
_REPORT_START = re.compile(
    r"^(?:tell\s+me|let\s+me\s+know|keep\s+me\s+posted|report(?:\s+back)?|confirm|notify\s+me|"
    r"inform\s+me|show\s+me|update\s+me|say)\b", re.I,
)
_REPORT_ANCHOR = re.compile(
    r"\b(?:tell\s+me|let\s+me\s+know|keep\s+me\s+posted|report(?:\s+back)?|confirm|notify\s+me|"
    r"inform\s+me|show\s+me|update\s+me)\b", re.I,
)

# Polite / temporal modifiers that may precede the verb (spec section 1).
_PREFIX = re.compile(
    r"^(?:(?:please|kindly|now|also|just|first|next|go\s+ahead\s+and|could\s+you|can\s+you|would\s+you|"
    r"will\s+you|i\s+need\s+you\s+to|i\s+want\s+you\s+to|you\s+should)\s+)+", re.I,
)
_NEGATION = re.compile(r"^(?:do\s+not|don't|dont|never|no\s+need\s+to|without|avoid)\b", re.I)
_TRAILING_FILLER = re.compile(
    r"(?:\s+(?:now|please|immediately|right\s+away|for\s+me|again|today|asap|straight\s+away))+$", re.I,
)
_LEADING_OPEN_NOISE = re.compile(r"^(?:up\s+)?(?:the\s+)?(?:app(?:lication)?\s+)?", re.I)
_LEADING_DB_NOISE = re.compile(r"^(?:that\s+)?(?:the\s+)?", re.I)
_LEADING_DEPLOY_NOISE = re.compile(r"^(?:to\s+|onto\s+|on\s+)?(?:the\s+)?", re.I)
_DB_OBJECT = re.compile(r"^database(?:\s+status)?$", re.I)
_DEPLOY_TARGET = re.compile(r"^(staging|production)$", re.I)
_AMBIGUOUS = {"it", "this", "that", "them", "these", "those", ""}

# ---- reporting-intent lexicon (spec section 11) --------------------------------------------------------------------
_REPORT_FAILURE = re.compile(r"\b(?:fail|fails|failed|failing|failure|broke|broken|error|errors)\b", re.I)
_REPORT_COMPLETION = re.compile(r"\b(?:complete|completes|completed|completion|done|finish|finished|finishes|gone|over)\b", re.I)
_REPORT_SUCCESS = re.compile(r"\b(?:work|works|worked|working|succeed|succeeds|succeeded|success|successful|opens|opened)\b", re.I)
_REPORT_STATUS = re.compile(r"\b(?:status|reachable|unreachable|healthy|unhealthy|up|down|live|alive|available|unavailable|state)\b", re.I)
_REPORT_RESULT = re.compile(r"\b(?:result|results|outcome|what\s+happened|response|output)\b", re.I)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def split_clauses(prompt: str) -> list[str]:
    """Deterministic connector segmentation.  Empty fragments are discarded."""
    return [c for c in (part.strip() for part in _SPLIT.split(prompt or "")) if c]


def reporting_intent(prompt: str) -> tuple[str, str | None]:
    """Reporting intent for the whole request.  Never yields an executable action."""
    anchor = _REPORT_ANCHOR.search(prompt or "")
    if anchor is None:
        return "NONE", None
    tail = (prompt or "")[anchor.start():]
    for pattern, intent in (
        (_REPORT_FAILURE, "REPORT_FAILURE"),
        (_REPORT_COMPLETION, "REPORT_COMPLETION"),
        (_REPORT_SUCCESS, "REPORT_SUCCESS"),
        (_REPORT_STATUS, "REPORT_STATUS"),
        (_REPORT_RESULT, "REPORT_RESULT"),
    ):
        if pattern.search(tail):
            return intent, _clean(tail)
    return "REPORT_RESULT", _clean(tail)


def _open_clause(rest: str) -> dict:
    target = _TRAILING_FILLER.sub("", _LEADING_OPEN_NOISE.sub("", rest).strip()).strip().rstrip(".!?").strip()
    if target.casefold() in _AMBIGUOUS:
        return {"primary_action": "OPEN_APP", "target": target or None, "target_resolved": False,
                "allowed_tool": None, "expected": None, "reason": "open_target_ambiguous"}
    urls = URL_RE.findall(target)
    if urls and urls[0].rstrip(".,;:!?") == target:
        return {"primary_action": "OPEN_URL", "target": target, "target_resolved": True,
                "allowed_tool": OPEN_URL, "expected": {"url": target}, "reason": "explicit_open_url"}
    expected, _ = canonicalize(OPEN_APP, {"name": target})
    return {"primary_action": "OPEN_APP", "target": target, "target_resolved": True,
            "allowed_tool": OPEN_APP, "expected": expected, "reason": "explicit_open_app"}


def _deploy_clause(rest: str) -> dict:
    target = _TRAILING_FILLER.sub("", _LEADING_DEPLOY_NOISE.sub("", rest).strip()).strip().rstrip(".!?").strip()
    match = _DEPLOY_TARGET.match(target)
    if match is None:
        return {"primary_action": "DEPLOY", "target": target or None, "target_resolved": False,
                "allowed_tool": None, "expected": None, "reason": "deploy_target_not_an_exact_environment"}
    return {"primary_action": "DEPLOY", "target": match.group(1).lower(), "target_resolved": True,
            "allowed_tool": DEPLOY, "expected": {"target": match.group(1).lower()}, "reason": "explicit_deploy"}


def _delete_clause(rest: str) -> dict:
    target = _TRAILING_FILLER.sub("", rest.strip()).strip().rstrip(".!?").strip()
    paths = PATH_RE.findall(target)
    if len(paths) == 1 and paths[0].rstrip("/") == target.rstrip("/"):
        return {"primary_action": "DELETE_PATH", "target": target, "target_resolved": True,
                "allowed_tool": DELETE, "expected": {"path": target}, "reason": "explicit_delete_exact_path"}
    return {"primary_action": "DELETE_PATH", "target": target or None, "target_resolved": False,
            "allowed_tool": None, "expected": None, "reason": "delete_target_not_exact_path"}


def _db_clause(rest: str) -> dict:
    obj = _TRAILING_FILLER.sub("", _LEADING_DB_NOISE.sub("", rest).strip()).strip().rstrip(".!?").strip()
    if _DB_OBJECT.match(obj):
        return {"primary_action": "GET_DATABASE_STATUS", "target": "database", "target_resolved": True,
                "allowed_tool": DB, "expected": {}, "reason": "explicit_database_read"}
    return {"primary_action": "UNKNOWN_ACTION", "target": obj or None, "target_resolved": False,
            "allowed_tool": None, "expected": None, "reason": "read_object_has_no_available_tool"}


def parse_clause(clause: str) -> dict:
    """Classify one clause as REPORTING, NEGATED, ACTION or NONE."""
    text = _clean(clause)
    core = _PREFIX.sub("", text).strip()
    row = {"clause": text, "core": core, "kind": "NONE", "primary_action": "NONE",
           "target": None, "target_resolved": None, "allowed_tool": None, "expected": None, "reason": "no_action_verb"}
    if not core:
        return row
    if _REPORT_START.match(core):
        return {**row, "kind": "REPORTING", "reason": "reporting_clause"}
    if _NEGATION.match(core):
        return {**row, "kind": "NEGATED", "reason": "negated_clause"}
    match = re.match(r"^([A-Za-z']+)\b\s*(.*)$", core, re.S)
    if match is None:
        return row
    verb, rest = match.group(1).lower(), match.group(2).strip()
    if verb in OPEN_VERBS:
        return {**row, "kind": "ACTION", "verb": verb, **_open_clause(rest)}
    if verb in DEPLOY_VERBS:
        return {**row, "kind": "ACTION", "verb": verb, **_deploy_clause(rest)}
    if verb in DELETE_VERBS:
        return {**row, "kind": "ACTION", "verb": verb, **_delete_clause(rest)}
    if verb in DB_VERBS:
        return {**row, "kind": "ACTION", "verb": verb, **_db_clause(rest)}
    if verb in UNSUPPORTED_VERBS:
        return {**row, "kind": "ACTION", "verb": verb, "primary_action": "UNKNOWN_ACTION",
                "reason": "requested_operation_has_no_available_tool"}
    return row


def parse(prompt: str) -> dict:
    """Full deterministic routing decision for one user request."""
    text = prompt or ""
    clauses = split_clauses(text)
    parsed = [parse_clause(clause) for clause in clauses]
    supported = [row for row in parsed if row["kind"] == "ACTION" and row["primary_action"] in SUPPORTED_ACTIONS]
    unknown = [row for row in parsed if row["kind"] == "ACTION" and row["primary_action"] == "UNKNOWN_ACTION"]
    intent, tail = reporting_intent(text)
    base = {
        "clauses": [row["clause"] for row in parsed],
        "clause_analysis": parsed,
        "connectors_present": sorted({m.group(0).strip().lower() for m in _CONNECTOR_FOUND.finditer(text)}),
        "reporting_intent": intent,
        "reporting_clause": tail,
        "action_clause_count": len(supported),
        "unknown_action_clause_count": len(unknown),
    }
    if len(supported) >= 2:
        return {**base, "primary_action": "MULTI_ACTION", "selected_clause": None,
                "multi_action": [{"primary_action": row["primary_action"], "target": row["target"]} for row in supported],
                "target": None, "target_resolved": False, "allowed_tool": None, "expected": None,
                "reason": "multiple_supported_executable_actions"}
    if supported:
        row = supported[0]
        return {**base, "primary_action": row["primary_action"], "selected_clause": row["clause"], "multi_action": [],
                "target": row["target"], "target_resolved": row["target_resolved"],
                "allowed_tool": row["allowed_tool"], "expected": row["expected"], "reason": row["reason"]}
    if unknown:
        row = unknown[0]
        return {**base, "primary_action": "UNKNOWN_ACTION", "selected_clause": row["clause"], "multi_action": [],
                "target": row["target"], "target_resolved": False, "allowed_tool": None, "expected": None,
                "reason": row["reason"]}
    return {**base, "primary_action": "NONE", "selected_clause": None, "multi_action": [], "target": None,
            "target_resolved": None, "allowed_tool": None, "expected": None, "reason": "no_explicit_action_intent"}

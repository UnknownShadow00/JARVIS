"""Task 13B10D — contradiction sweep across the frozen contract documents.

Documents are split into semantic units — a Markdown paragraph, table row or list item, or a
YAML line together with its parent key — because a contradiction is a property of a statement,
not of a hard-wrapped line.  For each concept that would contradict the contract if it were ever
*permitted*, every unit that mentions the concept is classified:

  PROHIBITIVE   the line forbids, denies or negates the concept (or records it as rejected)
  ADJUDICATED   the line is listed below with a written reason why it is not a contradiction
  UNRESOLVED    anything else — a candidate contradiction that must be fixed

Required outcome: 0 UNRESOLVED.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
DOCS = sorted(p for p in D.glob("*.md")) + [D / "agent-execution-contract.yaml"]

CONCEPTS = {
    "raw_operational_model_output_allowed": r"(?i)(raw model prose|model prose|MODEL_RAW|raw_model_prose|raw model output|model-raw)",
    "model_text_as_tool_result": r"(?i)(?:(?:tool[- ]result|TOOL_SUCCESS|TOOL_ERROR|tool output)[^.\n]{0,80}(?:model|prose|text)|(?:model|prose)[^.\n]{0,60}(?:tool[- ]result|shaped as a tool result|spoof))",
    "model_confirmation": r"(?i)(?:(?:model|prose|proceeding)[^.\n]{0,60}(?:confirm|confirmation)|confirmation[^.\n]{0,60}(?:model|prose))",
    "permission_bypass": r"(?i)(bypass|override|self-authorize|self authorise|without permission)",
    "user_fact_as_verified": r"(?i)(USER_FACT|USER_REPORTED|user-supplied|user-reported|user supplied)[^.\n]{0,80}(verified|verification)",
    "partial_multi_action": r"(?i)(partial(ly)? execut|multi[- ]action|multiple actions)",
    "tool_substitution": r"(?i)(nearest[- ]tool|substitut|mapped to a different tool|unrelated tool)",
}

# Markers that make a line prohibitive rather than permissive.
PROHIBITIVE = re.compile(
    r"(?i)(MUST NOT|SHOULD NOT|never|cannot|can not|no\s|does not|do not|did not|is not|are not|"
    r"not\s+(allowed|permitted|trusted|treated|be|substituted|silently|itself)|"
    r"forbidden|forbids|excludes|denial|denied|deny|blocked|contained|prevented|prevents|rejected|"
    r"remain distinguishable|suppress|:\s*false|=\s*false|:\s*\[\]|_forbidden|_allowed:\s*false|0\b|zero)")

ADJUDICATED = {
    # (document, exact line text fragment): reason it is not a contradiction
    "Conversational-lane permission of model prose is explicitly scoped to the non-operational lane":
        [r"CONVERSATIONAL.*raw_model_prose_may_be_final: true",
         r"model prose \*\*MAY\*\* be user-visible",
         r"model's own text may be returned",
         r"Conversational explanation may remain model-authored",
         r"conversational_explanation_in_authorized_lane",
         r"conversational-lane explanation",
         r"conversational explanation in authorized conversational lane",
         r"conversational_explanation",
         r"MAY be user-visible, subject to"],
    "Descriptions of the rejected alternative, recorded as history rather than as policy":
        [r"Trust model prose", r"Model-only structured tool behaviour",
         r"trusting model prose", r"could be trusted to report"],
    "Statements of measured containment (the unsafe behaviour happened and was contained)":
        [r"unsafe", r"fabricat", r"spoof", r"would have allowed"],
    "Section heading or metric name; names the concept without granting it":
        [r"^#+\s", r"confirmation_bypass, invented_destructive_target",
         r"multi-action detection"],
    "Describes a cost or a non-conforming implementation, not a permitted behaviour":
        [r"will read more narrowly than free model prose",
         r"A production implementation that reorders"],
    "Ownership table: the concept appears in the 'must never own' column":
        [r"passing model prose through on an operational turn"],
    "Future work explicitly gated behind separate authorization and validation":
        [r"MAY\*\* be introduced only through"],
    "Refers to the deterministic layer substituting its own template, not to tool substitution":
        [r"substituted the missing-context line"],
}


def adjudication_for(line: str) -> str | None:
    for reason, patterns in ADJUDICATED.items():
        for pattern in patterns:
            if re.search(pattern, line):
                return reason
    return None


def markdown_units(text: str):
    """Yield (first_line_number, unit_text) for paragraphs, table rows and list items."""
    unit: list[str] = []
    start = 0
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        standalone = line.startswith("|") or line.startswith("- ") or line.startswith("* ") or line.startswith("#")
        if not line or standalone:
            if unit:
                yield start, " ".join(unit)
                unit = []
            if line and standalone:
                yield number, line
            continue
        if not unit:
            start = number
        unit.append(line)
    if unit:
        yield start, " ".join(unit)


def yaml_units(text: str):
    """Yield (line_number, 'parent_key: line') so a flag is read with the block it belongs to."""
    parent = ""
    item = ""
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0 and line.endswith(":"):
            parent, item = line[:-1], ""
        match = re.match(r"-\s+name:\s*(\S+)", line)
        if match:
            item = match.group(1)
        prefix = " :: ".join(x for x in (parent, item) if x)
        yield number, (f"{prefix} :: {line}" if prefix else line)


rows = []
for doc in DOCS:
    body = doc.read_text()
    units = yaml_units(body) if doc.suffix == ".yaml" else markdown_units(body)
    for number, text in units:
        if not text or text.startswith("|---"):
            continue
        for concept, pattern in CONCEPTS.items():
            if not re.search(pattern, text):
                continue
            if PROHIBITIVE.search(text):
                verdict, reason = "PROHIBITIVE", ""
            else:
                reason = adjudication_for(text)
                verdict = "ADJUDICATED" if reason else "UNRESOLVED"
            rows.append({"document": doc.name, "line": number, "concept": concept,
                         "verdict": verdict, "reason": reason, "text": text[:220]})

by_verdict = {v: [r for r in rows if r["verdict"] == v] for v in ("PROHIBITIVE", "ADJUDICATED", "UNRESOLVED")}
summary = {
    "documents_reviewed": [d.name for d in DOCS],
    "concept_mentions_examined": len(rows),
    "prohibitive": len(by_verdict["PROHIBITIVE"]),
    "adjudicated": len(by_verdict["ADJUDICATED"]),
    "unresolved_contradictions": len(by_verdict["UNRESOLVED"]),
    "by_concept": {c: sum(1 for r in rows if r["concept"] == c) for c in CONCEPTS},
}
(D / "consistency-review.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n")
print(json.dumps(summary, indent=2))
for row in by_verdict["UNRESOLVED"]:
    print(f"UNRESOLVED {row['document']}:{row['line']} [{row['concept']}] {row['text']}", file=sys.stderr)
sys.exit(1 if by_verdict["UNRESOLVED"] else 0)

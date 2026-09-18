"""Section 38 counterfactual review.

For every scored turn that did not meet its frozen utility expectation, record what the
deterministic layer actually had available: the candidate set it built, the candidate it
selected, the frozen provenance snapshot, and whether any *already eligible* candidate would
have satisfied the expectation.  A failure that no eligible candidate could have satisfied is a
frozen-state limitation, not a selection bug; a failure that an eligible candidate could have
satisfied is a selection bug and is reported as such.
"""
from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path

E = Path("/home/jarvis/.hermes-poc/evidence/task13b10c5-operational-utility")
UTIL = json.loads((E / "utility-expectation.json").read_text())["expectations"]
rows = json.loads((E / "per-turn-ledger.json").read_text())

raw_by_id: dict[str, dict] = {}
for path in sorted(glob.glob(str(E / "raw-*-r*-a1.json"))):
    block = json.loads(Path(path).read_text())
    for case in block["cases"]:
        for turn in case["turns"]:
            raw_by_id[f"{block['suite']}:{case['scenario']}-r{block['repetition']}-t{turn['turn']}"] = turn

findings = []
for row in rows:
    if row["utility"]:
        continue
    turn = raw_by_id[row["id"]]
    expectation = UTIL[row["base_id"]]
    needle = expectation.get("require_substring", "")
    candidates = turn.get("response_candidates") or []
    satisfying = [c for c in candidates
                  if c.get("source") in expectation["accept"] and needle in (c.get("text") or "")]
    findings.append({
        "id": row["id"], "base_id": row["base_id"], "user": row["user"],
        "expected_sources": expectation["accept"], "required_detail": needle or None,
        "obligation": row["response_obligation"], "final_source": row["final_source"],
        "visible_text": row["visible_text"],
        "candidates_built": [{"obligation": c.get("obligation"), "source": c.get("source"),
                              "reason": c.get("reason"), "text": c.get("text")} for c in candidates],
        "eligible_candidate_would_have_satisfied": bool(satisfying),
        "verdict": "SELECTION BUG — an eligible candidate met the expectation and was not chosen"
                   if satisfying else
                   "FROZEN STATE LIMITATION — no candidate the frozen state supports could meet the expectation",
        "ledger_snapshot": turn.get("ledger_snapshot"),
        "trusted_results": [event.get("result") for event in turn.get("tool_ledger", [])
                            if isinstance(event.get("result"), dict)],
    })

summary = {
    "failing_turns": len(findings),
    "distinct_failing_cases": sorted({f["base_id"] for f in findings}),
    "selection_bugs": sum(f["eligible_candidate_would_have_satisfied"] for f in findings),
    "frozen_state_limitations": sum(not f["eligible_candidate_would_have_satisfied"] for f in findings),
    "by_case": dict(Counter(f["base_id"] for f in findings)),
}
(E / "counterfactual-review.json").write_text(json.dumps({"summary": summary, "findings": findings}, indent=2) + "\n")
print(json.dumps(summary, indent=2))

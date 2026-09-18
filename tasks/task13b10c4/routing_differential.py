"""C3 vs C4 request-classification differential over every reused scored prompt (no model)."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

C3 = Path("/home/jarvis/.hermes-poc/evidence/task13b10c3-provenance-lock")
C4 = Path(__file__).resolve().parent


def load(root: Path):
    for name in [m for m in sys.modules if m.startswith(("task13b10", "lane", "provenance_lock"))]:
        del sys.modules[name]
    sys.path.insert(0, str(root))
    try:
        guard = importlib.import_module("task13b10c_proposal_guard")
        classifier = importlib.import_module("task13b10c2_classifier")
        return guard, classifier
    finally:
        sys.path.pop(0)


scenarios = json.loads((C4 / "scenarios.json").read_text())
rows = []
for key in ("orig_cases", "g_cases", "h_sessions", "i_sessions", "j_sessions", "k_sessions"):
    suite = "orig" if key == "orig_cases" else key[0]
    for case in scenarios[key]:
        for index, prompt in enumerate(case["turns"], 1):
            rows.append({"suite": suite, "id": case["id"] + "-t" + str(index), "prompt": prompt})


def snapshot(guard, classifier, extra: bool) -> list[dict]:
    out = []
    for row in rows:
        rc = guard.classify_request(row["prompt"])
        entry = {"intent": rc["intent"], "allowed_tool": rc["allowed_tool"], "expected": rc["expected"],
                 "response_need": classifier.classify_response_need(row["prompt"])["class"]}
        if extra:
            entry.update({"primary_action": rc["primary_action"], "reporting_intent": rc["reporting_intent"],
                          "routing_target": rc["routing_target"], "target_resolved": rc["target_resolved"],
                          "clauses": rc["clauses"], "connectors_present": rc["connectors_present"]})
        out.append(entry)
    return out


g3, c3 = load(C3)
before = snapshot(g3, c3, False)
g4, c4 = load(C4)
after = snapshot(g4, c4, True)

out = []
for row, b, a in zip(rows, before, after):
    changed = {k: [b[k], a[k]] for k in ("intent", "allowed_tool", "expected", "response_need") if b[k] != a[k]}
    out.append({**row, "c3": b, "c4": a, "changed": changed or None})
changed_rows = [r for r in out if r["changed"] and r["suite"] != "k"]
k_rows = [r for r in out if r["suite"] == "k"]
summary = {
    "total_prompts": len(out),
    "reused_a_to_j_prompts": len(out) - len(k_rows),
    "new_k_prompts": len(k_rows),
    "reused_rows_changed": len(changed_rows),
    "reused_changed_ids": [r["id"] for r in changed_rows],
    "reused_response_need_class_changes": [r["id"] for r in changed_rows if "response_need" in r["changed"]],
    "reused_intent_name_only_changes": [r["id"] for r in changed_rows if set(r["changed"]) == {"intent"}],
}
(C4 / "routing-differential.json").write_text(json.dumps({"summary": summary, "rows": out}, indent=2) + "\n")
print(json.dumps(summary, indent=2))

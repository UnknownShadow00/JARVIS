"""Group every operational raw Granite draft by unique text for manual safety review."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

E = Path("/home/jarvis/.hermes-poc/evidence/task13b10c4-action-routing")
drafts = json.loads((E / "operational-draft-review.json").read_text())
groups = defaultdict(list)
for row in drafts:
    groups[(row["base_id"], row["text"])].append(row)
out = []
for (base_id, text), rows in sorted(groups.items()):
    out.append({"base_id": base_id, "count": len(rows), "old_detector": sorted({r["old_detector"] for r in rows}),
                "ids": [r["id"] + "#d" + str(r["draft"]) for r in rows], "text": text})
(E / "operational-draft-groups.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"operational_drafts": len(drafts), "unique_texts": len(out),
                  "unique_texts_by_case": {k: sum(1 for g in out if g["base_id"] == k) for k in sorted({g["base_id"] for g in out})}}, indent=2))

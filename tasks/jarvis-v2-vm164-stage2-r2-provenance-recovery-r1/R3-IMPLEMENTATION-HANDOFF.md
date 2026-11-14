# R3 implementation handoff — offline only

**Provenance blocker resolved. R3 remediation has not begun.**

Use exact baseline commit `5088a240943f2d39b67ca7d528ea8e5f7e51d6f9` (tree `089ec4e0364578548cceff4abadd65adfbac93dd`), parent `4c0f9ff666ac3bbce5f695a6b071e42320911652`, on branch `codex/jarvis-v2-stage2-r2-provenance-baseline-r1`. Verify it with tools/verify_baseline.py and the independent audit hash anchor before modifying any source. The commit is a new recovery of reviewed bytes, not a retroactive original R2 implementation commit.

The independent rejection is committed at tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2/. Read REPORT.md, FINDINGS.md, tests/test_independent.py and FIRST-SUPERVISED-ACTION.json. The prior blocked R3 folder remains in canonical and includes the sixteen-row traceability analysis; it was deliberately not copied into the baseline commit.

For a later separately initiated R3 engineering session, first confirm the proposed branch/worktree do not already exist. Then the intended local creation command is:

```text
git -c core.hooksPath=/dev/null -c core.symlinks=true worktree add -b codex/jarvis-v2-vm164-stage2-safety-remediation-r3 '../JARVIS-v2-vm164-stage2-safety-remediation-r3' 5088a240943f2d39b67ca7d528ea8e5f7e51d6f9
```

Run from canonical JARVIS root. This command is **not executed by provenance recovery**. Preserve the new baseline and all historical packets. Do not reuse or overwrite the canonical blocked R3 report. Implement the candidate in the new worktree's new versioned task folder as the later R3 task directs.

All sixteen failures remain open: stale captures/collision state, contradictory cancellation timing, post-expiry callback acceptance, contradictory systemd/process results, incomplete evidence sealing and R21 root-path rejection. evidence/KNOWN-FAILURE-EQUALITY.json lists the exact methods. R3 must preserve each before-fix reproducer, correct the acceptance rule, add adjacent adversarial regressions and demonstrate per-finding after-fix rejection. Reproducing the same expected baseline failures in this task does not resolve them.

Run the original 71, prior audit 30, regression/design 95 and latest 51 from the committed sources plus new R3 tests. Use separate output paths; legacy runners write within historical evidence folders and some contain absolute canonical references. The recovery wrapper shows how to relocate output and the one legacy fixture read without editing reviewed assertions. Fresh checkouts must preserve the five existing historical symlinks; do not follow their targets or install them.

No Stage 2 authorization follows from this handoff. Actual systemd257 semantics, clock mapping, WakeSystem, cancellation/cleanup timing, fresh nobody privilege/credential denial and host custody remain unqualified. The first eventual host action remains the independently reviewed read-only R01, only after corrected R3 review and separate finite human authorization. No host action now.

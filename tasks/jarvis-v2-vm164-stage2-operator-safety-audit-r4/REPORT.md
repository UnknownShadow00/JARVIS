# Independent R4 acceptance audit

**Verdict: REJECT.** R4 corrects the15 specific historical probe failures, but the complete evidence state machine still admits contradictory or incomplete evidence. Ten new independent failures in three defect groups prevent presenting this revision for human Stage2 authorization.

Reviewed commit `5c5d5c2543ed469025ec6cf06b0545c9bdb5eaa6`, tree `b0bfd1ea642a9d51ac580b152f2aa50c60aceb87`, parent `d153ccd001d1f673b6110782da288e6d114d8762` on `codex/jarvis-v2-stage2-safety-remediation-r4`. The reviewed worktree is clean. Source SHA256 `14ca4bdcc1f6b041914f1fd015ae7227bbd9ad06c66bb52b9665212a1eba39a7` and packet SHA256SUMS digest `7eea70156042705c61b4554491b263fbe8bbf74ade3e045822516e0b3a67cf95` match. Changes relative to R3 are237 new packet files plus its isolated completion-log append. No unrelated tracked application changes or runtime actuator were introduced.

The original independent39 harness reproduced24PASS/15FAIL against exact R3. All15 targeted historical cases pass against R4 with disclosed schema-compatible fixture ports; individual inputs, original acceptance and corrected rejection are traced. All439 engineering-reported distinct tests reproduce as passing. The42 fresh independent methods yield32PASS/10FAIL/0ERROR/0SKIP. The combined current-target result is471PASS/10FAIL across481 distinct methods. The twelve-case synthetic record passes; that is not live qualification.

Remaining authorization blockers (all MEDIUM assurance severity):

- **R4-A01:** Guard execution can start before timer creation, during an untouched waiting interval, or before the timer trigger. Complete final validation and per-case anchoring accept these contradictions.
- **R4-A02:** Plain exit journal rows accept malformed/prior-generation invocation IDs or conflicting foreign/owned unit attribution. Favorable exit text overrides contradictory raw provenance.
- **R4-A03:** A later retained full-journal capture may omit a previously required diagnostic while the prior anchor/ledger remain unchanged. Both new-generation admission and complete result validation accept the incomplete history.

Group verdicts: R3-A01 FAIL; R3-A02 FAIL; R3-A03 FAIL; R3-A04 PASS; R3-A05 PASS; R3-A06 FAIL. PASS for an exact old test does not mean its expanded security contract is complete. No host compromise or VM operation is demonstrated; the defects invalidate qualification-assurance claims.

Independent preservation reconciliation:49,248 path entries checked—48,840 regular files with content/mode and408 literal symlink targets. These cover VM164 task packets across the canonical repository and two predecessor worktrees, including repeated copies and a large lab-readiness tree. They are not49,248 unique application source files or a whole-host audit. Exact per-root/per-packet counts are in COVERAGE-RECONCILIATION.json. Local content equality passes; independently protected custody is not established. Tracked canonical application preservation is supported by Git diff/status; untracked application files outside this snapshot lack historical hash coverage. The canonical preexisting log is preserved; only the required audit completion append is added.

The proposed twelve cases remain non-root/non-VM and have finite bounds, explicit expiry, scoped cleanup and unknown-host stop rules. However, the common guard/journal/retention gaps prevent a coherent complete procedure. Real command serialization/precision, WakeSystem/clock mapping, cancellation/cleanup latency, actual failure transactions, fresh host custody and the strict retained-prefix capture budget remain unqualified. The cleanup planner versus mandatory original stop-receipt path also needs explicit feasibility resolution.

Recommendation: repair these reproductions through one coherent causal and immutable-evidence model; consider a separately reviewed simpler Stage2 workflow rather than accumulating divergent validators. No live command, host maintenance, VM access, credentials, network, packages, JARVIS executor or Gate6K was used. Tests ran only in disposable synthetic copies with effect-denying hooks and bounded outer Python processes. Reviewed source and historical evidence remain unchanged.

Precise next operator action: offline remediation/design review of R4-A01..A03, followed by another independent acceptance audit. The unchanged read-only R01 argv is preserved in FIRST-SUPERVISED-ACTION.json but remains NOT AUTHORIZED. Required eventual preconditions and hard stops are documented in PROCEDURE-REVIEW.md and GO-NO-GO.md.


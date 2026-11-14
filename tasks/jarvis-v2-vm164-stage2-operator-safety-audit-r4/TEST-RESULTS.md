# Independent test results

| Suite | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|
| Original preparation |71|0|0|0|
| Earlier audit against R4 |30|0|0|0|
| R2 design/regression |95|0|0|0|
| R2 independent probes against R4 |51|0|0|0|
| R3 adversarial suite against R4 |92|0|0|0|
| Latest historical probe port against R4 |39|0|0|0|
| R4 engineering regressions |61|0|0|0|
| Reported candidate total |439|0|0|0|
| NEW independent state-machine probes |32|10|0|0|
| Current-target distinct total |471|10|0|0|

All12 synthetic scenarios validate in the positive record. They are scenarios, not12 additional unique methods or live observations. All mandatory suites completed. The10 new failures are unsafe acceptance assertions, not expected successful negative cases.32 fresh passes comprise3 positive controls and29 correctly rejected negative cases.

Original unchanged R3 independent harness:39 methods,24PASS/15FAIL, process exit1. Targeted15 replay on R3:0PASS/15FAIL; on R4:15PASS/0FAIL. The targeted runner exits0 for the exact expected historical failure set, so process exit must not be mistaken for a positive qualification result. Original earlier audit20PASS/10FAIL and original catalogue design0PASS/3FAIL are deliberately retained by the baseline wrappers.

Across recorded method executions, including those repeats and deliberate historical failures:563 executions,510 passes,53 failures,0 errors,0 skips. This differs from481 distinct current-target methods (471/10). Two initial exploratory pure-validator calls returned unsafe PASS and were subsequently formalized; they are not counted as unittest methods. No mandatory suite is missing or skipped.

Raw logs, exact test IDs, per-process argv/timeouts/exits, input patches and observed returns are in evidence/. The seven primary suite processes have240s outer caps; all candidate wrappers exit0, original39 exits1, fresh42 exits1, targeted wrappers exit0 for their explicitly expected results. No assertion was weakened. Original independent source was retained byte-for-byte; the R4 fixture port's10 assertion/fail AST calls match. Exact diff documents its timestamp and legitimate-history adaptations.

Reproduce on disposable copies. WORKSPACE.json records the actual copy locations. Run tests/run_fresh.py with isolated Python (`python3 -I -B -S`) and a240s outer cap; it denies subprocess/network/NSS/live-path access internally and writes only this audit packet. Its baseline comes from the exact candidate copy. For the inherited suites, use the six replay_after.py phases recorded in SUITE-PROCESSES.json in a disposable copy; never run write-producing wrappers in the reviewed worktree. Recreate copies using the archived setup transcript if the temporary directory is gone, updating only the new audit copy's WORKSPACE.json. Preserve these audit results.

Integrity gates separately passed exact Git identity, R4 source/237-file manifest,207 audit-pinned predecessor files, original preparation29/sealed implementation96 inventories, and49,248 snapshot entries. They establish local content integrity, not protected external custody or real timer behavior.


A non-test post-log integrity-helper invocation exited1 with SyntaxError while adapting the audit helper to verify the mandated log append. The semicolon/newline typo was corrected only in this audit helper and the same integrity gate rerun. This is a disclosed audit-tooling error, separate from the0 errors in formal test suites; no target source or assertion was modified. See VERIFY-HARNESS-ERROR.json.

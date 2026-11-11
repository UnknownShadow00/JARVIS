# Fresh test results

Status: **PASS_OFFLINE_FINAL_INTEGRATION_REHEARSAL_PENDING_REVIEW**. All results in this packet were freshly executed; previous reports establish approval provenance only.

| Suite | Pass | Fail | Error | Skip | Incomplete | Gate / child exit |
|---|---:|---:|---:|---:|---:|---|
|coverage|217|0|0|0|0|0 / 0|
|reconciliation|66|0|0|0|0|0 / 0|
|r3|19|0|0|0|0|0 / 0|
|r2|45|0|0|0|0|0 / 0|
|original|32|0|0|0|0|0 / 0|
|existing|507|0|0|0|0|0 / 0|

Unique total886; seed16401. Repeats use seed42:217+66+19+45+32=379; existing507 is not repeated. No repeat or positive execution inside a contract is counted as another unique test. Exact trusted node IDs mapped to machine evidence IDs are in VERIFICATION.json; per-case setup/call/teardown and durations are in acceptance/*.json. All missing/unexpected counts are0, collection skips/deselections0 and sessions complete.

| Contract group | Expected-outcome checks | Outcome |
|---|---:|---|
|Gate before/after, collection, interruption, manifest, phase, skip/xfail and malformed evidence|22|22 pass|
|Retained leak/crash/partial/exit/count/skip negatives|14|14 pass|
|Enrollment/module/parameter/substitution/exclusion/regeneration adversaries|11|11 pass|
|Additional audit attacks, replayed on snapshot clones|12|12 reject safely|

Each group's SUMMARY.json records actual process exits; these are contract evaluations, not additional distinct pytest passes. Gate22 includes two positive controls: the intentionally defective historical R2 runner reproduces a false PASS, and a full legitimate45-case run passes. Adversaries11 includes a positive217-case regeneration-trap run; the proposal utility is never invoked. All intentionally negative current-gate cases have non-PASS and nonzero exits; failing JSON is retained, not suppressed.

The exact historical defect: expected45; R2 executed31, reported0 skips, PASS/exit0. The candidate executed31, reported0 test-level skips but1 collection skip, required_missing14, FAIL/exit1 despite child exit0. All14 absent identities are independently reconstructed in VERIFICATION.json. Additional import-time dictation skip yielded211/217 passes and6 missing, correctly rejected. Late substitution after collection recording yielded0 missing collection identities but incomplete execution, correctly rejected. This distinguishes collection proof from actual phase completion.

Scheduler-hardening module14 cases include installed APScheduler3.11.3 executor/store cleanup, cancellation/retry/concurrency, and explicitly synthetic protocol/future fixtures. They are not14 separate production backend qualifications. The45 R2 set also includes31 protocol cases. Existing/reconciliation/coverage include authenticated readiness and rejected credentials, ancestry replacement, WebSocket bounded cleanup/ownership, privacy/defaults and authorization failures. No unsafe or out-of-scope module is used as positive evidence.

Exact commands/exits: EXECUTION.json, AUDIT-ATTACK-EXECUTION.json, acceptance/RESULT.json and contract summaries. No mandatory failure/error/skip/incomplete case occurred. Deliberate negatives remain negative evidence. Acceptance evidence integrity123 hashes plus the outer packet hash manifest verified locally.

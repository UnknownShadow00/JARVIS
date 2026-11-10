# Final exact-source test results

Final acceptance is under acceptance/. All five suites have successful complete setup/call/teardown, normal sessions, zero required missing/unexpected identities, and real child/gate exits0. Source inventories before/after match current bytes. VERIFICATION.json binds digests and totals.

| Suite | Pass | Fail | Error | Skip | Incomplete | Gate exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| reconciliation | 66 | 0 | 0 | 0 | 0 | 0 |
| r3 | 19 | 0 | 0 | 0 | 0 | 0 |
| r2 | 45 | 0 | 0 | 0 | 0 | 0 |
| original | 32 | 0 | 0 | 0 | 0 | 0 |
| existing | 507 | 0 | 0 | 0 | 0 | 0 |

**669 distinct positives.** Additional66 comprise36 release-boundary,24 UE5 and6 module-policy/example tests. The162 seed42 cases (66+19+45+32) repeat the same case sets and are excluded from669. Assertions of all positive IDs, complete successful phases and source hashes are independently recomputed, not inferred from exit0.

Actual stock APScheduler3.11.3 is exercised in45 R2 cases. Reconciliation covers post-create ancestry, same-UID SQLite swap fixture, blank-token worker startup,401 refusal, websocket lifetime/capacity/cancellation, opted-out resource/example defaults and all12 ready client cases. Existing507 also cover durable receipts/recovery, execution admission and cancellation. No real provider, hardware or custom backend qualification is implied.

Additional final contracts:22 actual CLI gate contracts,14 retained negative CLI modes and4 actual enrollment CLI refusals. Negative checks intentionally produce FAIL/BLOCKED and nonzero nested exits; they are excluded from positive totals. enrollment-final/ rejects added/deleted/modified module and policy tampering before child imports. Sanitization marker checks pass. The22 matrix excludes the historical ignore-directory traversal fixture because it deliberately deletes fixture directories needed by the new reconciliation mount contract; unit R3 evidence and enrollment/source-set checks remain fail-closed for omission/deselection. Do not claim the old23 matrix was reproduced unchanged.

Fresh before evidence (compatibility-existing.json) reproduces495 pass/12 fail, zero errors/skips/incomplete, exit1. All12 cases are mapped in TWELVE-FAILURES.json; they fail at missing parser choice before request assertions. This is a diagnostic on unreconciled five-file bytes, NOT acceptance of the candidate. The same507 selected cases now all pass.

Historical development alternatives remain in preserved-development-tests/ and are not added to passing totals. An initial reconciliation proposal had63 pass/2 skips because historical fixtures were absent; the final namespace supplies those exact public fixtures. An intermediate65-pass run was correctly rejected for four randomly varying URL parameter IDs; an explicit12-name ID list preserves randomized inputs and assertions while making identities stable. These failing/skipped records are retained. An attempted repeat into existing evidence paths was refused with FileExistsError; rerunning to fresh enrollment-final/ paths passed all4 checks. Final evidence supersedes intermediate root/verified directories; no failing test evidence is suppressed.

Reproduce from this worktree, choosing NEW destinations:

```sh
python3 -B tasks/jarvis-v2-baseline-reconciliation-r1/run_acceptance.py /tmp/jarvis-reconciliation-acceptance-new
python3 -B tasks/jarvis-v2-baseline-reconciliation-r1/check_enrollment_cli.py /tmp/jarvis-enrollment-negative-new
python3 -B scripts/propose_required_inventory.py --output /tmp/jarvis-inventory-candidate-new.json
```

The first two commands must succeed and their structured evidence must satisfy counts/identity/session checks. The last command is maintenance-only, does not update acceptance files or module policy, and requires independent review before any promotion. It is never called by acceptance. run_acceptance.py records exact commands/exits and before/after hashes; existing local dependencies and interpreter versions are in ENVIRONMENT.json. Package/advisory network operations, coverage percentages and broad typechecker/linter qualification were not performed.

# Exact final offline test results

Only verified-acceptance/ is final snapshot acceptance. All positive cases have successful setup/call/teardown, normal sessions, zero required missing/unexpected identities and gate exit0.

| Suite | Pass | Fail | Error | Skip | Incomplete | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| coverage | 217 | 0 | 0 | 0 | 0 | 0 |
| reconciliation | 66 | 0 | 0 | 0 | 0 | 0 |
| r3 | 19 | 0 | 0 | 0 | 0 | 0 |
| r2 | 45 | 0 | 0 | 0 | 0 | 0 |
| original | 32 | 0 | 0 | 0 | 0 | 0 |
| existing | 507 | 0 | 0 | 0 | 0 | 0 |
| coverage-seed42 | 217 | 0 | 0 | 0 | 0 | 0 |
| reconciliation-seed42 | 66 | 0 | 0 | 0 | 0 | 0 |
| r3-seed42 | 19 | 0 | 0 | 0 | 0 | 0 |
| r2-seed42 | 45 | 0 | 0 | 0 | 0 | 0 |
| original-seed42 | 32 | 0 | 0 | 0 | 0 | 0 |

**886 distinct positives**:217 new coverage +66 reconciliation +19 R3 +45 R2 +32 original +507 existing. Original669 node lists are unchanged; newly enrolled modules have217 explicit new identities. Seed42 repeats379 cases and is excluded from886. Other repeated fixture executions inside gate/adversarial checks are also excluded. No full-repository or production qualification is claimed.

Final additional contracts:22 retained gate contracts,14 retained negative contracts,11 new adversarial contracts. The11 comprise10 expected refusals plus1 successful no-regeneration trap. They are separate from positive counts; complete commands/exits are recorded in RESULT.json and each helper SUMMARY.json.

| New adversary | Gate status | Gate exit | Child exit | Missing required | Unexpected |
| --- | --- | ---: | ---: | ---: | ---: |
| added | BLOCKED | 2 | None | None | None |
| deleted | BLOCKED | 2 | None | None | None |
| changed | BLOCKED | 2 | None | None | None |
| policy_tamper | BLOCKED | 2 | None | None | None |
| manifest_tamper | BLOCKED | 2 | None | None | None |
| module_omission | FAIL | 1 | 0 | 6 | 0 |
| parameter_omission | FAIL | 1 | 0 | 1 | 0 |
| substitution | FAIL | 1 | 0 | 1 | 1 |
| unexpected_exclusion | BLOCKED | 2 | None | None | None |
| excluded_selection | BLOCKED | 2 | None | None | None |
| regeneration_trap | PASS | 0 | 0 | 0 | 0 |

Collection-time dictation-module omission runs211 instead of217 and reports6 missing; a parametrized omission runs216 with1 missing; same-count substitution runs217 but reports1 missing/1 unexpected. All have child exit0 while the gate exits nonzero. Added/deleted/changed modules, corrupted policy/manifest, a declassified requirement and an excluded selection are refused BEFORE a child is imported. JSON is checked for synthetic payload marker absence. The no-regeneration trap replaces the proposal utility with a raising sentinel; coverage still runs217/pass, demonstrating acceptance does not invoke it.

Five integrity checks use the exact driver hash routines on disposable inputs: unchanged control plus changed/added/deleted test and changed harness; all expected comparisons pass. Source input SHA256s match original before/after, snapshot after, and final current files. All suite report digests verify.

Historical diagnostics: initial.json has205 pass/12 fail. dictation-before.json isolates0 pass/1 fail on unchanged parent source. ported.json has216 pass/1 fail until the stale screenshot-success expectation is replaced by explicit disabled/no-call assertions; compatible.json has217 pass but intentionally fails the old reconciliation inventory, because it is a diagnostic rather than acceptance. None is counted in final886. Initial snapshot acceptance/ passed886 cases but two fault harnesses failed because copied read-only permissions prevented fixture mutation. Only fixture copies were made writable and the full snapshot rerun succeeded. Those results/logs are retained.

Reproduce final acceptance from a clean committed checkout with existing qualified dependencies and a NEW output path:

```sh
python3 -B tasks/jarvis-v2-baseline-coverage-remediation-r2/accept_snapshot.py /tmp/jarvis-coverage-acceptance-new
```

The driver records source commit/Git tree, input hashes, required inventory/module-policy digests, snapshot path, all subprocess commands/exits, positive identities/phases and unique/repeat counts. It does not regenerate authority. Snapshot is read-only and outputs separate, owner-restricted. An ordinary source writer or same-UID/root compromise is outside independent-custody guarantees. Review RESULT.json and evidence digests, not only exit0.


## Fresh checks during recovery

The committed sealed candidate `18a9d82c1` has the same 266 acceptance-input hashes as tested source `5e1d5af0c`. Fresh tests use the retained read-only snapshot and the existing networkless unprivileged bwrap launcher. `resume-verification/RESULT.json` records commands and all five subprocess exits (all zero); the per-suite JSON records child/gate exits and all phases.

| Fresh suite | Pass | Fail | Error | Skip | Incomplete | Child/gate exit |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| coverage | 217 | 0 | 0 | 0 | 0 | 0 / 0 |
| reconciliation | 66 | 0 | 0 | 0 | 0 | 0 / 0 |

The 11 adversarial contracts pass again: ten deliberately blocked/failed inner gates (expected exits 1 or 2) and one successful no-regeneration trap (exit 0); the contract driver exits 0. Five disposable-copy integrity probes pass. These are not new application-test identities. All 886 distinct final positives, 379 seeded repeats and the retained 22/14 contract matrices were independently verified from their identities, phases, exits, source bindings and SHA256 manifests before reusing unchanged results. Fresh 283 positives are repeats within 886, not 283 additional cases.

Read-only evidence verification is reproducible locally with `python3 -B tasks/jarvis-v2-baseline-coverage-remediation-r2/verify_recovered_evidence.py`. Fresh checks can be repeated using `run_resume_verification.py NEW_OUTPUT_DIRECTORY`; it refuses an existing output path. It requires the retained source snapshot. For another host, use the full `accept_snapshot.py` command above from a clean commit with qualified existing dependencies. No package installation or network fallback is included.

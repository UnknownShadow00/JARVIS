# Exact test results

Final verified checkout executions:

| Suite/target | Tests | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|---:|
| Original preparation | 71 | 71 | 0 | 0 | 0 |
| Prior audit against original R1 | 30 | 20 | 10 | 0 | 0 |
| Old design controls | 3 | 0 | 3 | 0 | 0 |
| Prior audit against committed R2 | 30 | 30 | 0 | 0 | 0 |
| R2 design | 3 | 3 | 0 | 0 | 0 |
| R2 regression | 92 | 92 | 0 | 0 | 0 |
| Latest independent probes against committed R2 | 51 | 35 | 16 | 0 | 0 |
| **Final executions** | **280** | **251** | **29** | **0** | **0** |

There are 247 distinct methods. Thirty audit methods and three design methods run against two targets, so they are not counted as newly distinct tests. The required positive R2/preparation groups total 196 passes. The latest 51 comprise 35 passes and the exact sixteen expected failures. Thirteen additional failures belong to the older R1 baseline. No final unexpected failure, error, skip or incomplete mandatory baseline gate remains.

KNOWN-FAILURE-EQUALITY.json lists each of the sixteen failure IDs and verifies exact equality with the independent rejection audit. None was fixed or reclassified as a passing safeguard. The negative runner exits 1. The other two runners exit 0 according to their explicit expected-old-failure rules. The retained twelve-case artifact passes the existing synthetic validator; this is not a live qualification or proof that its unsafe predicates are corrected.

## First attempt retained

Before the final executions, all seven suites ran once. Their results were 280 executions, 249 passes, 31 failures, zero unit errors or skips. The two extra failures were Controls.test_evidence_leaf_symlink_rejected and Extended.test_artifact_loading_hash_and_symlink: the additional wrapper misinterpreted descriptor-relative `cases` as a canonical-root dependency. The same guard caused the r2 runner to stop after its suites during artifact loading. The baseline runner separately stopped after its suites because inherited core.symlinks=false checked out five historical links as text. Thus there were **two non-test runner interruptions**; these must not be hidden by the zero unit-error count.

The first attempt's logs, negative result, counterexamples, module record, wrapper and interruption descriptions are preserved under evidence/attempt-1/. Residual disposable fixture data is retained under temporary/. We corrected only the new wrapper's cwd and exact link representations in the new worktree. Reviewed implementation, tests, expected assertions, commit and tree stayed unchanged.

Across both attempts: **560 executions, 500 passes, 60 assertion failures, zero unit errors/skips; two first-attempt runner interruptions**. Those repetitions are not 560 distinct tests. Final baseline checks are all complete. No R3 after-fix tests, live timer tests or host inspection was performed.

# Traceability — Task 13B11L-P6

Every claim in `FINAL-REPORT.md` to the artefact that carries it. Paths are relative to the
evidence bundle `/home/jarvis/.hermes-poc/evidence/task13b11l-p6-obligation-engine/` unless
stated.

| Claim | Source |
|---|---|
| production began at `ea0cb320…`, parent `9ace0e3a…`, clean, 0 untracked | `01-entry-verification.txt` |
| `execution.mode=legacy`, both Hermes flags false | `01-entry-verification.txt`, `07-no-live-wiring.txt` §7 |
| Hermes `2237be35…`, clean, 0 processes, Ollama idle | `01-entry-verification.txt` |
| four evidence bundles verified, 0 manifest failures each | `01-entry-verification.txt` |
| the R1/R2 "bundle digest" convention is not reproducible — reported, not reconciled | `01-entry-verification.txt`, `FINAL-REPORT.md` §"Flagged" |
| blocked 13B11L bundle unmodified, `ca703e18…` matching its loop-log value | `01-entry-verification.txt` |
| R1 bundle `source/classifier.py` == production `9ace0e3a` (`3a7db133…`) | `01-entry-verification.txt` |
| `dispatch.py` byte-identical to the sealed 13B11K version (`72155a7d…`) | `01-entry-verification.txt` |
| `a0cc4d3c` is an ancestor; only R1 and R2 follow it | `01-entry-verification.txt` |
| 41/41 unsupported verbs reach `UNKNOWN_ACTION` + `OPERATIONAL` before any P6 code | `sweep.json`, `02-frozen-matrix-seal.txt` |
| classifier version `"2"` | `sweep.json`, `08-security-review.txt` check 32 |
| the matrix was frozen with the module provably absent | `02-frozen-matrix-seal.txt` |
| matrix digests v1 `77a42976…`, v2 `e6c53692…`, v3 `4d5c788a…` | `02-frozen-matrix-seal.txt`, `obligation-matrix.json`, `matrix-versions.txt` |
| v1 → v2 additive: 10 added, 0 removed, 0 moved | `matrix-versions.txt` |
| the module agreed with the frozen table on the first run, 0 failures / 442 rows | `05-verification.txt` |
| the min-rank priority proof holds per row | `05-verification.txt`, `obligations_matrix_test.py` |
| baseline suite 3744 passed, golden 12/20, probe `fc68a0b0…` | `03-baseline.txt` |
| after: 5122 passed, 0 failed; golden 12/20 same eight; probe byte-identical | `06-after.txt` |
| 24 critical production files IDENTICAL | `09-critical-and-diff.txt` |
| 7 files added, 0 modified, 0 deleted | `09-critical-and-diff.txt`, `10-production-diff-stat.txt` |
| no module under `app/` imports the engine; 0 call sites | `07-no-live-wiring.txt` §§2, 4, 6 |
| the P4 confirmation machine still has zero importers | `07-no-live-wiring.txt` §3 |
| the module imports exactly eight names | `07-no-live-wiring.txt` §1, `obligations_non_activation_test.py` |
| security review 34/34 | `08-security-review.txt` |
| production commit `8a70d179…`, parent `ea0cb320…`, not pushed | `11-production-commit.txt` |
| workspace commit | `12-workspace-commit.txt` |
| final state clean, mode legacy, Hermes disabled | `13-final-state.txt` |
| D-P6-01 (DENY → refusal family) and D-P6-02 (TIMEOUT → failure family) | `docs/OBLIGATION_CONTRACT.md` §6 |
| the confirmation-import violation and its repair | `docs/DECISION_INPUT.md` §3, `docs/IMPLEMENTATION.md` |

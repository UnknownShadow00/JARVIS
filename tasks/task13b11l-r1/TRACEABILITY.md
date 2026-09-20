# Traceability — every claim to its source

Evidence bundle:
`/home/jarvis/.hermes-poc/evidence/task13b11l-r1-classifier-reconciliation/`

## Entry (§3)

| claim | source |
|---|---|
| production HEAD was `a0cc4d3c…`, clean, 0 untracked | `01-entry-verification.txt` |
| `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false` | `01-entry-verification.txt` |
| Hermes `2237be35…`, clean, 0 processes | `01-entry-verification.txt`, `13-final-state.txt` |
| blocked 13B11L produced no production commit | `01-entry-verification.txt` — `obligations.py` absent, 0 commits touching `app/execution` since `a0cc4d3c` |
| 13B11L evidence intact, 32/32 OK, digest `a480f23f…` | `01-entry-verification.txt`; re-verified identical in `13-final-state.txt` |
| all twelve prior 13B11 bundles verify, 0 failures | `01-entry-verification.txt` |

`pgrep -af hermes` initially reported 1 process; that was the invoking `bash -c`
wrapper matching its own command line (the 13B7A lesson). Counted by explicit pattern
and confirmed 0 by hand — recorded in `01-entry-verification.txt` and `IMPLEMENTATION.md`
rather than silently corrected.

## The frozen tables (§6, §7, §8, §11–§14, §16)

| claim | source |
|---|---|
| tables were frozen **before** the edit | `02-frozen-tables.json` `frozen_at_utc` 03:17:12Z; edit applied 03:2x — `03-frozen-table-seal.txt` proves `classifier.py` was still `c554b34a…` with 44 verbs and coverage 21/41 at seal time |
| table hashes | `03-frozen-table-seal.txt`: json `1fee47f8…`, txt `8bfb9b0d…`, script `d01343e9…` |
| expectations derived, not executed | `scripts/freeze.py` restates rules R-01/R-02/R-03 and the lane table independently; it never runs repaired code |
| the nine extra controls were predicted then measured, 9/9 | `02-frozen-tables.txt` (prediction in `extra_chat_rationale`, measurement in `controls_must_not_move.extra_chat`) |

## Baseline (§17–§20)

| claim | source |
|---|---|
| suite 3247 passed / 11 deselected / 0 failed | `03-frozen-table-seal.txt` |
| golden 12/20, eight named IDs | `03-frozen-table-seal.txt` |
| probe `fc68a0b0…d98291`, matches the 13B11K seal | `04-probe-before.json`; sealed value from `task13b11k-dispatcher-foundation/09-probe-before.json` |
| 24 critical file hashes | `03-frozen-table-seal.txt` |
| legacy slice `9c43b6f9…`, `registry.call` 4 | `03-frozen-table-seal.txt` |

## Collateral (pre-edit, read-only)

| claim | source |
|---|---|
| 2,041 distinct strings from 29 test files + golden | `05-collateral-scan.txt` |
| exactly 2 movers, both `scale`, both toward `OPERATIONAL` | `05-collateral-scan.txt` |
| 0 moved `OPERATIONAL → CONVERSATIONAL` | `05-collateral-scan.txt` |
| both frozensets restored, nothing written | `05-collateral-scan.txt` restore block; `scripts/collateral.py` opens no file for writing |

## The repair

| claim | source |
|---|---|
| 44 → 64, 26 → 40, exactly +20 / +14, nothing removed | `06-verification.txt`, `13-final-state.txt` |
| 25 insertions, 0 deletions in `classifier.py` | `10-production-diff-stat.txt`, `10-production-diff.patch` |
| anchors matched exactly once; file digest checked first | `scripts/patch.py` refuses otherwise |
| 41/41 sweep, was 21/41 | `06-verification.txt` |
| 14/14 sensitive, 6/6 not promoted | `06-verification.txt` |
| 8/8 chat, 9/9 extra chat, 8/8 supported controls unchanged | `06-verification.txt` (full seven-field signature) |
| 5/5 §16 prompts operational; 0 conversational; 0 dispatchable | `06-verification.txt` |
| 0 nearest-action substitutions, 0 invented targets | `06-verification.txt` |

## After (§15, §17–§21)

| claim | source |
|---|---|
| suite 3464 passed / 0 failed | `08-after.txt`, `13-final-state.txt` |
| golden 12/20, the same eight IDs | `08-after.txt`, `13-final-state.txt` |
| probe byte-identical to before and to the seal | `08-after.txt` (`cmp` none), `07-probe-after.json` |
| 24 critical files `IDENTICAL`, 0 unauthorized | `08-after.txt`, `13-final-state.txt` |
| legacy slice unchanged, `registry.call` still 4 | `08-after.txt`, `13-final-state.txt` |
| live request path imports no `app.execution` module | `09-no-live-wiring.txt` (parsed imports) |
| classifier imports unchanged, 0 `try`, no I/O | `09-no-live-wiring.txt`, `11-security-review.txt` |
| security review 30/30 | `11-security-review.txt` |
| Hermes clean, 0 processes, 0 references in the diff | `08-after.txt`, `13-final-state.txt` |
| no model was run | no Ollama process at any capture; the diff contains 0 hermes/ollama/model references |

`08-after.txt`'s grep listed `app/execution/classifier.py` as importing the classifier.
That is a scan artefact: the pattern `execution.classifier` has a regex dot that matched
the literal path `tests/execution/classifier_lexicon_reconciliation_test.py` inside the
comment this repair added. `09-no-live-wiring.txt` is the accurate measurement, taken
over parsed imports, and says so in its own header.

## Commit (§23)

| claim | source |
|---|---|
| one commit `9ace0e3a0855708d992467a179d08f6affef43e1` | `12-production-commit.txt` |
| parent is `a0cc4d3c…` | `12-production-commit.txt`, `13-final-state.txt` |
| not pushed | `13-final-state.txt` — 11 ahead of `origin/main` |
| 5 files, 1606 insertions, 12 deletions | `12-production-commit.txt` |

## Inherited from task 13B11L (not re-measured here)

The 21/41 "before" figure, the signature-overlap finding
(`SEPARABLE BY STRUCTURED STATE: False`) and the identification of the twenty verbs come
from `task13b11l-obligation-engine/05-verb-sweep.txt`,
`06-fix-simulation.txt` and `docs/P3_RECONCILIATION.md`. The 21/41 figure was
independently re-measured here against the unpatched classifier
(`02-frozen-tables.txt`, `05-collateral-scan.txt`) and agreed. The eight chat and eight
supported-action controls were taken verbatim from that task's `scripts/fixsim.py`.

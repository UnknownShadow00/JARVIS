# Simultaneously applicable guards and first-stop proof

| Guard / rule | Source and owner | Stage / frozen order | Counterexample truth | Stops? / reason |
|---|---|---|---|---|
| Common shape / C-00 | Admission V1, P7 | S01 / 1 | valid pair, no confirmation | no |
| C-00a non-dispatchable invocation | RESULT_REPLAY, P7 using passive action set | S01 / 1 | invocation OPEN_URL is dispatchable | no; tests invocation, not later route |
| C-00b turn/session | RESULT_REPLAY, P1 association | S01 / 1 | all IDs equal | no |
| S02 / S03 | classifier/router actual owners | 2 / 3 | general explanation / NONE | no component error |
| Operational signal | Agent Contract §4.3 / lane | final S04 / 6 | result present | forces OPERATIONAL; no action grant |
| Valid recording | adapter owner | S05 / 5 | zero proposals, valid root keys | no |
| NONE + zero | O-R1 UPDATED_GUARD_ORDER / P7 | deterministic branch / 7 | true | exits supported-action walk toward non-action terminal; does not specify a mismatch stop |
| Complete settled state required for P6 terminal | O-R1 guard order and failure model | terminal precondition | not established: result association incomplete | forbids normal P6 continuation; exact refusal stage/reason absent |
| NONE + nonzero | O-R1 cardinality and contradiction policy | branch / 7, stop labeled S06_CARDINALITY | false in minimal input, true in variants | first stop for every positive count: unexpected_proposal |
| Supported-route exactly-one | O-R1 P7-D02 | S06_CARDINALITY / 8 | prerequisite false | cannot use proposal_required merely because count is zero |
| C-04 route agreement | Admission V1 | S09 / 17, after C-01–C-03 | would fail on NONE != OPEN_URL | guard not reachable; cannot reorder automatically |
| P6 non-dispatchable yet executed | sealed obligations.py | S11 / 19, third contradiction family | would fail if result injected | injection is not admitted; cannot substitute for association |

For positive proposal count, first stopping guard is uniquely determined by frozen authority: unexpected_proposal before any current permission or result consumption. For zero count, the first blocking requirement is the completeness/association condition on the non-action P6 branch, but no source assigns its exact failure stage/reason or grants an early C-04 evaluation. Naming invariant_violation from the closed enum alone does not determine a stage or predicate. Python branch order cannot supply a missing contract.

Result remains caller-held evidence; no output may report success, claim a new execution, dispatch or return raw operational prose. Those safety constraints are fully determined. The remaining choice is a passive admission rejection boundary, not a permission/confirmation policy change.

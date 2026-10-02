# CONTRADICTION HANDLING — specified, not implemented

Normative: 13B11O-R1 `CONTRADICTION_POLICY.md` and `contradiction-corpus.json` (six static
cases, digest `d1f8e74966a934f3967cdfea71d9c968e6a058966e6cfa3b7798e265b0e5b012`), plus the
contradiction rows of the 13B11P-R1 admission matrix. All fail-closed. No corpus was
executed and no case was measured, because no pipeline exists.

The §43 required coverage, mapped to the frozen row that already specifies it. Rows
prefixed `C` are the 13B11O-R1 corpus; `A`/`B`/`C`/`X` rows are the 13B11P-R1 admission
matrix.

| §43 case | Frozen row | Expected disposition | Implementable now? |
|---|---|---|---|
| confirmation + result simultaneously | `X01` | `STOP(S01_INPUT, invalid_input)` | needs field 15 |
| wrong-session confirmation | `B03` | `STOP(S08_CONFIRMATION, confirmation_invalid)` | needs field 15 |
| wrong-action confirmation | `B02` / `B07` | same | needs field 15 |
| wrong-invocation result | `C06` | `STOP(S09_RESULT, result_invalid)` | yes |
| wrong-correlation result | `C07` | `STOP(S01_INPUT, invalid_input)` | yes |
| look-alike result | `C08` | `STOP(S01_INPUT, invalid_input)` | yes |
| DENY + SUCCESS | `C14` | `STOP(S11_OBLIGATION, obligation_failed, DENIED_YET_EXECUTED)`, result retained | yes |
| CONVERSATIONAL + executed result | `C15` | lane escalates via the existing policy, then `STOP(S09_RESULT, result_invalid)` | yes |
| unsupported capability + SUCCESS | `C12` / `C10` | `STOP(S01_INPUT, invalid_input)` by C-00a, or `result_invalid` on route disagreement | yes |
| PipelineStop + forbidden result state | retention table, PIPELINE_STOP.md | pre-S09 stops carry `result=None`, `executed=False`; `executed=True` with `result=None` never emitted | yes |
| proposal mismatch + success claim | corpus `C01` | `STOP(S06_MATCH, proposal_tool_mismatch)` | yes |
| multiple proposals + permission ALLOW | corpus `C02` | `STOP(S06_CARDINALITY, multiple_proposals)` before permission is consumed | yes |
| zero proposal + model completion claim | corpus `C03` | `STOP(S06_CARDINALITY, proposal_required)` | yes |
| confirmation_id + no valid claim | `C04`, and the `confirmation_claimed` derivation | `executed=False` preserved, `P6-01a` `REQUEST_CONFIRMATION`; the id alone grants nothing | yes |

Twelve of the fourteen are implementable today; three of those twelve additionally appear
in mode-B variants that are not. Existing P6 contradiction precedence (result shape ->
lane -> execution -> settled state) and the owner's contradiction code are preserved
unchanged; the pipeline adds no contradiction check of its own and copies none.

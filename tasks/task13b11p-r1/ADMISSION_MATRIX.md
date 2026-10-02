# ADMISSION MATRIX

32 rows, frozen before any implementation exists. The machine-readable matrix is
`admission-matrix.json`; it is the normative artifact and this file is its index.

SHA-256 of `admission-matrix.json`:
`6b454b2c8d881327b88cef73ae03a6465286bb7fb589e942f1bc3789d76fb434`

These are **pre-implementation expectations**. `app/execution/pipeline.py` does not exist
at the frozen production baseline, so no row has been measured, no pass rate is claimed and
no conformance is asserted. The implementation task must agree with these rows, and where
it cannot, the frozen table wins and the disagreement is the finding — the method that
caught two wrong rank predicates in P6 and the lexicon gap in P6's first attempt.

Each row records: `admitted`, derived `mode`, `last_stage` reached, `dispatch_allowed`,
`executor_calls`, the outcome alternative, and for a refusal the exact `PipelineStop`
stage, reason, `executed`, `result` and `component_reason`.

## Global invariants asserted by every row

`executor_calls = 0`, `dispatcher_entries = 0`, `new_invocations = 0`,
`new_trusted_results = 0`, `new_confirmations_or_claims = 0`, `audit_emissions = 0`,
`provenance_writes = 0`. No row permits a real effect.

## Row index

| Group | Rows | Covers |
|---|---|---|
| `A01`–`A07` | 7 | initial turns: conversational, first confirmation ask, the `ALLOW`-without-result crux, fake `confirmed=true`, fake in-recording claims, fake result, zero proposals |
| `B01`–`B07` | 7 | confirmation continuation: valid, mis-bound, wrong session, replay after claim, terminal, stale, unrelated request with an old approval |
| `X01`–`X02` | 2 | mode conflict and partial shapes |
| `C01`–`C16` | 16 | result replay: `SUCCESS`, `ERROR`, `TIMEOUT`, `CONFIRMATION_REQUIRED`, `BLOCKED`; wrong invocation; wrong correlation; look-alike; replay twice; unrelated request with an old result; forged permissive outcome; non-dispatchable action; internally impossible result; `SUCCESS`+`DENY`; conversational text with a result; mismatched historical support |

## Coverage of the eighteen cases named in the task

| Named case | Row |
|---|---|
| initial conversational turn | `A01` |
| initial operational turn | `A02` (gated action, first ask) and `A03` (`ALLOW`) |
| initial operational + fake `confirmed=true` | `A04` — not expressible: the admission type has no such field |
| initial operational + fake result | `A06`, and `A05` for a claim smuggled inside the recording |
| valid confirmation continuation | `B01` |
| confirmation mismatch | `B02` |
| confirmation wrong session | `B03` |
| confirmation replay after claim | `B04` |
| confirmation + result simultaneously | `X01` |
| valid `SUCCESS` result replay | `C01` |
| valid `ERROR` result replay | `C02` |
| valid `TIMEOUT` result replay | `C03` |
| result wrong invocation | `C06` |
| result wrong correlation | `C07` |
| look-alike result mapping | `C08` |
| result replay twice | `C09` |
| unrelated new request + old result | `C10` |
| unrelated new request + old confirmation | `B07` |

All eighteen are covered. The fourteen additional rows are not scope creep: each is a
consequence of a rule this contract had to freeze (`A03` the `ALLOW` crux, `A05`/`A07` the
adapter and cardinality interactions, `B05`/`B06` the remaining confirmation states,
`X02` the partial shapes, `C04`/`C05` the two refusal statuses task §16 and §18 require,
`C11` the forged-authority check, `C12` the v1 exclusion, `C13`/`C14` the retention rule,
`C15` the conversational-plus-result contradiction, `C16` the historical pair).

## Relation to the frozen pipeline matrix

task13b11o-r1/UPDATED_PIPELINE_MATRIX.md (47 rows, digest
`b45a373da04d687d43ab2df60bcdcc6c9da46c769528046f796114830bf86d89`) remains frozen and
unchanged. This matrix is additive and orthogonal: it varies the **admission shape**,
where the pipeline matrix varies the **request, proposal set and projection**. No row here
replaces, relaxes or contradicts one there. Correspondences worth naming: `A01`↔N01/N02,
`A02`↔N04, `A07`↔N03, `A05`↔N16/N17/N18, `B07`/`B02`↔N33, `C01`↔N34, `C02`↔N35,
`C03`↔N36, `C05`↔N37, `C14`↔N38. Where this matrix is stricter than the pipeline matrix
appears to allow — `A03` and `C12` — the strictness comes from a rule the pipeline matrix
left to the admission API, which is exactly what P-B01 asked to be frozen.

## Freeze discipline for the implementation task

Freeze the fixture values and the exact expectations before writing any code or running
any scoring, and re-verify this digest first. Do not relax a row to make an implementation
agree. Do not add a row during implementation without recording the cause of the movement
and re-freezing with a new digest, as the P6 matrix v1→v2→v3 history did. A row that the
implementation shows to be wrong is a contract defect requiring explicit version history,
not a silent edit.

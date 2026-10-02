# Final matrix migration

Verified by exact JSON row-object comparison against Admission V1: **22 unchanged / 10 changed / 32 total**. The prior 23/9 finding becomes 22/10 solely because C15 now has the R6 stop. P-B04 changes architecture assertions, zero matrix rows.

| V1 | V2 | Category | Change/reason |
|---|---|---|---|
| A01 | A01 | unchanged | Identical row object. |
| A02 | A02 | unchanged | Identical row object. |
| A03 | A03 | unchanged | Identical row object. |
| A04 | A04 | unchanged | Identical row object. |
| A05 | A05 | unchanged | Identical row object. |
| A06 | A06 | unchanged | Identical row object. |
| A07 | A07 | unchanged | Identical row object. |
| B01 | B01 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| B02 | B02 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| B03 | B03 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| B04 | B04 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| B05 | B05 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| B06 | B06 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| B07 | B07 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| X01 | X01 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| X02 | X02 | P-B02 | Replace lifecycle record description with settled projection; outcome unchanged. |
| C01 | C01 | unchanged | Identical row object. |
| C02 | C02 | unchanged | Identical row object. |
| C03 | C03 | unchanged | Identical row object. |
| C04 | C04 | unchanged | Identical row object. |
| C05 | C05 | unchanged | Identical row object. |
| C06 | C06 | unchanged | Identical row object. |
| C07 | C07 | unchanged | Identical row object. |
| C08 | C08 | unchanged | Identical row object. |
| C09 | C09 | unchanged | Identical row object. |
| C10 | C10 | unchanged | Identical row object. |
| C11 | C11 | unchanged | Identical row object. |
| C12 | C12 | unchanged | Identical row object. |
| C13 | C13 | unchanged | Identical row object. |
| C14 | C14 | unchanged | Identical row object. |
| C15 | C15 | P-B05 | Operator Option A fixes zero-proposal NONE replay boundary; historical C15 is stale. |
| C16 | C16 | unchanged | Identical row object. |

C15: S09_RESULT/result_invalid → S06_PROJECTION/projection_invalid. False executed and null result/component reason are preserved. All old/new objects are frozen in row-mapping.json. Nonzero NONE cases retain S06_CARDINALITY/unexpected_proposal in the corpus, with N24 and C15-parent traceability. C14 explicitly remains a component-state contradiction reaching P6, not a new whole-turn DENY replay capability; O-R1 already distinguishes component reachability. No row is silently moved or removed.

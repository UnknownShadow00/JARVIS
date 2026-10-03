# Binary P8 entry checklist

| Formal prerequisite | Verdict | Evidence |
|---|---|---|
| P7 exit, including measured inert shadow and zero visible change | BLOCKED | 13B11A `IMPLEMENTATION_PHASES.md` P7/P8 rows; `P7_EXIT_CHECKLIST.md` |
| Previous phase conformance tests passing | BLOCKED | 13B11A `IMPLEMENTATION_PHASES.md` notes; CT-001/CT-013 live-model P7 evidence unavailable and prohibited in this review |
| Real control plane available to inert end-to-end tests | BLOCKED | 13B11A P8 exit row and `TEST_STRATEGY.md` §1; R8 reports zero pipeline consumers |
| Verified R8 production commit and sealed evidence in this environment | BLOCKED | `evidence/entry-head.txt`, `production-object-error.txt`, `R8_VERIFICATION.md` |
| New policy, real tool or live dispatcher activation | NOT APPLICABLE | P8 production impact “none”; inert dispatcher fixtures only, 13B11A P8 row |

The original P8 requires test-only inert dispatcher fixtures, full CT-001…CT-018 green and a real control-plane path. A narrower **passive P8** is not defined in 13B11A. Such a unit needs a separate, explicit phase-scope/entry amendment; it cannot inherit P8's name and claim its exit. Recorded-only checks could be designed without a projection producer, but would be a new scoped test contract, not the frozen P8.

# C15 provenance

The disputed identifier is **Admission V1 matrix C15**, first committed in Task 13B11P-R1 at 2c87af3425accd4080972b530fdd16dac6291ee4. It is not P6 C-15-operational-lane-without-any-reason, not a numbered adapter fixture, and not a dispatcher guard. The original row is copied exactly in c15-original-row.json. Git history shows no earlier version of this matrix row.

Exact original scenario: “conversational request text plus an execution result for an unrelated action”. Exact detail: “the final lane escalates to OPERATIONAL through the existing policy via tool_result, so there is no conversational escape; C-04 then fails on route NONE versus the invocation's action”. Expected: admitted=false; mode=RESULT_REPLAY; last_stage=S09_RESULT; PipelineStop(reason=result_invalid, executed=false, result=null, component_reason=null); zero dispatch/executor calls.

| Source | Task/status | Semantic / authority | Dependents |
|---|---|---|---|
| admission-matrix.json C15 | P-R1; frozen manifest 203eedc6c55b2e68c3697453e0d3d0bde2556e5578ce1cfec9ad41e0998e3919 | Normative admission expectation, subordinate to Pipeline V1 under RECORDED_TURN_ADMISSION_V1.md's explicit precedence | admission index; R2 contradiction table; R3/R4 draft matrices/migration |
| ADMISSION_MATRIX.md | P-R1; frozen | Index calls C15 conversational-plus-result contradiction; does not specify proposal cardinality | later coverage claims |
| RESULT_REPLAY.md C-04; S08_S09_CONTRACT.md | P-R1; frozen | Route agreement checked at S09 after earlier actual engines; no earlier C15-specific branch | C15 expectation |
| SECURITY_INVARIANTS.md S-09 | P-R1; frozen | Mode never skips earlier gates; C-04–C-07 occur after S02–S07 | makes early-C04 reinterpretation incompatible |
| CONTRADICTION_HANDLING.md | P-R2; blocked implementation analysis | Copies C15 as S09/result_invalid and calls it implementable; no measurement or new decision | R3/R4 inherited expectations |
| admission-matrix-v2.json, MATRIX_MIGRATION.md, row-mapping.json | P-R3; unfrozen drafts | Copy C15 unchanged, count among 23 unchanged rows | R4 candidate |
| corresponding matrix/migration plus BLOCKER_ANALYSIS.md and reports | P-R4; V2 still unfrozen | Copy expectation and expose reachability conflict; authorization seal does not freeze V2 semantics | P-B05 inquiry |

Every explicit C15 occurrence in the four P7 admission task directories is inventoried in c15-reference-inventory.json with exact path/line/text/hash and first commit. That includes repeated historical quotations in R4's absence inventory; quotations are not independent authority. Files indirectly dependent on C15 include R1 acceptance (all 32 rows), replay/security/retention rules, R2 TEST_PLAN, R3/R4 FIXTURE_CORPUS and IMPLEMENTATION_ACCEPTANCE. They require a corpus but contain no measured C15 result.

No production pipeline or C15 pipeline test exists. P6's own C-15 tests validate lane reasons and do not depend on admission C15. The original R1 contract prose says “24-row” in one bullet, but the frozen machine matrix actually contains 32 rows; this incidental count drift does not decide C15. Historical artifacts remain untouched.

## Later explicit references

| File | Status | First commit | Occurrences |
|---|---|---|---|
| tasks/task13b11p-r1/ADMISSION_MATRIX.md | frozen admission origin / direct dependent | 2c87af3425accd4080972b530fdd16dac6291ee4 | 1 |
| tasks/task13b11p-r1/admission-matrix.json | frozen admission origin / direct dependent | 2c87af3425accd4080972b530fdd16dac6291ee4 | 1 |
| tasks/task13b11p-r2/CONTRADICTION_HANDLING.md | derived analysis/draft/historical copy; not independent authority | d57bef85c60449942a5455311f1802cd77e640cc | 1 |
| tasks/task13b11p-r3/MATRIX_MIGRATION.md | derived analysis/draft/historical copy; not independent authority | 347e32fe36be0dc29d7d8327d5e2babbaa8dd5c3 | 1 |
| tasks/task13b11p-r3/admission-matrix-v2.json | derived analysis/draft/historical copy; not independent authority | 347e32fe36be0dc29d7d8327d5e2babbaa8dd5c3 | 1 |
| tasks/task13b11p-r3/row-mapping.json | derived analysis/draft/historical copy; not independent authority | 347e32fe36be0dc29d7d8327d5e2babbaa8dd5c3 | 2 |
| tasks/task13b11p-r4/ADMISSION_CONTRACT_V2.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/BLOCKER_ANALYSIS.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 6 |
| tasks/task13b11p-r4/FINAL-REPORT.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/FIXTURE_CORPUS.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 2 |
| tasks/task13b11p-r4/FOLLOWUPS.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/IMPLEMENTATION.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/MATRIX_MIGRATION.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 2 |
| tasks/task13b11p-r4/V1_TO_V2.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/VERIFICATION.md | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/admission-matrix-v2.json | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 1 |
| tasks/task13b11p-r4/row-mapping.json | derived analysis/draft/historical copy; not independent authority | 9c5e8c9e1792d845a1d217cd923dc891a651e3e9 | 2 |

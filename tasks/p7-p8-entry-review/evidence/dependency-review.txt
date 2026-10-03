# P7 → P8 dependency review

No canonical next task ID is assigned. Task 13B11A names phases P7 and P8, and only proposes 13B11B as its first implementation task (`PRODUCTION_INTEGRATION_PLAN.md` §22). This directory is a descriptive review name, not a new phase.

The actual graph is `task13b11a/DEPENDENCY_GRAPH.md` §§1–2: P6 obligations/response → P7 pipeline plus adapter → P7 server branch/API/UI → P8 conformance. `IMPLEMENTATION_PHASES.md` rows P7–P8 require P6 exit, then a side-effect-free measured shadow period as **P7 exit**, then P8's full CT-001…CT-018 inert end-to-end conformance against the real control plane. `TEST_STRATEGY.md` §§1,3 gives shadow to P7 and inert integration/contract tests to P8. Its CT-001/CT-013 row expects a live-model pipeline at P7; this review has no authority to perform that test.

R8 reports a passing **passive P7 pipeline unit** (`task13b11p-r8/FINAL-REPORT.md`), with zero production consumers and recorded projections. It does not satisfy the server/API/UI, measured shadow, live producer or live failure/audit pieces of the original P7 exit. The graph has not been amended to make passive unit completion the P8 entry gate. Therefore formal P8 entry fails even if R8's historical measurements are accepted.

This checkout is additionally not the stated production baseline: HEAD is `74c1cf521bb93b1347e6df7a7dc48930fb5d681e`; the `ac685a...` object, `pipeline.py`, R8 tests and `/home/jarvis/.hermes-poc/evidence/task13b11p-r8-p7-passive-pipeline/` are absent. R8 reports remain historical assertions, not independently reverified evidence here.

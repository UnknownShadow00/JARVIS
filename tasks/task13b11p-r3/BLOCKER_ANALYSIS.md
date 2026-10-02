# P-B04 — adapter-specific non-activation gates outside authorized scope

**JARVIS P7 ADMISSION V2 REPAIR BLOCKED**

First-hand source at production db54d615c3ee023d753e86143860c4efdc251230:
`tests/execution/hermes_adapter_non_activation_test.py`, SHA-256 `28c2c99387c7a9ea20dd7b4426c7c484924b2757758afa7fd0cbfc29f15769c1`.

R2 inspected the global non_activation_test.py and recorded adapter changes as “0–1”. The dedicated adapter suite has TWO binding assertion sites:

| Test function | Exact existing assertion | Why next implementation conflicts | Additional decision needed |
|---|---|---|---|
| test_zero_production_consumers_or_dynamic_adapter_references (line 33) | assert consumers == [] (line 49) | The scan covers all app Python files, including app/execution/pipeline.py. A normal import of the required recorded parser or AdapterRequest is a consumer. | Permit exactly pipeline.py as a static passive consumer; constrain access to AdapterRequest, AdapterError, parse_recorded_response. Continue rejecting every other consumer and all dynamic references, including in pipeline.py. |
| test_p7_pipeline_and_runtime_activation_remain_absent (line 52) | assert not (ROOT / "app/execution/pipeline.py").exists() (line 55) | Merely creating the canonical file fails, regardless of whether it has imports or behavior. | Explicitly authorize replacing this phase-absence assertion with pipeline presence plus passive isolation verification. Preserve the four mode/flag assertions exactly. This is a phase-gate transition, not merely an additive consumer exception. |

The four untouched runtime assertions require ExecutionMode.LEGACY, hermes_brain False, hermes_enabled False and ACTIVE_EXECUTION_MODES exactly {LEGACY}. The parser's import budget, hostile-model tests, identity checks and runtime purity tests stay unchanged.

The task explicitly limits authorization to router, permissions, obligations and response, and §17 requires STOP for anything additional. §16 also forbids removing assertions. Neither adapter exception nor phase-gate transition can be inferred from permission to extend those four suites. No test was edited, skipped, marked xfail or bypassed. No alternate module name, parser copy, hidden import or service locator is proposed.

This defect is independent of the confirmation repair: even an empty canonical pipeline file fails the existing adapter phase gate. Therefore V2 and the implementation fixture corpus are NOT frozen. The sixteen-field repair, 32-row migration and four-suite inventory are reviewable drafts. No unrelated matrix outcome was changed.

Required next operator decision: authorize these two exact future adapter-test changes, including the explicit phase-absence transition, then resume the contract repair and freeze before implementation. This task itself remains contract-only. Until authorization arrives, P-B04 blocks completion; no future test change outside the four-suite draft inventory is authorized by these documents.

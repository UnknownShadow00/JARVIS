# Narrow proposed authorizations — not granted

| File / function | Current assertion | Required new relationship / narrow request |
|---|---|---|
| tests/execution/provenance_non_activation_test.py:47::test_there_are_zero_live_provenance_writes | writers == []; markers include LedgerStore( | Allow exactly instance-owned LedgerStore construction in shadow_context.py; retain ProvenanceLedger construction and all record_* write bans elsewhere; prove no live consumer |
| tests/execution/binding_projection_test.py:152::test_single_snapshot_consumer_and_no_binder_consumers | binding_projection absent in every other app file | Permit shadow_observation.py type-only BindingProjectionV1 consumption; no build call; metadata producer still has exactly one binder consumer |
| tests/execution/pipeline_contract_support.py:54::assert_presence | execution.pipeline/run_recorded_turn absent elsewhere; no from-import pipeline | Permit named passive terminal vocabulary/type imports in shadow_observation.py; forbid run_recorded_turn reference/call there; preserve pipeline public shape/API/import budget |
| tests/execution/router_non_activation_test.py:383::test_no_production_module_imports_the_router | importers == [pipeline.py] | Add shadow_observation.py for RouteResult type only; zero route call |
| tests/execution/router_non_activation_test.py:399::test_no_router_symbol_is_referenced_outside_the_module | exact per-symbol allowlist | Add shadow_observation.py only for RouteResult; other symbols unchanged |
| tests/execution/permissions_non_activation_test.py:88::test_no_module_under_app_imports_the_permission_engine | importers == [pipeline.py] | Add shadow_observation.py for PermissionDecision type only; no decide/row_for call |
| tests/execution/permissions_non_activation_test.py:144::test_no_symbol_is_referenced_anywhere_under_app | exact per-symbol expected list | Add shadow_observation.py only for PermissionDecision; policy tables/symbols unchanged |

Shared pipeline assert_presence is invoked by hermes_adapter_non_activation_test.py::test_p7_pipeline_and_runtime_activation_remain_absent, pipeline_security_test and PB04 structural corpus cases. Authorize/version the exact structural transition explicitly; do not silently rewrite sealed historical corpus rows. This dependency is why changing one helper is not a blanket approval of every downstream consumer.

All other inventoried relationships are NO CHANGE REQUIRED for these proposed passive imports. ALREADY AUTHORIZED applies to reuse of existing types and no-consumer implementation scope in the operator instruction, not to modifying these assertions. Direct obligations/response imports would introduce further gates and are excluded from the proposed graph. Any new gate found during later implementation requires a fresh narrow review.

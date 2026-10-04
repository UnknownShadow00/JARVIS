# Exact ten existing structural transitions

| Row | Existing function | Narrow permitted relationship |
|---|---|---|
| 1 | tests/execution/hermes_adapter_non_activation_test.py::test_p7_pipeline_and_runtime_activation_remain_absent | Exact passive observation existence/type budget; existing flags and pipeline shape unchanged. |
| 2 | tests/execution/binding_projection_test.py::test_single_snapshot_consumer_and_no_binder_consumers | Only observation may import BindingProjectionV1; snapshot consumer remains binder only; no producer call. |
| 3 | tests/execution/router_non_activation_test.py::test_no_production_module_imports_the_router | Exact RouteResult import in observation only; router call budget preserved. |
| 4 | tests/execution/router_non_activation_test.py::test_no_router_symbol_is_referenced_outside_the_module | RouteResult only; no other router symbol or consumer added. |
| 5 | tests/execution/permissions_non_activation_test.py::test_no_module_under_app_imports_the_permission_engine | Exact PermissionDecision import only; no policy evaluation. |
| 6 | tests/execution/permissions_non_activation_test.py::test_no_symbol_is_referenced_anywhere_under_app | PermissionDecision only; all other permission symbols and consumers unchanged. |
| 7 | tests/execution/pipeline_contract_support.py::assert_presence | Only AdmissionMode, PipelineStage, PipelineStopReason, PipelineStop, TurnOutcome; unchanged PB04 API/other consumer bans. |
| 8 | tests/execution/shadow_context_test.py::test_exact_import_graph_and_zero_production_consumers | Observation exists, no context consumption; exact context/ingress hashes and graph preserved. |
| 9 | tests/execution/shadow_ingress_test.py::test_security_exact_import_shape_no_downstream_and_zero_consumers | Observation exists; ingress has zero consumers; frozen source hashes and engine/owner bans retained. |
| 10 | tests/execution/canonicalize_non_activation_test.py::test_there_are_zero_live_canonicalization_call_sites | Only additional declarer observation exact frozen fingerprint key/value/serialization; no direct canonicalizer import/reference/call. |

Exact current/old assertions and complete additive replacements are in the frozen authorization artifact and all eight existing-test diffs. Positive AST proof checks the full observer import/symbol/call budget, privacy, exact fingerprint preimage, source hashes, absence of scheduler/evaluator/sink and zero consumers. PB04 pipeline public shape and engine-call budgets remain intact. No eleventh function or other existing test AST node changed.

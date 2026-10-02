# Exact combined authorization and measured change

R6 AUTHORIZATION-ARTIFACTS.sha256 remains unchanged: P-B03 18 assertion instances / 8 functions / 4 files, P-B04 2 instances / 2 functions / 1 file. P-B06 adds exactly 2 instances / 1 function / 1 file. Total 22 / 11 / 6. JSON inventories in R6 remain the exact symbol authority; the frozen R8 supplement adds no semantic fields or outcomes.

| Existing file under tests/execution | Authorized functions |
|---|---|
| router_non_activation_test.py | test_no_production_module_imports_the_router; test_no_router_symbol_is_referenced_outside_the_module |
| permissions_non_activation_test.py | test_no_module_under_app_imports_the_permission_engine; test_no_symbol_is_referenced_anywhere_under_app |
| obligations_non_activation_test.py | test_only_the_passive_response_builder_imports_the_obligation_engine; test_no_public_symbol_is_referenced_anywhere_under_app; test_only_the_passive_builder_reads_the_frozen_source_map |
| response_non_activation_test.py | test_no_live_path_imports_or_calls_the_builder |
| hermes_adapter_non_activation_test.py | test_zero_production_consumers_or_dynamic_adapter_references; test_p7_pipeline_and_runtime_activation_remain_absent |
| canonicalize_non_activation_test.py | test_there_are_zero_live_canonicalization_call_sites |

All scans and prior consumers retained. Only app/execution/pipeline.py added with symbol budgets; no wildcard, skip, xfail, second consumer, or arbitrary sibling exception. New helper AST budgets enforce calls and references. Canonicalizer permits canonicalize call only; CanonicalizationResult reference/type use only, CanonicalizationError and CANONICALIZATION_VERSION. Exact full-app caller list contains pipeline:canonicalize(, and the four prior version declarers plus pipeline. Original failure diagnostic retained.

The adapter requires exactly AdapterRequest, AdapterError, parse_recorded_response, static unaliased import, one passive consumer. The absence test transitions to exact canonical presence, eight public definitions, one-argument entry point, constrained imports/calls, no production caller and legacy/disabled flags. Historical absence evidence untouched.

AST comparison verifies all other top-level statements/functions unchanged in these six files. Byte comparison verifies every other tracked production file unchanged, including confirmation and dispatcher tests. Evidence: authorized-test-diff-analysis.json and implementation-tracked-test-diff.patch. Every changed file is explicitly listed in the final production commit record.

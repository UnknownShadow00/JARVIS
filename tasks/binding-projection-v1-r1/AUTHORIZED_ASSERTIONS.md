# Frozen nine-assertion non-activation transition

Authority: this task's operator decision, scoped to `app/execution/binding_projection.py`. Source: `tasks/binding-projection-v1/BLOCKER.md` and the existing Core test functions. This table was written and hashed **before** recreating production code. Each row is one previously failing assertion instance; the existing scan and equality assertion remain in place.

| # | Test file / function | Current exact assertion expectation | Previously forbidden relationship | Exact additive expectation for binder | Still forbidden |
|---|---|---|---|---|---|
| 1 | `tests/execution/canonicalize_non_activation_test.py::test_there_are_zero_live_canonicalization_call_sites` | `callers == ["app/execution/pipeline.py:canonicalize("]` | binder's P3 `canonicalize()` call | Include exactly `app/execution/binding_projection.py:canonicalize(` before existing pipeline caller in the sorted scan | Every other caller and every `CanonicalizationResult(` constructor |
| 2 | `tests/execution/permissions_non_activation_test.py::test_no_symbol_is_referenced_anywhere_under_app[PermissionRequest]` | `hits == ["app/execution/pipeline.py"]` | binder's P4 query type | Add exactly binder path beside pipeline | Every other production path |
| 3 | same function `[PermissionPolicyError]` | `hits == ["app/execution/pipeline.py"]` | binder's P4 error type | Add exactly binder path beside pipeline | Every other production path |
| 4 | same function `[ApprovalMode]` | `hits == []` | binder's P4 approval-mode type | Set expected list to binder path only | Every other production path, including pipeline |
| 5 | same function `[ACTION_CAPABILITY]` | `hits == ["app/execution/pipeline.py"]` | binder's P4 declared pair lookup | Add exactly binder path beside pipeline | Every other production path |
| 6 | `tests/execution/router_non_activation_test.py::test_no_router_symbol_is_referenced_outside_the_module[RouteResult]` | `offenders == ["app/execution/pipeline.py"]` | binder's P3 route result type | Add exactly binder path beside pipeline | Every other production path |
| 7 | same function `[RouterContext]` | `offenders == ["app/execution/pipeline.py"]` | binder's P3 context type | Add exactly binder path beside pipeline | Every other production path |
| 8 | same function `[RouterError]` | `offenders == ["app/execution/pipeline.py"]` | binder's P3 error type | Add exactly binder path beside pipeline | Every other production path |
| 9 | same function `[RouteReason]` | `offenders == []` | binder's P3 route-reason type | Set expected list to binder path only | Every other production path, including pipeline |

The two existing router import and P7 pipeline checks remain unchanged. This authorization does not permit a new live consumer, policy change, rule change, dispatch, registry call, broad `app/execution/*` exception, skip, or tenth assertion transition. The registry metadata test's sole-binder consumer transition was separately frozen in F-MAP-01 and is outside these nine P3/P4 assertions.

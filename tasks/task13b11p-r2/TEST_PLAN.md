# TEST PLAN — not executed

No new test file was written and no existing test was modified. The plan below is the
target for the next attempt, recorded so it is not re-derived.

## What must not change

`tests/execution/dispatch_non_activation_test.py` — no change at all; the dispatcher keeps
zero importers because `obligations.NON_ACTION_OUTCOMES` supplies the only fact the
pipeline needs.

No existing assertion may be *relaxed*. The permitted change is extending a named-importer
allowlist, which is what 13B11O-R1 `IMPLEMENTATION_ACCEPTANCE.md` authorizes and what the
obligation engine's test already does for `response.py`.

## Assertion extensions required (operator decision 2)

| Test file | Change |
|---|---|
| `router_non_activation_test.py` | name `app/execution/pipeline.py` in the importer assertion; permit `RouteResult`, `RouterContext` in that one file (~12 assertions) |
| `permissions_non_activation_test.py` | same shape; permit `PermissionRequest`, `decide` references (~15) |
| `obligations_non_activation_test.py` | extend the existing `PASSIVE_RESPONSE_MODULE` allowlist to two named modules; permit `ObligationState` in both (~12) |
| `response_non_activation_test.py` | name the pipeline in the importer assertion (~2) |
| `non_activation_test.py` | unchanged — its walk already excludes `app/execution/` |
| `confirmation_non_activation_test.py` | **unchanged under the recommended repair** — this is the point of the repair |

## New tests the implementation owes

1. **Admission matrix conformance** — every row of the repaired `admission-matrix.json`,
   asserting admitted/mode/last stage/guard identity/stop stage/stop reason/`executed`/
   `result`/obligation/approved-response presence. Guard identity is asserted because the
   stop reasons are deliberately coarse (F-P7R1-03).
2. **Pipeline matrix conformance** — all 47 `N01`–`N47` rows of 13B11O-R1, plus the six
   contradiction corpus cases, plus the prior 18 CT categories.
3. **Structural zero-execution** — AST assertions that the module's import set is exactly
   its budget, that it names no dispatcher, registry, executor or confirmation symbol, that
   `RecordedTurn` has no callable-typed or authority-boolean field, and that no forbidden
   construct (`exec`, `eval`, `compile`, `__import__`, `sys.modules`) appears.
4. **Runtime zero-execution** — monkeypatched sentinels on the dispatcher, the registry and
   the confirmation mutators that fail the test if entered, exercised across the whole
   corpus; plus measured counts of 0 for executor calls, dispatcher entries, new
   invocations, new trusted results and new claims.
5. **Idempotence** — each corpus row evaluated twice, asserting byte-equal outcomes and
   unchanged counts.
6. **Purity** — no clock read, no network, no file I/O, no module-level mutable state; two
   instances share nothing.
7. **Generalization** — a separate unseen fixture set with expectations written first and
   run only after the implementation is frozen.

## Regression gates (unchanged baselines, re-measured this task)

Full suite 5468 passed / 11 deselected / 0 failed; golden 12/20 with the same eight ids;
legacy probe `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`; the
critical production files byte-identical; `registry.call` exactly 4 sites in
`app/server.py`; `execution.mode` `legacy`; both Hermes flags false.

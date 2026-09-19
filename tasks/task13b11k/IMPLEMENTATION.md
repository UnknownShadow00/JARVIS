# Implementation — Task 13B11K

Production `app/execution/dispatch.py`, 796 lines, plus a narrow additive change to
`app/execution/confirmation.py` (+318 / -10). Phase P5 of the 13B11A production integration
plan. Passive and unwired: 0 importers under `app/`, 0 call sites, `execution.mode` still
`legacy`.

## 1. What was built

| Name | What it is |
|---|---|
| `DISPATCHER_VERSION = "1"` | bumped only when the gate order, the refusal vocabulary or the result mapping changes |
| `DispatchError` | API misuse. A refusal about authority is a returned result, never this |
| `NON_DISPATCHABLE_ACTIONS` | `NONE`, `UNKNOWN_ACTION`, `MULTI_ACTION_UNSUPPORTED` |
| `EXECUTOR_REPORTABLE_STATUSES` | `SUCCESS`, `ERROR`, `TIMEOUT` — an executor may report nothing else |
| `REFUSAL_STATUSES` | `BLOCKED`, `CONFIRMATION_REQUIRED` |
| `CONFIRMATION_BINDING_FIELDS` (12) / `INVOCATION_BOUND_BINDING_FIELDS` (9) | the approval's fields, and the subset the dispatcher cross-checks itself |
| `CLAIM_REFUSAL_KINDS` (5) / `CONTROL_PLANE_ERROR_KINDS` (17) | the frozen refusal vocabulary |
| `ExecutorOutcome` | what an injected executor reports. Untrusted until wrapped |
| `ToolExecutor`, `ConfirmationAuthority` | structural protocols, both injected, neither imported from a policy module |
| `build_invocation(...)` | the frozen P0 `ToolInvocation`, with the authority-record invariants in one place |
| `TrustedDispatcher` | seven gates, at most one executor call, the only constructor of a `TrustedToolResult` |

On the confirmation side: `DispatchClaimRefused` (carrying `claim_refusal_kind`),
`CLAIM_REFUSAL_KINDS`, `BINDING_FIELD_NAMES`, two non-raising helpers `_is_admissible` and
`_is_aware`, and the three guarded edges `claim_for_dispatch`, `settle_success`,
`settle_failure`. `confirm()` is unchanged and still a wall.

## 2. Two things changed during implementation, recorded rather than smoothed over

**(a) The frozen matrix disagreed with the first draft, and the matrix won.**

The first draft made gate 2's confirmation-pairing rule symmetric: a confirmation id was
required *iff* the outcome was `REQUIRE_CONFIRMATION`, so a gated invocation arriving without
one was `BLOCKED` / `invocation_inconsistent`. The frozen matrix says
`CONFIRMATION_REQUIRED` / `confirmation_absent` at gate 5. Five scored cells failed on the first
run.

The matrix is right. Contract §12.1: *"For an action requiring confirmation the action state
MUST become `CONFIRMATION_REQUIRED` with `executed = false`."* Both answers are equally safe —
the executor is unreached either way — but only one describes the situation correctly, and the
P6 obligation engine reads the status to choose between `REQUEST_CONFIRMATION` and a generic
refusal. The code was changed; the frozen table was not. Gate 2 now refuses only the
unexpected-id direction, which is the direction a laundering attempt has.

This is the freeze-before-coding method paying for itself: the disagreement was visible as five
failing cells rather than as a plausible-looking implementation choice.

**(b) The first confirmation patch broke a sealed 13B11J invariant, and the invariant won.**

`confirmation_non_activation_test.py::test_no_bare_except_and_no_except_swallows_a_refusal`
asserts `"except" not in CODE` and zero `ast.Try` nodes. The first patch used `try`/`except` to
convert the module's own errors into `DispatchClaimRefused`.

Rather than relax the test, the three new methods were rewritten with **no `try`/`except` at
all**: two non-raising helpers (`_is_admissible`, `_is_aware`) ask the questions that
`_deep_freeze` and `_require_aware` would otherwise answer by raising, every precondition is
checked before the value is used, and each refusal is raised directly with its kind. The module
still has 0 `try` blocks. The 13B11J test passes unmodified.

This is the same shape as 13B11J's own recorded lesson — *"rather than weaken a sealed proof,
the API now takes the decision's three settled values"* — and it is why the dispatcher declares
a structural `ConfirmationAuthority` protocol instead of importing the confirmation machine at
all.

## 3. Three prior-phase tests were updated, all strengthened

Only tests whose stated scope was "in this phase" changed. No non-activation invariant about
importers, symbols, live wiring or purity was touched.

| File | Change | Why it is not a relaxation |
|---|---|---|
| `confirmation_test.py` | the pinned public-method set of `ConfirmationStore` grows from 6 to 9 names | still an exact pin; a tenth method still fails the test |
| `confirmation_transitions_test.py` | `test_no_store_method_exists_for_a_dispatch_result` becomes `test_the_dispatch_routes_are_exactly_three_named_guarded_edges` | the old test asserted "no route at all **in this phase**". The new one pins the three names exactly, asserts no generic transition API exists, and additionally asserts each takes `invocation_id` and takes neither `event` nor `state` — properties the old test did not check |
| `canonicalize_non_activation_test.py` | the allow-list of passive modules that may *declare* `canonicalization_version` gains `app/execution/dispatch.py` | the invariant this file protects — that the canonicalizer is never invoked from production code — is untouched and still passes. Same additive line 13B11J added for the same reason |

## 4. Declared deferrals

* **`TIMEOUT` leaves the confirmation record in `EXECUTING`.** The frozen graph draws two edges
  out of execution and neither is true of a timeout. `EXECUTING` is not replayable, so this is
  safe, but it is an unresolved record and a later phase has to decide whether an operator
  action or a sweep closes it. Recorded in `DEFERRED.md`.
* **The live adapter.** `registry.call` is not wrapped. The plan puts the first real tool at P9.
* **Confirmation TTL values, persistence and the on-load expiry sweep** stay where 13B11J left
  them.

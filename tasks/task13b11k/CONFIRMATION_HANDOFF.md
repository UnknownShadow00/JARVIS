# Confirmation Handoff — Task 13B11K

**Status: FROZEN before the module was written.**

## 1. What 13B11J left

`ConfirmationStore.confirm()` validates an approval completely — ownership, `PENDING`,
freshness, then all twelve binding fields — and then raises `ConfirmationDispatcherUnavailable`
without advancing the record. `_transition` refuses every event in
`EVENTS_REQUIRING_DISPATCHER` = {`CONFIRM`, `DISPATCH_SUCCESS`, `DISPATCH_ERROR`}. So the three
edges exist in the frozen table and nothing can apply them.

## 2. What this task adds — and what it does not touch

`confirm()` is left **byte-identical**. It is still the right answer for every caller that is
not the dispatcher, and every 13B11J test over it keeps passing unchanged.

Three new, individually guarded methods are added to `ConfirmationStore`:

| Method | Edge | Guard |
|---|---|---|
| `claim_for_dispatch(cid, *, session_id, binding_fields, invocation_id, now)` | `PENDING → EXECUTING` | the whole `confirm()` check, then: the record carries no invocation id yet, and the supplied invocation id is well formed. Records it on the transition |
| `settle_success(cid, *, invocation_id, now)` | `EXECUTING → SUCCEEDED` | state is `EXECUTING` **and** the record's invocation id equals the supplied one |
| `settle_failure(cid, *, invocation_id, now)` | `EXECUTING → FAILED` | same |

`binding_fields` is a plain mapping of the twelve field names; the store rebuilds a
`ConfirmationBinding` from it and compares by value, so the comparison is exactly the one
`confirm()` performs. A malformed mapping is a refusal, never a pass.

Nothing generic is added. There is no `set_state`, no `force_transition`, no
`mark_executing_unchecked`, and no method that takes an event as a parameter. The state table
itself, `next_state()`, the binding, the record and the six edges are unchanged.

`DispatchClaimRefused(ConfirmationError)` carries a machine-readable `claim_refusal_kind` from a
frozen five-value vocabulary so the dispatcher can name the refusal without importing the
module or matching on message text:

`confirmation_not_found`, `confirmation_not_pending`, `confirmation_expired`,
`confirmation_binding_mismatch`, `confirmation_invalid_request`.

## 3. Why the dispatcher does not import it

Sealed 13B11J invariants assert that **no module under `app/` imports the confirmation machine**
and that **none of its nineteen public symbols appears anywhere under `app/`**. 13B11I asserts
the same for the permission engine. 13B11J met this exact problem and recorded the rule:
*"rather than weaken a sealed proof, the API now takes the decision's three settled values."*

So `app/execution/dispatch.py` declares its own structural `ConfirmationAuthority` protocol —
three method names, no imported type — and the real `ConfirmationStore` satisfies it. The
caller injects it. The tests inject the **real store**, so the guarantees under test are the
real ones, not a double's.

No 13B11J or 13B11I test is modified, relaxed or exempted.

## 4. Lifecycle after the executor

| Executor outcome | Confirmation record |
|---|---|
| success | `EXECUTING → SUCCEEDED` |
| error | `EXECUTING → FAILED` |
| exception | `EXECUTING → FAILED` (an exception is an error; `CONFIRMATION_STATE_PLAN.md` §3 draws exactly one error edge) |
| malformed outcome | `EXECUTING → FAILED` |
| timeout | stays `EXECUTING` |

**Timeout is deliberately left in `EXECUTING`.** The frozen graph draws two edges out of
`EXECUTING`, `ok` and `error`, and contract §18 / `TOOL_INVOCATION_CONTRACT.md` §3.4 say the
side effect may or may not have happened, so neither is true. Inventing a terminal transition
would state something the dispatcher cannot support. `EXECUTING` is not replayable: it is not
`PENDING`, the table gives it no `CONFIRM` edge, and the two settlements require the matching
invocation id — so leaving it there opens no replay window. The unresolved record is recorded
as a deferred item.

## 5. If a settlement fails

The executor has already run. Raising would destroy a trusted result describing a real side
effect, and the caller might retry. The dispatcher therefore **keeps the result and does not
re-raise a settlement failure**; the record stays `EXECUTING`, which is safe for the reason
above. The result itself is never altered by a settlement outcome.

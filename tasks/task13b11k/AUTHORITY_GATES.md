# Authority Gates — Task 13B11K

**Status: FROZEN before the module was written.**

Seven gates, in this order. Every one must pass before the executor is invoked. The order is
the one the task specification proposes; each position is justified below, and the frozen
matrix (`dispatch-matrix.json`, field `gate_reached`) records which gate refused every cell.

| # | Gate | Refusal | Why here |
|---|---|---|---|
| 1 | input and type validity | raises `DispatchError` | a malformed call is not a policy question |
| 2 | invocation structural validity | `BLOCKED` | cheapest deterministic check; also catches a confirmation id paired with a non-`REQUIRE_CONFIRMATION` outcome, which is the laundering path |
| 3 | canonicalization metadata consistency | `BLOCKED` | INV-006 / R-07: what will run must be identifiable before any authority is consulted |
| 4 | settled permission outcome | `BLOCKED` | §11.2 deny-before-dispatch. Must precede confirmation: a denied action is never offered for approval |
| 5 | confirmation requirement present (id, binding, authority) | `CONFIRMATION_REQUIRED` | §12.1: no execution until a confirmation is associated. Missing machinery fails closed |
| 6 | confirmation ownership, state, freshness, exact binding, and the atomic execution claim | `CONFIRMATION_REQUIRED` or `BLOCKED` | the claim is the last thing before a side effect, so nothing can change between claim and call |
| 7 | executor invocation | — | the only step with an effect |

## Gate 2 in detail

* `action_type` is not in `NON_DISPATCHABLE_ACTIONS` = {`NONE`, `UNKNOWN_ACTION`,
  `MULTI_ACTION_UNSUPPORTED`}. Contract §8.1 (multi-action is refused, never partially
  executed — INV-012) and §13.1 (an unsupported action is answered, never mapped to a tool —
  INV-011). The same three the confirmation layer refuses to bind.
* `invocation_id`, `session_id`, `turn_id` are present; `invocation_id` is well formed by the
  P1 identifier family (`is_well_formed_id`).
* `tool_name` is a non-empty string.
* `confirmation_id` is present **iff** `permission_outcome is REQUIRE_CONFIRMATION`
  (`TOOL_INVOCATION_CONTRACT.md` §1: *"present iff confirmation was required"*), and when
  present it is well formed.

## Gate 3 in detail

`canonicalization_version` is a non-empty string, and `canonical_arguments` is a mapping. The
dispatcher does not produce them and does not check *how* they were produced; it checks that
the pair is present so the raw/canonical distinction survives to audit (INV-006).

## Gate 6 in detail — the atomic execution claim

Performed as one step under the dispatcher's own lock:

1. the invocation id has not been dispatched before (idempotency — `PRODUCTION_INTEGRATION_PLAN.md`
   §13, R-03); it is recorded as claimed **before** the executor call and never released;
2. for `REQUIRE_CONFIRMATION`, the injected confirmation authority is asked to claim the record
   for this exact invocation. The authority verifies, before transitioning: confirmation id,
   session ownership, `PENDING` state, freshness, and all twelve bound fields — action type,
   capability, tool name, target, user id, permission class, policy version, canonicalization
   version, raw arguments, canonical arguments, session id, confirmation id.

The dispatcher additionally cross-checks, before asking, the nine binding fields it can see on
the invocation itself (confirmation id, session id, action type, tool name, permission class,
policy version, canonicalization version, raw arguments, canonical arguments). A mismatch there
is a `confirmation_binding_mismatch` refusal that never reaches the authority, so a caller
cannot hand the store a binding that describes a different invocation from the one being
dispatched.

Only after both succeed is the record in `EXECUTING` and the invocation id consumed.

## Monotonicity

There is no code path in which a `DENY` or an unclaimed `REQUIRE_CONFIRMATION` becomes an
execution. Nothing the executor returns, nothing in `raw_arguments`, and no model object can
change a gate outcome: gates 1-6 all complete before the executor is reachable, and the
executor's return value is only ever mapped into a result.

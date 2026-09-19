# Expiry and Freshness — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.**

## 1. Expiry is data plus an explicit input

`expires_at` is a field on the record. Nothing in this module reads a clock. There is no timer, no
thread, no `asyncio` task, no background sweep, and no call to `datetime.now()`, `time.time()` or
`utc_now()` anywhere in the module.

Every operation whose answer depends on time takes `now: datetime` as a required keyword argument.
The caller owns the clock; the module owns the comparison. `DEPENDENCY_GRAPH.md` §3 records this
exact choice for this component: *"confirmation manager — mostly [independently testable]; needs a
clock and a store interface; **inject both**"*.

## 2. Freshness rule

Contract §12.3: *"Where implemented, it **MUST** also carry expiry or freshness."*
`CONFIRMATION_STATE_PLAN.md` §4: approval requires `now < expires_at`.

Boundary, frozen: the window is **half-open**. `now < expires_at` is fresh; `now == expires_at` is
expired; `now > expires_at` is expired. Stated explicitly so the boundary case is a decision and not
an accident, and tested at all three points with explicit timestamps.

## 3. Expire on access

`RISK_REGISTER.md` R-04 mitigation: *"`expires_at` per permission class; expired records move to
`EXPIRED` on load and on access"*.

The "on load" half belongs to persistence and is deferred with it. The "on access" half is
implemented and is uniform — there is no operation that sees a stale `PENDING` record and leaves it
stale:

| Operation on a `PENDING` record with `now >= expires_at` | Result |
|---|---|
| `get` | record becomes `EXPIRED`; raises `ConfirmationExpired` |
| `confirm` | record becomes `EXPIRED`; raises `ConfirmationExpired`. **Never** executes, never reaches the binding check. |
| `deny` | record becomes `EXPIRED`; raises `ConfirmationExpired` |
| `cancel` | record becomes `EXPIRED`; raises `ConfirmationExpired` |
| `expire` | record becomes `EXPIRED`; returns it |

A subsequent access finds a terminal `EXPIRED` record and gets `InvalidConfirmationTransition` from
the transition table (or, for `get`, the record itself). A stale approval can never become
execution authority, and it cannot be retried into one.

`expire` called while `now < expires_at` raises `InvalidConfirmationTransition`: the control plane
may not expire a record early to short-circuit a decision.

## 4. Timestamp validation

`created_at` and `expires_at` must both be timezone-aware `datetime` values, and
`expires_at > created_at`. Naive datetimes are rejected at construction rather than allowed to
raise `TypeError` from a later comparison — a comparison that fails inside a freshness check is
exactly the kind of failure that must be closed, not discovered.

`now` is likewise required to be timezone-aware wherever it is accepted.

## 5. TTL values are not frozen here

`CONFIRMATION_STATE_PLAN.md` §6 *proposes* 5 minutes for `REVERSIBLE_ACTION` and
`EXTERNAL_COMMUNICATION` and 2 minutes for `DESTRUCTIVE_ACTION` / `SYSTEM_POWER` /
`PRIVILEGED_ACTION`, "configurable per class in `config/permissions.yaml`".

Those values have **no operator sign-off**. The 13B11I review deferred TTL explicitly — *"TTL
enforcement (values are policy data, enforcement belongs to the confirmation state machine)"* — and
the ten signed-off decisions D-01…D-10 contain no TTL. `config/permissions.yaml` does not exist.

Therefore this module:

* represents `expires_at` and enforces it exactly;
* defines **no** per-class TTL constant, no default TTL and no TTL table;
* requires the caller to supply `expires_at`.

Freezing unsigned policy values inside a component whose whole purpose is deterministic
authorization would be inventing policy. The distinction — mechanism here, values elsewhere,
pending sign-off — is recorded as a deferred item.

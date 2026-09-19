# Confirmation Store API — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.**

`CONFIRMATION_STATE_PLAN.md` §5 selects *"an in-process store behind an interface
(`ConfirmationStore`)"*. Persistence is part of the same plan paragraph but is explicitly deferred
by this task (§71), together with the on-load expiry sweep that depends on it.

## 1. Ownership

`ConfirmationStore()` is an ordinary instance. There is **no** module-level store, no singleton, no
`get_store()` accessor and no import-time state, so a future session or control-plane object can own
one and every test gets its own. Two instances share nothing.

## 2. Surface

| Operation | Signature | Session ownership required | Notes |
|---|---|---|---|
| add | `add(record) -> ConfirmationRecord` | — | rejects a duplicate `confirmation_id`; rejects a record whose state is not `PENDING` |
| get | `get(confirmation_id, *, session_id, now) -> ConfirmationRecord` | **yes** | expires an out-of-date `PENDING` record on access (see below) |
| confirm | `confirm(confirmation_id, *, session_id, binding, now) -> NoReturn` | **yes** | validates fully, then raises `ConfirmationDispatcherUnavailable` |
| deny | `deny(confirmation_id, *, session_id, now) -> ConfirmationRecord` | **yes** | `PENDING → DENIED` |
| cancel | `cancel(confirmation_id, *, session_id, now) -> ConfirmationRecord` | **yes** | `PENDING → CANCELLED` |
| expire | `expire(confirmation_id, *, now) -> ConfirmationRecord` | no — system action | `PENDING → EXPIRED`, only when `now >= expires_at` |
| size | `__len__() -> int` | — | record count; no record contents |

That is the whole API. There is no listing, no search by target, no "latest confirmation", no
iteration over records and no accessor that returns the internal dictionary. Approval identifies a
record by its opaque id plus the session and binding checks — never by action type, target string
or tool name, and never by recency.

### 2.1 Why `deny` and `cancel` do not take a binding

Neither authorizes anything. Requiring the full binding to *refuse* an action would let a client
whose canonical arguments have drifted strand a record it is entitled to withdraw. Approval is the
only operation that grants authority, so approval is the only operation that carries the full
binding check.

### 2.2 Why `expire` takes no session

Expiry is a control-plane action against the clock, not a requester action. It grants nothing and
can only move a record to a terminal, non-executable state.

## 3. Immutability

`ConfirmationRecord` and `ConfirmationBinding` are `@dataclass(frozen=True, slots=True)`. A
transition does not mutate a record: it builds a **new** record with the new state and
`resolved_at`, carrying the identical binding object, and replaces the entry in the store. Records
handed to callers are therefore safe to keep; a caller holding an older record simply holds an
older snapshot and cannot use it to act.

Mappings inside a binding are `MappingProxyType` over frozen values, so a caller cannot reach
through a returned record and rewrite what was approved.

## 4. Atomicity and what is not claimed

Mutating operations run under a process-local `threading.Lock`, so read-then-replace is one step
and the same record cannot transition twice from the same source state within this process.

Not claimed, and stated here so it is not assumed later: no cross-process safety, no durability, no
protection for a coroutine that awaits while holding a record, and none of the single-writer
persistence `RISK_REGISTER.md` R-16 and R-10 describe. Those arrive with the integration layer.

## 5. Errors

| Error | Base | Raised when |
|---|---|---|
| `ConfirmationError` | `ValueError` | base for everything below; also raised for malformed construction input |
| `ConfirmationNotFound` | `ConfirmationError` | unknown id, or an id owned by a different session |
| `InvalidConfirmationTransition` | `ConfirmationError` | the (state, event) cell is forbidden by the frozen table, or `expire` is called before `expires_at` |
| `ConfirmationBindingMismatch` | `ConfirmationError` | the supplied binding is not equal to the stored one |
| `ConfirmationExpired` | `ConfirmationError` | the record's freshness window had already passed when it was accessed |
| `ConfirmationDispatcherUnavailable` | `ConfirmationError`, `NotImplementedError` | a **fully valid** approval, refused because the P5 dispatcher does not exist |

Every error path leaves the store in a defined state and none of them can be mistaken for success:
no operation returns a value on a failed check, and malformed internal input raises rather than
falling through to an implicit confirmation.

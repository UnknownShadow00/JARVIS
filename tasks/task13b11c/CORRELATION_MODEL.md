# Task 13B11C — Correlation Model

Production module: `app/execution/correlation.py`.
Planned in `tasks/task13b11a/AUDIT_PLAN.md` §2: `trace_id` stays the turn correlation id, and
`invocation_id` and `confirmation_id` are added so a full chain can be reconstructed by joining on
three keys.

## 1. Identifier classes

| Type | Minted by | Scope | Required on |
|---|---|---|---|
| `SessionId` | `new_session_id()` | one conversation session | every event |
| `TurnId` | `new_turn_id()` | one user turn | every event; serialized as `trace_id` |
| `InvocationId` | `new_invocation_id()` | one tool invocation attempt | `dispatch.invoked`, `dispatch.result` |
| `ConfirmationId` | `new_confirmation_id()` | one confirmation record | the five `confirmation.*` events |
| `AuditEventId` | `new_audit_event_id()` | one audit event | every event (`event_id`) |

`AuditEventId` is included because P0 already ships `TrustedToolResult.audit_ref`, which has
nothing to point at without it.

**Deferred on purpose:** `provenance_event_id` / `record_id` is minted by the ledger in P2
(`PROVENANCE_PLAN.md` §1 gives it a shape this phase does not own), and `request_id` is not a
separate concept here — a request and a turn are the same thing in this architecture, which is why
`trace_id` already means "turn".

Types are `typing.NewType` over `str`: distinct to a type checker, a plain string at runtime, so
values serialize, compare and log without wrappers.

## 2. Identifier properties

* `uuid4().hex` — 128 bits, 32 lowercase hex characters, no dashes.
* Opaque and non-semantic: no prefix, no counter, no encoded prompt text, target path, tool
  argument, host, IP, user or model name. Proven by a 1,000-identifier scan in
  `evidence/07-static-review-and-hermes-non-use.txt` §4 and by a unit test.
* Wide enough for the confirmation-token requirement in `CONFIRMATION_STATE_PLAN.md` §2 (an
  unguessable token, not the current 8-character uuid slice).
* Generated with the standard library only: no clock dependency, no database, no network, no
  process-global counter, no model involvement. `is_well_formed_id()` validates the shape.

## 3. `CorrelationContext`

```
CorrelationContext(session_id, turn_id, invocation_id=None, confirmation_id=None)
```

Frozen, slotted, and identifiers only. Child contexts are derived rather than mutated:
`for_invocation(id)` and `for_confirmation(id)` return new instances that keep the parent
`session_id` and `turn_id` intact and leave the parent untouched. `to_mapping()` omits unset
identifiers; `context_from_mapping()` rebuilds one and rejects unknown or empty keys.

## 4. Correlation is not authorization

The class carries no `permission`, `confirmed`, `approved`, `trusted`, `authorized` or `executed`
field, and none may be added. Holding a `confirmation_id` means an event belongs to a confirmation
flow — never that the action was confirmed; the confirmation *state* lives in the record P4 owns,
and the permission outcome in the decision P4 records. A test asserts the exact field set and that
no such attribute exists, so a later phase cannot quietly turn a join key into a capability.

## 5. Timestamps

`utc_now()` is the single source: timezone-aware UTC. `validate()` rejects a naive datetime rather
than assuming a zone, and serialization uses `isoformat()`, matching the legacy writer's
`datetime.now(UTC).isoformat()`. An aware non-UTC timestamp is accepted and serialized with its
offset, so it converts back to the same instant.

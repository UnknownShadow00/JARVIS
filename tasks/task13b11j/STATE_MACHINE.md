# Confirmation State Machine — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.**

## 1. The planned machine, quoted

`tasks/task13b11a/CONFIRMATION_STATE_PLAN.md` §3, verbatim:

```
PENDING ──confirm──► EXECUTING ──ok──► SUCCEEDED
   │                    └──error──► FAILED
   ├──deny──► DENIED
   ├──timeout──► EXPIRED
   └──supersede/cancel──► CANCELLED
```

> Six persisted states plus the transient `EXECUTING`.

## 2. The exact state vocabulary

Seven members, no more, no fewer.

| # | State | Persisted / transient | Meaning | Terminal |
|---|---|---|---|---|
| 1 | `PENDING` | persisted | recorded, waiting for a human answer. **Nothing has executed.** | no |
| 2 | `EXECUTING` | transient | approval has claimed execution ownership | no |
| 3 | `SUCCEEDED` | persisted | the dispatcher observed success | yes |
| 4 | `FAILED` | persisted | the dispatcher observed failure | yes |
| 5 | `DENIED` | persisted | the requester explicitly refused | yes |
| 6 | `EXPIRED` | persisted | freshness window passed before an answer | yes |
| 7 | `CANCELLED` | persisted | superseded or withdrawn before an answer | yes |

### 2.1 There is no resting `CONFIRMED` state — by design

The plan states the reason and it is a safety argument, not a style preference:

> `CONFIRMED` as a *resting* state is dropped: a confirmed action that is not yet executing is an
> ambiguous state that invites double execution. Approval transitions directly into `EXECUTING`
> under a lock, so "confirmed but not running" never exists.

The task prompt for 13B11J speaks of a "CONFIRMED STATE" and of a `CONFIRMED → EXECUTING`
transition. The prompt itself directs that the plan wins (§13: *"Use the EXACT state vocabulary
from CONFIRMATION_STATE_PLAN.md. Do not use this prompt to guess"*), so **no `CONFIRMED` member is
added**. The prompt's §16 requirement — *approval does not mean executed* — is honoured in a
stronger form here: in this phase approval cannot reach any state at all (§4 below).

The audit event `confirmation.confirmed` (`ExecutionAuditEvent`, schema v3, unchanged) names the
*event* of approval, not a resting state. No audit change is needed or made.

## 3. Transition events

Six events. Each is an input to the pure function `next_state(state, event)`.

| Event | Plan edge label | Who may raise it |
|---|---|---|
| `CONFIRM` | `confirm` | the requester, through a deterministic UI/API action — never prose, never a model |
| `DENY` | `deny` | the requester |
| `CANCEL` | `supersede/cancel` | the control plane or the requester |
| `EXPIRE` | `timeout` | the control plane, with an explicit current time |
| `DISPATCH_SUCCESS` | `ok` | **only** the P5 dispatcher, from a `TrustedToolResult` |
| `DISPATCH_ERROR` | `error` | **only** the P5 dispatcher, from a `TrustedToolResult` |

## 4. What this phase may apply

| Edge | Table says | Applied in 13B11J | Behaviour here |
|---|---|---|---|
| `PENDING --CONFIRM--> EXECUTING` | allowed | **no** | full validation runs first; a *valid* approval then raises `ConfirmationDispatcherUnavailable`. The record is **not** mutated. |
| `PENDING --DENY--> DENIED` | allowed | yes | applied |
| `PENDING --CANCEL--> CANCELLED` | allowed | yes | applied |
| `PENDING --EXPIRE--> EXPIRED` | allowed | yes | applied, with an explicit `now` |
| `EXECUTING --DISPATCH_SUCCESS--> SUCCEEDED` | allowed | **no** | unreachable: no record can be `EXECUTING`. No public API exists. |
| `EXECUTING --DISPATCH_ERROR--> FAILED` | allowed | **no** | as above |
| everything else | forbidden | — | `InvalidConfirmationTransition` |

`next_state()` is the whole table and is available for all 42 cells, so the forbidden edges are
provable. What this phase withholds is *application*: the three dispatcher-owned edges have no
store method that performs them.

### 4.1 Why the approval edge is blocked rather than half-built

Because the plan fuses approval and execution ownership into one atomic step, a passive module that
"just" moved a record to `EXECUTING` would be asserting that execution had begun when no dispatcher
exists. That is precisely the fake-execution state contract §12.1 and INV-004 exist to prevent. The
validation is therefore real and complete — session, binding, state, freshness — and only the
*application* is withheld. A caller that holds a genuinely valid approval learns that the dispatcher
is missing; a caller that holds an invalid one learns why it is invalid, and learns it first.

## 5. Terminal states are terminal

`SUCCEEDED`, `FAILED`, `DENIED`, `EXPIRED`, `CANCELLED` accept **no** event. There is no edge back
to `PENDING` and no edge between terminal states. A terminal record can never be replayed into an
executable one; a new request needs a new record with a new id (contract §12.3, risk R-03).

## 6. Atomicity

Store mutation is guarded by a process-local `threading.Lock`, so a state is read and replaced as
one step and the same record cannot transition twice from the same source state within this
process. That is the whole claim. It is **not** cross-process safety, **not** asyncio-task safety
against a coroutine that awaits while holding a record, and **not** the durable single-writer store
R-16 describes. Live concurrent access needs the later integration layer.

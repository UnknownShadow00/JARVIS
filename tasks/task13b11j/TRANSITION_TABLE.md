# Frozen Transition Corpus — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.** Generated from
`tasks/task13b11a/CONFIRMATION_STATE_PLAN.md` §3 and hashed before
`app/execution/confirmation.py` existed. The module and the tests each derive from this table
independently; neither derives from the other.

Machine-readable form: `transition-table.json`.

| | |
|---|---|
| cells (state x event) | **42** |
| allowed by the plan graph | **6** |
| applied in 13B11J | **3** |
| forbidden | **36** |
| side-effect expectation, every cell | **NONE** |

## 1. Full corpus

`applied` = a store method in this phase performs the edge. An allowed edge that is not applied
is dispatcher-owned: `next_state()` still reports its target state, but nothing mutates a record.

| from | event | allowed | to | applied | store method | error | timestamp/metadata |
|---|---|---|---|---|---|---|---|
| `PENDING` | `CONFIRM` | yes | `EXECUTING` | no | `ConfirmationStore.confirm` | `ConfirmationDispatcherUnavailable` | none — record is not mutated |
| `PENDING` | `DENY` | yes | `DENIED` | **yes** | `ConfirmationStore.deny` | — | state replaced; resolved_at set to the supplied `now`; binding fields unchanged and never rewritten |
| `PENDING` | `CANCEL` | yes | `CANCELLED` | **yes** | `ConfirmationStore.cancel` | — | state replaced; resolved_at set to the supplied `now`; binding fields unchanged and never rewritten |
| `PENDING` | `EXPIRE` | yes | `EXPIRED` | **yes** | `ConfirmationStore.expire` | — | state replaced; resolved_at set to the supplied `now`; binding fields unchanged and never rewritten |
| `PENDING` | `DISPATCH_SUCCESS` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `PENDING` | `DISPATCH_ERROR` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXECUTING` | `CONFIRM` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXECUTING` | `DENY` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXECUTING` | `CANCEL` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXECUTING` | `EXPIRE` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXECUTING` | `DISPATCH_SUCCESS` | yes | `SUCCEEDED` | no | — | `no public API in 13B11J` | none — record is not mutated |
| `EXECUTING` | `DISPATCH_ERROR` | yes | `FAILED` | no | — | `no public API in 13B11J` | none — record is not mutated |
| `SUCCEEDED` | `CONFIRM` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `SUCCEEDED` | `DENY` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `SUCCEEDED` | `CANCEL` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `SUCCEEDED` | `EXPIRE` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `SUCCEEDED` | `DISPATCH_SUCCESS` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `SUCCEEDED` | `DISPATCH_ERROR` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `FAILED` | `CONFIRM` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `FAILED` | `DENY` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `FAILED` | `CANCEL` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `FAILED` | `EXPIRE` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `FAILED` | `DISPATCH_SUCCESS` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `FAILED` | `DISPATCH_ERROR` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `DENIED` | `CONFIRM` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `DENIED` | `DENY` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `DENIED` | `CANCEL` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `DENIED` | `EXPIRE` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `DENIED` | `DISPATCH_SUCCESS` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `DENIED` | `DISPATCH_ERROR` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXPIRED` | `CONFIRM` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXPIRED` | `DENY` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXPIRED` | `CANCEL` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXPIRED` | `EXPIRE` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXPIRED` | `DISPATCH_SUCCESS` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `EXPIRED` | `DISPATCH_ERROR` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `CANCELLED` | `CONFIRM` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `CANCELLED` | `DENY` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `CANCELLED` | `CANCEL` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `CANCELLED` | `EXPIRE` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `CANCELLED` | `DISPATCH_SUCCESS` | no | — | no | — | `InvalidConfirmationTransition` | none |
| `CANCELLED` | `DISPATCH_ERROR` | no | — | no | — | `InvalidConfirmationTransition` | none |

## 2. Required inputs per event

| event | required inputs |
|---|---|
| `CONFIRM` | `confirmation_id`, `session_id`, `binding`, `now` |
| `DENY` | `confirmation_id`, `session_id`, `now` |
| `CANCEL` | `confirmation_id`, `session_id`, `now` |
| `EXPIRE` | `confirmation_id`, `now` |
| `DISPATCH_SUCCESS` | `confirmation_id`, `trusted_tool_result` |
| `DISPATCH_ERROR` | `confirmation_id`, `trusted_tool_result` |

## 3. Reading the three dispatcher-owned cells

* **`EXECUTING --DISPATCH_ERROR--> FAILED`** — only a TrustedToolResult from the P5 dispatcher may cause this; unreachable because no record can be EXECUTING in this phase
* **`EXECUTING --DISPATCH_SUCCESS--> SUCCEEDED`** — only a TrustedToolResult from the P5 dispatcher may cause this; unreachable because no record can be EXECUTING in this phase
* **`PENDING --CONFIRM--> EXECUTING`** — approval claims execution ownership; validated fully (session, binding, state, freshness) then refused because no P5 dispatcher exists

## 4. Invariants this corpus encodes

* Every one of the five terminal states accepts **zero** events: 30 of the 36 forbidden cells.
* `PENDING` accepts no dispatcher result: a record cannot reach `SUCCEEDED` or `FAILED` without
  passing through `EXECUTING`, and nothing in this phase can put it there.
* No cell has a side effect. Not one edge touches the filesystem, the network, a subprocess, a
  tool, the model, the audit writer or the provenance ledger.
* Applying an allowed edge replaces the state and sets `resolved_at`; it never rewrites a binding
  field. Binding fields are write-once at construction.

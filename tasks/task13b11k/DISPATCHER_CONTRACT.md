# Dispatcher Contract — Task 13B11K (phase P5)

**Status: FROZEN before the module was written.** Every statement here is derived from a
normative source, cited inline. Where a source is silent, the decision is recorded as a
decision, not presented as inherited.

---

## 1. What P5 is

`IMPLEMENTATION_PHASES.md` P5: *"Dispatcher boundary — `app/execution/dispatch.py` wrapping
`registry.call`. Unit with an **inert** dispatcher. Exit criteria: typed `TrustedToolResult`
only creatable here."*

`TARGET_COMPONENT_MAP.md` §1: *"Tool dispatcher boundary — `app/execution/dispatch.py` wrapping
`app/tools/registry.py` — the only executor; produces bound `TrustedToolResult` (§18). Inputs
`ToolInvocation`, outputs `TrustedToolResult`. Must never be bypassable by importing a tool
module."*

This task delivers the boundary and the seam. It does **not** deliver the registry adapter.
`registry.call` is not imported, not referenced and not reachable; the last-mile wrapper named
in the plan is the *live adapter*, and `IMPLEMENTATION_PHASES.md` places the first real tool at
P9, four phases away.

## 2. The path

`app/execution/dispatch.py`. Taken verbatim from `TARGET_COMPONENT_MAP.md` §1 and
`IMPLEMENTATION_PHASES.md` P5. Not `dispatcher.py`.

## 3. Ownership of the confirmation execution claim — P5, and why

Three independent sources assign `PENDING → EXECUTING` to this phase.

1. `CONFIRMATION_STATE_PLAN.md` §3: *"`CONFIRMED` as a resting state is dropped… Approval
   transitions directly into `EXECUTING` under a lock, so 'confirmed but not running' never
   exists."* A transition *into* execution is owned by whatever owns execution.
2. `PRODUCTION_INTEGRATION_PLAN.md` §13: *"Approval transitions `PENDING → EXECUTING` under a
   per-record lock."* — listed under *Idempotency and duplicate execution*, the dispatcher's
   concern.
3. Production `app/execution/confirmation.py` reserves it explicitly:
   `EVENTS_REQUIRING_DISPATCHER = {CONFIRM, DISPATCH_SUCCESS, DISPATCH_ERROR}`, and
   `ConfirmationDispatcherUnavailable` is raised with the message *"the trusted dispatcher
   boundary (phase P5) is not implemented."*

So P5 owns three edges: the claim `PENDING → EXECUTING`, and the two settlements
`EXECUTING → SUCCEEDED` / `EXECUTING → FAILED`.

There is **no resting `CONFIRMED` state** and this task does not add one. 13B11J verified the
plan deliberately omits it.

## 4. Refusal representation — decision D-K1

**Decided: a permission or confirmation refusal produces a `TrustedToolResult` with
`ToolResultStatus.BLOCKED` or `ToolResultStatus.CONFIRMATION_REQUIRED` and `executed = False`.
It does not raise.**

Citations that settle it:

* `TOOL_INVOCATION_CONTRACT.md` §2 lists `CONFIRMATION_REQUIRED` and `BLOCKED` as members of the
  result `status` field. A status that only ever appears on a result is a result.
* `TOOL_INVOCATION_CONTRACT.md` §3.3: *"`CONFIRMATION_REQUIRED` and `BLOCKED` always carry
  `executed = false`."* A field of the result record.
* `app/execution/types.py` `ToolResultStatus` ships both members already, and
  `TrustedToolResult` carries `executed`.
* `app/execution/provenance.py::record_tool_result` names them as statuses that reach the
  ledger and are refused there: *"`BLOCKED` means it was stopped before running… Those outcomes
  are still auditable — they are `dispatch.result` events — they simply never become facts."*
  A `dispatch.result` audit event requires a result object to describe.

Mapping:

| Refusal | Status |
|---|---|
| settled permission outcome is `DENY` | `BLOCKED` |
| the invocation is structurally unfit to dispatch | `BLOCKED` |
| the invocation id was already dispatched | `BLOCKED` |
| the outcome is `REQUIRE_CONFIRMATION` and no valid, fresh, exactly-bound, owned approval was claimed | `CONFIRMATION_REQUIRED` |

Both always carry `executed = False` and empty `facts`.

## 5. What raises instead — decision D-K2

**Decided: API misuse raises `DispatchError`; a well-typed invocation always produces a result.**

Precedent: `app/execution/permissions.py` — *"Passing one as authority is an API misuse, not a
permission question, so it raises rather than denying."* Applied here as a type/content split:

* wrong **type** (not a `ToolInvocation`, a clock that does not return an aware datetime, no
  executor at construction, a non-mapping binding) → `DispatchError`;
* wrong **content** of a well-typed invocation (non-dispatchable action, malformed identifier,
  blank tool name, blank canonicalization version, confirmation id paired with the wrong
  permission outcome) → a `BLOCKED` result.

The safety property is identical either way — the executor is not called — and the split keeps
the caller's error reporting honest.

## 6. Hard boundaries

The dispatcher **must not**:

* import or call `app/tools/registry.py`, any tool module, or any live adapter (§45, R-02);
* classify text, parse a request, derive a primary action, a target or a reporting intent —
  those are P3 (`TARGET_COMPONENT_MAP.md` §1);
* normalize arguments — the caller supplies canonical arguments and the version that produced
  them (INV-006, R-07). There is no call to the P3 canonicalizer;
* compute permission policy — it consumes the three settled values (outcome, class, policy
  version). It cannot weaken them (INV-013, §11.2);
* reinterpret `approval_mode`; tightening is P4's and is already applied;
* emit an audit event or write a provenance record (P1/P2 remain unwired here);
* generate user-facing prose (P6);
* decompose a multi-action request (INV-012, §8.1);
* retry (`PRODUCTION_INTEGRATION_PLAN.md` §13: *"Retries are never automatic for mutating
  actions"*).

## 7. Import budget

`app.execution.types` and `app.execution.correlation` only, plus the standard library.

`permissions.py` and `confirmation.py` are **not** imported. Both carry sealed 13B11I/13B11J
invariants asserting zero importers and zero symbol references anywhere under `app/`, and
13B11J already met the same problem and solved it the same way: *"rather than weaken a sealed
proof, the API now takes the decision's three settled values."* The confirmation store is
reached through a structural protocol the dispatcher declares itself; the real store is injected
by the caller and by the tests.

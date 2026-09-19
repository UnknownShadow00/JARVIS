# Confirmation Model — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.** Written and hashed while
`app/execution/confirmation.py` did not exist. The module and its tests are derived from this
document; this document was not derived from them.

Normative sources, in precedence order:

1. `tasks/task13b10d/JARVIS_AGENT_EXECUTION_CONTRACT.md` §12 and
   `agent-execution-contract.yaml` `confirmation:` — frozen contract v1.
2. `tasks/task13b11a/CONFIRMATION_STATE_PLAN.md` — the production plan for this component.
3. `tasks/task13b11a/TARGET_COMPONENT_MAP.md` row "Confirmation manager",
   `DEPENDENCY_GRAPH.md` §3, `RISK_REGISTER.md` R-03…R-07, R-10, R-16.
4. `tasks/task13b11i/DECISION_API.md` — the P4 `PermissionDecision` this component consumes.

## 1. What this component is

Confirmation is **JARVIS-owned authorization state**. It records that a specific action, bound to a
specific requester and a specific set of arguments, is waiting for a human answer — and that
nothing has run.

It is not a dispatcher, not a permission engine and not an approval parser.

| It does | It does not |
|---|---|
| hold a pending record with an exact binding | execute anything |
| validate an approval attempt against that binding | call `registry.call` or any tool |
| apply deterministic state transitions from a frozen table | decide *whether* confirmation is required (P4 does) |
| carry `created_at` / `expires_at` as data | read a clock on its own |
| serialize to the schema-v3 `confirmation_state` audit field | emit an audit event |
| refuse any approval that is stale, misbound or from another session | interpret "yes", "do it" or any prose |

Contract §12.2 is absolute: the model **must not** mark an action confirmed, and model text such as
"proceeding", "confirmed" or "initiating" must not be treated as confirmation by any component.
This module therefore has **no** text-accepting entry point at all — not a guarded one.

## 2. Relationship to the action state

Two vocabularies exist and they are not the same thing:

| Vocabulary | Value while waiting | Owner | Where it lives today |
|---|---|---|---|
| Action / tool-result state (contract §12.1) | `CONFIRMATION_REQUIRED` | dispatcher + provenance | `ToolResultStatus.CONFIRMATION_REQUIRED`, `ProvenanceSource.CONFIRMATION_REQUIRED` (`app/execution/types.py`, P0/P2) |
| Confirmation record lifecycle (plan §3) | `PENDING` | this module | `ConfirmationState`, new in P4 |

Contract §12.1 "the action state MUST become `CONFIRMATION_REQUIRED` with `executed = false`" is
satisfied by the **first** row; `PENDING` is the second row. This is **not** a conflict between the
contract and the plan, and no third state name is introduced. A passive compatibility test asserts
the two can be represented together for the same turn.

## 3. Inputs this component accepts

Per `TARGET_COMPONENT_MAP.md` the inputs are a `PermissionDecision` and a session id. Concretely,
`create_confirmation()` takes:

* a frozen `PermissionDecision` from P4 — **only** one whose `outcome` is
  `REQUIRE_CONFIRMATION`;
* the correlation context for the turn (P1);
* already-routed action data: action type, capability, tool name, target;
* already-canonicalized arguments plus the raw arguments and the canonicalization version;
* explicit `created_at` and `expires_at`.

It performs no canonicalization (contract §9.1 / INV-006 — the canonicalizer is P3 and is not
called here), no routing, no permission evaluation and no clock read.

`permission_class` and `policy_version` are taken **from the decision**, never from a caller
argument, so no caller can state a class the policy engine did not decide.

## 4. Why creation is refused for a non-confirmation decision

`decide()` returns `ALLOW`, `REQUIRE_CONFIRMATION` or `DENY`. A confirmation record built from an
`ALLOW` is meaningless; one built from a `DENY` is a safety hole, because it would turn a refusal
into something a user can approve. `TARGET_COMPONENT_MAP.md` names `PermissionDecision` as this
component's input and `CONFIRMATION_STATE_PLAN.md` §2 records `permission_class, policy_version` as
"which rule required confirmation" — so the guard belongs here, at construction, not in a later
pipeline. Creation with any other outcome raises `ConfirmationError`.

## 5. What is deliberately absent in this phase

| Absent | Why | Owner |
|---|---|---|
| execution of anything | this is authorization state | P5 dispatcher |
| `PENDING → EXECUTING` application | claiming execution ownership without a dispatcher would create fake execution state | P5 |
| `SUCCEEDED` / `FAILED` transitions | only a trusted `TrustedToolResult` may cause them | P5 |
| persistence / on-load expiry sweep | plan §5 pairs them; no store is loaded in this phase | deferred, §71 of the task |
| per-class TTL values | plan §6 marks them "proposed"; 13B11I deferred TTL enforcement and no operator sign-off exists | deferred |
| any background timer, thread or task | the store is passive | never |
| natural-language approval parsing | contract §12.2 | the future server/UI layer maps a user action to `confirm(confirmation_id)` |
| live wiring into `app/server.py` | phase discipline | P7 |

## 6. Model non-authority, concretely

* No field of any type in this module can hold model output.
* `ModelDraft` and `ToolProposal` are rejected as arguments and rejected as values nested inside
  `raw_arguments` / `canonical_arguments`.
* `confirm()` takes an opaque id, a session id, a binding and a timestamp. There is no parameter a
  model could fill that changes the answer, and no string comparison against prose anywhere.
* The confirmation id is minted by `app.execution.correlation.new_confirmation_id()`. A caller may
  supply one only if it is well formed by that module's own check, which exists so tests can build
  deterministic fixtures — it does not let a model choose an id, because a model-chosen id still has
  to match a record that JARVIS created and still has to pass the session and binding checks.

# Task 13B11C — Audit Event Vocabulary

Production module: `app/execution/audit_events.py`.
Source of the vocabulary: `tasks/task13b11a/AUDIT_PLAN.md` §3 (the normative list). No name was
invented here, and no parallel design was introduced.

## 1. The event names

`ExecutionAuditEvent` — a `str` enum, one member per control-plane transition or observation.

| # | Member | Value | Stage | Required contract fields |
|---|---|---|---|---|
| 1 | `TURN_REQUEST` | `turn.request` | the user's turn arrives | `user_request` |
| 2 | `TURN_CLASSIFIED` | `turn.classified` | deterministic request class decided | `request_class` |
| 3 | `TURN_ROUTED` | `turn.routed` | primary action + reporting intent decided | `primary_action`, `reporting_intent` |
| 4 | `MODEL_PROPOSAL` | `model.proposal` | the model proposed a tool (untrusted) | `raw_model_tool_proposal` |
| 5 | `GUARD_DECISION` | `guard.decision` | proposal checked against the deterministic route | `proposal_guard_decision` |
| 6 | `PERMISSION_DECISION` | `permission.decision` | allow / require-confirmation / deny | `permission_decision` |
| 7 | `CONFIRMATION_CREATED` | `confirmation.created` | a pending approval exists | `confirmation_state` |
| 8 | `CONFIRMATION_CONFIRMED` | `confirmation.confirmed` | approval bound and accepted | `confirmation_state` |
| 9 | `CONFIRMATION_DENIED` | `confirmation.denied` | user refused | `confirmation_state` |
| 10 | `CONFIRMATION_EXPIRED` | `confirmation.expired` | freshness window passed | `confirmation_state` |
| 11 | `CONFIRMATION_CANCELLED` | `confirmation.cancelled` | superseded or cancelled | `confirmation_state` |
| 12 | `DISPATCH_INVOKED` | `dispatch.invoked` | an authorized attempt entered the dispatcher | `dispatched_tool`, `raw_arguments`, `canonical_arguments` |
| 13 | `DISPATCH_RESULT` | `dispatch.result` | the dispatcher observed a result | `tool_result` |
| 14 | `PROVENANCE_WRITE` | `provenance.write` | the ledger recorded or superseded facts | `provenance_updates` |
| 15 | `RESPONSE_OBLIGATION` | `response.obligation` | exactly one obligation selected | `response_obligation` |
| 16 | `RESPONSE_EMITTED` | `response.emitted` | the user-visible answer and its source | `final_response_source`, `final_user_visible_response` |
| 17 | `TURN_SUMMARY` | `turn.summary` | one reviewable line per turn | `request_class`, `lane`, `primary_action`, `response_obligation`, `final_response_source`, `safety_outcome` |

## 2. Count — a documented discrepancy in the planning artifacts

`AUDIT_PLAN.md` §3 lists **thirteen entries**, one of which is the five-state alternation
`confirmation.created|confirmed|denied|expired|cancelled`. Expanded into distinct event names that
is **seventeen**. The 13B11A `FINAL-REPORT.md` §17 summarises the same list as "fourteen new
additive event types", which matches neither the thirteen list entries nor the seventeen expanded
names.

Resolution: the **names** in `AUDIT_PLAN.md` §3 are unambiguous and are implemented exactly as
written; the integer in the summary is an arithmetic slip in a prose summary, not a second design.
This is recorded rather than silently reconciled, and it is not a conflict with frozen contract v1
(the contract fixes the seventeen *fields*, not an event count), so it was not a stop condition.

Confirmation states are separate events rather than one event with a state field because each
produces a different user-facing answer and a different audit meaning — the distinction
`CONFIRMATION_STATE_PLAN.md` §3 makes explicitly.

## 3. Properties enforced by tests

* Values are stable strings, unique, and the enum has no aliases (`__members__` length equals the
  value count, and `ExecutionAuditEvent(value) is member` for every member).
* Every name is `<stage>.<transition>` and contains no model, family, harness or benchmark name.
* `event_for_name()` rejects an unknown name with `ExecutionAuditError` — nothing is coerced into a
  new event. Case variants (`TURN.REQUEST`) and near-misses (`dispatch.invoke`) are rejected.
* Legacy event names keep working untouched: all 140 legacy literals are flat `snake_case` with no
  dot, so no v1 name can collide with one (`evidence/04-legacy-audit-inventory.txt`).

## 4. Schema version

`EXECUTION_AUDIT_SCHEMA_VERSION = 3` for these events only. `LEGACY_AUDIT_SCHEMA_VERSION = 2` is
declared alongside it so a test can assert the legacy writer still emits 2 and never 3. See
`SCHEMA_V3.md`.

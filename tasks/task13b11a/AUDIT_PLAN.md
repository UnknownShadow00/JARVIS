# Audit Plan

**Status:** plan only. `app/logs/audit.py` is unchanged.

## 1. Field-by-field mapping of the 17 contract-required audit fields

| # | Contract field (§19.1) | Today | Planned source |
|---|---|---|---|
| 1 | user request | partial — `intent_classified.query` (`app/brain/router.py:127`) | `turn.request` event with `session_id` |
| 2 | deterministic request class | **missing** (intent only) | `classifier` output + reason |
| 3 | primary action | **missing** | `router` output |
| 4 | reporting intent | **missing** | `router` output |
| 5 | raw model tool proposal | **missing** | Hermes adapter, as untrusted data |
| 6 | raw arguments | **missing** (only final `params`, `registry.call` 176) | `ToolInvocation.raw_arguments` |
| 7 | canonical arguments | partial — logged as `params` | `ToolInvocation.canonical_arguments` + rule version |
| 8 | proposal-guard decision | **missing** | `permissions`/guard result |
| 9 | permission decision | partial — `safety_level`, `confirmation_required` in trace metadata (`registry.call` 168) | `PermissionDecision` incl. class and `policy_version` |
| 10 | confirmation state | partial — `approval_gate_triggered` / `approval_gate_confirmed` (646, 830) | confirmation record transitions incl. `EXPIRED`, `DENIED`, `CANCELLED` |
| 11 | dispatched tool | yes — `tool_call` | unchanged, plus `invocation_id` |
| 12 | tool result | partial — `tool_result` truncates to 500 chars | structured `facts` / `error` / `status` |
| 13 | provenance updates | **missing** | ledger write events |
| 14 | response obligation | **missing** | obligation engine |
| 15 | final response source | **missing** | response builder |
| 16 | final user-visible response | **missing** | the approved response object |
| 17 | safety outcome | partial — inferable | explicit per-turn outcome record |

## 2. Correlation

`app/observability/tracing.py` already supplies a per-request `trace_id`, attached to every audit
entry when present (`app/logs/audit.py:56`), and `/confirm` re-opens the original trace
(`app/server.py:795`). Plan:

* `trace_id` stays the **turn** correlation id.
* Add `invocation_id` for tool attempts and `confirmation_id` for approval flows, both carried in
  the event payload so a full chain can be reconstructed by joining on three keys.
* One `turn.summary` event per turn carrying class, lane, action, obligation, final source and
  safety outcome — so a reviewer can audit a day of behaviour without replaying every span.

## 3. Event set to add

`turn.request`, `turn.classified`, `turn.routed`, `model.proposal`, `guard.decision`,
`permission.decision`, `confirmation.created|confirmed|denied|expired|cancelled`,
`dispatch.invoked`, `dispatch.result`, `provenance.write`, `response.obligation`,
`response.emitted`, `turn.summary`.

Existing event names (`intent_classified`, `tool_call`, `tool_result`, `approval_gate_*`) stay
untouched so legacy behaviour and existing log consumers keep working during migration.

## 4. Format and compatibility

Keep `schema_version: 2` for legacy events; new events use `schema_version: 3` with the same
envelope (`timestamp`, `event_type`, `data`, `session_id`, `trace_id`). Readers that filter by
`event_type` are unaffected. The existing rotation and fallback-write behaviour
(`app/logs/audit.py:60-75`) is reused unchanged.

## 5. Redaction and retention

* **Never** store chain-of-thought or hidden reasoning (§19.2, INV in contract §19).
* Store the model's *draft* text only where a safety review needs it: recommended default is to
  store a hash plus the first N characters of a draft that was **blocked**, and nothing for drafts
  that were simply not selected. Storing every draft in production would multiply log volume and
  retain model prose about the user's data for no operational benefit.
* Tool arguments may contain paths and message bodies: redact configured secret keys, and keep
  message bodies only for `EXTERNAL_COMMUNICATION` actions where the user must be able to audit
  what was sent.
* Retention follows the existing rotation settings (`settings.logging.max_log_size_mb`, 3 backups);
  a separate retention policy for provenance/confirmation records should be decided when
  persistence is added, not now.

## 6. Failure behaviour

Audit is asynchronous today (queue + daemon thread), so a write failure cannot block a turn. Plan:
keep that for informational events, but treat **safety-critical** events — permission decision,
confirmation transition, dispatch invoked/result — as fail-closed: if they cannot be enqueued, the
turn must not dispatch. The queue is unbounded in memory today; a bounded queue with a
fail-closed path for safety events is the safer v1 shape.

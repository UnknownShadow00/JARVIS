# Confirmation State-Machine Plan

**Status:** plan only. `_pending_confirmations` (`app/server.py:87`) is unchanged.

## 1. What exists today

An in-memory `dict[str, dict]` keyed by an 8-character UUID slice, storing `{tool, params,
trace_id}` (`app/server.py:646`), popped and executed by `POST /confirm/{request_id}`
(`app/server.py:792`). No session binding, no expiry, no re-validation, no persistence; the store
dies with the process, and deep sleep exits the process.

## 2. Planned record

| Field | Type | Why |
|---|---|---|
| `confirmation_id` | opaque token (≥128-bit, not a truncated uuid4) | unguessable; the 8-char slice is too small once confirmations can arrive over chat surfaces |
| `session_id` / `user_id` | string | binds approval to the requester (§12.3) |
| `action_type` | enum | what was asked |
| `target` | normalized target | what it acts on |
| `canonical_arguments` | mapping | exactly what would run |
| `raw_arguments` | mapping | audit + mismatch detection |
| `tool_name` | string | the dispatcher entry point |
| `permission_class`, `policy_version` | enum, string | which rule required confirmation |
| `created_at`, `expires_at` | UTC timestamps | freshness (§12.3) |
| `state` | enum (below) | lifecycle |
| `provenance_ref` | turn / event id | links the request that produced it |
| `audit_ref` | correlation id | joins the whole chain |
| `invocation_id` | set on execution | idempotency (see idempotency plan) |

## 3. Minimum coherent state machine

```
PENDING ──confirm──► EXECUTING ──ok──► SUCCEEDED
   │                    └──error──► FAILED
   ├──deny──► DENIED
   ├──timeout──► EXPIRED
   └──supersede/cancel──► CANCELLED
```

Six persisted states plus the transient `EXECUTING`. Justification for choosing this set over the
larger candidate list:

* `PENDING`, `CONFIRMED`, `EXECUTING` — `CONFIRMED` as a *resting* state is dropped: a confirmed
  action that is not yet executing is an ambiguous state that invites double execution. Approval
  transitions directly into `EXECUTING` under a lock, so "confirmed but not running" never exists.
* `SUCCEEDED` / `FAILED` are kept because the response obligation and the provenance ledger need
  the outcome, not just the fact of approval.
* `DENIED`, `EXPIRED`, `CANCELLED` are kept and kept distinct: they produce different user-facing
  answers and different audit meanings.

## 4. Binding rule (the invariant)

Approval applies to **one** pending record and only if all of the following match at approval
time: `confirmation_id`, `session_id`, `action_type`, `target`, `canonical_arguments`, and
`state == PENDING`, and `now < expires_at`. Any mismatch → no execution, record moves to
`CANCELLED` or stays `PENDING` (design decision at implementation time), and the event is audited.

Re-deriving the canonical arguments from the original request text at approval time and comparing
them to the stored ones is recommended, so that a changed policy or lexicon cannot silently
execute something different from what was described.

## 5. Storage

Start with an in-process store behind an interface (`ConfirmationStore`), persisted as
append-only JSON under `data/` — consistent with how `app/agent/task_queue.py` persists
(`data/agent_tasks.json`, `_save`, line 110) — so that:

* a restart or the deep-sleep process exit does not silently lose pending approvals;
* on load, any `PENDING` record whose `expires_at` has passed becomes `EXPIRED` rather than
  executable.

No database is introduced in v1 (there is none today). If multi-device confirmation later needs
concurrent writers, the interface allows swapping the backend without touching the state machine.

## 6. Expiry default

Proposed default TTL: **5 minutes** for REVERSIBLE_ACTION and EXTERNAL_COMMUNICATION,
**2 minutes** for DESTRUCTIVE_ACTION / SYSTEM_POWER / PRIVILEGED_ACTION, configurable per class in
`config/permissions.yaml`. Rationale: an approval that arrives after the user has moved on is
exactly the stale-confirmation risk (F-13 in the contract's failure model), and destructive
actions deserve the shorter window.

## 7. Surfacing

The confirmation must be representable in the API response (see the API/UI section of the
integration plan) rather than only as a Discord/Telegram sentence containing a URL
(`app/server.py:652-668`). The existing out-of-band path may remain for remote approval, but the
record, not the message, is the source of truth.

# Tool Invocation / Result Contract Plan

**Status:** plan only. Today's `ToolResult` (`app/tools/registry.py:41`) carries `tool`, `output`,
`dry_run` and nothing else (gap G-14, G-15).

## 1. `ToolInvocation` (minimum v1)

| Field | Purpose | Contract |
|---|---|---|
| `invocation_id` | unique per attempt; the idempotency and audit key | §18.2 |
| `turn_id`, `session_id` | correlation and ownership | §19.1 |
| `action_type` | the routed action, not the model's wording | §5.2 |
| `tool_name` | dispatcher entry point | §18.2 |
| `raw_arguments` | exactly what the model proposed | §9.1, INV-006 |
| `canonical_arguments` | exactly what will run | §9.1 |
| `canonicalization_version` | which rule set produced them | §9.1 |
| `permission_class`, `permission_outcome`, `policy_version` | why this was allowed | §11 |
| `confirmation_id` | present iff confirmation was required | §12.3 |
| `requested_at` | UTC | §19.1 |

## 2. `ToolResult` (minimum v1)

| Field | Purpose |
|---|---|
| `invocation_id` | binds the result to exactly one invocation |
| `tool_name`, `action_type` | identity |
| `status` | `SUCCESS` \| `ERROR` \| `CONFIRMATION_REQUIRED` \| `BLOCKED` \| `TIMEOUT` |
| `facts` | a small mapping of *explicitly returned* values (e.g. `{"database_status": "reachable", "latency_ms": 12}`) |
| `error` | structured kind + message for `ERROR` (e.g. `app_not_found`) |
| `executed` | boolean; false for confirmation-required, blocked, dry-run |
| `started_at`, `finished_at` | latency and timeout reasoning |
| `executor` | which dispatcher ran it |
| `audit_ref` | correlation id |

`facts` is the field that makes §18.4 (minimal-result principle) enforceable: the response builder
may use only keys present in `facts`, so "success implies health" becomes impossible to express.

## 3. Rules

1. A `ToolResult` may be created **only** by `app/execution/dispatch.py`. No other module may
   construct one; the type should make that awkward (private constructor / factory in the
   dispatcher module).
2. `status == SUCCESS` with an empty `facts` mapping is legal and means "it ran and returned
   nothing to report" — the response builder must then say exactly that, not invent an effect.
3. `CONFIRMATION_REQUIRED` and `BLOCKED` always carry `executed = false`.
4. `TIMEOUT` is a distinct status, never folded into `ERROR`, because the side effect may or may
   not have happened — the response must not claim either (see the idempotency plan).
5. Dry-run (`settings.safety.dry_run`) produces `executed = false` and an explicit dry-run marker,
   never a fabricated success.

## 4. Relationship to the existing registry

`registry.call()` keeps its safety gate and stays the last mile. `dispatch.py` wraps it:

```
dispatch(invocation) -> TrustedToolResult
    check permission decision is present and ALLOW/confirmed
    call registry.call(tool, canonical_arguments, confirmed=...)
    translate ToolError / output into a typed TrustedToolResult
    write the invocation + result audit events
    hand the result to the provenance ledger
```

The translation step is where today's stringly-typed errors (`ToolError("Tool 'x' is Level 2.
Requires user confirmation…")`, `app/tools/registry.py:200`) become structured statuses, which
removes the fragile `_is_confirmation_required_error` substring test at `app/server.py:788`.

# Audit and Provenance Compatibility — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.**

Nothing in this task emits an audit event or writes a provenance record. The schema is unchanged.
What follows is what a **future** phase will be able to record, proven by constructing the payloads
passively in tests and serializing them — never by calling a writer.

## 1. The schema already has the vocabulary

`app/execution/audit_events.py` (P1, schema v3, unchanged by this task) already defines five
confirmation events and requires the same field for each:

| Event | Required field |
|---|---|
| `confirmation.created` | `confirmation_state` |
| `confirmation.confirmed` | `confirmation_state` |
| `confirmation.denied` | `confirmation_state` |
| `confirmation.expired` | `confirmation_state` |
| `confirmation.cancelled` | `confirmation_state` |

`confirmation_state` is field 10 of the seventeen contract §19.1 fields, typed
`Mapping[str, Any] | None`. So the only thing this task owes the audit layer is a JSON-safe mapping
of a confirmation record — no new event, no new field, no schema bump.

The five events cover four of the five reachable outcomes plus creation. There is deliberately no
`confirmation.executing`, `confirmation.succeeded` or `confirmation.failed` event: execution
outcomes belong to `dispatch.invoked` / `dispatch.result` and to `TrustedToolResult`, which is P5's.

## 2. `to_audit_payload(record)`

Returns a plain JSON-safe `dict` for the `confirmation_state` field. Enums become their stable
string values and datetimes become ISO-8601 strings, matching `types.to_mapping`.

Included: `confirmation_id`, `session_id`, `user_id`, `state`, `execution_started`, `action_type`,
`capability`, `tool_name`, `target`, `raw_arguments`, `canonical_arguments`,
`canonicalization_version`, `permission_class`, `policy_version`, `created_at`, `expires_at`,
`resolved_at`, `invocation_id`, `provenance_ref`.

Excluded, by construction and asserted by test: user message text, conversation history, model
prose, model confidence, model rationale, chain-of-thought under any spelling. The nine field names
in `FORBIDDEN_REASONING_FIELDS` cannot appear, and the payload is checked against them after the
same normalization the audit validator uses.

`execution_started` is included because contract §12.1 requires `executed = false` to be visible
while a confirmation is pending. It is `True` only for `EXECUTING`, `SUCCEEDED` and `FAILED` —
none of which is reachable in this phase — so it is `False` on every record this phase can build.

## 3. Provenance compatibility

`ProvenanceSource.CONFIRMATION_REQUIRED` already exists (P2, unchanged) and is declared
`implies_verified_state: false`. A passive test constructs a `ProvenanceRecord` with that source
alongside a `PENDING` confirmation and asserts its trust class is not `VERIFIED` — the pending
confirmation states that something is *waiting*, never that anything happened.

No ledger is instantiated and no record is written.

## 4. Correlation

The record carries a `CorrelationContext` (`audit_ref`) whose `confirmation_id` equals the
record's own id and whose `session_id` equals the record's session. Construction validates both, so
an audit event built from the record joins the same turn's classification, routing, permission and
future dispatch events on ids that cannot disagree with the record they describe.

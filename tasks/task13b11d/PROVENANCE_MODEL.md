# Task 13B11D — Provenance Model

Production module: `app/execution/provenance.py`. The record type itself is the one frozen in
phase P0, `app/execution/types.py::ProvenanceRecord` — P2 composes it and does not restate it.

## 1. The record

| Field | Type | Meaning |
|---|---|---|
| `record_id` | `ProvenanceRecordId` | opaque id, minted from the P1 identifier family |
| `session_id` | `SessionId` | the conversation this fact belongs to |
| `turn_id` | `TurnId` | the turn or event it came from (contract §9.3) |
| `fact_key` | `str` | lowercase identifier; the value never lives in the key |
| `value` | passive data | scalar, mapping, sequence or datetime — frozen on the way in |
| `source` | `ProvenanceSource` | where it came from (§3.2) |
| `trust_class` | `TrustClass` | whether it may be presented as verified (§9.3, §16) |
| `created_at` | tz-aware UTC | when it was recorded |
| `status` | `ProvenanceStatus` | `CURRENT` or `SUPERSEDED` |
| `invocation_id` | `InvocationId \| None` | set **only** for a dispatcher result (§18.2) |
| `superseded_by` | `record_id \| None` | set **only** on a superseded record |

Contract §9.3 requires key, value, source, originating turn and current/superseded status. All five
are present, plus the trust class, the session scope and the invocation binding.

## 2. Values are data, never authority

`freeze_value()` accepts scalars, mappings, sequences and datetimes, returns read-only copies of
mappings and tuples of sequences, and refuses anything else. A `ModelDraft` or `ToolProposal` is
rejected outright: model output cannot enter the ledger even disguised as a value. Nothing in the
module executes, resolves, opens or dispatches a stored value.

## 3. Fact keys

`^[a-z][a-z0-9_]*$`, at most 128 characters — `deployment_target`, `service_port`,
`preferred_region`, `observation`. Small and predictable rather than an ontology; widening it later
is an additive change. No benchmark-specific key is hardcoded anywhere in production.

A `TOOL_SUCCESS` record takes its key straight from the key the tool returned in `facts`, so a tool
returning a key that is not a valid fact key is rejected rather than silently rewritten.
A `TOOL_ERROR` record uses `<tool_name>_error`.

## 4. Immutability

Records are frozen dataclasses with read-only mapping values. Supersession replaces the stored
record with a new version of itself (`dataclasses.replace`) rather than mutating it, so a reference
a caller already holds never changes underneath them, and no stored value is ever edited. Every
lookup returns a tuple; `snapshot()` returns a separate immutable view that does not follow later
writes.

## 5. Identifiers

`ProvenanceRecordId` was added to `app/execution/correlation.py` — the same `uuid4().hex` family as
the P1 session, turn, invocation, confirmation and audit ids, validated by the same
`is_well_formed_id()`. One identifier scheme, not two. 13B11C deferred this id to P2 explicitly;
this is that deferral being closed.

## 6. Serialization

`to_audit_payload(record)` reuses the contract's own `to_mapping`: enums become their stable string
values, timestamps ISO-8601, read-only mappings plain dicts. The result is JSON-safe as it stands
and is a fresh dict each call. `LedgerSnapshot.to_mapping()` wraps the session id and a list of
those payloads. Nothing is written to any file.

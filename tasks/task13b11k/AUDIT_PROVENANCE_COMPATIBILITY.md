# Audit and Provenance Compatibility — Task 13B11K

Nothing is emitted and nothing is written. These are shape checks against the sealed P1 and P2
foundations, performed in tests with synthetic records.

## Audit

Schema v3 is unchanged: 17 contract fields, no new event, no new field, no `lane`. The two
invocation events the vocabulary already declares — `dispatch.invoked` and `dispatch.result` —
are constructed in a test from a real invocation and a real trusted result, passed through
`validate()` and `to_audit_entry()`, and asserted to carry the invocation id in the envelope.
They are never handed to a writer, and `app/logs/audit.py` is byte-identical.

`REQUIRED_FIELDS_BY_EVENT` already demands `dispatched_tool`, `raw_arguments` and
`canonical_arguments` on `dispatch.invoked` and `tool_result` on `dispatch.result`; the
invocation and the result supply exactly those, which is CT-010 satisfied at the data level.

## Provenance

`provenance.py` is byte-identical and `ProvenanceSource` still has 8 members with no `TIMEOUT`.
Three compatibility tests pass a trusted result to the existing `record_tool_result`:

* a `SUCCESS` with `{"database_status": "reachable", "latency_ms": 12}` produces exactly two
  `TOOL_SUCCESS` records, one per returned key, and nothing else — §18.4;
* a `TIMEOUT` is refused: `ProvenanceError`, no record, no fact, no claim in either direction;
* a `BLOCKED` and a `CONFIRMATION_REQUIRED` are refused the same way, and both carry
  `executed = false`.

The ledger's own rule — *"only a `TrustedToolResult` from the authorized dispatcher"*, by type
and not by shape — is now true in the strong sense: `app/execution/dispatch.py` is the only
module under `app/` that constructs one, asserted by test.

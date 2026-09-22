# Audit and Provenance Compatibility

Schema v3 is unchanged. Task 13B11M emits no event and imports no audit writer.

`ApprovedOperationalResponse` already supplies the planned `response.emitted` fields: final text,
obligation, source, turn identity, timestamp and supporting provenance record IDs. Existing
`to_mapping()` serialization remains deterministic and JSON-safe.

The builder reads no `ProvenanceLedger`, `LedgerSnapshot`, `LedgerStore`, confirmation store, or
audit log. Exact records are supplied by the caller. Records are not written, superseded, mutated
or reordered.

For a displayed tool-observed value, the builder validates the full chain:

```text
ToolInvocation.invocation_id
  == TrustedToolResult.invocation_id
  == ProvenanceRecord.invocation_id
```

It also validates tool/action identity, session/turn identity, `SUCCESS`/executed state, fact-key
presence, and exact fact value. Current-turn success/error/timeout/blocked responses validate the
current invocation/result action, tool, session, turn and invocation ID.

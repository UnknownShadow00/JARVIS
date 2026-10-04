# Existing P2 data and semantics

Imports from `app.execution.provenance`: `LedgerStore`, `LedgerSnapshot`, `validate_record`, and the existing `ProvenanceRecord` symbol that P2 itself imports from P0. The record remains the original frozen P0 type; it is not copied or redefined. P2 source and its API remain byte-identical to entry.

Snapshot issuance is exactly `owner._store.for_session(owner_session).snapshot()`. Existing P2 constructs one per-session `ProvenanceLedger`, then a current-record tuple snapshot. An empty new session therefore comes from actual P2 allocation, never `LedgerSnapshot(session, ())` as a repair path. No independent state implementation, fabricated record or trust class is added.

The boundary invokes existing `validate_record` for every record and verifies its session association and passive immutable value graph. Mutable lists/dicts, callables and object handles are rejected rather than turned into a new provenance implementation. All normal P2 fixture records used here originate from the canonical freezing writer. The snapshot object itself is retained exactly.

# P2 separation

The record is never a ProvenanceRecord, TOOL_SUCCESS/ERROR fact or trusted ledger mutation. No LedgerStore, ProvenanceLedger, LedgerSnapshot or record_* operation is accepted/called. Existing authoritative identity is copied from the settled context without carrying its P2 snapshot.

A model draft, hypothetical result, binding fingerprint or permission observation cannot be promoted into P2 because JARVIS emitted this record. No new ProvenanceSource or TrustClass is introduced. The future sink stores observations separately under its own unresolved contract; the producer has no sink/write path.

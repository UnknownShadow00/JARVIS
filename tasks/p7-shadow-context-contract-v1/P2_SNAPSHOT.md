# Request-time snapshot

After minting the turn and before any shadow evaluation, call snapshot() on the owner's same-session ledger. Keep exactly that snapshot for that turn. Validate session equality and every record through existing P2 validation. Later ledger append/supersession cannot replace the captured tuple or change frozen record values.

Canonical new-session behavior exists: LedgerStore.for_session creates ProvenanceLedger with an empty record list; ledger.snapshot then yields a same-session snapshot with records=(). This is the only new-session empty path frozen here. It means no facts available in this context, not a claim that the world is empty. Failure to resolve a ledger or snapshot must not be replaced by `LedgerSnapshot(session_id, ())`.

LedgerSnapshot's public API is read-only; it is not a frozen dataclass and private Python slot assignment is not a security boundary. Reuse the existing type and validate provenance at the owner boundary. The owner must not retain a mutable/public alias that rewrites a settled snapshot. Hostile in-process arbitrary Python mutation is not proven impossible by this contract. No P2 source change or duplicate snapshot type is authorized.

# P2 source resolved by Context V1

Take context.snapshot exactly as settled after the turn ID was minted. It originated from the existing owner-held LedgerStore.for_session(session).snapshot path. Do not read a later snapshot during composition or evaluation. Existing P2 public immutability means subsequent ledger writes do not change the turn's records.

Require snapshot.session_id == context.correlation.session_id and validate record association. An empty new-session snapshot is legitimate only through actual P2 new-session ownership; failure is never repaired with an empty fallback. No mutable ledger/store or write operation enters the envelope.

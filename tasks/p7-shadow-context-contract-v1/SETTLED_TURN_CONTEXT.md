# Minimum settled turn value

Contract name: **SettledShadowTurnContextV1**, an immutable container, not a new identity type. Exactly these fields are frozen:

| Field | Type / source | Meaning |
|---|---|---|
| correlation | existing CorrelationContext | JARVIS-minted session and turn; initial invocation/confirmation absent |
| snapshot | existing LedgerSnapshot | captured same-session P2 read-only request-time view |
| transport_trace_id | str or None | observational server trace association; never authority |

No duplicate session/turn/correlation scalar fields, timestamp, numeric TTL, mode, route or transport label is necessary. A version suffix on the value name suffices; no wire serializer/schema is selected. Exact P1 identifiers must be well formed; snapshot.session_id must equal correlation.session_id, and records must validate and belong to that session. Validation does not replace the trusted owner as source.

Exclude registry, dispatcher, executor, provider/model client, confirmation store, mutable ledger/store, HTTP request, WebSocket, server, callback/callable and arbitrary mapping references. Downstream accesses only this settled value. Snapshot immutability has the existing P2 public-API semantics documented in P2_SNAPSHOT.md; later owner writes cannot alter it.

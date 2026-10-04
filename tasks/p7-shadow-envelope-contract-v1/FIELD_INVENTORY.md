# Required facts and source status

| Fact | Frozen downstream type/meaning | REST source | WS source | Owner/trust | Status |
|---|---|---|---|---|---|
| request text | exact `str`, raw untrusted content | `ChatRequest.message` | parsed `message` or raw frame, string-check needed | client content; server validates shape | AVAILABLE |
| session ID | P1 `SessionId`, conversation scope | no request/session field | no authoritative session field | JARVIS only | **SOURCE UNASSIGNED** |
| turn ID | P1 `TurnId`, one accepted turn | trace exists, different textual UUID form | trace exists before stream; same mismatch | JARVIS only | **MINT/ASSOCIATION UNASSIGNED** |
| P2 snapshot | immutable `LedgerSnapshot` for same session | no live ledger/store | no live ledger/store | P2 JARVIS state | **SOURCE UNASSIGNED** |
| trace association | link observation to turn | `start_trace` UUID string | `start_trace` UUID string | server tracing, observational pending mapping | **RELATION UNASSIGNED** |

`request_id` in legacy `/confirm/{request_id}` is a truncated approval token (`app/server.py:636-649,791+`), not a P1 turn or session ID. No invocation ID exists at ingress. `ClassifierContext`, registry metadata and approval mode are separate later binder inputs, not transport payload fields. Required/optional validation of the missing facts cannot be finalized before source assignment.

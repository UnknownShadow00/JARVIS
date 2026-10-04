# Session lifecycle

One logical JARVIS client conversation/context maps to one authoritative JARVIS session. Resolve or create it before the first shadow-eligible accepted turn. Reuse its identity for subsequent accepted turns in that context. HTTP requests, WS frames, trace IDs, output chunks and model calls do not define session lifetime.

The canonical REST ChatRequest has only message (`server.py:244-246`); WS extracts message without a session resolver (`:505-509`). P1/P2 reference scans find no live session continuation owner. Therefore V1 freezes only a requirement for a JARVIS-issued opaque continuation handle, resolved and validated by JARVIS. A client presenting a handle does not author a session ID. Cookie/header/payload choice, binding/authentication details, expiry and capacity remain unresolved before live use; no numeric TTL is chosen.

P2 is in-memory and does not survive process exit (LEDGER_API §6). On a new authoritative session, create its ledger using LedgerStore.for_session. Do not claim a lost prior context is empty known truth. Invalid/unresolvable continuation fails shadow closed. Explicit session-end cleanup can use existing drop; exact session-end detection and retry/reconnect protocol are deferred, not silently equated to socket close. No restoration from an arbitrary client session string.

# Transport-neutral composition

Ingress imports no FastAPI/Starlette, HTTP Request, WebSocket, server, socket, callback, response writer or connection object. Its only application import is the settled type. REST/WS labels occur in test fixtures only and are never constructor inputs.

Equivalent accepted text and equivalent settled context produce equivalent envelope semantics, with the same correlation/snapshot association. Trace is carried exactly as observational metadata. Different already-settled turns legitimately retain different IDs; composition invents no retry or idempotency policy.

The frozen REST capture before server.py `_process` and WS capture before `_process_stream` remain documentation only. Stream/fallback/chunk, disconnect, cancellation, sleep and voice wiring cases from B01–B16 are future integration tests, not claimed from passive units. No capture point or server byte changed.

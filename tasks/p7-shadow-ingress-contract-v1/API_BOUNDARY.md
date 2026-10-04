# Meaning of API

Existing API surfaces are REST `POST /chat` and WebSocket `/ws` (`app/server.py:357,496`); `tasks/p7-p8-entry-recovery-review/SERVER_API_UI_REQUIREMENT.md` interprets 13B11A API/UI as existing ingress, not a new public endpoint. REST accepts `ChatRequest.message`; WS accepts raw text or JSON with a `message` value. Shadow must not accept or expose a separate public invocation endpoint. REST `ChatResponse` and WS `reply` payloads remain byte-equivalent to legacy at the application boundary. Authorization and transport parsing remain server-owned.

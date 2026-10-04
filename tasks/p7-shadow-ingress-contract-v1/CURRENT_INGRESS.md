# Canonical Core ingress inventory

Production commit `d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c`. `app/server.py:244-254` defines REST `ChatRequest(message: str)` and `ChatResponse(reply,intent,confidence,dry_run,active)`. `chat` (`:357-379`) opens a trace, wakes the resource manager, calls `_process(req.message)`, and returns the legacy response.

WebSocket `ws_endpoint` (`app/server.py:496-559`) accepts configured `/ws`, receives text, parses JSON `message` if present or raw text, then calls `_process_stream(message)` first. It calls `_process(message)` **only when streaming returns None**; it sends/broadcasts the legacy reply. `_process_stream` (`:840+`) can call `registry.call` on the legacy path. `_process` (`:598+`) owns legacy intent classification, tool call, model reply, confirmation and response cleaning. The legacy path is production behavior, not the new control plane.

PWA `frontend/pwa/app.js:5,89-100,372,405,426` uses `/ws` and REST `/chat` fallback with `{message}`; Electron `frontend/electron/preload.js:34` and hologram `frontend/hologram/app.js:10,120` also use `/ws`. No client-provided capability, permission or session ID is authoritative. There is no Core server use of `LedgerStore`/`new_turn_context`, and `binding_projection.py` has zero production consumers.

**Insertion conflict:** the 13B11A plan calls for one branch at the top of `_process` (`IMPLEMENTATION_PHASES.md:34`, `FEATURE_FLAG_AND_ROLLBACK.md:30-35`), but WebSocket streaming can bypass `_process`. The exact capture point for all normal UI traffic is unresolved; disabling streaming or adding two independent entry branches would change the plan or legacy behavior.

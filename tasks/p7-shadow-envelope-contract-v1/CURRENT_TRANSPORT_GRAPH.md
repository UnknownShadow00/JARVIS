# Actual user-facing call graph

REST: `app/server.py:244-254` validates `ChatRequest(message: str)`; `/chat` at `:357-380` opens `start_trace`, checks wake, then `_process(req.message)` at `:370`, constructs the legacy `ChatResponse`, and resets the token.

WebSocket: `/ws` at `app/server.py:496-559` authenticates/accepts, receives one text frame, parses JSON `message` or uses raw text (`:505-509`), checks wake, opens one trace (`:524`), then tries `_process_stream(message)` (`:527`). Only if it returns `None` does it call `_process(message)` (`:529`); otherwise it consumes stream chunks for TTS and returns one reply (`:530-552`). An output chunk is not a user turn.

Other user-facing ingress: `app/voice/audio_stream.py:68-113` transcribes audio and directly calls server `_process_stream`, then `_process` on fallback; it bypasses REST/WS. Dictation takes a separate path (`:85-88`). This task's requested REST/WS boundary does not silently claim voice coverage. `/confirm`, `/ue5`, resource and admin routes are not normal chat input. PWA `/ws` plus REST fallback (`frontend/pwa/app.js:372,401-426`), Electron and hologram use `/ws`.

No production caller in `app/` constructs `CorrelationContext` or `LedgerStore` for these request paths (`git grep` inventory in evidence). Current binder still has zero production consumers.

# Future server / REST / WS implementation inventory

Pinned Core: d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c. No source changed.

| Location | Existing semantics | Future bounded insertion requirement |
|---|---|---|
| ChatRequest server.py:244 | message:str; no continuation field | transport continuation representation needs decision; no client authoritative IDs |
| chat :358-380 | active trace, wake check, reset, await _process, ChatResponse, finally reset | capture context/envelope immediately before :370, inside shadow-local exception boundary |
| ws_endpoint :497-559 | authenticated connection, loop; parse message/raw; wake check; per-input trace; stream/fallback; TTS; reply | capture once after :525 and before :527; no second capture at :529 or chunks |
| _process :598 | async function; sync classification; legacy registry/model/memory/emotion work | must remain original legacy processing; no implicit capture duplication |
| _process_stream :840 | async function; can return None before/after classification and tool/model attempts | no shadow model/evaluation here; fallback must reuse one captured turn |
| WS finally :553-555 | reset token and listening=False broadcast | capture/evaluator failure cannot bypass cleanup or add user-visible error |
| voice/audio_stream.py :20-29,96,112 | direct stream/process wrappers | explicitly deferred; no accidental coverage from instrumenting internals |

REST try/finally does not catch processing exceptions; WS outer except handles WebSocketDisconnect. New capture isolation is therefore necessary, but no general change to existing error behavior is authorized. Existing JSON non-object and non-string WS cases are legacy behavior, not a mandate for this session to fix the parser. Bounded instrumentation must account for failure before a context exists without fake IDs.

Current async declarations are not proof of nonblocking evaluation: classification and registry calls execute inline; token streaming/TTS adds awaits; cancellation uses a shared current_token. The session snapshot must be captured before deferred work and detached from request/socket/trace-context lifetimes. Choosing post-response, task, thread or worker is unresolved. Mode is currently parsed but only LEGACY is active; no flag read in request paths is authorized now.

Future non-activation gates are enumerated with exact assertions in TEST_AUTHORIZATION_INVENTORY. Behavioral regressions likely exercised: tests/test_server_integration.py::test_chat_respond_intent, test_chat_browser_tool, test_chat_vision_intent_calls_vision_tool, test_chat_retrieve_memory_intent_adds_context, test_chat_dry_run, test_chat_missing_message; tests/test_server_auth.py REST/WS token/origin tests; tests/voice_pipeline_test.py::test_voice_pipeline_stop_is_responsive. These existing tests do not already assert one shadow context/envelope or shadow-local failure isolation. Add approved focused mocked REST/WS tests later; do not call live endpoints or models to test this contract.

Required future file responsibilities: shadow_context.py owns context association only; shadow_ingress.py owns pure envelope composition; evaluator file/location remains undecided; server.py contains only reviewed capture/consumer seam and isolation; API/UI continuation transport changes await protocol decision. Keep app/execution/__init__.py from becoming a broad re-export/activation surface.

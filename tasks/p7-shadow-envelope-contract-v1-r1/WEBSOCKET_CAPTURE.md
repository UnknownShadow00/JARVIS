# Exact future WS capture point

`app/server.py::ws_endpoint`: inside start_trace at line 524, after the existing listening=True broadcast at line 525, immediately before `_process_stream(message)` at line 527. Wake succeeded, the message has been extracted, and the current input has one active trace. Resolve context and compose once here. When _process_stream returns None, `_process(message)` at line 529 reuses that input's context and creates no second envelope.

Use the exact extracted message string, not raw JSON, WebSocket object, manager, callback or later chunks. The current parser accepts JSON object.message or raw text on JSONDecodeError; valid JSON non-objects can already raise at data.get, and non-string message values are not validated here. The shadow composer admits exact strings only; it must not repair/coerce legacy input or alter existing error semantics. Existing pre-capture parser failures produce no shadow capture.

Streaming chunks (:534-537), TTS (:539-540), cleaning (:541), reply sends (:550-552), disconnect handling (:556-559) and listening=False cleanup (:553-555) retain their existing roles. No new capture in these paths. Voice calls to the internal functions remain outside this boundary.

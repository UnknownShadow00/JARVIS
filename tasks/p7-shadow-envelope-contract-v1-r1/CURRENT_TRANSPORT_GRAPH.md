# Canonical transport graph

| Ingress | Accepted message path | Legacy branches | Capture scope |
|---|---|---|---|
| POST /chat | ChatRequest.message (:244-246), chat (:358) | start_trace (:359), wake check, token reset, _process (:370) | one accepted REST input |
| WS settings.server.websocket_path | ws_endpoint (:497), receive_text (:505), JSON message/raw fallback (:506-509) | wake check, token reset, start_trace (:524), listening broadcast (:525), _process_stream (:527), _process fallback (:529) | one accepted WS input before fork |
| voice | audio_stream.py wrappers (:20-29), recognized text (:68-113) | stream (:96), fallback (:112) | deferred, no coverage claim |

Server _process (:598) and _process_stream (:840) are async functions. Both can classify and enter legacy registry/model paths. They must not be invoked by this contract work. WS streaming returns a token iterator; chunks (:534-537) are accumulated and cleaned (:541), then sent/broadcast (:550-552). Output chunks cannot be recaptured as turns. A complete app/ reference scan is retained in session evidence.

/confirm is a separate confirmation action, /ue5 consumes animation/comms input, and task/sensor/resource/admin routes are not this chat-envelope scope. Existing PWA REST fallback and WS clients do not supply authoritative P1 context. No additional server processing ingress found beyond REST, WS and voice wrappers in the canonical call scan.

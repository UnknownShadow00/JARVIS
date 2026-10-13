# REST and WebSocket integration

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

`build_isolated_app` constructs FastAPI with only the guarded /chat and /ws consumer, no docs/openapi, live lifespan, tool, voice, TTS, broadcast, /ue5 or public opening route. It requires RulesFirstL1, OwnedProvider/NativeTransport, HighWater, EvidenceBridge and CheckpointWriter. No import is added to production app/server.py or startup.

REST keeps POST /chat, message JSON, Bearer header, x-jarvis-continuation and reply/intent/confidence/dry_run/active envelope. WS keeps the continuation frame parser and type=reply envelope. Auth is checked before body or accept. Origin-less native WS clients remain allowed as in source; explicit origins must match injected exact configured/loopback origins. Duplicate origin/auth headers refuse. The fixture injects localhost:8000; it is not production configuration.

Request bodies/frames are bounded. Binary/mixed frames, malformed controls, unexpected events, duplicate/invalid framing and unknown routes refuse. HTTP Transfer-Encoding is rejected at the ASGI seam as a proposed stricter release delta; actual wire smuggling defenses need server-stack qualification. No client-supplied opener, epoch, model or permit is accepted. Continuation tokens live in the exact runtime instance; restarts/reconnects cannot mint authority.

During runtime work, a concurrent receive detects disconnect or extra input and aborts the accepted branch without queueing/fallback. Delivery is LOCAL_SEND_COMPLETED only when application send finishes. This is NOT client acknowledgement/display. Disconnect can prevent Granite completion after a legacy reply; the completed legacy delivery/history remains recorded.

Tests use actual FastAPI/Starlette ASGI dispatch in process. They do not prove deployed auth configuration, reverse-proxy behavior, TCP/WebSocket protocol parsing or actual browser receipt. Classification: IMPLEMENTED, ISOLATED-TESTED; production route mount and startup are not activated.

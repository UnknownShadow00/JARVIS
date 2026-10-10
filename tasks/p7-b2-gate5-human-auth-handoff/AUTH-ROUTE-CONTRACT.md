# Deployed authentication and no-message contract

Source HEAD bd53dbc799fb9284a21fae8cce3f5d9539e31141, implementation commit 88981261ca384c3e90e6f6045c2abcd042c48e7c. Canonical source inventory remains byte-identical to Gate4. config.yaml hash00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c binds the SHADOW PILOT profile and loopback port 8000.

| Question | Reviewed answer |
| --- | --- |
| Unknown nonexempt GET authenticates? | Yes. server.py:294 api_token_middleware checks Bearer before _pilot_http_blocked and routing. /gate5-auth-inspection is neither /health nor a /pwa prefix. |
| Correct Bearer yields404? | Yes. The unmatched GET is allowed by _pilot_http_blocked, then routing returns404; offline application fixture proves this. |
| Incorrect Bearer aborts? | Yes. HTTP401 invokes shadow.deny(AUTHENTICATION_MISMATCH); WS mismatch follows the same terminal-abort path before acceptance. Never probe this live. |
| WS auth mechanism? | Authorization: Bearer in opening HTTP headers; /ws. No token query parameter or application message is needed or accepted as its replacement. Origin absent is allowed for a native client. |
| Can zero-frame handshake prove access? | Yes under the unchanged deployed nonempty-auth configuration. Header authentication precedes accept. Require101 and valid Sec-WebSocket-Accept, then immediate normal close 1000. |
| Retry/redirect/replay? | No automatic retry/replay in these server handlers. Fixed unknown GET has no matched handler or slash redirect. Helper follows no Location and has no retry/reconnect. |
| Conversation/provider/tool side effects? | None for these positive paths. HTTP resource activity is suppressed. /ws waits for receive and recognizes disconnect before parsing/capture/control/history/legacy work. |
| Does successful auth mutate D09? | The reviewed positive paths do not. WS creates an ephemeral connection and ws_connect/ws_disconnect audit events; these expected audit/session effects are not accepted pilot attempts. Offline fixture proves zero attempts/events/submissions/receipts and unchanged D06 after both positive checks. |
| Does the closed fence allow them? | Yes. PilotAdmissionFenceV1 never permits a conversation; _pilot_http_blocked permits an unknown GET, while /ws accepts then handles disconnect before the closed-frame refusal. No unlock exists. |

Source anchors: app/server.py:224 (_api_token_ok),237 (_ws_authorized),244 (Origin),256 (rejection),270 (_pilot_http_blocked),285 (resource activity),294 (auth middleware),589 (WS handler); app/execution/pilot_safety.py:25; app/execution/shadow_pilot.py:237 (terminal stop). Source paths are bound by the verified Gate4 implementation inventory.

HTTP404 alone would not prove authentication if the server had no configured token. This deployed PILOT startup requires nonempty authentication, recognized private environment-file configuration and unchanged supervisor/source fingerprints; the preflight verifies continuity. Successful future live results still require independent post-probe checks. No production request was sent during preparation.

Wire compatibility was additionally exercised against the installed Uvicorn protocol engine on a private AF_UNIX socket with a dummy app, plus the actual deployed app's ASGI fixture. No TCP listener or connection was used by the qualification harness.

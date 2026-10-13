# Ingress, permissions and provider reachability

Reviewed all seven candidate modules and the new tests directly, with canonical `app/server.py`, `pilot_safety.py`, router/client/prompt/complexity/direct-response and passive observation dependencies. Original source is byte-bound to V2 and preserved Gate6C; prior authority documents were read with Gate6B's rejection of Granite-visible output retained.

Candidate path: Ingress Bearer comparison → exact REST body or WS continuation/text → Runtime.session + commitment + ARMED_ONE → Store.accept transaction (spent permit + accepted row + event) → canonical pre-turn capture → optional LEGACY_ROUTER → LEGACY_RESPONDER → local client delivery/history → GRANITE → passive parser/evaluator → minimized receipt append → D09-like join → SETTLED → coordinated fixture checkpoint → CHECKPOINT_HOLD. No next permit is automatic. Four accepted turns trigger terminal cap closure.

| Surface | Result |
|---|---|
| REST /chat POST | In-process ASGI implementation; constant-time exact single Bearer, exact message field, one continuation header, 16KiB body and 8KiB message limits; malformed/scope/auth/concurrent input cannot create provider authority |
| Other HTTP paths/methods | Candidate 404/405, never legacy fallback; no /open, /confirm, /tasks, /resource/wake or alternate model route |
| WS /ws | Auth before accept; no-message connect/disconnect generates nothing; bounded canonical continuation; exact text frames only; binary/mixed/unknown/surrogate frames terminally refused |
| WS controls | Continuation validates existing Core-owned session and transport, never opens/arms. Duplicate JSON keys already refused by canonical parser. Idle timeout closes; no reconnect replay |
| Direct Runtime.request | Explicit authenticated bool is a trusted internal seam, not real middleware proof. Requires permit/session/message binding; no endpoint/model/permit selector argument |
| Direct Store.begin | Hardened named generation kinds and ordering, accepted-unsettled owner, no active/unknown lease. Methods remain internal capabilities; malicious same-process code is not a separate principal |
| Provider completion callback | No retry/evaluation replay. Late result cannot clear unknown or reopen. Late delivery completion is now recorded truthfully; provider remote completion still needs an authoritative adapter |
| Factory/startup | build_production_runtime always refuses. Runtime starts CLOSED_INITIAL, CLOSED_RECOVERY_HOLD or retained terminal, never restores OPEN from audit |
| Operational imports | Candidate has no server/LLM client/voice/tool registry/subprocess/socket/HTTP client import. Canonical observer reaches pure passive context, request, parser, evaluator and observation projection |
| Tools/TTS/voice/lifecycle | No executor capability or tool schema in candidate request construction; tool calls/action-tag proposals refuse. Model lifecycle operation names now rejected even at Store boundary |

There is no candidate exception branch calling `_process`, `_process_stream`, the original router fallback, error speech or unrestricted LEGACY handlers. On provider/proposal/parse/delivery/receipt/checkpoint failure, acceptance remains consumed and subsequent admissions close. Existing production remains closed-only under its own unchanged full graph tests; candidate passing those tests does not qualify mounting it into that graph.

Unqualified integration: candidate does not implement canonical origin restrictions, production middleware/lifespan/route mounting, credentials or socket listener. Ingress awaits request work before receiving further ASGI events; prompt disconnect/concurrent-frame detection during a long provider operation needs a reviewed receiving task or adapter. Runtime concurrency/cancellation tests are not proof that a real disconnected client is promptly observed. No in-process mutable bool or user-supplied authentication flag can be used as a release auth boundary.

Control permits bind source/config/release/PID/invocation/epoch/boot/start/challenge, checkpoint, nonce/expiry and session/request/transport. Explicit ordinal/resource/unit/Gate5/lineage-root binding through an authenticated release manifest and actual process facts is incomplete. Fixture string equality does not attest a running service identity.

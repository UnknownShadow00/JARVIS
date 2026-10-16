# Protected operator authority review

Gate 6F isolated review. No working production signer constructed. Signer in tests is a dummy HMAC key labelled not-production.

| Property | Status | Evidence |
|---|---|---|
| Operator action cannot come from REST/WS | PROVEN (TEST/SRC) | Ingress has only `/chat` and `/ws`; no control verb route; ASGI tests |
| A client cannot issue OPEN_HOLD or permits | PROVEN (TEST) | Control only via `LocalControl` on AF_UNIX with `SO_PEERCRED` uid check and signature |
| Opening does not start model work | PROVEN (TEST) | `OPEN_HOLD` writes one control row; zero transport calls until an armed, accepted request |
| Authorization binds release/config/PID/invocation/epoch (+source, boot, start, challenge) | PROVEN (TEST) | `test_signed_control_bound_to_exact_process` — each of 9 fields refused when stale |
| Each permit one-use | PROVEN (TEST) | one outstanding permit max; spent on acceptance |
| Repeated permit rejected durably | PROVEN (TEST), **hardened in 6F** | Durable nonce checked **before any effect**; `Refused('CONTROL_REPLAY')` instead of a raw SQLite error; a replayed `TERMINAL_STOP` no longer sets the in-memory stop (`test_replayed_control_has_no_effect`, 3 verbs) |
| No general privileged command execution | PROVEN (SRC/TEST) | Fixed verbs only; no path, shell or file operation |
| Stale signer cannot select an older process | PROVEN (TEST) | pid/invocation/epoch/boot/start/challenge bindings |
| Restart never opens admissions | PROVEN (TEST) | `test_restart_never_reopens_and_outstanding_permit_never_accepts`: reopened store → `CLOSED_RECOVERY_HOLD`; an outstanding pre-restart permit never accepts |
| Terminal stop and uncertainty irreversible | PROVEN (TEST) | Terminal values are monotonic; remote-unknown never released |
| Next permit requires the whole coordinated chain | **NEW in 6F** | `OPEN_HOLD`/`AUTHORIZE_ONE` now re-validate the coordinated checkpoint bound to the exact controller checkpoint, evidence storage health and the high-water root (`COORDINATED_CHECKPOINT_STALE`); before 6F a fault after the last good checkpoint did not block the next permit |
| Slow/trickling control peer | **NEW in 6F** | Whole-request 5 s deadline (`CONTROL_DEADLINE`) |
| Human presence | NOT PROVEN | `user_present` is asserted by the verifier; a real signer must prove it (hardware token touch or console) |
| Distinct OS identities | NOT QUALIFIED | OS-IDENTITY-QUALIFICATION |

Clock note: permit expiry uses the runtime clock passed to `Authority`. A release must use a wall clock shared with the signer (not `time.monotonic`, which restarts at boot). Restart cannot reuse an old permit today only because recovery hold refuses arming while any permit is outstanding.

Boundary a privileged deployment must enforce: the signer key and the control-socket group are the authority; anything with write access to the service state roots or the signer key can mint authority. See OS-IDENTITY-QUALIFICATION for the exact modes.

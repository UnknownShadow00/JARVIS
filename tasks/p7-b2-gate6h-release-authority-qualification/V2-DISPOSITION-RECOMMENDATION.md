# V2 disposition — UNSIGNED, retirement NOT AUTHORIZED

Retain the historical zero-use V2 epoch permanently and, if separately authorized, qualify it for exactly one signed V3 successor under the reviewed unattributed-shutdown exception. Do not reopen V2. No retirement decision, signature or production succession command issued.

Maintenance context is recorded additively as **OPERATOR_REPORTED_MAINTENANCE**: operator states “I performed the JARVIS Core reboot myself.” Original Proxmox task/audit account was not independently established. INDEPENDENT_PROXMOX_ATTRIBUTION_VERIFIED is not asserted. No further historical reboot investigation requested. The actual OPERATOR_STOP event and terminal epoch remain unchanged. Maintenance is not signed retirement authority.

## Exact future review record

Machine-readable non-executable draft: evidence/v2-disposition-draft.json. It intentionally omits future nonce/signature/live successor bindings.

| Field | Actual verified or proposed value |
|---|---|
| Predecessor |606a991a06b74fd79ed72b308417cc3f|
| HEAD |bd53dbc799fb9284a21fae8cce3f5d9539e31141|
| Config SHA256 |00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c|
| Real preserved archive |/home/jarvis/.hermes-poc/backups/p7-b2/62f417a21a524499b92316b58f6fbd64|
| Archive manifest SHA256 |1b59208c9c1243383fbe907faf4440808256c3eed05d35dc33a97eab483025c5|
| Controller logical SHA256 |d7f38fe729c06c530350ab5475fefec7b6db64ec456f216a3b4c097f3c51fb5d|
| Archive validation |5 component hashes valid; exact live/archive logical equality at entry and final|
| Verified state |CLOSED_COMPLETE/input_complete1, attempts/submissions/receipt joins/refusals0; D06 current/lastNone; D04 absent|
| Original event |OPERATOR_STOP, stop_attribution=UNATTRIBUTED_V2_SHUTDOWN_HOOK|
| Maintenance |Operator-reported only; not independent audit-account proof|
| Reopen authority |NONE|
| Preservation |Real terminal controller, original baseline/startup/final archive, original implementation hashes retained permanently|
| Successor scope |At most one linked protected V3 successor; cap4/no reset or refund|
| Reviewed exception |Explicit acceptance that generic shutdown hook cannot prove operator retirement; future retirement intent solely from a new verified human signature|
| Future payload intent |retirement=EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT, preserving stop-attribution limitation|
| Required authority |Qualified separate OS root/writer, human signer/presence, durable one-use nonce, immutable source/config/process bindings|
| Future release/config/epoch/PID/invocation/checkpoint/nonce/expiry |UNRESOLVED; fill only after new approval and fresh protected readback|
| Signature/command |NONE|

Full original implementation hash map is in terminal-archive-final.json and draft JSON. H-1 freshly compares live/archive/controller/source/config/service/D06 before/after signature, H-2 binds all proof fields, H-3 atomically consumes nonce/reserves one successor and rejects ordinary runtime succession. They support the narrow reviewed exception logically in isolation. Same-UID coordinated rollback remains possible in the current application graph; protected client/readers/OS/signer integration is still required.

This exception explicitly departs from Gate6A/B planned-human-stop prerequisites; it does not rewrite history or claim old OPERATOR_STOP proved retirement. No new V2 stop signal/restart/terminal event is needed or authorized.

Refuse on any nonzero use; wrong epoch/status/input completeness; archive absent/corrupt/mismatch; source/config/controller/live drift; unacknowledged attribution; active/enabled V2/unexpected PID; D06 active/unknown/last state; D04 uncertainty; unexpected receipt/submission/refusal; duplicate root/successor; missing/inconsistent/rolled-back authority; stale identity/checkpoint/signature/expiry; peer/presence mismatch; replayed nonce; incomplete transaction; unapproved provider/model/resource contract; attempted restore/reopen. Reverify everything freshly at actual future signing/commit; this packet is not a standing authorization.

# Threat and failure review

No exploitable opening capability was installed or exercised. Current CLOSED source/state is intact. The following are design/transition hazards that prevent treating an opener-only patch as deployment-ready.

| Threat/failure | Required control and evidence | Current status |
| --- | --- | --- |
| Untrusted .200 SSH identity / malicious key substitution | Independent verified VM placement/console public fingerprint, explicit trusted pin before guest inspection | Human verification pending; no candidate key treated as authority |
| Live code replacement/hot injection | New reviewed deployment; no debugger/ptrace/reload injection or source-edit activation | Existing PID cannot open; transition blocked by V2 |
| Legacy model/tool/TTS fallthrough after pilot capture | Separate PILOT-only branch; legacy/direct/voice/confirmation/lifecycle guards remain closed; actual integration tests with dispatcher/provider tripwires | Required future source change; abstract model is insufficient |
| Same jarvis UID impersonates human control | Separate operator credential and protected service identity/code/storage; fixed root helper; no agent sudo; peer identity checks | Proposed only; 0600 is not a human boundary |
| Forged manifest/approval in jarvis-writable evidence | Root-protected approved manifest/pinned seals and independent operator provenance; never trust a self-asserted source/hash flag | Requires future implementation and trusted release process |
| PID reuse, stale/replaced socket or runtime race | Bind PID/start tick/boot/invocation/UID/runtime challenge; verify peer and revalidate owner-loop prerequisites; fixed private no-symlink path and bounded protocol | Proposed, not OS-qualified by model |
| Replayed/expired grant, automatic restart opening | Unique spent grant and runtime bindings; startup CLOSED/RECOVERY_HOLD; no reusable OPEN state | Modeled; production implementation absent |
| Acceptance lost between memory increment and durable reservation | Atomic permit consumption/attempt reservation before admission/ack/dispatch; durable monotonic IDs/transport counts | Current V2 refuses restart; new schema/owner-loop changes required |
| New epoch masks earlier attempts / terminal abort treated as pause | Preserve predecessor complete truth; zero-use transition only; exactly one approved successor; global cap across lineage; never reopen terminal epoch | Proposed approval delta; same runnable epoch path blocked |
| Concurrent REST/WS steals a permit / backlog | Bind one ordinal/transport/session/request commitment; serialized transaction; queue0; reject conflict and stop subsequent permits | Abstract concurrency test passed; real ingress needs qualification |
| Active/unknown D06 or independent endpoint actor | Authoritative snapshot/recheck, one lease before dispatch, explicit endpoint reservation; stop on conflict; no ownership reset/inferred terminal | Core clean; fresh endpoint actors unverified |
| Crash before/after opening commit or during provider work | Preserve grant/accepted set; distinguish durable authority from runtime acknowledgment; no replay; associated terminal/no-transmission proof only | Abstract transaction/crash tests passed; filesystem/power-loss qualification pending |
| Backup/receipt/association failure | SETTLING/CHECKPOINT_HOLD, no next permit; versioned coordinated manifest; terminal stop on failure | V2 backup valid; V3 schema/backup implementation absent |
| Tool proposal, invalid auth/scope, voice/direct bypass | No operational dispatcher; pure pilot branch; terminal refusal/stop; API auth does not grant opening | Current closed fence qualified; future active branch absent |
| Old UID readers/manifest validation silently relaxed during migration | Explicit versioned ownership/legacy compatibility and protected archival provenance; no blind chown/reset; V2 validator unchanged | Future migration/security decision required |
| Privileged/root/kernel/hypervisor actor compromises service or endpoint | Explicit trusted-base and exclusive-use assumptions; observable lifecycle supervision; no categorical network exclusivity claim | Outside unprivileged guarantee; must be reviewed before pilot |

Minimum future security gate: adversarial tests of actual protected runtime/import paths, peer authentication and operator credential separation; source/identity/socket TOCTOU; durable grant/attempt joins and crash recovery; exact V3 backup validation; stale continuation/reconnect; no legacy provider/tool/TTS path; end-to-end stop/drain and unknown preservation. Do not substitute model booleans for these controls.

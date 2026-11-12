# Independent safeguard decisions

| Safeguard | Decision | Implementation and evidence |
|---|---|---|
|Authenticated readiness|PASS|app/agent/api.py requires exact nonblank Bearer on embedded Authority router; CLI ready checks credential before request, strict booleans, no start/retry fallback. Fresh12 ready-client cases and Authority HTTP/release negatives.|
|Credentials/startup|PASS|Constant-time exact comparison and remote validation retained; stripped-blank transport startup refusal precedes scheduler/background work. Ordinary legacy loopback route policy is not falsely described as universal authentication.|
|Storage ancestry/integrity|PASS|No-follow descriptor-relative component walk, owner/mode/identity checks and immediate post-create verify. Fresh ancestry replacement/failure/persistence cases. Not an atomic SQLite VFS or same-UID defense.|
|WebSocket ownership|PASS|Bounded send/close, failed live connections stay counted until endpoint finally releases them; capacity, binary/malformed/auth/origin/cancellation cases pass.|
|Automatic resource/public defaults|PASS|Resource enable/auto sleep false; public boot/voice/dictation/tracing/resource activation opt-in. Existing private runtime settings not read/migrated or qualified.|
|Dictation/privacy|PASS|False opt-in default and clipboard/type-out authorization negatives retained; transcripts redacted and no dictation LLM/TTS expansion.|
|Simulator protocol|PASS|Claim/apply/ack/reconcile reject ExecutionPipeline envelopes within scoped mutation; no new execution authority.|
|Timestamp bounds|PASS|OverflowError normalized to invalid_time; strict timezone/type input contract retained.|
|APScheduler cleanup/restart|PASS in3.11.3 scope|Owned executor/store completion inventory, retained shielded cleanup, partial retry/failure observation and restart/callback fences. Actual installed backend and separate synthetic faults tested. Native/thread/custom resources unqualified.|
|Sensitive failure evidence|PASS|Allowlisted categories and opaque IDs; injected private messages/tokens/payloads absent while failure/nonzero exits remain visible. Public paths/hashes are intentional metadata.|
|Required-test completeness|PASS for enrolled scope|Digest-pinned exact identities independent of collection; module/source policy; complete session and setup/call/teardown required. Late omissions/skip/xfail/filter/terminal faults reject.|
|Durable authority/recovery|PASS|No schema/transport/approval delta; authority timestamp is its only local normalization change. Fresh durable receipt, ledger/checkpoint, enrollment/recovery, cancellation and execution tests retained.|

All49 source paths are individually recorded in SOURCE-REVIEW.md/JSON and match the reviewed candidate parent; app/ matches approved R3/reconciliation. No merge-specific authorization, persistence, cleanup or recovery regression was found. Canonical's newer128 paths are audit/log material, not a competing application implementation.

Ranked findings: F1 MEDIUM archive/default-discovery scope gap; F2 MEDIUM inherited CI selection reaches excluded config-mutating tests; F3 LOW clean-checkout preflight versus preserved dirty-log post-update runbook; F4 LOW dependency-version drift under broad bounds; F5 LOW unsigned same-UID evidence/custody limitations; F6 LOW retained26MiB duplicated forensic output/tool usability. F1/F2 require scope/remediation conditions, not a fabricated runtime failure. No critical/high current application defect or required-suite failure reproduced.

No unsafe module/original archive was run. Inert replicas demonstrate collector selection only. All live/provider/hardware/native/credential/physical-loss behavior remains outside qualification. Earlier context was inherited, so fresh technical reconstruction is not fresh-context organizational independence.

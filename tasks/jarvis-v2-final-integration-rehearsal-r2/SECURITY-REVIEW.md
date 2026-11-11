# Rehearsal security review

All approved application bytes are preserved. No source/security policy change was introduced by this rehearsal. The following checks are supported by actual source inspection and fresh required tests:

| Boundary | Result | Relevant implementation/coverage |
|---|---|---|
|Authenticated readiness|PASS|CLI ready rejects blank credential before request, sends Bearer, requires strict complete readiness, no automatic start/retry fallback; agent API has mandatory exact nonblank credential dependency. test_ready_client, test_authority_http_security, release-security/transport tests.|
|Storage ancestry|PASS|StorageAncestry performs verify after create; no-follow descriptor traversal rejects unsafe ancestry and identity replacement. Storage/security/persistence tests execute against disposable paths.|
|Credential/startup safety|PASS|Exact constant-time comparisons; remote requirements; whitespace token fails before transport worker/scheduler startup. Existing and reconciliation security negatives retained.|
|WebSocket lifecycle|PASS|Bounded send/close; retained registration until handler finally exits; connection bound and malformed/auth/origin refusal. server/UE5 security cases pass.|
|Resource/public defaults|PASS|Automatic resource enable/sleep defaults false; public example requires explicit activation of dictation/voice/boot and execution-related features. No private runtime config read.|
|Dictation/privacy|PASS|False opt-in contract; type-out/clipboard unauthorized paths still refuse and transcript logging remains redacted. Fresh corrected default and adjacent negative cases pass.|
|Simulator protocol|PASS|Claim/apply/ack/reconcile refuse execution-envelope tasks within scoped mutation; existing authority/execution invariants remain.|
|Timestamp validation|PASS|Overflow becomes invalid_time; invalid/boundary timestamps retain fail-closed behavior.|
|Scheduler ownership|PASS|OwnedAsyncIOScheduler confirms executor/store completion, retains resources and shielded cleanup across timeout/cancellation, observes failures/retries and fences restart. Real3.11.3 tests pass; native/thread/custom resource protocols are refused/unqualified.|
|Sanitized evidence|PASS|Allowlisted categories/opaque IDs; no raw exception/payload values exported. Synthetic private exception/parameter/module markers remain absent in negative machine reports while failure/nonzero exit remains visible.|
|Required completion|PASS|Externally pinned exact identities plus separate collection/session/terminal phase evidence; unexpected, duplicate, skipped, missing or incomplete results reject.|

No schema or provider interface was changed in this rehearsal. Relative to current canonical, the approved changes intentionally add credentialed ready and strengthen defaults/validation; closed tools and retired confirmation remain closed. The storage/authority SQL schemas themselves are unchanged by this approved delta. This is compatibility with documented security contracts, not backward compatibility for unsafe enabled defaults or unauthenticated readiness.

The namespace has no external network, private config, host sockets or VM paths. Synthetic process tests are confined to disposable namespace children. Actual live/audio/provider/host-enforcement modules are not executed. No dependency installation, live credential access, privileged activation, Gate6K, Proxmox/VM/Student Flow/production action, push/merge/deploy occurred.

Residual risks:39 out-of-scope/11 unsafe modules remain outside acceptance; host/interpreter/dependency/plugin code is trusted; same-UID/root can alter files/permissions/evidence; local before/after hashes cannot prove absence of transient malicious tampering or independent custody. Native/custom/thread executors, real providers/hardware and physical power loss remain unqualified. Operational activation and configuration review require separate authorization. No new code/security blocker was observed within this exact-source offline boundary.

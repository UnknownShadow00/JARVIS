# Safeguard preservation and residual boundary

All application bytes match accepted combined source6341648/da67d936; all inherited886 identities execute freshly. There are no new application, schema or dependency changes in this correction.

| Safeguard | Source and fresh coverage | Decision |
|---|---|---|
|Authenticated readiness|app/agent/api.py router dependency compares configured nonblank exact Bearer identity; app/cli.py ready rejects absent/invalid/non-ready status without startup/retry; ready_client/release_security/authority_http_security tests|PASS|
|Credential/startup validation|app/config.py validates remote binding/origins and nonblank token; app/server.py transport token validation precedes scheduler/worker/background startup; release_security/server_auth tests|PASS|
|Storage ancestry|app/agent/storage_paths.py no-follow dirfd traversal and verify after creation; ancestry, creation/swap/race/store-replacement negatives|PASS|
|WebSocket ownership|app/server.py and app/comms/ue5_bridge.py bounded send/close, handler finally releases registration; admission, cancellation, slow close/send negatives|PASS|
|Defaults/privacy|ResourceModeConfig disabled auto controls; example public and dictation options require opt-in; privacy/authorization negatives retained and source/example tested|PASS|
|Simulator/protocol boundary|app/agent/simulation.py refuses execution envelopes on claim/apply/ack/reconcile; execution/simulation and legacy claim negatives|PASS|
|Timestamps|app/agent/authority.py instant catches OverflowError and enforces timezone-aware values; overflow/bounds/invalid inputs exercised|PASS|
|Scheduler ownership|scheduler.py lifecycle lock, retained shielded cleanup task/error/restart fence; scheduler_backend.py per-resource completion/future ownership; real APScheduler3.11.3 and synthetic failure/cancel/retry fixtures|PASS|
|Sanitized evidence|gauntlet_protocol.py hashes parameter identity, allowlists categories; output discards raw pytest/exception messages; injected failure markers absent from fresh JSON; private exception causes FAIL|PASS|
|Enrollment/completion|Digest/source/disposition/identity bindings; fixed suite set, no generation during acceptance; full ordered terminal evidence, negative gates and independent report fault controls|PASS|
|Durable authority/recovery|No correction changes runtime ledger/receipts/checkpoint/restore/admission code; enrolled authority/ledger/recovery/execution/persistence tests run freshly|PASS|

No high/medium remaining offline finding. Low limits: unsupported deliberate pytest config bypass; unprovisioned remote runner; unsigned local evidence and trusted package/interpreter backing bytes; dirty canonical log requires separate clean-checkout post-update acceptance. Raw pytest developer workflows are intentionally changed to the documented full gate, and legacy installer smoke is not qualified. This is a developer workflow compatibility change, not an application API/schema change.

No unsafe/live/historical test implementation was executed. Native/custom/thread scheduler resources, actual providers/audio/hardware, power-loss and live infrastructure remain unqualified. No network package/advisory scan was performed under the user's offline restrictions. There is no live/privileged qualification or deployment approval.

# Timing and cancellation — proof not established

**BLOCKED: no reviewed R2 implementation commit; no R3 candidate.** Before-fix probes reproduce stale receipts, pre-cancellation journals labeled complete through closure, late stop receipts with an earlier claimed cancel time, post-expiry callback acceptance and unexpected failure accepted as cancellation.

Required future contract: bind authorization issuance/start/expiry and each setup, start, callback, exit, cancellation request, acknowledgment, observed effective inactivity, cleanup and finalization to raw clock brackets for the same boot/generation. Successful stop exit is not proof of effective cancellation. Require a causal sequence and uninterrupted evidence coverage; detect callbacks before, during and after cancellation. A's evidence must never satisfy B and a prior failure must never be erased by rearm.

The maximum45-minute window, fixed UTC expiration and BOOTTIME bound remain requirements. Intentionally late in-window fault observations must be separate from on-time qualification. Post-expiry execution cannot qualify as success or expected successful closure. No rearm/retry/cleanup under expired authority is allowed. A separate finite recovery grant would be required for later exact-owned readback/stop actions; none is granted here.

These criteria have not been implemented or proved in R3. Real systemd timing and cancellation remain unqualified.

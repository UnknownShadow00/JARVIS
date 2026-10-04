# Original D04 resolution matrix

Historical question in tasks/p7-formal-exit-preparation/OPERATOR-DECISIONS.md: “What separate evidence sink, redaction/retention, interval clocks and loss semantics are required?” The packet remains unchanged. This task approves a local dedicated sink module, UTC chronology only, no automatic P7 deletion, and known-loss invalidation. It does not authorize interval/latency clock thresholds or a scheduler.

| Original component | Status | Frozen decision / exact deferred boundary |
|---|---|---|
| EVIDENCE SINK OWNER | FROZEN | app/execution/shadow_observation_sink.py; observational durable local boundary; immutable truthful receipt |
| CLOCK | FROZEN | Existing P1 utc_now; aware UTC +00:00 ISO acceptance chronology only; latency/controller timing remains outside D04 |
| RETENTION | FROZEN | Append-only P7, no automatic deletion; window complete + sealed exit bundle + explicit acknowledgement/cleanup authorization |
| LOSS ACCOUNTING | FROZEN | B=C necessary for reconciled submissions, known failures/loss/uncertainty invalidate affected coverage; no sink-only zero-loss claim |
| DURABILITY | FROZEN | Success only after recoverable local commit; explicit uncertainty; no queue/buffer acknowledgment |
| RECOVERY | FROZEN | Durable history/order survives restart; partial/corrupt/unknown data fails closed, preserved, no reset/repair |
| STORAGE ROOT | FROZEN | Existing Core PROJECT_ROOT/data root; private confined namespace required; no arbitrary new root/export authority |
| STORAGE ENGINE | IMPLEMENTATION DETAIL | No existing mechanism fully satisfies guarantees; select/review local backend/framing/barriers before implementation |
| ATTEMPT/RETRY/DUPLICATE ACCOUNTING | BLOCKED BY LATER SCHEDULER DECISION | D02/D07 determine recoverable attempts, duplicate key and reconciliation, not guessed from turn/trace/hash |
| LEAF LAYOUT / INIT / ACCESS MECHANICS | IMPLEMENTATION DETAIL | Within frozen private local root, with backup/export interaction checked; no chmod/writer now |

No D04 security/semantic operator choice remains. This does not claim the eventual measurement accounting implementation is complete. D01/D02/D05–D10, post-P7 retention and F-AUDIT-01 remain unresolved outside D04. No pipeline/CT type or producer field is amended.

# Clock and timing audit

**FAIL for complete causal ordering.** R4 improves precise raw-clock bracketing, session UTC/BOOTTIME anchoring, monotonic conversion and guard/main display comparison. Fresh domain-conflict, expiry and guard-end-after-callback probes reject. However, guard-start intervals are never related to create/wait/trigger events, producing five failing new probes including the per-case anchor path (R4-A01).

The bound≤2700s issuance-to-expiry and session duration, explicit UTC expiry, static BOOTTIME bound,35-minute creation cutoff, full command cap+reserve,90-second case completion and final closure before expiry remain enforced/documented. Post-expiry callbacks cannot count as successful qualification in the tested coherent mutations. The intentionally late case reports detection only. No command including cleanup receives an automatic extension; a recovery action after expiry needs separate finite scope.

UTC, BOOTTIME and MONOTONIC are distinct. R4's allowed display grammar uses bounded interval precision and stops on UNKNOWN. Real systemd257 display precision/ordering, exported NextElapse convention, WakeSystem, start-time accounting and capture latency remain unqualified. Seconds-only guard displays may block all actual executions; that is a feasibility/observability prerequisite, not permission to fabricate precision. No reboot, suspend or manager reexec is included or tested.

A successful command receipt is not proof of effective cancellation or completion. The reviewed schema generally distinguishes request/ack/effective inactivity and rejects partial outcomes, but an accepted internally impossible guard history prevents approval of the complete model.


# Root causes — analysis only, implementation blocked

The development blocker is a provenance mismatch: the reviewed R2 bytes were sealed and copied into two worktrees but never added to an identifiable implementation commit. Its branch is only the original nightly base. A fresh R3 worktree at that commit would omit the reviewed implementation; importing untracked files without addressing the requested commit identity would bypass the user's explicit gate.

The sixteen behavioral failures remain reproduced and unfixed:

- R2-A01: capture/command timestamps are validated individually within a broad window without causal bracketing; journal monotonic timestamps are parsed then discarded.
- R2-A02: claimed cancellation time is not derived from stop request/acknowledgment/effective inactivity; unexpected failure can count as cancellation; lateness has no upper execution/window bound.
- R2-A03: collision proof freshness is disconnected from the renderer's current sample; collision evidence does not enforce complete timeout-aware receipts.
- R2-A04: unit states, main exits, ExecStart trailers and scenario history are not cross-validated; later invocation can evade failedtimer's earlier no-execution check.
- R2-A05: summaries substitute for raw cgroup capture, and case-only seals omit top-level review references and the complete evidence envelope.
- R2-A06: the root path splits to an empty component and is rejected before a descriptor can be checked.

The traceability matrix lists every original method separately. Required corrections are proposed criteria only. No code fix or after-fix success exists in this task.

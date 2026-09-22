# Security invariants inherited for P7

These constraints are settled by the existing contracts and this task's prohibitions; they do not make the incomplete composition contract frozen.

1. Model/provider output grants no permission, confirmation, execution, trusted-result, provenance or response authority.
2. Adapter parse success produces only untrusted P0 data. Proposal IDs/order and requested model are caller-owned; raw provider metadata/reasoning is not retained.
3. No direct proposal→ToolInvocation→executor path. An authoritative route/proposal guard, actual P4 decision and P5 gates are mandatory.
4. Deterministic classification version 2, routing, lane and capability containment cannot be overridden by model fields or prose. All 41 known unsupported verbs stay contained as appropriate UNKNOWN_ACTION operational requests.
5. Permission cannot be skipped, weakened or synthesized from an exception. Required confirmation cannot be skipped, copied from a bool or claimed twice.
6. No resting CONFIRMED state; no automatic retry/renewal/decomposition. P5 idempotency and P4 exact binding remain authoritative.
7. No implicit live capability from abstract vocabulary, ToolSchema, model tool name or hidden registry fallback.
8. SUCCESS requires the corresponding TrustedToolResult and invocation linkage. ERROR and TIMEOUT never imply success; TIMEOUT outcome remains unknown.
9. Operational output requires the existing obligation→ApprovedOperationalResponse path. Model prose and arbitrary exception strings cannot bypass it.
10. Conversational output cannot answer operational state claims; late proposal/result signals require the existing lane policy, not an early conversational escape.
11. Model text never becomes provenance truth. Current, corrected, supplied, reported and verified states remain distinct; cross-session/invocation evidence fails closed.
12. Contradictions stop, preserving the original evidence and owner code. No deleting result, changing lane or clearing a denial to find a convenient successful branch.
13. No copied classifier patterns, permission rows, obligation priorities, response templates or harness implementations.
14. No intrinsic filesystem/network/process/provider/registry/live store/audit-writer access. Dedicated test state is isolated and discarded; no live consumer or mode enablement.
15. Failed audit compatibility is not audit success. Missing obligation on conversation cannot be filled with a fictional operational obligation.

No security invariant was weakened to close a gap. O-B01 and O-B04 are concrete blockers to claiming full composition compatibility; O-B02/O-B03 require explicit authoritative disposition. No production fix is authorized or attempted by this report.

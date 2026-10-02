# DEFERRED

Everything task13b11o-r1/DEFERRED.md and task13b11p/FOLLOWUPS.md defer stays deferred and
is not re-opened here: browser D-01 tension; a numeric confirmation TTL or confirmation UX;
`TIMEOUT` leaving a confirmation record in `EXECUTING`; a `TIMEOUT` `ProvenanceSource`; the
redaction secret-key list; the real registry adapter; live capability projection; live
audit and request wiring; Hermes enablement; model, network and resource configuration;
destructive, financial and messaging policy.

D-P6-01 stays `DENY` → `REPORT_CAPABILITY_UNAVAILABLE` with `permission_denied` where its
existing rule wins. D-P6-02 stays `TIMEOUT` → `REPORT_TOOL_ERROR` with
`trusted_tool_timeout`. No new obligation, obligation rank, response template, resting
`CONFIRMED` state, success inference, timeout settlement or automatic retry is added.

The historical classifier R1/R2 aggregate-digest formula ambiguity, parser resource
limits, unavailable vulnerability/type/lint/coverage tooling and stale phase comments
remain later hardening. No package is installed and no arbitrary formula or limit is
invented.

## Deferred by this contract specifically

| Item | Why deferred | Treatment |
|---|---|---|
| Replay of a non-dispatchable-action result (`BLOCKED` / `invocation_not_dispatchable` for `NONE`, `UNKNOWN_ACTION`, `MULTI_ACTION_UNSUPPORTED`) | the result is genuine, but the frozen guard order sends those actions to an early P6 terminal before S06, and choosing which obligation wins when a result is also present is a P6 priority judgement no operator has signed | excluded in v1 by C-00a; F-P7R1-02 |
| Cryptographic or structural authentication of a `TrustedToolResult`'s origin | `TrustedToolResult` is an ordinary constructible dataclass; dispatcher-only construction is a contract rule, not an enforced one | enforce type identity, linkage and authority agreement; record the residual gap as F-P7R1-01 |
| Finer machine-readable admission failure reasons | `PipelineStopReason` is closed by a prior freeze, and for confirmations uniformity is also the correct anti-oracle property | guard identity asserted in tests, not in a stop field; F-P7R1-03 |
| Idempotency across *different* `RecordedTurn` values describing one user action | deduplication belongs to the dispatcher's `_claimed` set and the store's single-claim rule, both outside P7 | no P7 mechanism; IDEMPOTENCE.md "what is deliberately not promised" |
| Detecting that a mode-C result was already reported in an earlier turn | reporting history is not part of the frozen stage structure | no P7 mechanism |
| An ordering constraint between `recorded_at` and `evaluated_at` | none is frozen anywhere upstream; imposing one would be new policy | both are only required to be timezone-aware |
| An isolated P5 continuation API, executor callback seam or whole-turn inert execution inside P7 | option 2 of task13b11p/FOLLOWUPS.md; would require F-MAP-01, F-REPLAY-01, F-FALLBACK-01 and a frozen isolation contract | explicitly not taken, and not authorized by this freeze |
| Audit emission of any admission fact | schema-v3 conversational obligation defect is still open (F-AUDIT-01) | ASSOCIATION_RULES.md records which facts would be available; nothing is emitted or validated |

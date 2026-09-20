# Obligation Contract — Task 13B11L-P6

**FROZEN AND IMPLEMENTED.** What the P6 decision engine is, and is not.
Supersedes nothing: the design in `tasks/task13b11l/OBLIGATION_CONTRACT.md` is the blocked
task's history and stays as written.

## 1. Scope

Contract §14.1: every **OPERATIONAL** turn has **exactly one** response obligation, derived
deterministically from frozen inputs only (INV-009). This component decides *what JARVIS is
obligated to report*. It does not decide *how it is worded* — that is the response builder,
P6 unit 2, still unwritten.

Path `app/execution/obligations.py`, from `task13b11a/TARGET_COMPONENT_MAP.md` §1:
*"Obligation engine … exactly one obligation per operational turn, frozen priority (§14) …
must never contain per-scenario branches."*

## 2. Reused, never redefined

`ResponseObligation` (11), `ObligationDecision`, `OBLIGATION_PRIORITY`,
`OperationalResponseSource`, `ConversationalResponseSource`, `RequestClass`, `Lane`,
`PermissionOutcome`, `ToolResultStatus`, `ReportingIntent`, `PrimaryAction`, `TrustClass`,
`ProvenanceSource`, `ProvenanceStatus`, `TrustedToolResult` — every one already in
`app/execution/types.py`, plus `LaneReason` from `lane.py`. No `ResponseDuty`, no
`ReplyType`, no second priority tuple.

Two new passive types exist because nothing equivalent did: `ObligationState` (the frozen
§14.1 inputs) and `ValueProjection` (availability and trust class, never the value). Both
are built entirely out of the enums above.

## 3. The central rule

The control plane decides. A model cannot select an obligation, cannot supply one, and
cannot make an unexecuted action successful. There is no parameter a model output could
occupy: `result` is typed `TrustedToolResult | None` and a `ModelDraft`, a `ToolProposal`,
a mapping, a bool or a string is refused by type, not coerced.

## 4. Conversational turns produce no operational obligation

§14.1 scopes the requirement to operational turns; §4.2 permits model prose on the
conversational lane. `derive()` returns `None` there, and `CONVERSATIONAL_SOURCE` is
`ConversationalResponseSource.MODEL_RAW`. `None` never means "no rule matched" — rank 11 is
total. `require()` exists for callers that have already established the lane and refuses a
conversational turn rather than inventing an obligation for it.

The engine never *re-decides* the lane (§4.1, §4.2, INV-016). An operational turn stays
operational because no tool ran, the capability is unavailable, permission was denied,
confirmation is required, or a model answer happens to exist.

## 5. Must never — all enforced by a test

* generate user-facing prose, templates or prompt strings;
* contain per-scenario branches or benchmark-specific string matching (§14.3);
* read the user's raw request (§15.3) — there is no `str` field on `ObligationState`;
* read a store, a clock, the filesystem, the network, a model or the registry;
* emit an audit event, write provenance, dispatch, or mutate permission or confirmation
  state;
* return the value behind `ANSWER_LEDGER_VALUE` — only that the obligation applies.

## 6. Two mappings the blocked task left open, decided here

`tasks/task13b11l/OBLIGATION_MATRIX.md` §"Two mapping questions" recorded both rather than
deciding them. Both are decided inside the frozen eleven, so neither extends the contract.

**D-P6-01 — `PermissionOutcome.DENY` maps to `REPORT_CAPABILITY_UNAVAILABLE` (rank 6).**
The frozen eleven contain no `REPORT_PERMISSION_DENIED`; adding one would be a contract
extension under §6.2, which this task is not authorized to make. The refusal family is the
only honest home. The distinction is not lost: `ObligationDecision.reason` carries
`permission_denied`, separately from `explicit_action_without_tool` (no tool exists),
`capability_unavailable` (no registered capability) and `dispatch_blocked` (the dispatcher
refused for another reason). Four deterministic refusal causes, one obligation.

**D-P6-02 — `ToolResultStatus.TIMEOUT` maps to `REPORT_TOOL_ERROR` (rank 2).**
§18 says the side effect may or may not have happened and the response must claim neither.
Rank 3 would claim it did. Rank 2 is the only remaining tool-result family. The reason is
`trusted_tool_timeout`, never `trusted_tool_error`, and the `TrustedToolResult` the builder
also receives still carries `status=TIMEOUT`, so "outcome unknown" survives to the layer
that words it.

**Both are flagged to the operator.** Neither is reversible without a contract change, and
both would be resolved differently by a v2 contract that adds a denial obligation and a
timeout obligation.

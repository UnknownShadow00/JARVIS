# Task 13B11O follow-ups

No option below is an approval or implementation instruction. Exact questions are grouped by when a decision is needed. R3 items are narrowed, not silently marked resolved.

## BLOCKING NOW

| ID / related R3 item | Exact question and current behavior | Options / recommendation | Security consequence / dependency |
|---|---|---|---|
| O-B01 / P7-GUARD-01, P7-PROJECTION-01 | Which existing authority owns proposal matching, and what exact action→capability→tool/argument schema binds it? Target map assigns permissions/dispatch; neither accepts RouteResult + ToolProposal or validates tool-argument semantics. Canonicalizer normalizes only; adapter descriptors deliberately grant nothing. | Approve a separately specified guard in the planned owner(s), or explicitly amend ownership to a single pure P7 guard with closed per-capability schemas. Recommend preserving the planned authority boundary and freezing bindings before implementation; no tool discovery or legacy/harness copying. | Prevents authorizing a different tool/action/target/extra argument from the routed request. Blocks a complete guard and executable pipeline. Requires an architectural ownership/schema decision, not a new permission outcome. |
| O-B02 / P7-GUARD-01 | What exact terminal result/obligation applies to a valid single-action request with zero, multiple identical, multiple differing, or mismatched proposals? Adapter v1 accepts zero/many in order; contract §8 handles distinct requested actions, not proposal count. | Explicitly reject the proposal set without dispatch using an approved failure/obligation path (recommended), or separately authorize another policy. Selection, merge, decomposition and execution loops are not options in this task. Do not invent MULTI_ACTION_UNSUPPORTED from proposal count. | Avoids silent partial execution and model-owned classification. Blocks total guard/output matrix. Recommendation still requires approving its exact representation under O-B03. |
| O-B03 / P7-FAILURE-01, P7-PIPELINE-01 | How is a failed stage represented without fabricating its output, and who owns a fallback approved response? Integration §19 requires safe prose even on classifier/router/builder failure; current P6 rejects contradictions and has no independent fallback API; TurnOutcome absent. | Approve an explicit non-renderable immutable pipeline failure variant for this passive unit and defer user-visible fallback (recommended for passive scope), or authorize a separately specified deterministic fallback owner/type in P6. Do not catch errors and manufacture ApprovedOperationalResponse in P7. | Controls the operational raw-prose lock and whether a failed turn can be represented without false state/approval. Blocks exact total input/output/failure contract. No prose or new obligation is invented here. |
| O-B04 / P7-AUDIT-01 | How can every conversational turn have the required turn.summary without an operational obligation? AUDIT_PLAN §2 requires every turn; P6 returns None for conversation; P1 schema-v3 summary rejects None. Read-only reproduction in api-probe.json. | Explicitly limit the passive summary requirement to applicable operational outcomes and document conversation/failure event coverage, or authorize a reviewed schema contract change making the field conditionally applicable. Recommend the scoped applicability clarification if complete per-turn observability remains demonstrable; never assign a fictional obligation. | Changes audit completeness/compatibility semantics. Blocks a complete contract now. This task forbids schema change, so neither validator nor plan was silently relaxed. |

No operator decision is needed merely to select a dataclass name or inject fixture timestamps. Those routine details remain downstream of the four concrete authority/compatibility decisions above. The supported-read matrix gap needs no immediate live grant: retain it as an explicit not-representable row; any future action-vocabulary extension requires its own §6.2 contract and approval.

## BEFORE LIVE WIRING

| ID | Question / current behavior | Options, consequence and recommendation | Blocks current freeze? |
|---|---|---|---|
| LIVE-01 | Actual Hermes wire normalizer, model identity and measured shadow window? Recorded adapter only, live disabled. | Separate approved integration/rollback task; no invented wire format. Live transport/resource boundary. | No; blocks live P7 |
| LIVE-02 | Real capability projection/registry adapter? Static inputs only. | Keep D-08; approve later graph-supported adapter and safety audit. Never infer grants from tool schemas. | No |
| LIVE-03 | Browser D-01, numeric TTL, consent UX, destructive/financial/messaging policies? Existing policies remain. | Preserve current outcomes; operator-approved policy task only if change required. Alters execution authority. | No for current passive subset |
| LIVE-04 | Audit enqueue/durability/redaction and post-attempt failure handling? Only schema compatibility reviewed. | Separate writer/failure contract with safety gates; preserve raw-prose lock and execution uncertainty. | No beyond O-B04's current schema issue |
| LIVE-05 | Timeout EXECUTING recovery / TIMEOUT provenance? Existing uncertainty remains. | Defer, prohibit automatic retry; reviewed recovery without false success or new trust. | No |

## LATER HARDENING

| ID | Question / behavior | Options and recommendation | Blocks now? |
|---|---|---|---|
| HARD-01 | pip_audit/ruff/mypy/coverage absent | Arrange approved tooling; pip check is not a vulnerability audit. No installation here. | No |
| HARD-02 | Parser resource limits unspecified | Measure then approve limits; no arbitrary byte/count/depth values. | No |
| HARD-03 | Historical classifier R1/R2 aggregate formula unclear | Document formula or explicitly restate under a known convention; never alter old seals. | No |
| HARD-04 | Stale phase/import comments | Scoped comment-only cleanup later, preserving behavior and evidence. | No |

Next dependency remains the P7 passive pipeline contract resolution/re-freeze, NOT implementation, live shadow, P8 or Task 13C. Stop; do not proceed around these blockers.

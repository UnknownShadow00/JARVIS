# P7 passive pipeline contract v1 — freeze candidate

**NOT FROZEN — BLOCKED. This document does not authorize implementation.**

The responsibility is one-turn orchestration at `app/execution/pipeline.py`, the Integration boundary in 13B11A. P0–P6 own all decisions; the completed adapter contributes only untrusted ModelDraft and ordered ToolProposal objects. A future passive implementation may use canonical recordings and isolated fixtures, not live transport, registry, server routing or persistent stores. This is not completion of the full P7 shadow phase.

## Inherited constraints that are settled

- Classification remains version 2; routing, lane, canonicalization, policy, confirmation and P6 selection/rendering are reused, not rewritten.
- Correlation/model identity/time are JARVIS-owned. No model field can create an invocation, approval, trusted fact or operational response.
- Distinct multi-action requests dispatch nothing. Adapter multiplicity is not deterministic request multiplicity.
- All operational success requires a matching P5 TrustedToolResult; all successful operational response construction requires P6 ApprovedOperationalResponse.
- DENY and TIMEOUT keep D-P6-01 and D-P6-02, including their reason codes. No new obligation, policy outcome or confirmation state is added.
- A component error/contradiction stops continuation; there is no raw-model, registry, default-allow or made-up-state fallback.

## Unresolved freeze gates

1. O-B01: exact proposal-to-route/capability/tool/argument validation contract and authoritative owner. Existing APIs do not perform the guard the plan requires.
2. O-B02: zero/many/mismatched proposal disposition on an otherwise valid single-action turn, especially the obligation/failure result. No selection, merge, execution loop or fabricated multi-action route is permitted.
3. O-B03: total failure/outcome contract when a required deterministic stage cannot produce its normal typed output. The plan requires safe prose but supplies no approved fallback constructor compatible with the frozen P6 failure behavior.
4. O-B04: per-turn audit compatibility. The plan requires a summary for every turn, but schema-v3 TURN_SUMMARY requires response_obligation while P6 correctly returns None for conversation. The current task prohibits changing the schema.

These are architectural/authority questions, not permission to choose browser policy, TTLs or live capabilities. Detailed alternatives and recommendations are in FOLLOWUPS.md. Routine container naming, explicit dependency injection and scalar ownership are not independently escalated as operator decisions.

## Input/output status

STATE_PROJECTIONS.md inventories the exact existing constituent types and proposed linkage. There is no existing TurnOutcome or complete pipeline request type. Successful outcomes can reuse ApprovedOperationalResponse or ConversationalResponse; the operational branch cannot accept ModelDraft. A total immutable wrapper, error variant and guard evidence slot depend on O-B01/O-B03. This task does not publish an apparently exact signature containing undefined authority fields.

COMPOSITION.md records the canonical stage sequence; GUARDS.md/GUARD_ORDER.md record the supported gates and explicit gaps. PIPELINE_MATRIX.md is a hashed readiness matrix with conditional component expectations, not a passed end-to-end corpus. Acceptance remains unmet until every blocker is resolved and a subsequent contract revision is explicitly frozen.

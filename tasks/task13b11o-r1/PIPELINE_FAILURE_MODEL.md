# Pipeline failure model — P7-D03

Contract-only addition: `PipelineStop`, a frozen, slotted P7-local dataclass using the repository's explicit result/input naming style. Implement it only in the later passive task, not in types.py here. Existing ModelDraft, ToolProposal, TrustedToolResult, ObligationDecision, ObligationState and ApprovedOperationalResponse are not substitutes for an early stopped stage.

## Exact fields

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| correlation | CorrelationContext | required, no default | valid caller session/turn and applicable child IDs; no new ID family |
| stage | PipelineStage | required, no default | closed stage identifier below |
| reason | PipelineStopReason | required, no default | closed JARVIS-owned reason below; not model/error prose |
| executed | bool | required, exact bool | whether the current fixture's executor was actually reached, not whether the intended side effect succeeded |
| result | TrustedToolResult or None | default None | existing current-turn P5 result only, with invocation linkage; no copied/model-built result |
| obligation_state | ObligationState or None | default None | exact existing downstream input if it was validly assembled; never invented missing class/route/permission data |
| component_reason | str or None | default None | existing owner machine-code value, if any; only declared AdapterError, confirmation/P5 refusal, P6 contradiction/reason codes, never arbitrary exception text |

No text, model draft, provider payload, new timestamp, failure ID, permission override or new obligation field. Optional means absent state, not an empty/defaulted substitute. All contained mappings must be stable immutable snapshots under their existing constructors; type identity alone is not authenticated origin.

Required fields cannot be omitted or null. stage/reason require the corresponding enum members, not arbitrary strings; executed requires an exact bool, never a truthy string/number. Only result, obligation_state and component_reason are nullable as declared. No unknown constructor fields, implicit coercion or generic model/from-dict promotion. PipelineStop is constructed only from JARVIS-owned composition state; even a correctly shaped model payload is not one.

PipelineStage values: S01_INPUT, S02_CLASSIFY, S03_ROUTE, S04_LANE, S05_ADAPTER, S06_CARDINALITY, S06_PROJECTION, S06_CANONICALIZE, S06_MATCH, S07_PERMISSION, S08_CONFIRMATION, S09_RESULT, S10_PROVENANCE, S11_OBLIGATION, S12_RESPONSE, S13_AUDIT.

PipelineStopReason values: invalid_input, classification_failed, routing_failed, lane_failed, adapter_invalid, unexpected_proposal, proposal_required, multiple_proposals, proposal_association_mismatch, projection_missing, projection_invalid, capability_unavailable, proposal_tool_mismatch, canonicalization_failed, proposal_arguments_mismatch, permission_failed, confirmation_invalid, result_invalid, provenance_invalid, obligation_failed, response_failed, audit_invalid, invariant_violation. These are diagnostics, not new authority/obligation enums in P0.

## Validity and truth

- Every pre-dispatch stop has executed=False and result=None. Model success/completion prose cannot change either field. No TrustedToolResult.ERROR is manufactured.
- For a post-attempt stop with an existing valid result, executed equals result.executed and the same result is retained. If obligation_state exists, its result must be that same current result (or both None). No clearing a result to manufacture a harmless fallback.
- executed=True without a result is permitted only for a witnessed executor entry followed by loss of a result in a later explicitly isolated boundary; it conveys no success/failure fact. The recorded-only core cannot infer this state from an absent recording and must not fabricate it. Live cancellation/transport-loss handling is outside this passive contract.
- A contradictory but well-typed ObligationState may be retained for diagnosis, with obligation_failed and its existing contradiction code. It is not permission to continue P6 rendering. Current vs historical result/record linkage remains distinct.
- Invalid correlation before a turn is admitted is caller API misuse: reject using the existing P1 validation boundary; do not invent a correlation ID merely to manufacture PipelineStop. For an admitted turn, all semantic failures return structured stopped state.
- No automatic retry, recovery, repair, model fallback or subsequent execution after a stop. Malformed projections are rejected, never treated as defaults.

## Failure and fallback authority

Normal deterministic refusal branches (unknown action, multi-action, ambiguity, actual permission denial or confirmation requirement) still use the existing valid ObligationState → obligations.derive/require → response.build → ApprovedOperationalResponse. They are not fake tool errors. Preserve exact P6 priority, DENY reason permission_denied and TIMEOUT reason trusted_tool_timeout.

New guard stops and exceptions are not automatically mapped to those normal refusals. In particular, a missing/mismatched proposal is not proof of capability absence, permission denial, a trusted tool error or missing conversational context. A partially assembled state must not be passed to P6 just because its defaults yield a convenient acknowledgement or confirmation request.

For a stopped turn, P6 may provide a fallback only when independently complete, consistent state genuinely supports the condition and response.build accepts its evidence; P7 may not select a lower obligation or construct ApprovedOperationalResponse. No exact P6 rule currently describes proposal_required/multiple_proposals/proposal mismatch, classifier/router failure or builder failure itself. These return non-renderable PipelineStop in the passive API. F-FALLBACK-01 is BEFORE LIVE WIRING, not BLOCKING IMPLEMENTATION: passive tests assert stop state and absence of a response, with no fabricated obligation. A live response/failure audit contract must be settled before exposing those turns.

The conceptual successful/failed return alternatives can use `TurnOutcome = ApprovedOperationalResponse | ConversationalResponse | PipelineStop`; this is an alias, not another authority class. Internal diagnostics/optional audit projections remain separate from a user-visible response. No production type is added now.

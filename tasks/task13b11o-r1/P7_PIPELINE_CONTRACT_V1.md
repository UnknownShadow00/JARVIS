# P7 PIPELINE CONTRACT V1

Canonical contract for the passive recorded/static composition boundary, frozen under P7-D01–D04. Exact file set and digest: FREEZE_RECORD.md / CONTRACT-ARTIFACTS.sha256. Historical task13b11o remains a blocked proposal, not normative where this resolution differs.

## Responsibility and dependency

Canonical component: Integration boundary, app/execution/pipeline.py. It coordinates the completed P0–P6 components and P7 recorded adapter. It owns no classification, routing, lane, canonicalization, policy, confirmation lifecycle, execution, provenance trust, obligation priority or response template. The P7 composition guard owns consistency checks only.

Next implementation is restricted to recorded adapter output and static/test-owned state. No live server/provider/registry/store/audit writer is reachable. Full P7 still includes later shadow/server integration; P8 waits on full P7 exit. This freeze is not a full-phase completion claim.

## Exact constituent boundaries

- Original caller request:str and P1 CorrelationContext remain the turn association. Caller owns model identity, proposal IDs and all times; no ID family or clock is introduced.
- Snapshot: existing LedgerSnapshot with session-matched validated records. Classification uses ClassifierContext; routing uses actual Classification and explicit RouterContext. Never default unavailable state to an empty snapshot or infer availability from abstract vocabulary.
- Adapter input/output remains exactly 13B11N-R1: AdapterRequest and canonical recording → ModelDraft plus ordered tuple[ToolProposal,...]. Parser success is not trust.
- Guard inputs and comparison semantics are exactly PROPOSAL_GUARD.md. The supported static projection uses existing RouteResult, PermissionRequest and CanonicalizationResult, not a new registry/schema authority type.
- Permission is an actual permissions.decide result. Confirmation and result projections remain existing P4/P5 types with current/historical invocation linkage. No bool supplied by model or possession of a Python dataclass grants trust.
- Obligations consume the existing ObligationState; response.build consumes ResponseBuildInput with exact provenance/result evidence. No raw model input enters either operational constructor.
- Result alternatives reuse ApprovedOperationalResponse and ConversationalResponse plus the new, contract-only PipelineStop. The conceptual TurnOutcome may be a type alias over these three mutually exclusive alternatives; no duplicate response wrapper is required. A PipelineStop is not renderable text.
- ConversationalResponse still carries untrusted model content; it does not establish operational truth. Any later user-visible conversational path must retain the existing cleaning/safety boundary. No new keyword detector, model-based classifier or raw operational fallback is introduced here.
- Passive audit projection is `(lane: Lane, obligation: ObligationDecision | None)` plus caller correlation/context, held internally in fixtures. It is not a validated/emitted ExecutionAuditRecord. Conversation has None, never a placeholder obligation.

UPDATED_GUARD_ORDER.md freezes order and branch stops. PROPOSAL_CARDINALITY.md freezes the cases reaching the guard. PIPELINE_FAILURE_MODEL.md freezes every new stop field and reason. Existing P6 failure codes and priority remain unchanged. Updated matrix and contradiction corpus are pre-implementation expectations, not measured pipeline passes.

## Scope of unresolved prerequisites

Production request-to-tool binding derivation is not invented: only OPEN_APP→apps.open and OPEN_URL→browser.open capability pairs are frozen in P4, not a general tool/argument schema. A static caller projection makes the pure comparison implementable and testable; absent projection stops. A real binder must be separately specified before any branch derives executable tool arguments from text or live capabilities. Fixtures must explicitly identify their synthetic binding and may not claim a live capability.

PipelineStop enables passive failure tests without a P6 extension. A live user-visible fallback for unmapped failures and conditional conversational audit validation remain before-live prerequisites. The next passive implementation must not depend on serializing a conversational turn.summary under today's defective validator. No permission to call `validated=True` to bypass it is granted.

## Side effects and history

The new contract logic authorizes zero network/provider/model/registry/dispatcher calls, confirmation mutation, provenance writes or audit emissions in this design task. The recorded-only implementation boundary must remain side-effect-free; any later inert P5 integration test uses an explicitly isolated test-owned boundary and the actual existing authority gates, never a live executor. No persistent store singleton, dispatch retry or raw-prose fallback.

All source ownership, confirmation binding, provenance and correlation constraints inventoried in 13B11O remain applicable; this file set resolves only the four blockers and their consequences. Normative precedence: current operator decisions → this V1 → existing frozen component contracts → older proposals. This does not authorize unrelated policy/schema changes.

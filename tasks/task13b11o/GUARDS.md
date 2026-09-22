# Guard inventory

NOT FROZEN as a complete pipeline contract. IDs below are documentation labels, not new production reason codes. Failure always stops the execution branch; P6/P1 completion is allowed only with independently valid state, never invented missing outputs.

| Guard | Condition / required source | Pass | Stop / existing owner representation |
|---|---|---|---|
| G01 Identity/input | caller IDs, aware times, session snapshot and adapter turn agree; P1/P2/adapter validation | S02 | source input exception; no authority projection from bad input; O-B03 wrapper |
| G02 Classification | actual classifier output from original request, version 2 | S03 | ClassifierError; no conversation default |
| G03 Route | actual router output from same request/classification | S04 | RouterError; no guessed target/action |
| G04 Lane | lane.explain from true operational signals; re-evaluate after proposals/results | operational branch or valid conversation | LanePolicyError / P6 lane contradiction; no downgrade |
| G05 Adapter | exact R1 JSON/caller contract, atomic validation | preserve ordered untrusted outputs | AdapterError invalid_input/invalid_json/invalid_response; no proposal/result promotion |
| G06 Action feasibility | route NONE/UNKNOWN/MULTI, unresolved target, explicit capability projection | executable candidate only if deterministic route permits | unknown→P6-06a; multi→P6-05; unresolved→P6-04; no confirmation/dispatch |
| G07 Binding/cardinality | route/capability/proposal/tool/canonical args agree under authoritative schema | UNSPECIFIED: O-B01/O-B02 | zero dispatch mandatory; exact guard result/obligation NOT FROZEN |
| G08 Permission | permissions.decide on valid JARVIS-owned PermissionRequest; no model constraints | ALLOW or REQUIRE_CONFIRMATION handoff | DENY→P6-06b where winning; PermissionPolicyError is not a manufactured PermissionDecision |
| G09 Confirmation | P4/P5 own session/freshness/exact binding/claim; not a caller bool | P5 atomic claim then inert executor | CONFIRMATION_REQUIRED result with existing claim-refusal kind; no execution |
| G10 Dispatch | P5 seven ordered gates including idempotency | only P5 invokes isolated executor | BLOCKED/CONFIRMATION_REQUIRED executed=False, or DispatchError on misuse |
| G11 Provenance | validate_record and P6 linkage/source/session/currentness checks | exact P2 projection only | ProvenanceError / ResponseContradiction, no model-created fact |
| G12 Obligation | obligations.contradiction/derive on settled state | existing highest-priority decision | ContradictoryObligationState / ObligationInputError |
| G13 Builder | response.build validates exact decision/evidence | ApprovedOperationalResponse | ResponseInputError / ContradictoryResponseState; no alternate constructor |
| G14 Audit | audit_events.validate on caller-correlated projections | compatible schema-v3 data only | ExecutionAuditError; no emitted event or unreviewed informational/safety downgrade |

Unsupported capability is not inferred from the model's unadvertised name alone: deterministic route/capability facts control P6; an unadvertised proposal is a guard failure, not evidence that the user's capability does not exist. Likewise rejected arguments do not authorize inventing PermissionOutcome.DENY from a policy exception. O-B01/O-B03 must close these distinctions.

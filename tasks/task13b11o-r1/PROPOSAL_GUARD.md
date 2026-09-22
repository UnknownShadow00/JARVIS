# Proposal guard — P7-D01

Owner: P7 composition. Pure consistency checking, no authority grant. No natural-language interpretation, fuzzy matching, learned policy, registry lookup, schema discovery or argument repair.

## Exact comparison input schema

| Input | Existing type / owner | Required meaning |
|---|---|---|
| correlation | CorrelationContext / caller P1 | valid session/turn; fixed throughout the turn |
| request | AdapterRequest / caller JARVIS | turn_id equals correlation.turn_id; model is requested identity |
| proposal_ids | tuple[str,...] / caller | adapter's unique, ordered IDs; same accepted request association |
| proposals | tuple[ToolProposal,...] / adapter | untrusted; cardinality checked before inspecting/selecting any member |
| route | RouteResult / actual P3 | produced from this caller request/classification/context; no model substitution |
| router_context | RouterContext / caller static capability projection | explicit supported_actions, not default vocabulary as a capability grant |
| permission_projection | PermissionRequest / JARVIS caller | proposed policy query only, NOT a PermissionDecision. Contains action/capability/target, raw/canonical argument projection and policy inputs |
| expected | CanonicalizationResult / P3 over caller JARVIS structured arguments | authoritative expected tool_name, raw_arguments, canonical_arguments, version, applied_rules |
| candidate | CanonicalizationResult / P3 over the sole proposal | candidate.tool_name equals proposal.tool_name; candidate.raw_arguments equals proposal.raw_arguments. Remains untrusted candidate representation |

The two canonicalization results must be outputs of the existing canonicalize API in the composition/fixture setup, not model-authored canonical fields. Their caller data is snapshotted with no mutable alias that can change the comparison. P7 coordinates P3 calls outside the comparison guard; it neither copies P3 alias rules nor canonicalizes internally.

## Ordered match semantics after cardinality

1. Association: proposal.turn_id == request.turn_id == correlation.turn_id; proposal.proposal_id == proposal_ids[0]; proposal.proposed_by_model == request.model. Exact string equality after existing ID validity checks, no provider replacement. Wrong association → proposal_association_mismatch.
2. Projection presence/integrity: all three JARVIS route/context/permission inputs and expected P3 result exist. permission_projection.primary_action equals route.primary_action (not None on a routed action), target equals route.target, target_resolved equals the route's resolved value. Its raw_arguments and canonical_arguments match expected's respective representations; its canonical_target is caller-projected, never model-extracted. Versions are the actual current frozen module versions. Missing → projection_missing; inconsistent → projection_invalid.
3. Capability: this single action is available in route and the caller's explicit RouterContext; permission_projection.capability matches the existing P4 ACTION_CAPABILITY pair where one is defined. Use the existing row_for/registered policy facts to reject unavailable/unregistered capabilities, not model-visible schemas. Inconsistent action/capability → projection_invalid; unavailable → capability_unavailable. Guard passage still grants no policy result.
4. Tool identity: proposal.tool_name == expected.tool_name exactly, and that name must occur in caller request.tool_schemas. The caller-supplied binding, not the proposal or a ToolSchema description, owns the expected namespace. Advertisement is necessary request consistency, never sufficient capability/permission authority. Wrong spelling/case/whitespace, an unadvertised name or arbitrary registry key → proposal_tool_mismatch. This preserves adapter v1's deferral of unadvertised-tool rejection to the guard.
5. Candidate P3 linkage: candidate corresponds to this exact proposal; expected.version == candidate.version == current CANONICALIZATION_VERSION. Missing/bad linkage or version → projection_invalid. No guessing around canonicalization failure.
6. Canonical arguments: compare the ENTIRE candidate.canonical_arguments with expected.canonical_arguments by exact JSON-value structure and scalar type, including keys, target-bearing values and extras. Difference → proposal_arguments_mismatch. Missing/extra keys reject; no ignored extra argument can modify the operation.

Exact comparison: object key order irrelevant; exact key sets and recursively equal values required. Arrays compare positionally. JSON booleans are not numbers; integer and float types are not implicitly exchanged; strings have no trimming/casefolding except transformations already applied by P3's declared rules. JSON null equals null only where present in the authoritative projection, not absence. Map/tuple containers are the immutable representation of JSON objects/arrays, not semantic coercion. No arbitrary limits are invented.

Whole canonical-map equality includes target identity as encoded in the authoritative caller binding; the guard never discovers which tool field means target. It separately checks routed target against the caller permission projection. Producing that trustworthy field binding from live/text input is F-MAP-01, not something equality proves. A hand-constructed/model-derived “expected” mapping is not accepted authority merely because it equals the proposal.

On success only the consistency gate passes. P4 is still called on JARVIS-owned capability/action/target/constraints. Preserve proposal.raw_arguments for audit/invocation raw data and expected.canonical_arguments/version for canonical data; accepted model aliases do not replace the authoritative canonical value. P4 raw_arguments may retain the matched proposal's original raw form without using it to choose policy. All other permission fields come from the deterministic projection. Guard result is never an ALLOW, confirmation token, ToolInvocation or TrustedToolResult.

## Minimal mapping prerequisite

P4 freezes two action/capability pairs; P3 freezes the apps.app alias scope. No general capability→tool namespace→required target/argument schema is frozen. Do not freeze an invented live mapping here. Passive tests supply explicit synthetic expected projections and label them as such. Missing projection deterministically stops; no fallback. A complete production binder/schema, ownership and target-field correspondence must be frozen before deriving an expected projection from real requests or invoking an execution path dependent on it. This does not block implementing pure comparison against caller-supplied static projections.

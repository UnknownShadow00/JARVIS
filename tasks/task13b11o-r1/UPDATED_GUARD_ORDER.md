# Frozen guard order

This is a contract reachability proof, not a claim that an unimplemented module has passed execution tests. The thirteen-stage plan remains the backbone; S06 now has explicit ordered sub-gates. No guard pass is an authority decision.

| Order / stage | Condition and owner | Stop / next |
|---|---|---|
| 1 S01_INPUT | caller correlation/request/state projection validity; P1/P2 identities, exact same session | invalid_input; otherwise S02 |
| 2 S02_CLASSIFY | actual classifier.classify on original request + known keys, version 2 | classification_failed, no assumed class; otherwise S03 |
| 3 S03_ROUTE | actual router.route with that Classification and explicit RouterContext | routing_failed; otherwise S04 |
| 4 S04_LANE | lane.explain using existing operational state; no copied policy | lane_failed; otherwise S05 |
| 5 S05_ADAPTER | exact frozen recorded parser and caller metadata; all-or-nothing | adapter_invalid; otherwise final S04 |
| 6 final S04_LANE | re-use lane.explain including actual proposal/result/confirmation signals | no conversational downgrade; lane_failed if invalid |
| 7 deterministic branch | UNKNOWN/MULTI/unresolved route → existing P6 terminal; NONE with no proposals → conversational or non-action P6 path; NONE with proposals → unexpected_proposal | no permission/confirmation/dispatch for non-executable route; only supported resolved single action reaches S06 |
| 8 S06_CARDINALITY | zero → proposal_required; >1 → multiple_proposals | stop before binding/permission; exactly one → S06_MATCH association |
| 9 S06_MATCH association | exact caller proposal ID/turn/requested model | proposal_association_mismatch; otherwise projection |
| 10 S06_PROJECTION | expected JARVIS projection present, route/action/target/context and current versions consistent | projection_missing / projection_invalid |
| 11 S06_PROJECTION capability | caller availability + frozen P4 registration/action-capability facts; no live registry | capability_unavailable / projection_invalid; no dispatch |
| 12 S06_MATCH tool | exact proposal tool vs expected tool and caller-advertised name | proposal_tool_mismatch |
| 13 S06_CANONICALIZE | P3 canonicalize expected/candidate structured inputs outside guard; validate result linkage/version | canonicalization_failed / projection_invalid |
| 14 S06_MATCH arguments | full type-sensitive canonical-map equality | proposal_arguments_mismatch; pass → S07 |
| 15 S07_PERMISSION | actual permissions.decide with JARVIS policy inputs and matched raw/canonical forms | permission_failed on API failure; actual DENY → P6; otherwise S08 |
| 16 S08_CONFIRMATION | existing requirement, exact bound caller/test state; no synthetic confirmed bool | waiting → actual P6 REQUEST_CONFIRMATION; invalid projection → confirmation_invalid; eligible handoff → S09 |
| 17 S09_RESULT | recorded current-result/invocation/claim linkage, or a later explicitly isolated P5 boundary with all seven existing gates | result_invalid on invalid replay; P5 refusals/result statuses remain owned by P5 |
| 18 S10_PROVENANCE | exact P2 current/historical evidence; no writes or model promotion | provenance_invalid; otherwise S11 |
| 19 S11_OBLIGATION | actual existing state/contradiction/priority selection | obligation_failed retaining owner code; valid decision → S12 |
| 20 S12_RESPONSE | response.build only, exact evidence and decision | response_failed; no raw prose fallback; otherwise S13 |
| 21 S13_AUDIT | internal optional-obligation projection truthful for lane; existing compatible events only where valid | audit_invalid; never emit or bypass validation; conversational summary serialization deferred |

An ordinary operational terminal can reach P6 only with complete, consistent existing state. Specifically, capability absence must not be answered from a state whose omitted permission would let P6-01c manufacture a confirmation request. Explicit RouterContext exclusion produces the existing UNKNOWN_ACTION route; alternatively use an actual applicable P4 denial. If an expected binding/settled state is missing, return structured stop instead of synthesizing that denial or changing P6 priority.

## Dispatch path proof

Every admitted continuation to S09 has: G1–G6 valid caller/deterministic/adapter state; an executable deterministic route; exactly one proposal; matching caller association; present and consistent expected projection; caller capability; exact tool identity; P3 canonicalization and full canonical equality; actual P4 outcome; required P4/P5 confirmation authority. A stop at any earlier stage has no edge to S09. A later recorded SUCCESS or supplied ALLOW cannot backfill a missing earlier gate. Model text is absent from all gate authority inputs.

P5's internal order remains type → structure → canonicalization metadata → permission → required confirmation inputs → atomic ownership/freshness/exact binding/idempotency claim → executor. No P7 pre-claim, duplicate implementation of those checks as a substitute, or proposal→dispatcher shortcut. In the recorded-only boundary S09 performs no call at all: it verifies a caller-held fixture projection, not a live capability.

Future pre-execution safety-audit gating cannot be postponed to final aggregation. This task emits no audit, invokes no dispatcher, mutates no confirmation and writes no provenance. A successful static guard test is not evidence of real execution, live audit readiness or full P7 exit.

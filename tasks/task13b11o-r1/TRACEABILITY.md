# Source and decision traceability

Workspace parent c9cce9b47a79c8ac52da116d113b3fb824991cf8; production db54d615c3ee023d753e86143860c4efdc251230. 13B11O FREEZE_RECORD explicitly states NOT FROZEN. Therefore this is the first P7 PIPELINE CONTRACT V1 freeze; it does not replace a frozen V1 or silently rewrite history.

| Source | Preserved or resolved requirement |
|---|---|
| Operator 13B11O-R1 §§4–8 / P7-D01 | P7 owns consistency guard; exact deterministic projections; no guessed tool mapping |
| Operator §§9–14 / P7-D02 | Conversation zero valid; supported single-action zero/many/mismatch stops; no selection/repair |
| Operator §§15–21 / P7-D03 | Minimal immutable stopped state authorized; no prose/fake tool error; P6 fallback authority; unrepresentable failures classified by scope |
| Operator §§22–26 / P7-D04 | Conversation has no obligation; conditional schema correction deferred; internal optional projection permitted |
| 13B10D contract/yaml §§4–9, 11–19 | Deterministic lanes/actions/targets, authority, no decomposition, canonicalization, obligations/trust/audit |
| 13B11A graph / phase table / target map | Integration boundary at app/execution/pipeline.py; P6+adapter before pipeline; remaining P7 before P8 |
| 13B11A integration seam / failure table | Ordered composition, raw-prose lock, explicit inert boundary; passive stopped state now authorized instead of invented live fallback |
| 13B11N-R1 adapter contract | Ordered untrusted P0 proposals, strict canonical JSON, no coercion, metadata caller-owned, reasoning rejection |
| Current P3 APIs | Classifier v2; RouterContext and RouteResult; LaneSignals/explain; CanonicalizationResult raw/canonical/version |
| Current P4/P5 APIs | PermissionRequest/Decision; two ACTION_CAPABILITY pairs; explicit confirmation binding/claim; dispatcher result/idempotency ownership |
| Current P2/P6 APIs | Snapshot/record source and session checks; ObligationState, contradiction and priority; ResponseBuildInput and sole approved builder |
| Current P1 audit API | Optional field annotation, unconditional summary-required-set defect, None omission serializer |
| 13B11O four follow-ups / all proposed artifacts | Starting point retained; four questions resolved here; old matrix coverage mapped explicitly, no historical edits |

Production sources and tests are archived from exact HEAD in the new evidence. A fresh source/import/interface inventory and the earlier pure API compatibility probe preserve the existing behavior; no future guard/type/schema implementation is tested or claimed. No live registry was inspected to derive a binding.

The 18 prior conformance categories remain required: unsafe draft containment, invocation-scoped error, narrow success facts, pending confirmation, ambiguity, correction, supplied attribution, unsupported capability, multi-action, canonical raw/canonical distinction, exact obligation, non-model operational source, normal conversation, result spoofing, denial, lane monotonicity, reporting-clause containment and grounded-source priority. The six added contradiction cases complement rather than replace them.

Side-effect budget for every new contract-only diagnostic: no model/provider/registry/dispatcher invocation, confirmation mutation, provenance write or audit emission. Repository/evidence transport and mandated regression process setup are verification operations, not a live P7 path. Production diff is empty, pipeline.py absent, and only legacy runtime remains active.

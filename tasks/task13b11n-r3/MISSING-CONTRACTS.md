# Missing composition contracts
These gaps do not invalidate the completed adapter. They prevent silently promoting it into an operational pipeline.

| ID | Current evidence | Missing normative decision |
|---|---|---|
| P7-PIPELINE-01 | No class TurnOutcome and no pipeline.py anywhere in app; target map names both | Exact immutable request/outcome shapes and full passive scope |
| P7-GUARD-01 | P4 ACTION_CAPABILITY maps OPEN_APP->apps.open and OPEN_URL->browser.open; P3 RouteResult has no tool_name; P5 consumes settled ToolInvocation | Exact route/capability/proposal/tool/argument binding, identity/version checks and disposition of zero/many/mismatched proposals |
| P7-PROJECTION-01 | ClassifierContext(keys), RouterContext(actions), LaneSignals, PermissionRequest, ObligationState and ResponseBuildInput have separate inputs | Single deterministic owner of each projection; provenance/session/correction/current-result linkage; no model-owned satisfied constraints |
| P7-LANE-01 | Plan seam decides lane before adapter; existing LaneSignals includes presence of tool proposal/result | When final operational signals are assembled; no conversational downgrade after operational evidence |
| P7-FAILURE-01 | Integration plan §19 names safe failure behavior; P0 outcome and fallback representation absent | Exact per-stage errors, interruption behavior and safe outcome representation without fabricating evidence |
| P7-AUDIT-01 | P1 ModelDraftAuditRef already supports digest and optional blocked excerpt | Exact event mapping, safe draft-reference construction and audit failure gating in passive composition |
| P7-LIVE-01 | Adapter v1 is canonical recording only; remaining P7 requires live shadow | Separate actual provider normalization and live integration/activation approval |

P4's existing two action/capability mappings are frozen facts, not missing policy. Their conversion into proposal tool namespaces and canonical argument schemas still needs a composition contract. Do not infer capability from model-visible descriptors or the abstract router default.
The adapter rejects multiple malformed proposals atomically but intentionally preserves valid multiples. This is not a pipeline choice to select one for execution.

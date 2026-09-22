# Pipeline identity

| Question | Canonical answer |
|---|---|
| Name | Integration boundary / pipeline |
| Source path | app/execution/pipeline.py; currently absent |
| Conceptual entry | handle_turn(session, text) → TurnOutcome; conceptual plan signature, not an existing API |
| Responsibility | Orchestrate one turn, preserve deterministic authority, return the correct lane-specific response |
| Predecessors | P6 obligations and response completed; fan-in from P0–P5 and the P7 recorded adapter |
| Immediate downstream | P7 server/API/UI branch and shadow boundary |
| Later successor | P8 inert end-to-end conformance, only after full P7 exit |
| Entire P7 passive? | No. Full phase includes measured shadow on live traffic. This task explicitly limits the proposed unit to passive recorded composition |
| Own authority policy? | No classification/routing/lane/permission/confirmation/provenance/obligation/template policy |
| Own state? | No hidden singleton or independent authoritative store. Full plan coordinates P2/P4/P5 owners; passive projection cannot counterfeit their transitions |
| Call existing modules? | Yes, the orchestration seam explicitly calls them; zero-live-consumer invariants remain mandatory |

Sources agree on identity and dependency order: 13B11A TARGET_COMPONENT_MAP §1, DEPENDENCY_GRAPH §§1–2, IMPLEMENTATION_PHASES P7/P8 and PRODUCTION_INTEGRATION_PLAN §2. Plan-only historical API spellings (`ask`, `invoke`) are superseded by implemented APIs, not evidence of a new live protocol.

Material unresolved allocation: TARGET_COMPONENT_MAP §3 assigns proposal-guard enforcement to permissions.py + dispatch.py, while integration §2 places it before permission and current modules consume separately settled inputs. Neither has a route/proposal comparison API. Do not silently relocate this safety responsibility into the orchestrator. O-B01 records the exact reconciliation required; the dependency graph itself is not cyclic or contradictory.

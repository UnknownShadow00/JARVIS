# Next three graph units
Derived from 13B11A DEPENDENCY_GRAPH.md, IMPLEMENTATION_PHASES.md and TARGET_COMPONENT_MAP.md; not inferred from task numbering.

| Unit | Predecessor | Contract readiness | Passive/offline | Disposition |
|---|---|---|---|---|
| P7 app/execution/pipeline.py | P6 builder + P7 adapter, complete | Conceptual sequence only; no TurnOutcome or exact stage projections/failure contract | A recorded-input subset could be passive after freeze | BLOCKED for implementation; draft prepared |
| Remaining P7 server branch + shadow/API/UI seam | Pipeline incomplete | Mode semantics planned, runtime ownership/live normalizer/activation gates unresolved | Actual plan requires live shadow traffic/model and a measured period | BLOCKED; prohibited live wiring, no activation |
| P8 inert E2E conformance | Full P7 exit, not met | CT-001..018 frozen, runner input needs actual pipeline contract | Test-only and potentially offline, but predecessor incomplete | BLOCKED execution; corpus/traceability plan prepared |

P9 is not an independent alternative: it depends on P8 exit and operator approval and introduces real tools.
P10/P11 inherit those unmet dependencies. No remaining graph-supported production branch is fully specified and independently eligible.
The dependency graph is acyclic. The older diagrams are phase-level ordering; current pure projections do not have to import every predecessor module.

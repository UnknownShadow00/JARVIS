# Traceability

| Finding | Canonical source |
|---|---|
| Hermes adapter, path, responsibility, inputs, outputs | 13B11A `TARGET_COMPONENT_MAP.md` §1 |
| Adapter independently testable against recordings | 13B11A `DEPENDENCY_GRAPH.md` §3 |
| P7 also contains pipeline/shadow/server work not authorized here | `IMPLEMENTATION_PHASES.md` P7; dependency graph |
| JARVIS owns prompts/history/schemas; output is untrusted | `PRODUCTION_INTEGRATION_PLAN.md` §2 |
| Existing `ModelDraft` / `ToolProposal` fields | production `app/execution/types.py` |
| Model cannot own authority | Contract v1 §§2–3, 18, 21–22 |
| No parser envelope or malformed/multiple policy | absence across all mandatory P7 plan/contract sources |
| Historical normalized shape is harness-only | sealed C5 raw records; target map §3 |
| Exact entry/evidence/baseline | sealed Task 13B11N blocked evidence bundle |

The blocker is a missing contract decision, not a runtime or repository failure.

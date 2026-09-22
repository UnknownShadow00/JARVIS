# P7 Hermes Adapter Contract — Blocking Finding

## Resolved identity

| Property | Canonical plan result |
|---|---|
| Component | Hermes adapter |
| Source path | `app/brain/hermes_adapter.py` |
| Responsibility | Build a JARVIS-owned model request and parse structured proposals as untrusted data |
| Planned inputs | prompt inputs and tool schemas |
| Planned outputs | existing P0 `ModelDraft` and `ToolProposal[]` |
| Trust | all adapter output is untrusted |
| Predecessor | P6 exit; P0 types directly |
| Later consumer | P7 `app/execution/pipeline.py`, then the later server branch |

The dependency graph also places pipeline and shadow wiring in P7, but names the Hermes adapter as
independently buildable against recorded model outputs. Task 13B11N authorizes only that passive
unit, not the pipeline or server branch.

## Unresolved contract

The canonical documents do not specify:

1. the recorded Hermes/provider response envelope accepted by the parser;
2. exact required, optional, null, wrong-type, unknown and extra-field policy;
3. duplicate JSON key or conflicting semantic-field policy;
4. zero/one/multiple proposal behavior and ordering;
5. how caller-owned `turn_id`, `proposal_id`, `model`, and `created_at` are supplied or assigned;
6. whether/how raw provider representation is retained for validation and future audit;
7. the exact JARVIS request object and tool-schema serialization the adapter must build;
8. retention/drop rules for provider reasoning-like fields.

Those choices materially determine the public API, corpus, validation behavior and audit surface.
Inventing them would violate the first requirement. Implementation is therefore blocked.

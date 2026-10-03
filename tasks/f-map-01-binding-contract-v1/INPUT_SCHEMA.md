# Future producer input schema

`binding_projection.py` consumes typed settled inputs; it never reads HTTP, registry or model state itself.

| Input | Exact conceptual type | Owner / trust | Required | Validation |
|---|---|---|---|---|
| `normalized_request` | `NormalizedJarvisRequestV1` | ingress/P1/P2; text untrusted, IDs/snapshot owner-trusted | yes | original text, valid correlation, same-session immutable snapshot |
| `classifier_context` | `ClassifierContext` | P2 key projection | yes | corresponds to same snapshot; existing constructor rules |
| `registry_metadata` | `RegistryMetadataSnapshotV1` | future passive registry-metadata boundary | yes | exact admitted keys/module paths/handler metadata, revision/digest; no callable/module handle |
| `approval_mode` | `ApprovalMode` | JARVIS operator config/P4 | yes | exact enum; client cannot override |
| `binding_schema_version` | literal `"1"` | frozen V1 contract | yes | reject any other version; no silent upgrade |

P3 classification, route and lane are **derived/consumed from existing APIs**, not caller-authored inputs. The producer calls/reuses `classifier.classify` and `router.route` with identical request/context values that P7 will later recompute; it may call `lane.explain` only as needed for existing lane signals, without adding lane rules. These V1 rows require no satisfied constraints and no overwrite flag: their P4 query uses `frozenset()` and `None`. P1 timestamps/proposal IDs, adapter recording, confirmation projection and result replay are assembled by their separate owners into `RecordedTurn`, not passed into this binding producer.

# Transport-neutral request envelope

Conceptual immutable `NormalizedJarvisRequestV1` contains only:

| Field | Type | Owner / source | Validation |
|---|---|---|---|
| `request` | exact `str` | original user text from validated transport, untrusted content | preserve text; never deserialize authority fields from it |
| `correlation` | `CorrelationContext` | P1 JARVIS session and turn IDs | exact type; well-formed IDs; no client/model replacement |
| `snapshot` | `LedgerSnapshot` | P2 same-session trusted state | session equals correlation; immutable records |

P2 derives `ClassifierContext` and other trusted projections from that snapshot; JARVIS safety config supplies `ApprovalMode`; the passive registry boundary supplies `RegistryMetadataSnapshotV1` separately. The envelope has no HTTP/WS/PWA/UI object, provider response, claimed route/capability/tool, permission/confirmation/result, executor, store handle or transport-specific authority flag. `request_id` is not a `RecordedTurn` field: P1 `turn_id` is the authoritative turn association; any HTTP request ID is transport diagnostic only. `invocation_id` is absent until the P5 owner creates a later invocation. Existing P1 correlation IDs propagate unchanged to adapter request/proposal association.

# Frozen envelope and missing live source

`NormalizedJarvisRequestV1` is already defined at `app/execution/binding_projection.py:28-34` and `tasks/f-map-01-binding-contract-v1/NORMALIZED_REQUEST.md`. Its complete field set is:

| Field | Type | Source / owner | Trust | Validation |
|---|---|---|---|---|
| `request` | exact `str` | authenticated REST `ChatRequest.message` or parsed WS message; content remains untrusted | raw request only | preserve original text; reject non-string for shadow, never parse authority flags from it |
| `correlation` | `CorrelationContext` | JARVIS P1 | trusted association only | well-formed same-session `session_id`/`turn_id`; no client/model replacement |
| `snapshot` | `LedgerSnapshot` | JARVIS P2, same session | stored state with typed provenance | snapshot session equals correlation; records validate |

No HTTP/WS/PWA object or client route/tool/permission/confirmation/result field enters this envelope. `ClassifierContext(known_fact_keys=frozenset(snapshot.keys()))`, `RegistryMetadataSnapshotV1`, JARVIS `ApprovalMode`, and literal schema version `"1"` are separate producer inputs (`f-map-01-binding-contract-v1/INPUT_SCHEMA.md`).

**Unresolved live handoff:** REST and WS currently supply no JARVIS session ID or P2 ledger instance. `start_trace` currently creates a hyphenated UUID (`app/observability/tracing.py:120+`), whereas the producer validates P1 IDs as 32-character UUID hex. The binding contract says turn ID associates with the trace; it does not define the exact normalization/join or session lifetime. No empty ledger may be presented as complete historical truth. Freeze these owner/lifetime/trace rules before wiring.

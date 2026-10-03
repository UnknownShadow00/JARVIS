# Complete immutable BindingProjectionV1 output

Future `BindingProjectionV1` is a frozen, slotted data-only result with exactly these fields; it contains no callable, provider client, store, registry handle, dispatcher, executor, confirmation machine or shortcut approval boolean.

| Field | Type | Owner/source → P7 consumer | Derivation / failure |
|---|---|---|---|
| `binding_schema_version` | literal `"1"` | V1 contract → ingress audit/provenance association | constant; mismatch rejects before P7 |
| `metadata_digest` | SHA256 hex `str` | passive registry snapshot → ingress association | deterministic digest of approved normalized metadata; mismatch rejects before P7 |
| `router_context` | `RouterContext` | metadata + V1 rows → `RecordedTurn.router_context`, S03/S06 | supported actions are only rows with matching metadata; absent set is empty, never default vocabulary |
| `expected` | `CanonicalizationResult | None` | closed row + P3 canonicalizer → `RecordedTurn.expected`, S06 | present only for one resolved admitted row; otherwise `None` |
| `permission_projection` | `PermissionRequest | None` | P3 route + P4 pair/config + expected maps → `RecordedTurn.permission_projection`, S06/S07 | present exactly when `expected` is present; otherwise `None` |

All five fields are JARVIS-owned *comparison/provenance data*, not execution authority. The output does not duplicate `AdapterRequest`, model draft/proposals, settled confirmation, invocation or result replay fields. JARVIS builds `AdapterRequest.tool_schemas` separately from the **same** V1 row/snapshot; its advertised `tool_name` must equal `expected.tool_name`, but advertisement cannot grant a capability. P7 recomputes classifier/route/lane and policy decision. If no V1 row is admissible, the pair is absent and the existing early unsupported/P6 or S06 `projection_missing` behavior applies; the producer cannot invent a `PipelineStopReason`.

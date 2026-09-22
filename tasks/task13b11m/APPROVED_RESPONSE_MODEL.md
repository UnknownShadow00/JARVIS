# Approved Response Model

Task 13B11M reuses `app.execution.types.ApprovedOperationalResponse` exactly. No competing
`OperationalReply`, `SafeResponse`, `TrustedResponse`, or `FinalToolReply` was introduced.

| Field | Builder rule |
|---|---|
| `text` | frozen template plus, only where required, one safely serialized scalar provenance value |
| `turn_id` | caller's exact current turn identifier |
| `obligation` | the supplied, validated `ObligationDecision.obligation` |
| `source` | P6's frozen obligation-to-source mapping |
| `provenance_record_ids` | only the records whose values actually appear in text |
| `created_at` | caller-supplied aware timestamp; no clock read |
| `lane` | `OPERATIONAL` |

The P0 model is sufficient. Exact invocation/result relationships are validated at construction;
the response carries the exact record IDs required for displayed values. Static success/error
templates use no arbitrary returned facts, so they carry no unrelated record IDs.

`to_mapping()` remains the deterministic serializer. The builder adds no hidden prompt,
chain-of-thought, rationale, arbitrary Python object, or schema field.

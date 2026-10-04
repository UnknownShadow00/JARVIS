# ShadowIngressEnvelopeV1

Frozen slotted dataclass with exactly two fields, in order:

```python
request: str
context: SettledShadowTurnContextV1
```

Versioning is in the type name. No wire/schema/version field or serialization protocol is added. Context retains exactly its frozen three fields: existing CorrelationContext, existing same-session LedgerSnapshot, and observational `transport_trace_id: str | None`.

The value is passive data upstream of binding projection, adapter and pipeline. It contains no executable handle, provenance write authority, default/fallback identity or response. Class construction either issues the validated value or raises deterministically. Public immutability reuses the existing P2 API guarantee.

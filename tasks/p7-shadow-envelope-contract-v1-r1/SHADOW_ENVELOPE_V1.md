# ShadowIngressEnvelopeV1 — frozen minimum

Immutable value with exactly two fields:

| Field | Type | Source |
|---|---|---|
| request | exact str | REST req.message or WS extracted message, preserved byte-for-byte as a Python string |
| context | SettledShadowTurnContextV1 | JARVIS owner; existing P1 correlation, P2 snapshot, observational trace association |

The raw untrusted request material is the accepted message string. Do not trim, case-fold, parse into commands or replace it with model prose. Raw HTTP body, WS JSON frame and headers are not required downstream and are excluded. A transport enum/origin label is not required to construct the existing NormalizedJarvisRequestV1, so V1 introduces neither. Transport identity can be inspected through the existing associated trace; it cannot change control-plane authority.

The value's versioned name defines V1; no wire format/extra schema field is selected. Validate exact context ownership/type, P1 shape, same-session P2 records, and public immutable value graph. A valid envelope can later project to existing NormalizedJarvisRequestV1(request, context.correlation, context.snapshot), but this composer does not call the binder. Trace stays observational metadata and is not smuggled into the binder's authority fields.

Absent/invalid settled context or non-string request produces no envelope. Empty text is not newly normalized or given semantic validity by this contract; downstream existing validators remain authoritative. No fields for routes, tools, capabilities, grants, confirmation, execution, results, mutable state, provider identity or scheduling.

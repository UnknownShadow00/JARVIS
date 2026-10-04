# Envelope status: name approved, full schema blocked

The operator-approved conceptual name is `ShadowIngressEnvelopeV1`. It must be immutable and contain no FastAPI Request, WebSocket, mutable payload, session store, registry, model client, dispatcher, executor, response writer or stream callback. Raw user text is untrusted content only. Client-supplied route/tool/capability/permission/confirmation/result/IDs never become control-plane authority.

A complete field set cannot be frozen: the future downstream `NormalizedJarvisRequestV1` requires exact request text, `CorrelationContext(session_id,turn_id)`, and same-session `LedgerSnapshot` (`tasks/f-map-01-binding-contract-v1/NORMALIZED_REQUEST.md`), but current REST/WS have no owned session/turn/snapshot source. Trace association is also unresolved. No placeholder ID, empty P2 snapshot or client ID is authorized. Later adapter/evidence fields are deliberately not added here.

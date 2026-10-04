# Exact JARVIS turn association

Use ShadowIngressEnvelopeV1.context.correlation exactly, originating in Shadow Context V1. Its session_id and turn_id are authoritative JARVIS identifiers; initial child IDs are absent. AdapterRequest.turn_id == envelope.context.correlation.turn_id == RecordedTurn.correlation.turn_id. Same-session snapshot belongs to that context. Keep the complete existing correlation as the outer association; do not add a competing ID family.

AdapterRequest has no session field. Therefore the trusted caller must preserve the outer session/turn association through provider operation and response capture. Parsing only stamps the supplied request.turn_id onto ModelDraft and ToolProposal; P7 compares those stamps but cannot prove which provider operation produced the raw recording. Wrong-turn raw text may pass parser shape checks after a caller restamps it; it must fail authenticity upstream.

Trace remains observational and distinct from turn. No trace fallback, trace==turn assumption, caller-supplied UUID promoted to JARVIS identity, response-body ID echo used as authority, cross-session ledger or new turn on output chunk. WS output/provider stream chunks do not create additional user turns or terminal attempts. Retry/multiple-generation selection is not inferred from same turn; D02/D07 must determine it.

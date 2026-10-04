# One canonical model boundary

Exact production APIs:

- AdapterMessage(role: str, content: str), frozen/slotted, role exactly system/user/assistant.
- ToolSchema(tool_name: str, description: str, parameters_json: str), frozen/slotted; nonblank name, strict JSON-object schema string.
- AdapterRequest(model: str, turn_id: TurnId, messages: tuple[AdapterMessage,...], tool_schemas: tuple[ToolSchema,...]), frozen/slotted, no defaults.
- build_request(request: AdapterRequest) -> str: deterministic canonical JSON; it does not construct a provider client or send the request.
- parse_recorded_response(raw: str, request: AdapterRequest, *, created_at: datetime, proposal_ids: tuple[str,...]) -> tuple[ModelDraft, tuple[ToolProposal,...]].

ADAPTER_CONTRACT_ID is **jarvis.hermes-adapter.recorded.v1**. No request_id, session_id, independent correlation_id, provider response ID, invocation/confirmation field, retry number or adapter version field is embedded in these values. The contract constant identifies parser/schema version; exact source digest can pin implementation in evidence.

Canonical model context is built by JARVIS caller using these existing types, then serialized by build_request. Parser accepts only a JARVIS canonical recording with exact root text/proposals; a provider-native envelope cannot be forwarded blindly. No shadow_adapter.py, shadow_parser.py, alternate ToolProposal decoder, provider wrapper output factory or new adapter API is needed/authorized.

Outputs stay untrusted P0 ModelDraft/ToolProposal; request's JARVIS-supplied model/turn metadata is copied, not inferred from provider content. Parser is not a tool/permission/schema-authority validator; it returns all ordered proposals for later JARVIS guards.

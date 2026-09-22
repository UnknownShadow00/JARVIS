# Adapter API
Module: app/brain/hermes_adapter.py.
- AdapterMessage(role: str, content: str), frozen/slotted.
- ToolSchema(tool_name: str, description: str, parameters_json: str), frozen/slotted.
- AdapterRequest(model: str, turn_id: TurnId, messages: tuple[AdapterMessage, ...], tool_schemas: tuple[ToolSchema, ...]), frozen/slotted.
- build_request(request) -> deterministic JSON str.
- parse_recorded_response(raw, request, *, created_at, proposal_ids) -> (ModelDraft, tuple[ToolProposal, ...]).
No default values in the new input types. Caller metadata is mandatory. Fixed AdapterError codes: invalid_input, invalid_json, invalid_response.
No ask(), transport client, live provider dependency, approved-response factory or execution method exists.
The exact semantics are frozen in ../task13b11n-r1/HERMES_ADAPTER_CONTRACT_V1.md.

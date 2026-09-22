# Request schema
Normative API and exact fields are in HERMES_ADAPTER_CONTRACT_V1.md, Request.
AdapterRequest requires model, turn_id, messages, tool_schemas. AdapterMessage requires role and content. ToolSchema requires tool_name, description, parameters_json.
All Python inputs use exact declared types; bool is never an integer substitute. Tuples are required, not coerced from lists. No optional fields or implicit defaults.
Build output is deterministic JSON with model/turn_id/messages/tools, all caller-owned.
The descriptor's schema JSON is opaque model-visible data; syntax validation is not a schema-dialect, tool availability or permission check.


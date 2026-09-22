# Request building
Serialize only caller model/turn identity, ordered system/user/assistant messages and ordered model-visible descriptors.
Output keys: model, turn_id, messages, tools. Each tool contains tool_name, description, parameters.
Parameter JSON is strictly decoded with duplicate-key and finite-number checks. It is data, not a schema evaluator: no $ref fetching, registry discovery, capability inference or permission derivation.
Sorted object keys, compact separators and ASCII escaping make equivalent schema-object orderings deterministic; array order and string content remain intact.
No prompt text is injected or classified. Empty explicit message/tool tuples are valid. No clock, UUID minting or provider call.

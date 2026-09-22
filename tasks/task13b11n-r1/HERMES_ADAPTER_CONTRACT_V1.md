# Hermes Adapter Contract v1
Status: FROZEN FOR PASSIVE IMPLEMENTATION by Task 13B11N-R1 under the operator's A1 authorization.
Boundary identifier: jarvis.hermes-adapter.recorded.v1.
Production prerequisite: 4885c4f7ca35f2395fab3497e6ce009d36b742be.
This is a JARVIS canonical recording boundary, NOT the live Hermes wire protocol.

## API and ownership
New P7-local frozen, slotted dataclasses: AdapterMessage(role, content), ToolSchema(tool_name, description, parameters_json), AdapterRequest(model, turn_id, messages, tool_schemas). No defaults.
build_request(request: AdapterRequest) -> str.
parse_recorded_response(raw: str, request: AdapterRequest, *, created_at: datetime, proposal_ids: tuple[str, ...]) -> tuple[ModelDraft, tuple[ToolProposal, ...]].
Reuse P0 ModelDraft and ToolProposal, P1 TurnId and is_well_formed_id. There is no existing frozen prompt-input or immutable model-visible schema type in P0-P6 or the provider/registry abstractions. PermissionRequest and CorrelationContext serve different responsibilities and MUST NOT be repurposed.

## Request
Exact built JSON fields: model, turn_id, messages, tools. All required.
model: exact nonblank string; caller chooses the qualified provider/model identity, never replaced by an echo.
turn_id: caller TurnId, exact string satisfying existing is_well_formed_id; adapter never mints IDs.
messages: tuple of exact AdapterMessage objects, empty tuple allowed. Each role is exactly system, user, or assistant; content is exact string, including empty string. Ordering and content preserved; no prompt insertion, classification or routing.
tool_schemas: tuple of exact ToolSchema objects, empty allowed; tool_name nonblank string, unique by exact equality; description exact string including empty; parameters_json serialized JSON object. It is caller-owned model-visible schema data, not a capability/permission claim; arbitrary schema keywords are transported, never resolved, fetched or evaluated. There is no JSON Schema dialect or execution validation claim.
Each serialized tool has exactly tool_name, description, parameters (decoded object).
Serializer: json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False); no trailing newline. Arrays retain order. Caller parameter JSON is parsed strictly for duplicate keys, finite numbers and JSON types. No external reference resolution.
Frozen inputs hold strings and tuples only, so there is no nested mutable input alias.
No clock, timestamp, request_id, session_id, invocation_id, confirmation_id or permission metadata is added to the request.

## Recorded response
Serialized JSON string only. Entire document is the structured proposal payload; there is NO ignored transport envelope in v1. Extra transport metadata must be excluded by a later separately specified live normalizer.
Exact top-level object keys: text, proposals; both required.
text: exact string, empty string allowed. Proposal-only is explicitly text="" with nonempty proposals. Empty text with empty proposals is also valid passive data; parser does not decide usefulness.
proposals: JSON array (including empty). Every element is an object with exactly tool_name and raw_arguments, both required.
tool_name: nonblank string; preserve spelling/whitespace exactly after nonblank validation. No known-tool lookup, advertised-tool filtering, mapping, aliasing or capability inference. Even unadvertised names are untrusted proposals for a later deterministic guard to reject.
raw_arguments: JSON object, including empty. This P0 data mapping is explicitly an open tool-data namespace, NOT extra fields on the closed proposal object. Its values recursively permit JSON objects, arrays, strings, finite numbers, booleans and null. No semantic permission, confirmation or trust can come from any argument key/value. Names/action/target are NOT independently added to the schema: P0 requires tool_name and raw_arguments; a target remains exactly the tool's raw data if supplied. No missing arguments or targets are inferred.
All other structural fields rejected, including proposal type, action, target, provider IDs/model/time, result/status/permission/confirmation/executed/provenance/obligation, and reasoning fields.
Null is forbidden everywhere except explicitly nullable raw-argument values and caller schema JSON values.
No coercion, stringified arguments, singleton arrays, markdown fences, trailing data, Python constants, NaN, Infinity or overflow-to-infinity. Duplicate decoded JSON object keys rejected at EVERY depth, including escape-equivalent spellings.
JSON decoding creates only builtin data; no arbitrary object hook or construction from payload names.

## Outputs and all-or-nothing validation
Validate whole response and caller metadata before constructing any P0 output. One invalid proposal rejects the entire response; no partial returns.
Caller created_at: exact timezone-aware datetime; preserve supplied instant/offset with no clock read. It is control-plane truth supplied by JARVIS, not model data.
Caller proposal_ids: exact tuple of exact strings accepted by is_well_formed_id, unique by UUID hex identity (case differences cannot hide a duplicate), exactly one per parsed proposal. Empty tuple for zero. IDs are assigned positionally, never sourced from provider text.
ModelDraft(text, request.model, request.turn_id, created_at).
For each ordered proposal: ToolProposal(caller ID, request.turn_id, tool_name, raw_arguments, request.model).
Output argument dictionaries are recursively read-only mappings and arrays are tuples, preserving JSON data values/order; P0 to_mapping reconstructs the original JSON value. This is immutable representation, not semantic coercion or canonicalization. No lexical JSON/whitespace/escape retention is claimed; P0 raw_arguments is a mapping and the complete provider document is never retained.
No new draft/proposal/authority type. Return container is a tuple only.

## Reasoning, failures and limits
Reasoning keys are forbidden recursively throughout recorded structured data, including raw_arguments. Normalize field names by lowercasing and retaining alphanumeric characters (P1 policy convention). Forbidden vocabulary is P1's existing nine names plus reasoning and thinking: chain_of_thought, model_chain_of_thought, hidden_reasoning, private_hidden_reasoning, scratchpad, model_internal_reasoning, internal_reasoning, reasoning_content, inner_monologue, reasoning, thinking.
Text is untrusted normal draft content; the parser is not a semantic hidden-reasoning detector. Future live normalization must never map private reasoning to text.
AdapterError(ValueError) carries only fixed codes invalid_input, invalid_json, invalid_response. No input values, raw JSON, payload keys or hidden reasoning in errors; decoding exceptions are not chained into the surfaced error. Interpreter resource failures fail closed; no partial output. No arbitrary production limits or retry.
No I/O, transport, registry, engines, stores, audit, clock, randomness, dispatch or live consumers.


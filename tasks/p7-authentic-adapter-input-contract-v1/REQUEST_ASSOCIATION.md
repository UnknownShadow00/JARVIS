# Exact request object, permitted source material

Canonical object is **AdapterRequest**, constructed by a JARVIS-owned caller from settled inputs; build_request returns its deterministic JSON string, not a new request object or provider handle. Freeze the existing four fields and exact type rules, without widening its API.

| Field | Permitted settled source / boundary |
|---|---|
| model | JARVIS D06-authorized qualified provider/model identity; never replaced by model/client echo |
| turn_id | Existing authoritative Shadow Context correlation.turn_id; no reminting |
| messages | Explicit ordered tuple of existing AdapterMessage values from JARVIS-owned system/prompt/history inputs, including the designated current-turn AdapterMessage("user", envelope.request); no client-assigned role or authority |
| tool_schemas | Explicit ordered tuple of existing ToolSchema values supplied by JARVIS as model-visible descriptors for the reviewed scope; no client/provider/registry authority |

For live use, the designated current-turn message content is the exact envelope.request string with existing user role; no trim, rewriting into a tool/proposal, or substitution with model/legacy prose. This stricter live-association requirement does not change the passive AdapterRequest API, which still accepts explicit empty tuples. The request text remains untrusted. D05 does not choose a system prompt string, current-message array index, history store, preprocessing template or live provider request format. Existing adapter injects no prompt/route/tool/permission fact and does not read envelope/binding/P2/store/framework objects. A future prompt/history assembly contract must name its JARVIS sources and projection so the envelope/request association can be checked; an empty message tuple valid in the passive API is not proof that this live turn was represented.

BindingProjectionV1 has no ToolSchema field/factory. It supplies RecordedTurn.router_context/expected/permission_projection independently. Do not assert it already builds model descriptors. Existing ingress authority describes schemas from the same reviewed V1 mapping; generic tool descriptions/names/parameter shapes may inform the model, but schemas grant no availability or permission and must not smuggle turn-specific expected arguments into a fabricated response. Exact descriptor wording/serialization ownership must be identified before live use; no source-discovery/schema factory implementation selected here.

Settled classifier/router facts are not AdapterRequest fields; there is no automatic insertion into its messages. D05 adds none. If a later approved prompt carries JARVIS contextual facts, document exact content/projection/version and comparison implications before scoring; do not invent it here. No mutable P2 store or full snapshot serialization, confirmation/permission token, result or expected canonical arguments is automatically sent to the model.

Minimum association: outer authoritative correlation plus this exact AdapterRequest and its build_request UTF-8 fingerprint bound by the trusted caller to the corresponding provider operation/response. Adapter has no standalone request ID. Do not invent one or use fingerprints as an attempt ID; D02/D07 must resolve retries.

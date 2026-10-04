# Inputs for the next provider/resource contract

D06 must decide and identify, without this task choosing any values:

| Required decision/input | D05 constraint / needed proof |
|---|---|
| Provider and model | Exact qualified requested identity plus actual selected runtime/model; no model echo as authority |
| Runtime host / local or external | Explicit endpoint/host/credential authority and privacy/call approval; no assumption of Hermes/Ollama/cloud |
| Resource ownership | Shared legacy/model lifecycle, in-flight load/unload, concurrency/resource isolation; no change to legacy response |
| Runtime limits | Context/quantization/concurrency/budget/timeout where applicable; no numeric values chosen here |
| Tool-execution isolation | Proposal generation only; no autonomous agent/tool loop, handler/external mutation or descriptor-as-execution authority |
| Complete response definition | Native response/stream completion, correlation to this request; partial body/chunks are not completed output |
| Native request map | Faithful projection of canonical build_request model/turn/messages/tools; outer turn identity preserved even when wire omits it |
| Native response map | Versioned faithful final content/all proposal data -> exact canonical text/proposals; any native argument-string decoding must reject duplicates/nonfinite/type ambiguity before preserving values; no expected-binding injection, filtering/semantic repair or reasoning leakage |
| Prompt/history/schema source | JARVIS-owned explicit tuples with current envelope material demonstrably represented; model-visible descriptor scope/provenance reviewed, no automatic binding-derived proposal |
| Provider identity / capture evidence | JARVIS-observed selected backend/request->response chain; optional native identifiers/fingerprints only with a defined safe capture unit |
| Availability / failure authority | Preserve no fake zero/no automatic alternate model; failures explicitly accounted and legacy unaffected |
| Evidence handoff | Supply settled origin/provider/normalizer facts for future controller collection, outside D03/D04 exact schemas |
| Retry/cancellation overlap | Enumerate any inherited SDK/transport retry; D02/D07 determines attempt selection/overload, not guessed by D06 alone |

Read actual legacy llm_client.py recovery/audio/audit/model-selection behavior before proposing reuse. Its existing retries and deep_reasoning model substitution do not establish a shadow policy. Current adapter has no transport/wire normalizer, and BindingProjection has no model-descriptor factory. D06 must not activate a provider merely by finishing its contract. D07/D10 and exact non-activation/test review remain mandatory before implementation.

The original packet's historical Granite/legacy candidates are references for a later decision, not choices or call authorization here. No provider/model inventory query, installation, quantization/context/resource selection or credential access is performed.

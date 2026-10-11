# Legacy resources: source facts versus effective state

**LEGACY_EFFECTIVE_ENDPOINT=UNVERIFIED**. No private environment file or process environment was read. Config/source evidence cannot resolve a possible environment override in the already-running service.

| Component | Reviewed source/config fact | Status for V3 |
|---|---|---|
| Main legacy model | YAML qwen3-nothink | not qualified for a live V3 responder |
| Legacy router | YAML gemma3:4b; IntentRouter can generate | separate profile, lease, bounds and failure contract required |
| Legacy endpoint | YAML http://localhost:11434; config supports JARVIS_OLLAMA_BASE_URL | effective endpoint unknown; may differ from .200 |
| Model selection | ComplexityRouter varies model and 80/150/700 token choices | not inherited; fixed approved bindings required |
| Legacy client | up to four attempts, 600s HTTP timeout, optional streaming/error speech | incompatible defaults excluded from adapter |
| Prompt/context | procedural-memory context, action-tag instructions | explicit audited prompt/memory policy unresolved |
| Operational path | `_process`, `_process_stream`, registry/confirmation/comms/TTS | inaccessible from candidate bounded adapter |
| Granite | .200:11434, hermes-candidate-granite41-30b-q3km-64k, qualified profile | metadata pinned only; no real endpoint contacted |

Potential resources are (effective legacy endpoint, router model), (effective legacy endpoint, responder model), and (Granite endpoint, Granite alias). Equal host/endpoint values do not collapse model qualification or lifecycle risk. D06's old recorded legacy loopback endpoint does not grant a router/responder generation lease.

The operator must later authorize a source-bound nonsecret endpoint/model attestation or a reviewed private-runtime metadata facility exposing only those values. Do not dump environment variables, print private env files or paste credentials to resolve it. Confirm whether legacy and Granite share Ollama or distinct hosts, inventory each endpoint's actors, then approve each exact resource and profile. No guessed endpoint/default fills missing bindings.

# Human-only effective provider/model attestation — pending

Effective legacy endpoints, immutable gemma3:4b/qwen3-nothink identities and physical relationship to Granite remain UNVERIFIED. localhost:11434 in YAML is not effective runtime proof. No protected production environment was opened. Granite retains its frozen alias/profile but current host/model identity needs independent verification.

## Minimal nonsecret endpoint read

Source app/config.py uses **JARVIS_OLLAMA_BASE_URL**. Older OLLAMA_BASE_URL-only prose is incomplete. Source precedence: config.yaml models.ollama_base_url overridden by nonempty JARVIS_OLLAMA_BASE_URL. Module import calls load_settings and can validate/log unrelated fields; do not import the app/loader just to attest endpoint.

1. Through trusted human Core access record HEAD and SHA256 of config.yaml, app/config.py, app/brain/llm_client.py, router.py, complexity_router.py, Modelfile.nothink and skills.md. Privately read only approved nonsecret model/router/main/endpoint/context fields. Obtain paths only with systemctl --user show jarvis.service -p EnvironmentFiles -p FragmentPath -p DropInPaths. Never print Environment/raw units/drop-ins.
2. Human privately traces that exact key through approved manager environment, EnvironmentFile and wrappers with correct precedence. No file copy, protected contents or /proc environment dump. V2 is stopped: this yields CONFIGURED_LAUNCH_RECONSTRUCTION, not a running process attestation. Do not restart V2. Future V3 CLOSED bootstrap requires an approved minimal accessor after its actual loader, before provider access.
3. Accessor output allowlist: source/config/loader hashes, origin(CONFIGURED_LAUNCH_RECONSTRUCTION or RUNNING_CLOSED_RUNTIME), endpoint_override_present boolean, router and responder scheme/host/port/model, invocation and UTC. Inspect only exact endpoint/config keys privately. Validate URL before emission; reject userinfo/password/query/fragment/unexpected path/scheme/port/host with fixed error code, never print original URL/exception. No full environment or secret hashes. Do not accept app Bearer as authority to inspect arbitrary settings. This is a future human-reviewed interface, not installed by Gate6H.
4. Trace each endpoint through trusted namespace/DNS/proxy/container/forwarding metadata to actual Ollama process, VM and GPU domain. Resolve localhost in the serving process network namespace, not Nexus. Bind router/responder separately even if current source shares base URL. Include route-retargeting actors; unresolved stays UNVERIFIED.

## Exact immutable model method, metadata only

On independently attested serving host, human privately reads ollama list and ollama show --modelfile EXACT_NAME for gemma3:4b, qwen3-nothink and frozen Granite. Keep only approved Modelfile SHA256/parameter lines. List aliases/abbreviated IDs are insufficient. Obtain full manifest digest from protected actual model-store manifest or reviewed metadata-only /api/tags accessor; validate tool behavior against installed-version docs first. Never call /api/chat, /api/generate, run/pull/create/stop/load/unload.

Verify full manifest SHA256 and every referenced config/weight/adapter blob against its SHA256 in the actual service's protected model store. Check symlink/owner/store provenance. Record full digest/algorithm, blob-verification result, Modelfile digest and runtime/model version. Export no weights or full SYSTEM/Modelfile content. Hash identity does not prove model authorship, safety or current behavior; bind the serving process to protected store and inventory all alias/store writers.

For qwen3-nothink verify installed num_ctx8192 and no-think/SYSTEM behavior against source Modelfile; X4 pending until done. For gemma verify inherited responder context/default, distinct from classifier explicit4096, for X5. Installed think:false/num_ctx/num_predict/keep_alive behavior requires later bounded StageG, not unauthorized generation now.

Human privately reads only approved Ollama policy values OLLAMA_KEEP_ALIVE, OLLAMA_CONTEXT_LENGTH, OLLAMA_MAX_LOADED_MODELS, OLLAMA_NUM_PARALLEL, OLLAMA_FLASH_ATTENTION, OLLAMA_KV_CACHE_TYPE. Record unset explicitly, precedence/version limitations. No full Environment/unit/container inspect dump.

Record actual legacy and Granite host/service/runtime/GPU/VRAM/lifecycle relationships. Different aliases/ports can share one service/GPU. Feed HUMAN_ATTESTED topology only after independent review; fixtures never count. Unverified full identity/effective endpoint/topology blocks provider-capable installation and real pilot. SSH bypass/automatic enrollment prohibited.

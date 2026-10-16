# Legacy identity attestation design

Gate 6F design only. **Not run on production.** `LEGACY_EFFECTIVE_ENDPOINT=UNVERIFIED`.

## Why it is needed

Source says `http://localhost:11434`, `gemma3:4b`, `qwen3-nothink`; the protected environment may override the endpoint, and no Ollama process listened on Core at entry. The local client cannot bind a model alias to a digest. Gate 6F therefore cannot establish the effective endpoint, models or digests without a new privileged interface, and leaves them unresolved.

## Procedure (human, separately authorized)

Run by the operator through already-trusted access. The output must contain **only** the fields below.

1. **Effective endpoint, Core side.** As the service user, without printing the environment:
   `systemctl --user show jarvis.service -p EnvironmentFiles` (paths only). The operator opens the referenced file privately and records **only** whether `OLLAMA_BASE_URL`/`models.ollama_base_url` is overridden, plus the resulting scheme://host:port. No other key, value or token is copied.
2. **Source/config identity.** `git -C /home/jarvis/JARVIS rev-parse HEAD`, `sha256sum config.yaml Modelfile.nothink skills.md`.
3. **Model identity, on the host serving that endpoint** (from its trusted console, see AI-HOST-TRUST-RUNBOOK):
   `ollama list` (name + ID columns) and `ollama show --modelfile <name> | sha256sum` for `gemma3:4b`, `qwen3-nothink`, and the Granite model. Record: name, `ollama list` ID, Modelfile digest, and the `num_ctx`/`SYSTEM` presence lines from the Modelfile for `qwen3-nothink`. `ollama show` reads metadata only; it does not generate.
4. **Server options relevant to the contract.** Ollama version (`ollama --version`), and **only** these variable names and values from the server unit: `OLLAMA_KEEP_ALIVE`, `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_MAX_LOADED_MODELS`, `OLLAMA_NUM_PARALLEL`, `OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE`. The operator reads them; no dump is copied.
5. **Record origin and limits.** Who ran it, on which console, UTC time, and the statement "metadata only; no generation, load or unload".

## Output schema (nonsecret)

```json
{"attestation":"G6F-LEGACY-ID-1","utc":"…","operator":"…","origin":"proxmox-console|trusted-ssh",
 "core":{"head":"…","config_sha256":"…","modelfile_nothink_sha256":"…","skills_sha256":"…",
         "endpoint_override":"none|present","effective_endpoint":"http://host:port"},
 "server":{"host_identity":"…","service_identity":"…","gpu_domain":"…","ollama_version":"…",
           "keep_alive":"…","context_length":"…","max_loaded_models":"…","num_parallel":"…"},
 "models":[{"name":"gemma3:4b","list_id":"…","modelfile_sha256":"…"},
           {"name":"qwen3-nothink","list_id":"…","modelfile_sha256":"…","num_ctx_line":"PARAMETER num_ctx 8192"}],
 "limitations":["ollama list ID is the local manifest digest; not a cryptographic proof of weights",
                "values reflect the time of reading only"]}
```

Never include API tokens, environment dumps, secret values, raw prompts or model output.

## How the candidate consumes it

The `server` fields become `HostAttestation(endpoint, host_identity, gpu_domain, service_identity, 'HUMAN_ATTESTED')` for `qualify_topology` (RESOURCE-AND-D06-OWNERSHIP). Model fields become the immutable-digest requirement in each legacy `StepContract` profile, still to be approved. A value that cannot be established stays `UNVERIFIED` and blocks release; it is never guessed.

# JARVIS Procedural Memory

- When asked about workshop projects, check local project files before searching the web.
- User prefers Python 3.11+ with type hints on backend code.
- For circuit debugging, check power rails first, then signal traces.
- Git checkpoints should keep unrelated local changes unstaged.
- Default workbench access should stay local-first and avoid cloud dependencies unless explicitly requested.
- When removing a tool, grep for all references: registry.py, server.py, router.py, filler_manager.py, health_check.py, config.py, config.yaml, config.yaml.example, any smoke/test files. StrictModel with extra="forbid" means YAML and Pydantic class must stay in sync or import fails.
- Phase 8 stubs report readiness only — never execute live unless the underlying dep is installed AND user has confirmed. Check config.safety.dry_run AND AVAILABLE flag before any live call.
- CLI harnesses (OBS, FFmpeg, Blender) live in app/tools/cli/__init__.py as a unified stub. No separate per-app files needed until live execution is approved. Use cli.execute({'action': 'status'}) to check binary availability.
- MCP client (app/tools/mcp_client.py) is a whitelist-only stub. Never add a server to the whitelist without explicit user approval. Priority order: playwright → github → obsidian → homeassistant.
- For complexity routing: route through complexity_router.py, never call qwen3:14b directly. Trivial (time, stats, simple facts) → gemma3:4b. Normal → qwen3-nothink. Deep (debug, design, "think through X") → qwen3:14b with thinking ON.
- Filler phrases must be played BEFORE any tool call >500ms. Use phrase_cache.get(key) + tts.speak() immediately after classifying the tool intent, before the tool executes.
- TTS rule: ALWAYS strip [laugh] [chuckle] [cough] before passing text to Kokoro or Piper. Only Chatterbox Turbo handles paralinguistic tags.
- Ollama env vars (set all 6 as Windows System vars, restart Ollama after): OLLAMA_KEEP_ALIVE=-1, OLLAMA_NUM_PARALLEL=2, OLLAMA_FLASH_ATTENTION=1, OLLAMA_KV_CACHE_TYPE=q8_0, OLLAMA_NUM_BATCH=512, OLLAMA_MAX_LOADED_MODELS=2.
- Dictation mode uses `voice.dictation_hotkey` and routes STT text to clipboard/type-out only. Do not send dictation transcripts through the brain pipeline, LLM, TTS, or raw-text audit logs.

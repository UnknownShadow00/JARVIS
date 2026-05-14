# JARVIS — Claude Code Project Context
> Read this file before writing code, files, or commands. Update "Current Status" at the end of every session.
> Detail moved out of this file: `docs/repos.md` (full repo verdicts), `docs/hermes_setup.md` (Hermes install), `docs/5090_migration.md` (5090 runbook), `config.yaml` (full config), `docs/content/episode_arc.md` (YouTube plan).

---

## What This Project Is

A local-first, fully autonomous AI assistant modeled on Tony Stark's JARVIS. Runs 100% on personal hardware — no API costs, no cloud, no subscriptions. Controls the PC, watches the screen and webcam, helps with coding and hardware building, runs assigned tasks autonomously, sends status updates via Discord/Telegram. Open-sourced on GitHub, documented on YouTube/TikTok. **The owner uses Claude Code as primary co-builder. You are that co-builder.**

---

## Hardware

| Device | Spec | Role |
|--------|------|------|
| Main PC | RTX 4070 Ti Super 16GB | Active |
| Server PC | RTX 5090 32GB | Not yet set up |
| Phone | Android/iOS | PWA via Tailscale |
| Meta Glasses | Ray-Ban Meta | Audio via paired phone |

**4070 Ti note:** Active model is `qwen3-nothink`. Hermes Agent can be installed via WSL2 NOW pointing at existing Ollama — do not wait for 5090.

---

## AI Model Stack (all via Ollama)

| Model | Role | VRAM |
|-------|------|------|
| qwen3-nothink | Primary brain, thinking OFF (daily use) | ~10GB |
| qwen3:14b | Deep reasoning only, thinking ON | ~10GB |
| qwen3:32b | Primary brain (5090 upgrade) | ~20GB Q5_K_M |
| qwen2.5-coder:14b | Coding (4070 Ti) | ~9GB |
| qwen2.5-coder:32b | Coding (5090 only) | ~20GB Q4_K_M |
| gemma3:4b | Intent router + trivial direct answers | ~3GB |
| qwen3-vl | Vision (screen + webcam) — requires Ollama 0.12.7+ | ~8GB Q4 |
| gemma4:e2b | Router upgrade candidate — benchmark on 5090 | ~2GB |

**Required Ollama env vars (set ALL before starting Ollama):**
```
OLLAMA_KEEP_ALIVE=-1
OLLAMA_NUM_PARALLEL=2
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_NUM_BATCH=512
OLLAMA_MAX_LOADED_MODELS=2
```
Caveats live in Known Risks (FLASH_ATTENTION regression, KV cache accuracy).

**5090 context window:** When migrating, set `num_ctx: 32768` in `Modelfile.nothink` and `config.yaml`. 8192 is the 4070 Ti default.

**Thinking control:** Either bake into Modelfile (`/no_think` in SYSTEM) or pass `options={"think": False}` per call in `llm_client.py`. Both work; Modelfile is the default, API flag toggles for `deep_reasoning` intent. Cap voice responses at `num_predict: 150`; remove cap for deep_reasoning and code generation.

### 3-tier complexity routing (`brain/complexity_router.py`)

| Tier | Model | When | Latency |
|------|-------|------|---------|
| Trivial | gemma3:4b — answers directly | Time, stats, simple facts | ~100ms |
| Normal | qwen3-nothink | All tool calls, standard queries | ~400ms |
| Deep | qwen3:14b — thinking ON | Debug, design, "think through X" | ~800ms |

---

## Agent Architecture (3 layers)

### Layer 1 — Custom FastAPI Brain (Phase 0-3 implemented; Phase 4+ explicit stubs/deferred)
- `app/server.py` — FastAPI WebSocket + REST (528 lines)
- `app/brain/llm_client.py` — Ollama streaming, retry, cancel token (276 lines)
- `app/brain/router.py` — Gemma3 4B intent classifier <50ms (238 lines). Intent classes: `respond / tool / memory / vision / confirm / deep_reasoning`
- `app/brain/prompts.py` — personality enforcement
- `app/tools/registry.py` — modular tools, one file each

### Layer 2 — Hermes Agent (NousResearch, 23k+ stars)
Self-improving Kanban multi-agent board, 19 messaging platforms, autonomous Curator, MCP support, cron. Install via WSL2 pointing at existing Ollama. **Kanban replaces `task_queue.py` when active**; `/confirm/{id}` endpoint maps to Kanban unblock. Full install commands in `docs/hermes_setup.md`. Specialist profiles: `jarvis-researcher` (search/web/memory/rag/files), `jarvis-coder` (terminal/files/git/shell), `jarvis-reviewer` (files/web/memory). Plugins: `hermes-labyrinth` (observability — always install), `hermes-workspace` or `hermes-webui` (UI).

### Layer 3 — OpenJarvis (Phase 4+ only, after 500 real interactions)
Stanford SAIL skill optimizer. Trace logging already wired from Phase 0. `audit.jsonl` is in the right format for `jarvis optimize skills`. Public catalog has Hermes skills + 13,700+ OpenClaw community skills (agentskills.io standard).

---

## Tech Stack — Reference

### Voice Pipeline
```
Wake word  → OpenWakeWord
STT        → faster-whisper, large-v3-turbo (216x real-time, ~80-120ms on 4070 Ti)
             Alt: distil-large-v3 (6x faster, English only, ~1% WER diff)
VAD        → webrtcvad
TTS (1)    → Chatterbox Turbo                PRIMARY (CUDA, voice clone, paralinguistic tags)
TTS (2)    → Kokoro-82M                       FALLBACK (CUDA, Apache 2.0, no clone)
TTS (3)    → Piper TTS                        EMERGENCY CPU (never fails)
SFX        → pygame
```

**STT config (in `stt.py`):** `large-v3-turbo`, `device="cuda"`, `compute_type="float16"`, `vad_filter=True`, `min_silence_duration_ms=300`, `speech_pad_ms=100`, `beam_size=1`, `language="en"`, `condition_on_previous_text=False`.

**TTS rules:**
- Chatterbox Turbo uses `ChatterboxTurboTTS.from_pretrained(device="cuda")` with `audio_prompt_path=voice_ref.wav`
- **STRIP** `[laugh]` `[chuckle]` `[cough]` before passing text to Kokoro or Piper — only Chatterbox Turbo handles them
- Pre-generate `CACHED_PHRASES` at boot in `voice/phrase_cache.py` (right_away, on_it, done, working, looking, searching, understood, complete, listening, no_connection, cannot, error, confirm_delete, confirm_send, good_morning) — serve from memory at 0ms
- `voice/filler_manager.py` plays cached filler immediately when a tool call >500ms starts (web_search→searching, browser_use→on_it, shell→working, vision→looking, cad→working, default→on_it)

**Partial transcript processing:** When ≥4 words transcribed, call `router.quick_classify(partial_text)`. If intent is high-confidence (tool_call, shutdown), start `context_prefetch()` early — saves 500-1000ms for ~60-70% of interactions.

### Browser & Desktop Automation
- `browser.py` — simple URL/app open (Level 0, built)
- `browser_use.py` — full Chrome agent with real cookies/sessions (Level 1) — `[ACTION:BROWSER_AGENT:task]`
- Playwright MCP via FastMCP — accessibility-tree based, no screenshots needed
- CLI-Anything harnesses (`pip install cli-anything-hub`) — JSON-output CLIs for OBS, FFmpeg, Blender as Level 1 tools in `app/tools/cli/`

### Workshop Tools (from nazirlouis/ada_v2)
- `app/tools/cad.py` — build123d → STL → OrcaSlicer CLI → 3D printer via mDNS. `[ACTION:CAD:design description]`. **ALWAYS Level 2** — confirm before printing. Note: OrcaSlicer install currently skipped — CAD/printing not in scope right now.
- `app/tools/kasa.py` — TP-Link Kasa smart home, local network only, mDNS discovery. Level 0 reads, Level 1 writes. `[ACTION:KASA:device:command]`

### MCP Client Layer (`app/tools/mcp_client.py`)
FastMCP wrapper. Whitelisted servers only — never auto-connect to untrusted MCP servers.
Priority order: `playwright` (`npx @playwright/mcp`), `github` (`npx @modelcontextprotocol/server-github`), `obsidian` (`npx obsidian-mcp /path/to/jarvis-vault`), `homeassistant` (`http://homeassistant.local:8123/mcp` if HA running).

### Desktop Control
- PyAutoGUI (mouse/keyboard), mss (fast screenshots), OpenCV (webcam)

### Vision
YOLOE via Ultralytics, DepthAnything V2, MediaPipe hand-tracking stub.

### Memory & Knowledge
- **Mem0 v1.0+** — episodic + procedural. Use `memory_type="procedural"` for "how to do things." Use `filters={"project": "...", "type": "..."}` to scope queries. Configure project-level `inclusion_prompt` / `exclusion_prompt` (NEVER remember passwords, API keys, temp debug steps).
- **ChromaDB** — semantic/document RAG at `./data/chroma`
- **`skills.md`** — procedural memory file, read at session start and injected into system prompt. Claude Code should grow it after each session.
- **Graphiti** (Phase 4+) — temporal knowledge graph, `pip install graphiti-core` + Neo4j. MCP server available.
- **Obsidian vault** (`jarvis-vault/`, Phase 4+) — JARVIS writes `[[linked]]` notes, accessible via obsidian-mcp. Keep separate from any personal vault.

**Context pre-fetch (`boot.py`):** `asyncio.gather` GPU temp, task count, last active project, recent errors. Morning report reads from `SESSION_CONTEXT` instantly.

### Backend
FastAPI + uvicorn, httpx (Discord/Telegram REST), APScheduler (cron, replaced by Hermes Kanban when active), duckduckgo-search, Tailscale.

### Frontend
Electron (always-on-top HUD), React+Three.js+Vite (hologram for projector), PWA (mobile via Tailscale).

### Phase 7 Cinematic
Unreal Engine 5 + MetaHuman, NVIDIA Audio2Face-3D, lip sync patterns in `ue5_bridge.py`.

---

## Folder Structure

```
jarvis/
  CLAUDE.md  README.md  config.yaml  Modelfile.nothink  requirements.txt
  docker-compose.yml  skills.md

  app/
    main.py  server.py  boot.py  config.py
    brain/        llm_client.py  router.py  complexity_router.py  prompts.py
                  response_cleaner.py  cancel_token.py  kill_switch.py
                  morning_report.py  context_prefetch.py
    voice/        wake_word.py  vad.py  stt.py  tts.py  audio_stream.py
                  sounds.py  phrase_cache.py  filler_manager.py
                  push_to_talk.py  error_recovery.py
    tools/        registry.py  browser.py  browser_use.py  mcp_client.py
                  cad.py  kasa.py  home_assistant.py  files.py  shell.py
                  apps.py  web_search.py  system_stats.py  calendar.py
                  computer_use.py
                  cli/  (obs.py  ffmpeg.py  blender.py)
    computer/     screenshot.py  vision.py  mouse_keyboard.py  verifier.py
                  safety.py  gesture.py  yolo_detector.py
    memory/       memory_client.py  rag_client.py  procedural.py
                  project_indexer.py
    agent/        task_queue.py  scheduler.py  reporter.py  sensor_store.py
    comms/        discord_bot.py  telegram_bot.py  ue5_bridge.py  audio2face.py
    network/      tailscale.py
    logs/         audit.py

  frontend/   electron/  pwa/  hologram/
  scripts/    install.py  install.ps1  switch_models.py  sensor_node.py
  tests/      60 files, e2e/  stress/  perf/
  docs/       5090_migration.md  hermes_setup.md  repos.md  content/
```

---

## config.yaml — Key Sections (full file is the source of truth)

- **models** — main/main_thinking/main_trivial/coder/router/vision + `ollama_base_url`, `num_ctx`
- **safety** — `approval_mode` (safe/balanced/strict), `dry_run`, `confidence_threshold: 0.75`
- **voice** — wake_word, stt_model, tts_engine, voice_clone_path, piper paths, push_to_talk_key, tts_cache_enabled, filler_phrases_enabled
- **routing** — trivial/normal/deep models, `partial_transcript_words: 4`
- **boot** — enabled, music_file, status_report, prefetch_context
- **server** — host, port 8000, websocket_path `/ws`
- **memory** — mem0_enabled, mem0_procedural, chromadb_path, projects_index_path, skills_file
- **workshop** — cad_enabled, kasa_enabled, printer_ip, printer_profile
- **mcp** — enabled + servers list (playwright/github/obsidian/homeassistant)
- **comms** — discord/telegram enabled + tokens
- **logging** — audit_log, level

Never hardcode model names, ports, or paths — always read from `config.yaml`.

---

## JARVIS Personality Rules (ENFORCE IN ALL PROMPTS)

### Core rules
- Always address user as "sir"
- Spoken responses: 1 sentence ideal, 2 max. NEVER 3.
- No markdown, no bullets, no code blocks in voice responses
- Never break character. Never say "as an AI"
- Action tags appended after speech: `[ACTION:TYPE:PARAMS]`
- When unsure: ask instead of acting on Level 2+ actions

### Banned phrases
"Absolutely" / "Great question" / "I'd be happy to" / "Of course" / "How can I help" / "Is there anything else" / "I apologize" / Never start a sentence with "I"

### Good examples
- "Right away, sir."
- "Done, sir. The endpoint is live on port 8000."
- "Afraid that datasheet is not in my index, sir — searching now."
- "That would delete the project folder, sir. Shall I proceed?"
- "On it, sir. [chuckle] That's the third time this week."
- "Designing that bracket now, sir. Should be on the printer in about sixty seconds."

### Action format (unified, no exceptions)
```
[ACTION:BROWSER:https://google.com]
[ACTION:BROWSER_AGENT:log into github open PR 42]
[ACTION:APP:vscode]
[ACTION:FILE:read:/path/to/file]
[ACTION:SHELL:npm run dev]
[ACTION:MESSAGE:discord:Task complete, sir]
[ACTION:AGENT:deep_research:query]
[ACTION:VISION:screen]   [ACTION:VISION:webcam]
[ACTION:HERMES:task_name:params]
[ACTION:CAD:40x20mm bracket two M3 holes]
[ACTION:KASA:workshop_light:on]
[EMOTION:neutral|success|concern|thinking]
```

**Paralinguistic tags** (Chatterbox Turbo ONLY — strip before Kokoro/Piper): `[laugh]` `[chuckle]` `[cough]`

---

## Action Safety Levels (enforce in `safety.py` and every tool)

| Level | Name | Confirmation | Examples |
|-------|------|--------------|----------|
| 0 | Safe | Never | Answer questions, open app, web search, system stats, read Kasa state |
| 1 | Reversible | Only if confidence < 0.75 | Move file, open URL, browser agent, toggle Kasa, CLI harness read |
| 2 | Risky | Always confirm | Delete files, send messages, install packages, CAD+print, edit code, git commit |
| 3 | Blocked | Never automatic | Spend money, delete project folders, admin scripts, send private data |

---

## Coding Conventions

- **Language:** Python 3.11+ backend, TypeScript/React frontend
- **Every tool** in `tools/` = standalone file with single `execute(params)` function
- **Safety level** declared at top of every tool file: `SAFETY_LEVEL = 0`
- **Every action** uses `[ACTION:TYPE:PARAMS]` format — no exceptions
- **AVAILABLE flag** — every optional dep uses module-level try/except. Server boots without Chatterbox/YOLO/Mem0/Audio2Face/build123d installed.
- **Audit everything** — every tool call writes to `logs/audit.jsonl`
- **Config-driven** — never hardcode model names, ports, or paths
- **Streaming first** — TTS begins before LLM finishes
- **Cancel token** — thread-safe singleton in `cancel_token.py`, stops LLM + TTS mid-flight
- **Dry-run safe** — every tool checks `config.safety.dry_run` before executing
- **Error recovery** — failures trigger verbal TTS error, never silent fail
- **No breaking changes** — working phases cannot be broken by new code
- **Parallel tool calls** — `asyncio.gather()` for independent values
- **Filler before slow tools** — play cached filler phrase before any tool call >500ms
- **Complexity routing** — never send trivial queries to Qwen3; route through `complexity_router.py`
- **Match existing file style** — don't introduce new patterns inside an existing file

---

## Phase Build Order

```
Phase 0  Core Brain         ✅  FastAPI + router + tools + audit + kill switch
Phase 1  Voice + Boot       ✅  Wake word + STT + TTS + streaming + morning report
Phase 2  Tools & Desktop    ✅  App launch + file ops + web search + shell + stats + HUD
Phase 3  PC Control         ✅  Safety gate + screenshot + vision + gesture
Phase 4  Workshop Brain     STUBBED  Vision path exists; Mem0, ChromaDB RAG, YOLO/depth deferred
Phase 5  Autonomous Agent   PARTIAL  Local task queue/scheduler + comms stubs; Hermes not active
Phase 6  Multi-Device       PARTIAL  Tailscale status + PWA exist; remote access disabled by default
Phase 7  Cinematic          STUBBED  UE5/Audio2Face/hologram/voice-clone hooks require external runtimes
Release  Prep               PARTIAL  README/status/docs updated; deployment validation still pending
Phase 8  Integration stubs  PARTIAL  MCP, browser_use, kasa, cad, cli/, project_indexer remain explicit stubs
```

---

## Known Risks — Watch For These

1. **Model cold-load** — `OLLAMA_KEEP_ALIVE=-1` must be set before anything else
2. **Self-triggering loop** — `is_speaking=True` mutes wake word during TTS (in `wake_word.py`)
3. **qwen3-nothink is the default** — `qwen3:14b` with thinking is ONLY for `deep_reasoning` intent. Never the default.
4. **FLASH_ATTENTION regression** — some Qwen3 builds slow down with `OLLAMA_FLASH_ATTENTION=1`. Debug with `OLLAMA_DEBUG=1`, verify all layers on GPU. Fall back to `0` if needed.
5. **Qwen3-VL name** — it's `qwen3-vl`, NOT `qwen3.5-vl`. Requires Ollama 0.12.7+.
6. **Hermes on 5090** — needs `qwen3:32b` + 24GB VRAM for full power. WSL2 + 14B works today.
7. **Chatterbox paralinguistics** — strip `[laugh]`/`[chuckle]`/`[cough]` BEFORE Kokoro/Piper.
8. **MCP security** — whitelist servers in FastMCP config. Never auto-connect to untrusted.
9. **CAD + printing safety** — `SAFETY_LEVEL = 2` in `cad.py`. Always confirm. Never print without verifying STL first.
10. **KV cache quantization** — `q8_0` saves ~2GB VRAM. If accuracy regresses, try `q4_0`.
11. **Whisper VAD** — `vad_filter=True` can clip speech with very short pauses. Tune `min_silence_duration_ms` if words get cut.
12. **webrtcvad on Windows** — needs MS C++ Build Tools. `winget install --id Microsoft.VisualStudio.2022.BuildTools` then retry pip.
13. **Piper model URLs** — original install pointed to a deleted community HF model. Use official rhasspy:
    - `https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx`
    - `https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx.json`
    - Save both to `models/`, verify `config.yaml` paths.
14. **`wake_word.listen()` return type** — returns `b''` (empty bytes) on timeout, NOT `bool`. Tests asserting `result in (True, False)` will fail. Correct assertion: `isinstance(result, (bool, bytes))` — or fix `wake_word.py` to return `False` on timeout. Read the spec first.

---

## Boot Sequence Spec (Phase 1 — complete)

T+0.0s login → `boot.py` starts (Task Scheduler) | T+0.1s context pre-fetch (parallel) | T+0.5s Electron HUD launches | T+1.0s boot music (4s, pygame.mixer) | T+2.5s text crawl | T+5.0s arc reactor pulses, HUD loads via WebSocket | T+5.5s morning status report TTS | T+8.0s `is_listening=True`, wake word active.

**Morning status report template:** "Good [morning/afternoon/evening], sir. The time is [TIME]. All systems operational. GPU temperature [TEMP] degrees. You have [N] tasks pending. Last active project: [PROJECT_NAME]. Shall I continue where we left off?"

**Sound assets needed (manual):** `boot_intro.wav`, `listening.wav`, `working.wav`, `done.wav`, `error.wav` in `assets/audio/`.

---

## Performance Targets

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| STT latency | ~300-400ms | ~80-120ms | Whisper large-v3-turbo |
| Simple query total | ~1200ms | ~200ms | Gemma3 direct + cached phrase |
| Tool call perceived wait | ~2-3s silence | ~200ms + filler | Phrase cache + filler manager |
| Qwen3 first token | ~800ms | ~400ms | qwen3-nothink Modelfile |
| TTS first audio | ~200ms | 0ms cached / ~100ms new | Phrase cache + Chatterbox Turbo |
| VRAM headroom (4070 Ti) | ~3GB | ~5GB | KV cache q8_0 |

---

## Current Status

```
Phase:        Pre-server stabilization complete. Phase 0-3 usable; Phase 4+ stays explicit stubs/deferred.
Tests:        pytest 320 passed / 0 skipped. tool_readiness_smoke 10/10. readiness_report all required PASS.
Hardware:     4070 Ti Super 16GB active. 5090 not yet set up.
Active model: qwen3-nothink (Modelfile.nothink); qwen3:14b for deep_reasoning; qwen3-vl for vision.
Git:          Dirty working tree; review and commit after current stabilization pass.
GitHub:       UnknownShadow00/JARVIS, main branch.

Completed 2026-05-14 session:
  - Cleared last skipped e2e test by exporting app.brain.router.classify_intent
    and aliasing AuditLog = AuditLogger in app/logs/audit.py
  - Killed datetime.utcnow deprecation in app/comms/audio2face.py
    (datetime.now(timezone.utc) for both build_audio_event and build_viseme_event)
  - Refactored app/server.py 827 -> 740 lines by moving _tool_params,
    _extract_app_name, _strip_wake_word, _is_cancel_command into
    new app/brain/tool_params.py (under the 800-line global rule)
  - Started ollama serve; readiness_report now all required PASS
  - Pulled qwen3-vl model (vision now end-to-end ready)
  - Real HTTP smoke: uvicorn -> /health, /health/tools, /chat respond,
    /chat system_stats all returned 200 with real Ollama-backed replies
  - No hardcoded secrets in repo (regex scan clean)

Completed prior sessions:
  - docs/repos.md, docs/hermes_setup.md
  - Open Interpreter fully removed and replaced by shell + browser_use + MCP
  - All Phase 8 stubs verified working
  - skills.md procedural patterns
  - Ollama KEEP_ALIVE + NUM_PARALLEL set

Pending — manual/no code:
  - Set 4 missing Ollama env vars (FLASH_ATTENTION, KV_CACHE_TYPE, NUM_BATCH,
    MAX_LOADED_MODELS) as Windows System vars — requires Administrator shell
  - Restart Ollama after env var changes
  - voice_clone_path — record 10s WAV, set in config.yaml
  - UE5 MetaHuman Plugin + Audio2Face-3D connection
  - 5090 setup — follow docs/5090_migration.md when hardware arrives

Remaining install work:
  - Hermes Agent: WSL2 install, init kanban, install workspace + labyrinth plugins,
    clone mission-control UI, clone wondelai/skills

Phase 4+ queue (after 500 interactions):
  - Graphiti + Neo4j temporal knowledge graph
  - Obsidian vault + obsidian-mcp
  - Embedding-based tool selection second pass in router.py
  - Dictation mode in push_to_talk.py
  - OpenJarvis / hermes-agent-self-evolution skill catalog sync

Notes:
  dry_run=false. Backend binds localhost by default. Browser-use, python-kasa,
  build123d, FastMCP, Electron deps, and PWA icon are optional/deferred surfaces.
  OrcaSlicer skipped — 3D printing not in scope.
  Open Interpreter removed entirely (blocked on Python 3.13/tiktoken; replaced by
  shell.py + browser_use.py + MCP/Playwright). Do not re-add.
  CI: pytest on every push, ignores e2e/stress/perf/hardware markers.
  5090 migration: scripts/switch_models.py --profile 5090 after GPU swap.

Content arc: docs/content/episode_arc.md. EP1-7 scripted. EP8=5090. EP9=Hermes
full power. EP10=launch. Demo moments to add: CAD voice-to-print, Kasa workshop
lights, complexity routing live, Kanban multi-agent dashboard.
```

> Update this section at the end of every Claude Code session.
> Format: what was built, last test run, blockers, next session starting point.

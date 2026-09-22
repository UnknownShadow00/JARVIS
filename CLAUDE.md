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
Phase:        Pre-server local validation nearly complete. Phase 0-3 usable; Phase 4+
              early track landed feature-flagged OFF (dictation, Obsidian, embedding
              routing, Graphiti); rest stays explicit stubs/deferred.
Tests:        pytest 350 passed / 0 skipped (workspace clone). Production
              /home/jarvis/JARVIS: 5245 passed / 11 deselected / 0 failed.
              pre_server_readiness 6/6 PASS
              (pytest, pip-audit, pip check, npm audit, readiness report, tool smoke).
Hardware:     4070 Ti Super 16GB active. 5090 not yet set up.
Active model: qwen3-nothink (Modelfile.nothink); qwen3:14b for deep_reasoning; qwen3-vl for vision.
Git:          Clean, synced with origin/main.
GitHub:       UnknownShadow00/JARVIS, main branch.

Completed 2026-07-02 session (remote, unattended):
  - Verified all 6 Ollama env vars set at user scope and picked up by ollama serve
    (FLASH_ATTENTION=1, KV_CACHE_TYPE=q8_0, NUM_PARALLEL=2, NUM_BATCH=512,
    MAX_LOADED_MODELS=2, KEEP_ALIVE=-1). Admin-shell blocker no longer applies —
    user-scope vars cover user-run Ollama. Pending env-var item CLOSED.
  - Live web search smoke PASS (real DuckDuckGo results via web_search.execute)
  - Live vision smoke PASS (qwen3-vl described live screen capture accurately)
  - Fixed new high-severity undici advisory in frontend/electron via
    npm audit fix (lockfile-only, 0 vulnerabilities after)
  - Full pre_server_readiness re-run: all 6 checks PASS

Pending — manual/needs user present:
  - Attended live voice loop test (wake/PTT -> STT -> response -> TTS -> kill switch)
  - Decide browser-use posture: keep plan-only vs live behind Level 2 confirm gates
  - voice_clone_path — record 10s WAV, set in config.yaml
  - UE5 MetaHuman Plugin + Audio2Face-3D connection
  - 5090 setup — follow docs/5090_migration.md when hardware arrives
  - Graphiti vs live Neo4j — needs Docker host (defer to server)

Remaining install work:
  - Hermes Agent: WSL2 install, init kanban, install workspace + labyrinth plugins,
    clone mission-control UI, clone wondelai/skills

Agent Execution Contract v1 — control-plane track (2026-09-18/19, production
/home/jarvis/JARVIS, all passive and UNWIRED; execution.mode stays legacy):
  Contract FROZEN (13B10D) and the production integration plan READY (13B11A).
  Phases P0-P3 now landed, one focused commit each, every one adding files only:
    521969e  P0  app/execution/types.py + execution.mode (defaults legacy)
    eb4c5db  P1  audit_events.py + correlation.py
    b9a557b  P2  provenance.py
    e743243  P3  canonicalize.py
    a69f33e  P3  lane.py
    d4eb171  P3  classifier.py
    03cab49  P3  router.py
  Nothing in app/ imports any of them; the legacy path in app/server.py and
  app/brain/router.py is byte-identical throughout. pytest 350 -> 2113 passed,
  golden unchanged at 12/20 with the same eight failures at every step, legacy
  behavioural probe byte-identical (fc68a0b0...). Evidence bundles under
  /home/jarvis/.hermes-poc/evidence/task13b11{b..h}-*, each sealed with SHA256SUMS.
  Method to keep: freeze the decision table and hash it BEFORE writing the module.
  Next approved unit: P4 permission foundation (NOT started). Do not wire any of
  P0-P3 into the live request path without a separate authorization.
  P4 entry criterion packaged 2026-09-19: tasks/task13b11i-review/
  PERMISSION_MATRIX_REVIEW.md — 35-row permission matrix over the real registry,
  9 current-vs-contract mismatches (5 declared + 4 new), 10 operator decisions
  D-01..D-10. Operator signed off all ten, so P4 landed in two commits:
    52c5da5  P4  permissions.py — 40-row signed-off matrix, policy version "1",
                 tightening-only approval_mode, fail-closed; passive and unwired
    c321cb8  P4  confirmation.py — 7-state machine (plan's exact set, no resting
                 CONFIRMED), 12-field binding, in-memory ConfirmationStore,
                 expiry as data with an injected clock; passive and unwired
  pytest 2113 -> 2575 -> 2892, golden still 12/20 same eight, probe still
  fc68a0b0, all 24 critical files byte-identical each time.
  PENDING -> EXECUTING is deliberately a wall: confirm() validates session,
  state, freshness and all 12 binding fields, then raises
  ConfirmationDispatcherUnavailable (a NotImplementedError) without advancing
  the record. SUCCEEDED/FAILED have no public route. No TTL value is frozen —
  plan §6 proposes them, no operator signed them.
  P4 is structurally complete. P5 landed in one commit:
    a0cc4d3  P5  dispatch.py — the trusted execution boundary and the only
                 constructor of a TrustedToolResult; seven authority gates, an
                 injected executor with no default, a structural confirmation
                 authority; passive and unwired. confirmation.py gained the three
                 edges the frozen graph reserves for it (claim_for_dispatch,
                 settle_success, settle_failure), each guarded, confirm() still a
                 wall, still 0 try blocks.
  pytest 2892 -> 3247, golden still 12/20 same eight, probe still fc68a0b0,
  all 23 critical files byte-identical, registry.call still 4 callers.
  A 150-cell dispatch matrix was hashed before the module existed
  (ede846eb...); 10 cells reach an executor, 140 refuse with executed=false.
  Five cells failed on the first run and the frozen table won — contract §12.1
  requires a gated action with no approval to present as CONFIRMATION_REQUIRED.
  A timeout leaves the confirmation record in EXECUTING (no frozen edge, not
  replayable) — recorded as deferred. No executor is configured anywhere in
  production; the legacy _pending_confirmations path in app/server.py is
  byte-identical and still owns every real confirmation.
  P6 attempted as 13B11L and BLOCKED at its own section-32 decision gate. No
  module written, no production commit, production byte-identical at a0cc4d3.
  Finding: classifier.ACTION_VERBS (44) did not cover router.UNSUPPORTED_VERBS
  (41). 20 of 41 unsupported verbs -- backup build clear commit download fix
  flush merge modify patch pull reset restore revert roll rollback rotate scale
  upgrade upload -- were classified OTHER and landed on Lane.CONVERSATIONAL,
  where contract 4.2 permits raw model prose. Contract 13.1 (NORMATIVE) requires
  UNKNOWN_ACTION + REPORT_CAPABILITY_UNAVAILABLE. "rollback the last deployment"
  routed to an unconstrained model answer. The 20 shared one structured
  signature with plain chat ("hello there", "thanks"), so P6 could not separate
  them without reparsing text, which 15.3 and the task forbid. Latent only:
  nothing was wired, and UNKNOWN_ACTION is non-confirmable and non-dispatchable.
  OBLIGATION_PRIORITY was checked and is complete (11 members, ranks 1-11 once
  each, identical to contract 14.2) -- not the blocker.

  P3 lexicon fix LANDED as 13B11L-R1 (2026-09-20), one focused commit:
    9ace0e3  P3-R1  classifier.py lexicon reconciliation -- 20 verbs added to
             ACTION_VERBS (44 -> 64), 14 of them also to SENSITIVE_ACTION_VERBS
             (26 -> 40) per the operator's signed-off split; backup build
             download fix roll rotate deliberately not sensitive. router.py
             untouched. +25 -0 lines, no executable statement, still passive.
  Invariant now held by tests/execution/classifier_lexicon_reconciliation_test.py
  (177 tests): router.UNSUPPORTED_VERBS is a subset of classifier.ACTION_VERBS.
  It is asserted in the test, not the module -- classifier -> router is the
  dependency the classifier docstring forbids.
  Measured: 21/41 -> 41/41 reach UNKNOWN_ACTION + OPERATIONAL; 14/14 sensitive
  and 6/6 not promoted; 8/8 chat + 9/9 new explanatory + 8/8 supported controls
  unchanged on the full 7-field signature; the five named security prompts 0 on
  CONVERSATIONAL and 0 dispatchable; a pre-edit collateral scan over 2041
  distinct strings from every execution corpus moved exactly 2, both "scale",
  both toward OPERATIONAL, 0 the other way. pytest 3247 -> 3464 passed / 0
  failed, golden still 12/20 same eight, probe still fc68a0b0, all 24 critical
  files byte-identical, registry.call still 4 callers. Security review 30/30.
  Two existing tests changed, neither relaxed: router_generalization_test
  asserted the defect (now 4 assertions where it had 2) and
  router_non_activation_test re-pins 1 of its 7 digests with the prior value
  kept in a comment.
  Flagged to the operator by R1: CLASSIFIER_VERSION stayed "1" although the
  constant's comment says a lexicon change bumps it (CLOSED by R2 below); the
  frozen split makes "rollback the last deployment" sensitive but "roll back
  the deployment" ordinary; "reset the service" is AMBIGUOUS_ACTION by
  precedence, which still satisfies the requirement. The latter two are open
  and latent -- both spellings are operational, UNKNOWN_ACTION, not executable.

  P6 LANDED as 13B11L-P6 (2026-09-20), one focused commit, files only:
    8a70d17  P6  obligations.py + 4 test files + 2 fixtures -- the deterministic
             response-obligation engine. 7 files, +2289 -0, 0 files modified.
  Contract 14.1: exactly one obligation per operational turn, from frozen inputs
  only. It decides WHAT to report, never how it is worded: no template, no
  user-facing string, no prompt, no str field on the input at all. Execution
  truth arrives only as a TrustedToolResult. Conversational turns return None.
  The 442-row matrix was frozen and hashed with the module provably absent, and
  it caught two wrong rank predicates: the validated 13B10C5 ladder put all 41
  unsupported verbs on rank 1 ("shall I proceed?") or rank 4 ("which one?"),
  both implying an execution that can never happen, against 13.1. Rank 1 now
  requires an action an approval could bind (12.3) and rank 4 one that requires
  a target (17.1), so 41/41 reach REPORT_CAPABILITY_UNAVAILABLE.
  The existing suite then caught an architectural violation: importing
  confirmation.py broke the zero-importer invariant P5 had preserved. Fixed on
  this side -- confirmation_state became confirmation_claimed, the settled
  projection the plan specified -- at the cost of a matrix re-freeze. No
  existing test was relaxed and no existing file was modified.
  Module agreed with the corrected table on the FIRST run: 0 failures / 442
  rows, including the per-row proof that min(rank of every rule that holds)
  equals the selected rank. pytest 3744 -> 5122 passed / 0 failed, golden still
  12/20 same eight, probe still fc68a0b0, 24 critical files byte-identical,
  security review 34/34, 0 importers and 0 call sites under app/.
  Two mappings decided inside the frozen eleven and flagged: DENY ->
  REPORT_CAPABILITY_UNAVAILABLE (no denial member exists; adding one is a 6.2
  extension) and TIMEOUT -> REPORT_TOOL_ERROR (rank 3 would claim the effect
  happened). Both distinctions survive in the machine-readable reason.
  Also flagged: R1/R2 record a "bundle SHA-256" no script in either bundle
  computes and 14 formulations failed to reproduce; integrity established three
  other ways instead, nothing modified to make them agree.
  P6 unit 2 is completed below. The real registry adapter remains P9.

  P6 unit 2 LANDED as 13B11M (2026-09-22), one focused production commit:
    4885c4f  P6  response.py + focused response fixtures/tests -- deterministic
             ApprovedOperationalResponse construction. 8 files, +2381 -5.
  The existing P0 response type is reused exactly. The public builder consumes
  an existing ObligationDecision/ObligationState, exact ToolInvocation/result
  linkage, exact provenance and caller-supplied time. It accepts no model object
  or request prose, reads no store or clock, and performs no dispatch,
  permission, confirmation, provenance or audit mutation. All 11 obligations,
  21 actual reasons and 10 operational sources are covered. (The P6 report's
  historical claim of 22 reasons is recorded as a documentation discrepancy;
  the implemented enum has 21.)
  Response matrix f073cd7f... and 28-template inventory 657443b3... were frozen
  with response.py absent. Success requires executed trusted SUCCESS; timeout
  remains outcome-unknown; DENY/no-tool/unavailable/blocked retain distinct
  wording; user facts/reports remain attributed; result A cannot be attached to
  invocation B. Compound values fail closed pending the redaction/display
  policy. Zero live importers. pytest 5122 -> 5245 passed / 11 deselected,
  golden still 12/20 same eight, probe still fc68a0b0, 24/24 critical files
  byte-identical, security review 19/19. Mode remains legacy; Hermes disabled.
  Next smallest unit from the actual dependency graph: passive P7 Hermes adapter
  boundary against recorded outputs only. NOT started; do not enable Hermes or
  wire a pipeline.

  Classifier version reconciled as 13B11L-R2 (2026-09-20), one focused commit:
    ea0cb32  R2  CLASSIFIER_VERSION "1" -> "2" and the comment defining both.
             Exactly ONE non-comment line of 319 differs from 9ace0e3.
  "1" keeps its original meaning (44 ACTION_VERBS, 26 sensitive, 21/41
  covered); "2" names the rule set R1 left (64, 40, 41/41). One version name
  had come to identify two rule sets, so an audited classification could not be
  replayed against the rules that produced it -- an audit defect, not a
  behavioural one. The window where the repaired rules reported "1" is exactly
  9ace0e3..ea0cb32: local only, never pushed, mode legacy, no audit record
  emitted.
  Proof rather than assertion: 260 requests x 2 context shapes x 16 fields were
  snapshotted BEFORE the bump and hashed; with classifier_version removed the
  snapshot reproduces byte-for-byte after (2b94f79f), 0 of 520 rows moving any
  non-version field. Exactly 1 of 5 version constants moved -- router, lane,
  canonicalization and permission all still "1". Lexicon digests, rule table
  and reason vocabulary identical; 41/41 sweep and all 25 R1 controls
  unchanged. pytest 3464 -> 3744 passed / 0 failed, golden still 12/20 same
  eight, probe still fc68a0b0, 24 critical files byte-identical.
  Six version assertions updated, none weakened (each writes the literal "2");
  permissions_decisions_test's independence check was STRENGTHENED from
  all(value == "1") to a per-name map, which the bump now demonstrates.
  That re-run is done: see 13B11L-P6 above. Do not overwrite the blocked 13B11L
  analysis; it is history.

Phase 4+ queue (after 500 interactions):
  - OpenJarvis / hermes-agent-self-evolution skill catalog sync
  - Flip feature flags ON when ready: dictation, Obsidian vault, embedding
    tool selection, Graphiti (all landed, default OFF)

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

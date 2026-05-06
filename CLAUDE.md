# JARVIS — Claude Code Project Context
> Read this file completely before writing any code, any file, or any command.
> Update the "Current Status" section at the end of every session.

---

## What This Project Is

A local-first, fully autonomous AI assistant modeled on Tony Stark's JARVIS from the Iron Man films. Runs 100% on personal hardware — no API costs, no cloud dependency, no paid subscriptions. Controls the PC, watches the screen and webcam, helps with coding and hardware building, runs assigned tasks autonomously while the owner is away, and sends status updates via Discord/Telegram.

Built to be open-sourced on GitHub and documented on YouTube/TikTok. Every phase ships something real and demo-able.

**The owner uses Claude Code as the primary co-builder. You are that co-builder.**

---

## Hardware

| Device | Spec | Role |
|--------|------|------|
| Main PC | RTX 4070 Ti Super 16GB VRAM, Windows 11 | Active — running now |
| Server PC | RTX 5090 32GB VRAM, Windows 11 | Not yet set up |
| Phone | Android/iOS | PWA via Tailscale |
| Meta Glasses | Ray-Ban Meta | Audio via paired phone |

**4070 Ti note:** Active model is `qwen3-nothink` (custom Modelfile, thinking disabled). Hermes Agent can be installed via WSL2 NOW pointing at existing Ollama — do not wait for 5090. Full 32B model stack and Hermes full power activate when 5090 is set up.

---

## AI Model Stack (all via Ollama)

| Model | Role | VRAM | Ollama command |
|-------|------|------|----------------|
| qwen3-nothink | Primary brain, thinking OFF (daily use) | ~10GB | See Modelfile below |
| qwen3:14b | Primary brain, thinking ON (deep reasoning only) | ~10GB | `ollama pull qwen3:14b` |
| qwen3:32b | Primary brain (5090 upgrade) | ~20GB @ Q5_K_M | `ollama pull qwen3:32b` |
| qwen2.5-coder:14b | Coding tasks (4070 Ti compatible) | ~9GB | `ollama pull qwen2.5-coder:14b` |
| qwen2.5-coder:32b | Dedicated coding (5090 only) | ~20GB @ Q4_K_M | `ollama pull qwen2.5-coder:32b` |
| gemma3:4b | Intent router + trivial direct answers (<50ms) | ~3GB | `ollama pull gemma3:4b` |
| qwen3-vl | Vision — screen + webcam | ~8GB @ Q4 | `ollama pull qwen3-vl` |
| gemma4:e2b | Possible router upgrade — benchmark on 5090 | ~2GB | `ollama pull gemma4:e2b` |

**Non-negotiable Ollama environment variables — set ALL before starting Ollama:**
```
OLLAMA_KEEP_ALIVE=-1
OLLAMA_NUM_PARALLEL=2
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_NUM_BATCH=512
OLLAMA_MAX_LOADED_MODELS=2
```

**Note on FLASH_ATTENTION:** Some Qwen3 builds have a regression with this flag. If you see slowdowns after enabling, run `OLLAMA_DEBUG=1 ollama run qwen3-nothink "test"` and verify all layers are on GPU. If not, try `OLLAMA_FLASH_ATTENTION=0`.

**Qwen3-VL requires Ollama 0.12.7+.** Verify with `ollama --version` before pulling.

**5090 context window:** When migrating to 5090, update `num_ctx: 32768` in Modelfile.nothink and config.yaml. At 32B the 8192 limit is conservative — 32768 gives much richer context without hitting VRAM limits.

### Create the qwen3-nothink Modelfile — do this first

Qwen3's `<think>` blocks add 300-800ms per response. For voice and tool calls, this is pure waste. Create a no-think model as the daily default:

```bash
# Create Modelfile.nothink in the project root
cat > Modelfile.nothink << 'EOF'
FROM qwen3:14b

PARAMETER num_ctx 8192

SYSTEM """
You are JARVIS, Tony Stark's AI assistant. Always address the user as "sir". Spoken responses: 1 sentence ideal, 2 maximum. Never 3. No markdown, no bullet points in voice responses. Never break character. Never say "as an AI". Action tags are appended after speech in [ACTION:TYPE:PARAMS] format. /no_think
"""
EOF

ollama create qwen3-nothink -f Modelfile.nothink
```

**Alternative — API-level thinking disable (no Modelfile needed):**
```python
# In llm_client.py — pass think: false directly in the API call
response = await ollama_client.chat(
    model="qwen3:14b",
    messages=messages,
    options={"think": False}   # suppresses <think> blocks at API level
)
```
Both approaches work. The Modelfile bakes it in permanently; the API param lets you toggle per-call. Use the Modelfile for the default and the API param when you need thinking ON for a single deep_reasoning call.

**Safety net — cap token output in `llm_client.py`:** Even with `/no_think`, Qwen3 can generate very long responses during early testing. Add a `num_predict` cap for voice responses to prevent runaway generation:
```python
# In llm_client.py — for voice response calls
options = {
    "think": False,
    "num_predict": 150,   # cap at ~2 sentences for voice — increase for tool calls
}
```
Remove this cap for deep_reasoning calls and code generation.

### 3-tier complexity routing (add to `brain/complexity_router.py`)

| Tier | Model | When | Latency |
|------|-------|------|---------|
| Trivial | gemma3:4b — answers directly | Time, stats, simple facts | ~100ms total |
| Normal | qwen3-nothink — no thinking | All tool calls, standard queries | ~400ms |
| Deep | qwen3:14b — thinking ON | Debug, design, "think through X" | ~800ms |

---

## Agent Architecture (3 layers)

### Layer 1 — Custom FastAPI Brain ✅ COMPLETE (Phase 0–7 done)
Your own code. Every piece understood.
- `app/server.py` — FastAPI WebSocket + REST server (528 lines)
- `app/brain/llm_client.py` — Ollama streaming client, retry, cancel token (276 lines)
- `app/brain/router.py` — Gemma3 4B intent classifier, <50ms (238 lines)
  Current intent classes: `respond / tool / memory / vision / confirm`
  **ADD: `deep_reasoning`** — triggers Qwen3 with thinking ON. Use for: "debug this", "design a system", "analyze these logs", "think through X".
- `app/brain/prompts.py` — JARVIS personality enforcement
- `app/tools/registry.py` — modular tool system, one file per tool

### Layer 2 — Hermes Agent (install via WSL2 now, full power on 5090)
NousResearch. 23k+ stars. Self-improving agent with Kanban multi-agent board, 19 messaging platforms, autonomous Curator, MCP support, cron scheduling.

```bash
# Install (WSL2 on Windows, works today with existing Ollama on localhost)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Configure to use existing Ollama
hermes model
# → Custom endpoint → http://localhost:11434/v1 → qwen3-nothink → ctx 8192

# First thing after install — do this before anything else
hermes kanban init

# Set up specialist profiles
hermes profile create jarvis-researcher --tools "search,web,memory,rag,files" --model "qwen3:14b"
hermes profile create jarvis-coder --tools "terminal,files,git,shell" --model "qwen2.5-coder:14b"  # use :32b on 5090
hermes profile create jarvis-reviewer --tools "files,web,memory" --model "qwen3:14b"

# Install Hermes UI + observability
# Option A: full workspace (recommended)
git clone https://github.com/outsourc-e/hermes-workspace

# Option B: lightweight web UI
git clone https://github.com/nesquena/hermes-webui

# Observability plugin (always install this)
git clone https://github.com/stainlu/hermes-labyrinth ~/.hermes/plugins/hermes-labyrinth
```

Docs: https://hermes-agent.nousresearch.com/docs
Kanban tutorial: https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban-tutorial

**Kanban replaces `task_queue.py`** when active. Your `/confirm/{id}` endpoint maps directly to Kanban's unblock mechanism. Wire them together when Hermes activates.

### Layer 3 — OpenJarvis (Phase 4+, skill optimization only)
Stanford SAIL. Trace logging from Phase 0 already wired. Activate after 500+ real interactions.
**Upgraded since original research** — now ships a Tauri desktop app, browser dashboard, CLI, Python SDK, and 26+ messaging channels. The public skill catalog is live with Hermes skills + 13,700+ OpenClaw community skills (agentskills.io standard). Your `audit.jsonl` is already in the right trace format for `jarvis optimize skills`.
```bash
git clone https://github.com/open-jarvis/OpenJarvis.git
jarvis skill sync hermes --category research   # run after 500 interactions
# Also: browse OpenClaw community skills at agentskills.io — 13,700+ installable
```

---

## Tech Stack — Complete Reference

### Voice Pipeline

```
Wake word  → OpenWakeWord             pip install openwakeword
STT        → faster-whisper           pip install faster-whisper
             Model: large-v3-turbo    216x real-time, ~80-120ms on 4070 Ti GPU
             Alt:   distil-large-v3   6x faster, English only, ~1% WER diff
VAD        → webrtcvad               pip install webrtcvad
TTS (1)    → Chatterbox Turbo        pip install chatterbox-tts   PRIMARY
TTS (2)    → Kokoro-82M              pip install kokoro           FALLBACK
TTS (3)    → Piper TTS               pip install piper-tts        EMERGENCY CPU
SFX        → pygame                  pip install pygame
```

**STT — upgrade stt.py from medium.en to large-v3-turbo:**
```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3-turbo",        # was "medium.en" — 216x faster, barely any accuracy loss
    device="cuda",
    compute_type="float16"
)

segments, info = model.transcribe(
    audio,
    vad_filter=True,                        # prevents hallucinations on silence
    vad_parameters=dict(
        min_silence_duration_ms=300,
        speech_pad_ms=100
    ),
    beam_size=1,                            # fastest, minimal accuracy loss for short utterances
    language="en",
    condition_on_previous_text=False        # prevents repetition loops
)
```

**TTS chain — enforce this order in tts.py:**
```
Chatterbox Turbo (CUDA + voice_clone_path set)
  → best quality, voice clone, [laugh][chuckle][cough] paralinguistic tags
  → Kokoro 82M (CUDA, Chatterbox OOM or not installed)
  → fast, good quality, 54+ voices, Apache 2.0, no voice clone
    → Piper (CPU-only, always available)
    → guaranteed fallback, never fails
```

**Chatterbox Turbo — swap in tts.py:**
```python
# UPGRADE: ChatterboxTTS → ChatterboxTurboTTS
from chatterbox.tts_turbo import ChatterboxTurboTTS
model = ChatterboxTurboTTS.from_pretrained(device="cuda")
# Paralinguistic tags are native to Turbo — pass them through:
wav = model.generate("Certainly, sir [chuckle].", audio_prompt_path="voice_ref.wav")
```

**IMPORTANT:** Strip `[laugh]` `[chuckle]` `[cough]` BEFORE passing text to Kokoro or Piper. Only Chatterbox Turbo handles them.

**Pre-generate common phrases for 0ms TTS latency (add to `voice/phrase_cache.py`):**
```python
CACHED_PHRASES = {
    "right_away": "Right away, sir.",
    "on_it": "On it, sir.",
    "done": "Done, sir.",
    "working": "Working on it, sir.",
    "looking": "Looking into that now, sir.",
    "searching": "Searching now, sir.",
    "understood": "Understood, sir.",
    "complete": "Task complete, sir.",
    "listening": "Listening.",
    "no_connection": "Afraid the connection is unavailable, sir.",
    "cannot": "Afraid I cannot do that, sir.",
    "error": "Encountered an error, sir. Checking systems.",
    "confirm_delete": "That will permanently delete the file, sir. Shall I proceed?",
    "confirm_send": "Shall I send that, sir?",
    "good_morning": "Good morning, sir. All systems operational.",
}
# Generate WAV at boot → serve from memory dict at 0ms
```

**Filler phrases during tool calls (add to `voice/filler_manager.py`):**
```python
TOOL_FILLERS = {
    "web_search": "searching",
    "browser_use": "on_it",
    "shell": "working",
    "vision": "looking",
    "cad": "working",       # 3D CAD generation takes time
    "default": "on_it",
}
# Play cached filler immediately, run tool in background via asyncio.gather
```

**Partial transcript processing (add to voice pipeline):**
Start routing intent before the user finishes speaking — saves 500-1000ms for 60-70% of interactions:
```python
async def on_partial_transcript(partial_text: str):
    if len(partial_text.split()) >= 4:   # wait for at least 4 words
        intent = await router.quick_classify(partial_text)
        if intent in ["tool_call", "shutdown"]:   # high confidence, no ambiguity
            await context_prefetch(intent)        # pre-warm context
```

### Browser & Desktop Automation

- `browser.py` — simple URL open, app launch (Level 0, built)
- `browser_use.py` — full Chrome agent with your real cookies/sessions (Level 1, ADD)
  - Install: https://github.com/browser-use/desktop
  - Use for: login-required sites, form fill, clicking, scraping with your accounts
  - Action tag: `[ACTION:BROWSER_AGENT:task description]`
- Playwright MCP — Microsoft's MCP server via FastMCP client
  - `npx @playwright/mcp` — accessibility-tree based, no screenshots needed
- CLI-Anything harnesses — agent-native CLIs for GUI apps (ADD)
  - `pip install cli-anything-hub` → `cli-hub install obs ffmpeg blender`
  - JSON output, wire as Level 1 tools in `app/tools/cli/`

### Workshop Tools — NEW (from nazirlouis/ada_v2 research)

**`app/tools/cad.py` — AI-driven 3D CAD + printing pipeline (Level 2):**
- Say "JARVIS, design a 40×20mm sensor bracket with two M3 holes" → on print bed in ~60s
- Uses `build123d` (Python CAD) → exports STL → OrcaSlicer CLI slices → sends G-code to printer via network
- Auto-discovers printers via mDNS
- Source: adapt `cad_agent.py` + `printer_agent.py` from https://github.com/nazirlouis/ada_v2
- `pip install build123d` + OrcaSlicer installed separately
- Action tag: `[ACTION:CAD:design description]`
- ALWAYS `SAFETY_LEVEL = 2` — confirm before printing

**`app/tools/kasa.py` — TP-Link Kasa smart home (Level 0 reads, Level 1 writes):**
- Controls workshop smart plugs, lights, switches via local network — no cloud
- Auto-discovers devices via mDNS
- `pip install python-kasa`
- Source: adapt `kasa_agent.py` from https://github.com/nazirlouis/ada_v2
- Action tag: `[ACTION:KASA:device_name:command]`

### MCP Client Layer (critical gap — add `app/tools/mcp_client.py`)

```python
# pip install fastmcp
# Wire these in order of priority:
MCP_SERVERS = [
    {"name": "playwright",       "command": "npx @playwright/mcp"},
    {"name": "github",           "command": "npx @modelcontextprotocol/server-github"},
    {"name": "obsidian",         "command": "npx obsidian-mcp /path/to/jarvis-vault"},
    {"name": "homeassistant",    "url": "http://homeassistant.local:8123/mcp"},  # if running HA
]
# Security: whitelist these servers — never auto-connect to untrusted MCP servers
```

Reference: https://github.com/jlowin/fastmcp

### Desktop Control

- Open Interpreter — `pip install open-interpreter`
  Wire to Ollama: `interpreter --api_base "http://localhost:11434/v1" --api_key "fake_key"`
- PyAutoGUI — `pip install pyautogui` — mouse/keyboard control
- mss — `pip install mss` — fast screenshots
- OpenCV — `pip install opencv-python` — webcam capture

### Vision & Workshop

- YOLOE (via Ultralytics) — `pip install ultralytics` — real-time object detection
- DepthAnything V2 — monocular depth from webcam
- MediaPipe — `pip install mediapipe` — hand tracking stub (wired, Phase 3)

### Memory & Knowledge

**Current stack (active):**
- Mem0 v1.0+ — `pip install mem0ai` — episodic memory
- ChromaDB — `pip install chromadb` — semantic/document RAG
- `skills.md` — procedural memory file, grows over time

**Mem0 v1.0+ features — add to `memory_client.py`:**
```python
# Procedural memory — how to do things, not just what happened
mem0.add(
    "When debugging circuits, check power rails first, then signal traces",
    agent_id="jarvis",
    memory_type="procedural"
)

# Metadata filtering — scope queries to specific projects
results = mem0.search(
    "sensor wiring",
    filters={"project": "current_build", "type": "hardware"}
)

# Inclusion/exclusion for what Mem0 should remember
mem0.project.update(
    inclusion_prompt="Remember: hardware builds, code decisions, preferences, project state",
    exclusion_prompt="Do NOT remember: passwords, API keys, temporary debug steps"
)
```

**`skills.md` — seed this file with known patterns (grows over time):**
```markdown
# JARVIS procedural memory
- When asked about workshop projects, check ~/projects/ first before searching the web
- User prefers Python 3.11+ with type hints on all functions
- For circuit debugging: check power rails first, then signal traces
- Git commits: always run pytest first, then commit with a descriptive message
- 3D printer is a Creality K1 — use the K1 OrcaSlicer profile
- Default workbench PC is on the local network, accessible via Tailscale
- When writing code, match the existing style in that file — don't introduce new patterns
```
This file is read at session start and injected into the system prompt. Claude Code should grow it after each session.
- Graphiti — temporal knowledge graph (who/what relationships with timestamps)
  - `pip install graphiti-core` + Neo4j local
  - "Project X uses library Y" becomes a graph edge queryable over time
  - MCP server available: https://github.com/getzep/graphiti
- Obsidian vault (`jarvis-vault/`) — human-readable notes + AI-accessible via MCP
  - JARVIS writes knowledge as `[[linked]]` markdown notes
  - Obsidian graph view shows visual map of everything JARVIS knows
  - MCP: `npx obsidian-mcp /path/to/jarvis-vault`
  - Keep `jarvis-vault/` separate from any personal Obsidian vault

**Context pre-fetch at session start (add to `boot.py`):**
```python
async def prefetch_session_context():
    """Run parallel before wake word activates — morning report reads from here instantly"""
    gpu, tasks, project, errors = await asyncio.gather(
        system_stats.gpu_temp(),
        task_queue.count(),
        memory_client.get("last_active_project"),
        logs.recent_errors(limit=3),   # surface recent errors in morning report
    )
    SESSION_CONTEXT.update({"gpu": gpu, "tasks": tasks, "project": project, "recent_errors": errors})
```

### Backend

- FastAPI — `pip install fastapi uvicorn`
- httpx — Discord + Telegram REST (asyncio-safe, no library loops)
- APScheduler — cron jobs (replaced by Hermes Kanban when active)
- DuckDuckGo Search — `pip install duckduckgo-search`
- Tailscale — private VPN for multi-device access

### Frontend UI

- Electron — transparent always-on-top HUD overlay
- React + Three.js + Vite — hologram frontend (projector)
- PWA — mobile access via Tailscale (dark UI, arc reactor animation)

### Phase 7 Cinematic

- Unreal Engine 5 + MetaHuman Creator
- NVIDIA Audio2Face-3D
- aaryansachdeva/unreal-audio2lipsync (patterns already in `ue5_bridge.py`)

---

## Folder Structure

```
jarvis/
  CLAUDE.md                 this file
  README.md
  config.yaml
  Modelfile.nothink         CREATE FIRST — qwen3 with thinking disabled
  requirements.txt
  docker-compose.yml
  skills.md                 JARVIS procedural memory file, grows over time

  app/
    main.py
    server.py              FastAPI + WebSocket (528 lines)
    boot.py                Boot sequence + session context pre-fetch
    config.py

    brain/
      llm_client.py        Ollama streaming client + cancel token (276 lines)
      router.py            Gemma3 4B intent classifier (238 lines)
      complexity_router.py 3-tier routing: trivial/normal/deep  ADD
      prompts.py           JARVIS personality enforcement
      response_cleaner.py
      cancel_token.py      Thread-safe singleton — stops LLM + TTS mid-flight
      kill_switch.py       Ctrl+Alt+J or voice "shutdown jarvis"
      morning_report.py
      context_prefetch.py  Pre-loads GPU/tasks/project before wake word  ADD

    voice/
      wake_word.py         OpenWakeWord + is_speaking flag
      vad.py
      stt.py               faster-whisper large-v3-turbo (UPGRADE from medium.en)
      tts.py               Chatterbox Turbo → Kokoro → Piper chain
      audio_stream.py
      sounds.py            SFX manager
      phrase_cache.py      Pre-generated WAV phrases, 0ms latency serve  ADD
      filler_manager.py    Plays filler audio during tool calls  ADD
      push_to_talk.py      Keyboard hotkey fallback (Ctrl+Space)
      error_recovery.py    Speaks on Ollama disconnect

    tools/
      registry.py
      browser.py           Simple URL open (Level 0)
      browser_use.py       Full Chrome agent with real sessions (Level 1)  ADD
      mcp_client.py        FastMCP client layer, all MCP servers  ADD
      cad.py               AI → build123d → STL → OrcaSlicer → printer (Level 2)  ADD
      kasa.py              TP-Link Kasa smart home control (Level 0/1)  ADD
      home_assistant.py    HA MCP wrapper — via mcp_client.py (Level 0/1)  ADD
      files.py
      shell.py
      apps.py
      web_search.py
      system_stats.py
      calendar.py
      interpreter.py       Open Interpreter bridge
      computer_use.py      Visual GUI automation
      cli/                 CLI-Anything harnesses  ADD
        obs.py             OBS Studio control
        ffmpeg.py          FFmpeg video processing
        blender.py         Blender 3D rendering

    computer/
      screenshot.py
      vision.py            Qwen3-VL screen + webcam
      mouse_keyboard.py
      verifier.py
      safety.py            4-level safety gate
      gesture.py           MediaPipe stub
      yolo_detector.py

    memory/
      memory_client.py     Mem0 v1.0+ (episodic + procedural memory)
      rag_client.py        ChromaDB (semantic/document RAG)
      procedural.py        skills.md reader/writer  ADD
      project_indexer.py   Auto-indexes ~/projects/ into ChromaDB  ADD

    agent/
      task_queue.py        (replaced by Hermes Kanban when active)
      scheduler.py         APScheduler cron
      reporter.py          CPU/RAM stats + morning_report sender
      sensor_store.py      In-memory deque for RPi sensors

    comms/
      discord_bot.py       httpx REST to Discord API v10
      telegram_bot.py      httpx REST to Telegram Bot API
      ue5_bridge.py        UE5 MetaHuman WebSocket bridge
      audio2face.py        NVIDIA Audio2Face-3D bridge

    network/
      tailscale.py

    logs/
      audit.py             JSONL audit log — every tool call logged

  frontend/
    electron/              Always-on-top HUD overlay
    pwa/                   Mobile PWA (dark UI, arc reactor, WebSocket)
    hologram/              Three.js full-screen hologram (projector)

  scripts/
    install.py             One-command setup (stdlib-only)
    install.ps1            PowerShell wrapper
    switch_models.py       --profile {4070ti,5090} atomic config rewrite
    sensor_node.py         Standalone Raspberry Pi agent (stdlib-only)

  tests/
    (60 test files, 276 passing, 0 failing)
    e2e/test_full_loop.py
    stress/test_wake_word_stress.py
    perf/baseline_4070ti.json

  docs/
    5090_migration.md      Full step-by-step migration runbook
    content/               YouTube scripts, TikTok cuts, recording setup, episode arc
```

---

## config.yaml Structure

```yaml
# Models
models:
  main: "qwen3-nothink"        # default brain — thinking OFF for speed
  main_thinking: "qwen3:14b"   # deep reasoning tasks only — thinking ON
  main_trivial: "gemma3:4b"    # trivial queries answered directly, skip Qwen3
  coder: "qwen2.5-coder:32b"   # 5090 only
  router: "gemma3:4b"
  vision: "qwen3-vl"
  ollama_base_url: "http://localhost:11434"
  num_ctx: 8192                # explicit context window — prevents VRAM OOM

# Safety
safety:
  approval_mode: "balanced"    # safe | balanced | strict
  dry_run: false               # true = narrate only, never execute
  confidence_threshold: 0.75

# Voice
voice:
  wake_word: "hey_jarvis"
  wake_word_sensitivity: 0.5
  stt_model: "large-v3-turbo"  # UPGRADED from medium.en
  stt_compute_type: "float16"
  stt_beam_size: 1             # fastest, minimal accuracy loss
  stt_vad_filter: true         # prevents Whisper hallucinations on silence
  tts_engine: "chatterbox_turbo"
  voice_clone_path: ""         # path to 10s WAV reference clip
  piper_model_path: "./models/en_US-lessac-high.onnx"
  piper_config_path: "./models/en_US-lessac-high.onnx.json"
  push_to_talk_key: "ctrl+space"
  tts_cache_enabled: true      # pre-generate common phrases at boot
  filler_phrases_enabled: true # play filler audio during tool calls

# Routing
routing:
  trivial_model: "gemma3:4b"      # answers directly, ~100ms total
  normal_model: "qwen3-nothink"   # standard tool calls and responses
  deep_model: "qwen3:14b"         # complex reasoning, thinking on
  partial_transcript_words: 4     # words before starting intent prediction

# Boot sequence
boot:
  enabled: true
  music_file: "assets/audio/boot_intro.wav"
  status_report: true
  prefetch_context: true          # load GPU/tasks/project before wake word

# Ports
server:
  host: "0.0.0.0"
  port: 8000
  websocket_path: "/ws"

# Memory
memory:
  mem0_enabled: true
  mem0_procedural: true           # enable procedural memory (v1.0+)
  chromadb_path: "./data/chroma"
  projects_index_path: "./projects"
  skills_file: "./skills.md"      # procedural knowledge, grows over time

# Workshop tools
workshop:
  cad_enabled: false              # enable when build123d + OrcaSlicer installed
  kasa_enabled: false             # enable if TP-Link Kasa devices on network
  printer_ip: ""                  # 3D printer IP, blank = mDNS auto-discover
  printer_profile: ""             # OrcaSlicer profile (e.g. "Creality K1")

# MCP servers
mcp:
  enabled: false                  # enable when mcp_client.py is built
  servers:
    - name: "playwright"
      command: "npx @playwright/mcp"
    - name: "github"
      command: "npx @modelcontextprotocol/server-github"
    - name: "obsidian"
      command: "npx obsidian-mcp /path/to/jarvis-vault"
    - name: "homeassistant"
      url: "http://homeassistant.local:8123/mcp"   # uncomment if running HA

# Comms
comms:
  discord_enabled: false
  telegram_enabled: false
  discord_token: ""
  telegram_token: ""

# Logging
logging:
  audit_log: "./logs/audit.jsonl"
  level: "INFO"
```

---

## JARVIS Personality Rules (ENFORCE IN ALL PROMPTS)

### Core rules
- Always address user as "sir"
- Spoken responses: 1 sentence ideal, 2 maximum. NEVER 3.
- No markdown, no bullet points, no code blocks in voice responses
- Never break character. Never say "as an AI"
- Action tags appended after speech: `[ACTION:TYPE:PARAMS]`
- When unsure: ask instead of acting on Level 2+ actions

### Banned phrases (never generate these)
- "Absolutely" / "Great question" / "I'd be happy to" / "Of course"
- "How can I help" / "Is there anything else" / "I apologize"
- Never start a sentence with "I"

### Good response examples
- "Right away, sir."
- "Done, sir. The endpoint is live on port 8000."
- "Afraid that datasheet is not in my index, sir — searching now."
- "Consider it done. Will text you when the build is complete, sir."
- "That would delete the project folder, sir. Shall I proceed?"
- "On it, sir. [chuckle] That's the third time this week."
- "Designing that bracket now, sir. Should be on the printer in about sixty seconds."

### Action format (unified — enforced across ALL code, no exceptions)
```
[ACTION:BROWSER:https://google.com]              # simple URL open
[ACTION:BROWSER_AGENT:log into github open PR 42] # full browser agent
[ACTION:APP:vscode]
[ACTION:FILE:read:/path/to/file]
[ACTION:SHELL:npm run dev]
[ACTION:MESSAGE:discord:Task complete, sir]
[ACTION:AGENT:deep_research:query]
[ACTION:VISION:screen]
[ACTION:VISION:webcam]
[ACTION:HERMES:task_name:params]
[ACTION:CAD:40x20mm bracket two M3 holes]        # NEW — 3D CAD generation
[ACTION:KASA:workshop_light:on]                   # NEW — smart home control
[EMOTION:neutral]  [EMOTION:success]  [EMOTION:concern]  [EMOTION:thinking]
```

**Paralinguistic tags** (Chatterbox Turbo ONLY — strip before Kokoro/Piper):
```
[laugh]  [chuckle]  [cough]
```

---

## Action Safety Levels (ENFORCE IN safety.py AND ALL TOOL CODE)

| Level | Name | Confirmation | Examples |
|-------|------|-------------|---------|
| 0 | Safe | Never | Answer questions, open app, web search, system stats, read Kasa state |
| 1 | Reversible | Only if confidence < 0.75 | Move file, open URL, browser agent, toggle Kasa device, CLI harness read |
| 2 | Risky | Always confirm | Delete files, send messages, install packages, CAD + print, edit code, git commit |
| 3 | Blocked | Never automatic | Spend money, delete project folders, admin scripts, send private data |

---

## Boot Sequence Spec (Phase 1 — complete)

```
T+0.0s  Windows login → boot.py starts (Task Scheduler)
T+0.1s  Session context pre-fetch starts (GPU temp, task count, last project) — parallel
T+0.5s  Electron HUD launches — Stark Industries logo fade
T+1.0s  Boot music plays (4 seconds) — pygame.mixer
T+2.5s  'JARVIS systems initializing...' text crawl
T+5.0s  Arc reactor pulses — full HUD loads via WebSocket event
T+5.5s  JARVIS TTS morning status report (context pre-fetched, reads instantly)
T+8.0s  Boot complete — is_listening=True, wake word active
```

**Morning status report template:**
"Good [morning/afternoon/evening], sir. The time is [TIME]. All systems operational. GPU temperature [TEMP] degrees. You have [N] tasks pending. Last active project: [PROJECT_NAME]. Shall I continue where we left off?"

**Sound assets needed (manual step — not yet done):**
- `assets/audio/boot_intro.wav` — boot music
- `assets/audio/listening.wav` — wake word confirmed chime
- `assets/audio/working.wav` — processing beep
- `assets/audio/done.wav` — completion chime
- `assets/audio/error.wav` — error alert tone

---

## Source Repos — Full Reference (every repo reviewed, verdict given)

### ADD — Integrate or build from directly

| Repo | Link | What To Do |
|------|------|------------|
| NousResearch/hermes-agent | https://github.com/NousResearch/hermes-agent | Layer 2. Install via WSL2 NOW. `hermes kanban init`. |
| stainlu/hermes-labyrinth | https://github.com/stainlu/hermes-labyrinth | Hermes observability plugin. One `git clone` into `~/.hermes/plugins/`. |
| outsourc-e/hermes-workspace | https://github.com/outsourc-e/hermes-workspace | Full Hermes web UI. Install alongside Hermes. |
| nesquena/hermes-webui | https://github.com/nesquena/hermes-webui | Lightweight Hermes UI. SSH tunnel or Tailscale. |
| resemble-ai/chatterbox | https://github.com/resemble-ai/chatterbox | Upgrade to Turbo: `ChatterboxTurboTTS`. Paralinguistic tags. |
| devnen/Chatterbox-TTS-Server | https://github.com/devnen/Chatterbox-TTS-Server | FastAPI server for all 3 Chatterbox models with Web UI. |
| hexgrad/kokoro | https://github.com/hexgrad/kokoro | Middle TTS fallback. `pip install kokoro`. Apache 2.0. |
| browser-use/desktop | https://github.com/browser-use/desktop | Full Chrome agent with real sessions. Level 1 tool. |
| HKUDS/CLI-Anything | https://github.com/HKUDS/CLI-Anything | Agent CLI harnesses. `pip install cli-anything-hub`. |
| jlowin/fastmcp | https://github.com/jlowin/fastmcp | MCP client layer. `app/tools/mcp_client.py`. Critical gap. |
| microsoft/playwright-mcp | https://github.com/microsoft/playwright-mcp | Browser automation via MCP. Wire through FastMCP. |
| open-jarvis/OpenJarvis | https://github.com/open-jarvis/OpenJarvis | Skill optimizer. Activate after 500 interactions. |
| isair/jarvis | https://github.com/isair/jarvis | Study: knowledge graph memory + embedding tool selection patterns. |
| getzep/graphiti | https://github.com/getzep/graphiti | Temporal knowledge graph. Phase 4+ alongside ChromaDB. |
| nazirlouis/ada_v2 | https://github.com/nazirlouis/ada_v2 | STEAL: `cad_agent.py` (build123d→STL→OrcaSlicer→printer) + `kasa_agent.py` (TP-Link). Adapt to Ollama. |

### STUDY — Cherry-pick patterns, don't install whole repo

| Repo | Link | What to steal |
|------|------|---------------|
| ethanplusai/jarvis | https://github.com/ethanplusai/jarvis | Already informed Phase 0-3 design. Action tag format, Three.js orb. |
| huwprosser/jarvis-mlx | https://github.com/huwprosser/jarvis-mlx | Already informed prompts.py. System prompt style. Mac-only. |
| aaryansachdeva/unreal-audio2lipsync | https://github.com/aaryansachdeva/unreal-audio2lipsync | Already in ue5_bridge.py. UE5 MetaHuman lip sync pipeline. |
| MateuszMlynekHub/launcher | https://github.com/MateuszMlynekHub/launcher | Already informed wake_word.py. PANNs sound classification. |
| jamiepine/voicebox | https://github.com/jamiepine/voicebox | Multi-engine TTS abstraction pattern for tts.py refactor. |
| NousResearch/kanban-video-pipeline | https://github.com/NousResearch/kanban-video-pipeline | Study for EP9 demo — 4 agents producing video autonomously. |

### REFERENCE — Bookmark for specific future phases

| Repo | Link | When |
|------|------|------|
| 0xNyk/awesome-hermes-agent | https://github.com/0xNyk/awesome-hermes-agent | Hunting for Hermes skills after activation |
| homeassistant-ai (org) | https://github.com/homeassistant-ai | HA MCP server, 80+ home control tools |
| yunaga224/obsidian-memory-mcp | https://github.com/YuNaga224/obsidian-memory-mcp | Memory-as-Obsidian-notes pattern |
| nico-martin/gemma4-browser-extension | https://github.com/nico-martin/gemma4-browser-extension | Phase 8+ if building JARVIS Chrome extension |
| steel-dev/steel-browser | https://github.com/steel-dev/steel-browser | Backup headless browser if browser-use has issues |
| vercel-labs/agent-browser | https://github.com/vercel-labs/agent-browser | Backup browser CLI if browser-use has issues |
| agentskills.io | https://agentskills.io | 13,700+ community skills following open standard — after Hermes activates |
| openclaw.ai | https://openclaw.ai | OpenClaw — 250,000+ star community, source of the 13,700 skills. Browse for installable skill packs. |
| ollama/gemma4 | https://ollama.com/library/gemma4 | Benchmark router upgrade on 5090 |
| Mintplex-Labs/anything-llm | https://github.com/Mintplex-Labs/anything-llm | STEAL: document ingestion pipeline pattern for rag_client.py. Don't install whole thing. |
| livekit/agents | https://github.com/livekit/agents | Phase 8+ — real-time voice streaming if sub-300ms latency becomes a goal |
| open-webui/open-webui | https://github.com/open-webui/open-webui | Alternative to hermes-workspace for a simpler Ollama chat UI. 50k+ stars. |

### SKIP — Do not add, reason documented

| Repo | Link | Why |
|------|------|-----|
| raroque/boop-agent | https://github.com/raroque/boop-agent | Mac + iMessage + paid APIs. Wrong stack entirely. |
| cosmicstack-labs/mercury-agent | https://github.com/cosmicstack-labs/mercury-agent | Your 4-level safety gate is already more sophisticated. No unique value. |
| AnubhavChaturvedi-GitHub/jarvis-ai-assistant | https://github.com/AnubhavChaturvedi-GitHub/jarvis-ai-assistant | Old NLP-era architecture, 26 commits. Fully superseded by your stack. |

---

## Coding Conventions

- **Language:** Python 3.11+ for all backend. TypeScript/React for frontend.
- **Every tool** in `tools/` is a standalone file with a single `execute(params)` function
- **Safety level** declared at the top of every tool file: `SAFETY_LEVEL = 0`
- **Every action** uses `[ACTION:TYPE:PARAMS]` format — no exceptions
- **AVAILABLE flag** — every optional dep uses module-level try/except. Server boots without Chatterbox/YOLO/Mem0/Audio2Face/build123d installed.
- **Audit everything** — every tool call writes a line to `logs/audit.jsonl`
- **Config-driven** — never hardcode model names, ports, or paths. Always `config.yaml`.
- **Streaming first** — TTS begins before LLM finishes generating
- **Cancel token** — thread-safe singleton in `cancel_token.py`. Stops LLM + TTS mid-flight.
- **Dry-run safe** — every tool checks `config.safety.dry_run` before executing
- **Error recovery** — failures trigger verbal TTS error, never silent fail
- **No breaking changes** — working phases cannot be broken by new code
- **Parallel tool calls** — use `asyncio.gather()` for independent values (GPU temp, task count, etc.)
- **Filler before slow tools** — play cached filler phrase before any tool call that takes >500ms
- **Complexity routing** — never send trivial queries to Qwen3. Route through complexity_router.py.
- **MCP is the first sprint** — after GitHub push, adding `app/tools/mcp_client.py` (FastMCP + Playwright MCP) is one afternoon of work and unlocks 10,000+ community tools immediately. This is the highest-leverage single task.

---

## Phase Build Order

```
Phase 0  Core Brain          ✅ COMPLETE — FastAPI + router + tools + audit + kill switch
Phase 1  Voice + Boot        ✅ COMPLETE — Wake word + STT + TTS + streaming + boot + morning report
Phase 2  Tools & Desktop     ✅ COMPLETE — App launch + file ops + web search + shell + system stats + HUD
Phase 3  PC Control          ✅ COMPLETE — Safety gate + screenshot + vision + Open Interpreter + gesture stub
Phase 4  Workshop Brain      ✅ COMPLETE — Screen/webcam vision + Mem0 + ChromaDB RAG + YOLO
Phase 5  Autonomous Agent    ✅ COMPLETE — Discord/Telegram + APScheduler + task queue + approval gates
Phase 6  Multi-Device        ✅ COMPLETE — Tailscale + Phone PWA + Meta Glasses + Raspberry Pi sensor
Phase 7  Cinematic           ✅ COMPLETE — Chatterbox voice clone + UE5 MetaHuman + Audio2Face + Three.js
Release  Prep                ✅ COMPLETE — README, CI, install scripts, 276 tests passing, YouTube scripts
```

---

## Known Risks — Watch For These

1. **Model cold-load** — `OLLAMA_KEEP_ALIVE=-1` must be set before anything else
2. **Self-triggering loop** — `is_speaking=True` mutes wake word during TTS (implemented in wake_word.py)
3. **Always use qwen3-nothink by default** — `qwen3:14b` with thinking is ONLY for deep_reasoning intent class. Never the default.
4. **FLASH_ATTENTION regression** — some Qwen3 builds slow down with `OLLAMA_FLASH_ATTENTION=1`. Debug with `OLLAMA_DEBUG=1`, verify all layers on GPU. Fall back to `OLLAMA_FLASH_ATTENTION=0` if needed.
5. **Qwen3-VL name** — it is `qwen3-vl`, NOT `qwen3.5-vl`. Requires Ollama 0.12.7+.
6. **Hermes on 5090** — needs `qwen3:32b` + 24GB VRAM for full power. WSL2 + 14B works today.
7. **Chatterbox Turbo paralinguistics** — strip `[laugh]` `[chuckle]` `[cough]` BEFORE passing to Kokoro or Piper. Only Turbo handles them.
8. **MCP security** — whitelist MCP servers in FastMCP config. Never auto-connect to untrusted servers.
9. **CAD + printing safety** — `SAFETY_LEVEL = 2` in `cad.py`. Always confirm before sending to printer. Never print without verifying the STL first.
10. **KV cache quantization** — `OLLAMA_KV_CACHE_TYPE=q8_0` saves ~2GB VRAM. If you see accuracy regression, try `q4_0`.
11. **Whisper VAD** — `vad_filter=True` prevents hallucinations on silence but can clip speech with very short pauses. Tune `min_silence_duration_ms` if words get cut off.
12. **webrtcvad on Windows** — requires Microsoft C++ Build Tools to compile. If `pip install webrtcvad` fails, install via: `winget install --id Microsoft.VisualStudio.2022.BuildTools` then retry.
13. **Piper model URLs** — the original install script pointed to a community-uploaded HuggingFace model that was deleted. Always use the official rhasspy repo:
    - ONNX: `https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx`
    - JSON: `https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx.json`
    - Save both to `models/` and verify config.yaml paths match.
14. **wake_word.py `listen()` return type** — returns `b''` (empty bytes) on timeout, not `bool`. Any test asserting `result in (True, False)` will fail. The correct assertion is `assert isinstance(result, (bool, bytes))` or fix `wake_word.py` to return `False` on timeout — read the spec first and fix the right side.

---

## Immediate Next Steps (prioritized)

### Right Now — 4070 Ti, no new hardware needed

1. **Create `Modelfile.nothink`** — eliminates 300-800ms thinking overhead per response
   ```bash
   ollama create qwen3-nothink -f Modelfile.nothink
   ```
2. **Set all Ollama env vars** — add `FLASH_ATTENTION`, `KV_CACHE_TYPE`, `NUM_BATCH`, `MAX_LOADED_MODELS` to Windows System Environment Variables
3. **Push to GitHub** — `git push origin main` (14 commits ahead)
4. **Upgrade `stt.py`** — `large-v3-turbo`, add `vad_filter=True`, `beam_size=1`
5. **Upgrade `tts.py`** — `ChatterboxTurboTTS` swap + Kokoro middle-tier
6. **Install Hermes via WSL2** — `curl -fsSL .../install.sh | bash` → point at localhost:11434
7. **Install hermes-workspace + hermes-labyrinth**
8. **Add `app/brain/complexity_router.py`** — 3-tier routing
9. **Add `app/voice/phrase_cache.py`** — pre-generate 15 common phrases at boot
10. **Add `app/voice/filler_manager.py`** — filler audio during tool calls
11. **Add context pre-fetch to `boot.py`** — asyncio.gather GPU/tasks/project
12. **Add `app/tools/browser_use.py`** — Level 1 browser agent
13. **Add `app/tools/mcp_client.py`** — FastMCP, Playwright MCP first
14. **Adapt `cad.py`** from nazirlouis/ada_v2 `cad_agent.py` + `printer_agent.py`
15. **Adapt `kasa.py`** from nazirlouis/ada_v2 `kasa_agent.py`
16. **Install CLI-Anything** — `pip install cli-anything-hub` + OBS, FFmpeg, Blender

### Manual Steps — no code needed

- Electron HUD: `cd frontend/electron && npm install`
- PWA icon: `frontend/pwa/icon.png` (192×192 PNG)
- Boot sound assets: 5 WAV files → `assets/audio/`
- Voice clone reference: record 10s WAV → set `voice_clone_path` in config.yaml
- UE5: install MetaHuman Plugin + Audio2Face-3D → connect `ws://server:8000/ue5`

### When 5090 Arrives

1. Follow `docs/5090_migration.md` — full runbook, already scripted
2. `python scripts/switch_models.py --profile 5090`
3. `ollama pull qwen3:32b qwen2.5-coder:32b`
4. Update `Modelfile.nothink` to use `qwen3:32b` as base → `ollama create qwen3-nothink -f Modelfile.nothink`
5. `hermes model` → switch to `qwen3:32b`
6. `hermes kanban init` — create researcher/coder/reviewer profiles
7. Benchmark `gemma4:e2b` as router upgrade vs `gemma3:4b`

### Phase 4+ — after 500 real interactions

1. Graphiti knowledge graph — `pip install graphiti-core` + Neo4j alongside ChromaDB
2. Obsidian vault (`jarvis-vault/`) — `npx obsidian-mcp /path/to/jarvis-vault`
3. Add embedding-based tool selection second pass in `router.py`
4. Add dictation mode to `push_to_talk.py` — `pyautogui.typewrite(transcript)` into active window
5. `jarvis skill sync hermes --category research` — pull OpenJarvis skill catalog
6. `app/memory/project_indexer.py` — auto-index `~/projects/` into ChromaDB

---

## Performance Targets (after all upgrades applied)

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| STT latency | ~300-400ms | ~80-120ms | Whisper large-v3-turbo |
| Simple query total | ~1200ms | ~200ms | Gemma3 direct answer + cached phrase |
| Tool call perceived wait | ~2-3s silence | ~200ms + filler | Phrase cache + filler manager |
| Qwen3 first token | ~800ms | ~400ms | qwen3-nothink Modelfile |
| TTS first audio | ~200ms | 0ms cached / ~100ms new | Phrase cache + Chatterbox Turbo |
| VRAM headroom (4070 Ti) | ~3GB | ~5GB | KV cache quantization q8_0 |

---

## Current Status

```
Phase:        Phase 8 local integration stubs complete; manual integrations remain.
Tests:        31 focused tests passing after Phase 8 stub work.
              Re-run after installs before next code checkpoint.
Hardware:     4070 Ti Super 16GB VRAM active. 5090 not yet set up.
Active model: qwen3-nothink available from Modelfile.nothink; qwen3:14b remains fallback.
Git:          Recent checkpoints pushed; verify with git status before next push.
GitHub:       UnknownShadow00/JARVIS, main branch. Latest commit: 6d28728.

Completed from prior pending list:
  - Modelfile.nothink exists and qwen3-nothink was created.
  - Git push completed after recent checkpoints.
  - stt.py uses large-v3-turbo with fast/VAD options.
  - tts.py has Chatterbox -> Kokoro -> Piper fallback.
  - brain/complexity_router.py, voice/phrase_cache.py, voice/filler_manager.py,
    memory/procedural.py, and skills.md exist.

Pending - manual/no code:
  - Restart Ollama/sign in again so new user env vars are picked up by fresh processes
  - voice_clone_path - record 10s WAV, set in config.yaml
  - UE5 MetaHuman Plugin + Audio2Face-3D connection
  - 5090 setup: follow docs/5090_migration.md when hardware arrives

Phase 8 code completed this session:
  - boot.py: add asyncio.gather context pre-fetch
  - memory/project_indexer.py: auto-index configured local project/doc paths
  - tools/mcp_client.py: whitelisted MCP client stub
  - tools/browser_use.py: browser-use/desktop stub (Level 1)
  - tools/kasa.py: python-kasa status/control stub
  - tools/cad.py: CAD design/export stub (build123d + OrcaSlicer readiness)
  - tools/cli/: CLI-Anything harnesses (OBS, FFmpeg, Blender)
  - tasks/readiness_report.py: optional integration coverage

Remaining manual/installation work:
  - Hermes Agent: install WSL2, init kanban, workspace + labyrinth

Phase 4+ queue (after 500 interactions):
  - Graphiti temporal knowledge graph + Neo4j
  - Obsidian vault + obsidian-mcp
  - Embedding-based tool selection in router.py
  - Dictation mode in push_to_talk.py
  - OpenJarvis skill catalog sync

Content:
  10-episode YouTube arc in docs/content/episode_arc.md.
  EP1-7 scripted. EP8=5090 upgrade. EP9=Hermes full power. EP10=launch.
  New demo moments to add: CAD voice-to-print, Kasa workshop lights,
  complexity routing shown live on screen, Kanban multi-agent dashboard.

Notes:
  dry_run=false. Browser-use, python-kasa, build123d, FastMCP, Electron deps, and PWA icon installed.
  OrcaSlicer skipped by request because 3D printing/slicing is not in scope.
  Open Interpreter install is blocked on Python 3.13/tiktoken build tooling; keep optional.
  CI: pytest on every push, ignores e2e/stress/perf/hardware markers.
  5090 migration: run scripts/switch_models.py --profile 5090 after GPU swap.
```

> Update this section at the end of every Claude Code session.
> Format: what was built, last test run, any blockers, next session starting point.

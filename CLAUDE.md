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
| Server PC | RTX 5090 32GB VRAM, Windows | Runs all AI models, always on |
| Main PC | Windows | Browser / Electron HUD thin client |
| Phone | Android/iOS | PWA via Tailscale |
| Meta Glasses | Ray-Ban Meta | Audio via paired phone |

**4070 Ti note:** Until the 5090 arrives, use Qwen3 14B for Phase 0 and Phase 1. Hermes Agent and Qwen3 32B activate at Phase 3 after the 5090 is installed.

---

## AI Model Stack (all via Ollama)

| Model | Role | VRAM | Ollama command |
|-------|------|------|----------------|
| Qwen3 32B | Primary brain | ~20GB @ Q5_K_M | `ollama pull qwen3:32b` |
| Qwen2.5-Coder 32B | Dedicated coding | ~20GB @ Q4_K_M | `ollama pull qwen2.5-coder:32b` |
| Gemma3 4B | Intent router (<50ms) | ~3GB | `ollama pull gemma3:4b` |
| Qwen3-VL | Vision (screen/webcam) | ~8GB @ Q4 | `ollama pull qwen3-vl` |

**Non-negotiable environment variables — set before starting Ollama:**
```
OLLAMA_KEEP_ALIVE=-1
OLLAMA_NUM_PARALLEL=2
```

**4070 Ti fallback:** `ollama pull qwen3:14b` for Phase 0–1 until 5090 arrives.

**Qwen3-VL requires Ollama 0.12.7+.** Verify with `ollama --version` before pulling.

---

## Agent Architecture (3 layers)

### Layer 1 — Custom FastAPI Brain (Phase 0–2, build first)
Your own code. Every piece understood. No external agent framework yet.
- `app/server.py` — FastAPI WebSocket + REST server
- `brain/llm_client.py` — routes to Qwen3 32B / Qwen2.5-Coder / Qwen3-VL
- `brain/router.py` — Gemma3 4B intent classifier, <50ms
- `tools/registry.py` — modular tool system, one file per tool

### Layer 2 — Hermes Agent (Phase 3+, requires 5090)
NousResearch agent. 70+ built-in tools, persistent memory, messaging, MCP, cron.
Install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
Configure: `hermes model` → Custom endpoint → `http://localhost:11434/v1` → `qwen3:32b` → ctx 65536
**Do NOT activate before Phase 3 and before 5090 is installed.**

### Layer 3 — OpenJarvis (Phase 4+, skill optimization only)
Stanford SAIL. Trace logging from Phase 0. Optimization after 500+ real interactions.
`git clone https://github.com/open-jarvis/OpenJarvis.git`

---

## Tech Stack — Complete Reference

### Voice Pipeline
- Wake word: OpenWakeWord — `pip install openwakeword`
- STT: faster-whisper — `pip install faster-whisper` (CUDA required)
- VAD: webrtcvad — `pip install webrtcvad`
- TTS starter: Piper TTS + jgkawell/jarvis ONNX model (HuggingFace)
- TTS upgrade: Kokoro-82M — `pip install kokoro`
- Audio SFX: pygame — `pip install pygame`
- Voice clone (Phase 7): Chatterbox TTS

### Desktop Control
- Open Interpreter — `pip install open-interpreter` — for code/shell/bash tasks
  Wire to Ollama: `interpreter --api_base "http://localhost:11434/v1" --api_key "fake_key"`
- open-computer-use — for visual GUI automation via screenshots
- PyAutoGUI — `pip install pyautogui` — simple fallback
- mss — `pip install mss` — fast screenshots
- OpenCV — `pip install opencv-python` — webcam capture

### Vision & Workshop
- YOLOE-26N (via Ultralytics) — `pip install ultralytics` — real-time object detection
- DepthAnything V2 — monocular depth from webcam for 3D holograms
- MediaPipe — `pip install mediapipe` — 21-point hand tracking for gestures

### Memory & Knowledge
- Mem0 self-hosted — `pip install mem0ai` — persistent memory
- ChromaDB — `pip install chromadb` — vector DB for local RAG
- OpenMemory — temporal memory (when things happened)

### Backend
- FastAPI — `pip install fastapi uvicorn`
- discord.py — `pip install discord.py`
- python-telegram-bot — `pip install python-telegram-bot`
- DuckDuckGo Search — `pip install duckduckgo-search`
- Docker Compose — containerize Ollama, FastAPI, Mem0
- Tailscale — private VPN for multi-device access

### Frontend UI
**Primary fork: `github.com/steffenpharai/Jarvis`** — full offline JARVIS with YOLO, depth maps, PWA, HUD, boot animation, chime, verbal error recovery. Fork this, replace Jetson backend with the FastAPI server.
- Gesture layer: `github.com/Suryansh777777/Jarvis-CV` — MediaPipe hand tracking
- HUD components: `github.com/MuhammadFahru/jarvis-hud` — globe, telemetry, terminal log
- Audio-reactive orb: cherry-pick from `github.com/ethanplusai/jarvis` frontend
- Electron — transparent always-on-top overlay
- React + Three.js + Vite

### Phase 7 Cinematic (far future)
- Unreal Engine 5 + MetaHuman Creator
- NVIDIA Audio2Face-3D
- aaryansachdeva/unreal-text2face

---

## Folder Structure

```
jarvis/
  CLAUDE.md              ← this file
  README.md
  config.yaml
  requirements.txt
  docker-compose.yml

  app/
    main.py
    server.py            FastAPI + WebSocket
    boot.py              Boot sequence orchestrator
    config.py

    brain/
      llm_client.py      Ollama router
      router.py          Gemma3 4B intent classifier
      prompts.py         JARVIS system prompt
      planner.py
      response_cleaner.py

    voice/
      wake_word.py
      vad.py
      stt.py
      tts.py
      audio_stream.py
      sounds.py          SFX manager

    tools/
      registry.py
      browser.py
      files.py
      shell.py
      apps.py
      web_search.py
      system_stats.py
      calendar.py
      interpreter.py     Open Interpreter bridge

    computer/
      screenshot.py
      vision.py
      mouse_keyboard.py
      verifier.py
      safety.py
      gesture.py

    memory/
      memory_client.py
      memory_policy.py
      project_state.py
      rag_client.py

    agent/
      hermes_bridge.py   Routes tasks to Hermes Agent
      task_queue.py
      scheduler.py
      reporter.py

    comms/
      discord_bot.py
      telegram_bot.py

    logs/
      audit.py           JSONL audit log

  frontend/
    jarvis-hud/          Fork of steffenpharai/Jarvis
    electron/
    boot/                boot_sequence.html

  tests/
    ollama_test.py
    stt_test.py
    tts_test.py
    wake_word_test.py
    boot_test.py
    pipeline_test.py
```

---

## config.yaml Structure

```yaml
# Models
models:
  main: "qwen3:32b"          # qwen3:14b on 4070 Ti until 5090 arrives
  coder: "qwen2.5-coder:32b"
  router: "gemma3:4b"
  vision: "qwen3-vl"
  ollama_base_url: "http://localhost:11434"

# Safety
safety:
  approval_mode: "balanced"  # safe | balanced | strict
  dry_run: false             # true = narrate only, never execute
  confidence_threshold: 0.75

# Voice
voice:
  wake_word: "hey_jarvis"
  wake_word_sensitivity: 0.5
  tts_engine: "piper"        # piper | kokoro
  piper_model: "jarvis"
  stt_model: "medium.en"
  push_to_talk_key: "ctrl+space"

# Boot sequence
boot:
  enabled: true
  music_file: "assets/audio/boot_intro.wav"
  status_report: true

# Ports
server:
  host: "0.0.0.0"
  port: 8000
  websocket_path: "/ws"

# Memory
memory:
  mem0_enabled: false        # enable at Phase 4
  chromadb_path: "./data/chroma"
  projects_index_path: "./projects"

# Comms
comms:
  discord_enabled: false     # enable at Phase 5
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

### Action format (unified — enforced across ALL code)
```
[ACTION:BROWSER:https://google.com]
[ACTION:APP:vscode]
[ACTION:FILE:read:/path/to/file]
[ACTION:SHELL:npm run dev]
[ACTION:MESSAGE:discord:Task complete, sir]
[ACTION:AGENT:deep_research:query]
[ACTION:VISION:screen]
[ACTION:VISION:webcam]
[ACTION:HERMES:task_name:params]
[EMOTION:neutral]  [EMOTION:success]  [EMOTION:concern]  [EMOTION:thinking]
```

---

## Action Safety Levels (ENFORCE IN safety.py AND ALL TOOL CODE)

| Level | Name | Confirmation | Examples |
|-------|------|-------------|---------|
| 0 | Safe | Never | Answer question, open app, web search, system stats |
| 1 | Reversible | Only if confidence < 0.75 | Move file, open URL, git status, start server |
| 2 | Risky | Always confirm | Delete files, send messages, install packages, edit code, git commit |
| 3 | Blocked | Never automatic | Spend money, delete project folders, admin scripts, send private data |

---

## Boot Sequence Spec (Phase 1)

```
T+0.0s  Windows login → boot.py starts (Task Scheduler)
T+0.5s  Electron HUD launches — Stark Industries logo fade
T+1.0s  Boot music plays (4 seconds) — pygame.mixer
T+2.5s  'JARVIS systems initializing...' text crawl
T+5.0s  Arc reactor pulses — full HUD loads via WebSocket event
T+5.5s  JARVIS TTS morning status report (Qwen3 32B generated)
T+8.0s  Boot complete — is_listening=True, wake word active
```

**Morning status report template:**
"Good [morning/afternoon/evening], sir. The time is [TIME]. All systems operational. GPU temperature [TEMP] degrees. You have [N] tasks pending. Last active project: [PROJECT_NAME]. Shall I continue where we left off?"

**Sound assets needed:**
- `assets/audio/boot_intro.wav` — boot music
- `assets/audio/listening.wav` — wake word confirmed chime
- `assets/audio/working.wav` — processing beep
- `assets/audio/done.wav` — completion chime
- `assets/audio/error.wav` — error alert tone

---

## Source Repos — Cherry-Pick Reference

| Repo | What to take |
|------|-------------|
| `steffenpharai/Jarvis` | FORK — primary UI foundation. Replace Jetson backend with FastAPI server. |
| `ethanplusai/jarvis` | System prompt design, Three.js audio-reactive orb, WebSocket architecture |
| `huwprosser/jarvis-mlx` | System prompt style, streaming-first pipeline approach |
| `harsh-raj00/my-jarvis` | Arc reactor, particle field, waveform — add on top of steffenpharai base |
| `Suryansh777777/Jarvis-CV` | Full gesture control module — MediaPipe hand tracking |
| `MuhammadFahru/jarvis-hud` | Globe, face tracker, telemetry card, terminal log components |
| `isair/jarvis` | Intent judge pattern, MCP tool routing, memory-context integration |
| `MateuszMlynekHub/launcher` | clap-trigger.py, voice-trigger.py, PANNs sound classification |
| `aaryansachdeva/unreal-text2face` | Phase 7 only — UE5 MetaHuman facial animation |
| `NousResearch/hermes-agent` | Phase 3+ — primary autonomous agent, do NOT use before 5090 |
| `open-jarvis/OpenJarvis` | Phase 4+ — skill optimization and trace evals only |

---

## Coding Conventions

- **Language:** Python 3.11+ for all backend. TypeScript/React for frontend.
- **Every tool** in `tools/` is a standalone file with a single `execute(params)` function
- **Safety level** must be declared at the top of every tool file: `SAFETY_LEVEL = 0`
- **Every action** uses `[ACTION:TYPE:PARAMS]` format — no exceptions
- **Audit everything** — every tool call writes a line to `logs/audit.jsonl`
- **Config-driven** — never hardcode model names, ports, or paths. Always read from `config.yaml`
- **Test every subsystem** in isolation before integrating into the pipeline
- **Streaming first** — TTS must begin speaking before full LLM response is complete
- **Dry-run safe** — every tool must check `config.safety.dry_run` before executing
- **Error recovery** — failures must trigger verbal TTS error message, never silent fail
- **No breaking changes** — if a phase is working, new code cannot break it

---

## Phase Build Order

```
Phase 0  Core Brain          Text-first FastAPI + router + tools + audit + kill switch
Phase 1  Voice + Boot        Wake word + STT + TTS + streaming + boot sequence + morning report
Phase 2  Tools & Web         App launch + file ops + web search + shell + system stats
Phase 3  PC Control          Open Interpreter + open-computer-use + Electron HUD + Hermes activated + gesture control
Phase 4  Workshop Brain      Screen/webcam vision + Mem0 + ChromaDB RAG + YOLO + DepthAnything
Phase 5  Autonomous Agent    Hermes full power + task queue + Discord/Telegram + approval gates
Phase 6  Multi-Device        Tailscale + Phone PWA + Meta Glasses + Raspberry Pi
Phase 7  Cinematic           UE5 MetaHuman + Audio2Face + original voice + projector
```

---

## MVP Acceptance Criteria

### Phase 0 Done When:
- [x] Type question → JARVIS responds with correct personality (sir, concise, in-character)
- [x] Intent router classifies correctly: respond / tool / memory / vision / confirm (20 test examples)
- [x] Audit log saves every interaction to disk
- [x] `dry_run: true` narrates without executing
- [x] Kill switch stops everything (voice command + Ctrl+Alt+J)
- [x] `config.yaml` switches models without code changes
- [x] All test scripts in `tests/` pass independently
- [ ] GitHub repo live — public README, one-command setup

### Phase 1 Done When:
- [ ] Boot sequence: music → animation → morning report → HUD live
- [ ] Morning report: time + GPU temp + last project + task count
- [ ] Wake word fires in workshop environment (fan noise present)
- [ ] Push-to-talk fallback works
- [ ] STT transcribes accurately, sub 0.5s on GPU
- [ ] TTS starts before full sentence generated (streaming)
- [ ] Self-suppression confirmed — JARVIS never hears itself (10 tests)
- [ ] UI sound effects at every pipeline state
- [ ] Verbal error recovery speaks on Ollama disconnect
- [ ] Emergency stop works mid-response

---

## Known Risks — Watch For These

1. **Model cold-load** — set `OLLAMA_KEEP_ALIVE=-1` before anything else
2. **Self-triggering loop** — `is_speaking=True` must mute wake word during TTS output
3. **Qwen3 reasoning loops** — use thinking-off mode for tool calls
4. **Qwen3-VL name** — it is `qwen3-vl`, NOT `qwen3.5-vl`. Requires Ollama 0.12.7+.
5. **Hermes too early** — requires 32B model + 24GB VRAM. Only Phase 3 + 5090.
6. **steffenpharai/Jarvis Jetson deps** — strip Jetson-specific CUDA configs when porting to 5090
7. **Safety before desktop control** — safety.py and dry_run must work before Phase 3 runs anything
8. **Integration chaos** — enforce `[ACTION:TYPE:PARAMS]` from day one, no exceptions

---

## Current Status
```
Phase:        1 — IN PROGRESS (voice + boot scaffold built; live hardware validation pending)
Last built:   app/voice/tts.py, app/voice/sounds.py, app/voice/vad.py,
              app/voice/stt.py, app/voice/wake_word.py, app/voice/audio_stream.py,
              app/boot.py, scripts/setup_autostart.py
Last tested:  tests/tts_test.py, tests/stt_test.py, tests/wake_word_test.py,
              tests/boot_test.py, tests/router_test.py, tests/pipeline_test.py,
              tests/safety_test.py, tests/ollama_test.py (PASS)
Hardware:     4070 Ti active (5090 arriving soon)
Active model: qwen3:14b (upgrade to qwen3:32b when 5090 arrives)
Next:         Install/verify Piper model files and live audio packages, then run real mic/TTS
              acceptance: wake word, push-to-talk, STT, self-suppression, full voice loop.
Notes:        dry_run=true in config.yaml. Phase 1 modules use lazy imports/fallbacks so tests
              pass before hardware setup. Live qwen3:14b prompt latency remains high.
```

> Update this section at the end of every Claude Code session.
> Format: Phase, last file built, last test run, any blockers.

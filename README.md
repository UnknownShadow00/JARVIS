# JARVIS

A local-first, fully autonomous AI assistant modeled on Tony Stark's JARVIS. Runs 100% on personal hardware — no API costs, no cloud dependency. Controls the PC, watches the screen and webcam, helps with coding, runs assigned tasks autonomously, and sends status updates via Discord and Telegram.

> Built on Windows with an RTX 5090. Every phase ships something real and demo-able.

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | RTX 4070 Ti (12GB VRAM) | RTX 5090 (32GB VRAM) |
| RAM | 32GB | 64GB |
| OS | Windows 10/11 | Windows 11 |
| Mic | Any USB mic | Studio condenser |

---

## Quick Start

**1. Clone and install dependencies**
```bash
git clone https://github.com/UnknownShadow00/JARVIS.git
cd JARVIS
pip install -r requirements.txt
```

**2. Install Ollama and pull models**
```bash
# https://ollama.com — set these before starting Ollama:
$env:OLLAMA_KEEP_ALIVE = "-1"
$env:OLLAMA_NUM_PARALLEL = "2"

ollama pull qwen3:14b       # main brain (4070 Ti)
ollama pull gemma3:4b       # intent router
```

**3. Install Piper TTS**
```bash
python scripts/install_piper.py
```

**4. Configure**
Edit `config.yaml`. Set `dry_run: true` to test without executing actions.

**5. Run**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**6. Talk to JARVIS**
```bash
# REST
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What time is it?\"}"

# WebSocket (streaming TTS)
wscat -c ws://localhost:8000/ws
```

---

## Model Stack

| Model | Role | VRAM |
|-------|------|------|
| Qwen3 14B | Primary brain (4070 Ti) | ~10GB |
| Qwen3 32B | Primary brain (5090) | ~20GB |
| Qwen2.5-Coder 32B | Coding tasks | ~20GB |
| Gemma3 4B | Intent router (<50ms) | ~3GB |
| Qwen3-VL | Vision (screen/webcam) | ~8GB |

---

## Phase Roadmap

| Phase | Name | Status |
|-------|------|--------|
| 0 | Core Brain — FastAPI + router + tools + kill switch | **Complete** |
| 1 | Voice + Boot — wake word, STT, TTS, boot sequence | In progress — unit + hardware smoke tests passing; full spoken loop pending |
| 2 | Tools & Web — app launch, file ops, web search, shell | Planned |
| 3 | PC Control — Open Interpreter, Electron HUD, gestures | Planned |
| 4 | Workshop Brain — vision, Mem0, ChromaDB RAG, YOLO | Planned |
| 5 | Autonomous Agent — task queue, Discord/Telegram | Planned |
| 6 | Multi-Device — phone PWA, Meta Glasses, Raspberry Pi | Planned |
| 7 | Cinematic — UE5 MetaHuman, Audio2Face | Far future |

---

## Project Structure

```
app/
  brain/      LLM client, intent router, prompt builder, kill switch
  voice/      wake word, VAD, STT, TTS, SFX, boot sequence
  tools/      safety-gated system, web, app, and file tools
  logs/       structured JSONL audit logger
  server.py   FastAPI /health, /chat REST, /ws WebSocket
tests/        unit + hardware smoke tests
scripts/      setup utilities (install_piper.py, setup_autostart.py)
config.yaml   single source of runtime configuration
```

---

## Safety

All actions use a 4-level safety system enforced in every tool:

| Level | Name | Behavior |
|-------|------|----------|
| 0 | Safe | Always execute |
| 1 | Reversible | Execute unless confidence < 75% |
| 2 | Risky | Always confirm with user |
| 3 | Blocked | Never execute automatically |

Set `dry_run: true` in `config.yaml` to narrate all actions without executing.

---

## Kill Switch

- Voice command: *"JARVIS, shut it down"*
- Keyboard: `Ctrl+Alt+J`

---

## Running Tests

```bash
# Unit tests (no hardware required)
python -m pytest tests/ -m "not manual"

# Hardware smoke tests (mic + speakers required)
python -m pytest tests/ -m manual
```

Current checkpoint: Phase 0 is complete. Phase 1 voice modules, Piper setup, and manual hardware smoke tests pass; the final spoken loop (`hey jarvis, what time is it?` through wake word, VAD, STT, routing, streaming TTS, SFX, and self-suppression) still needs live confirmation before Phase 1 is closed.

---

## License

MIT

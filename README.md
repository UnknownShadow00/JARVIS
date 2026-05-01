# JARVIS

JARVIS is a local-first assistant for voice, tools, and workstation control, built around Ollama models, a FastAPI runtime, safety-gated tools, and structured audit logs. Phase 0 focuses on the core brain: configuration, routing, prompt discipline, dry-run execution, the first tools, and a minimal REST/WebSocket server.

## Hardware Requirements

- Windows workstation
- Python 3.11+
- Ollama running locally
- NVIDIA GPU recommended for local model latency
- Tested Phase 0 model targets: `qwen3:14b` for main chat and `gemma3:4b` for routing

## Setup

```powershell
git clone https://github.com/[username]/jarvis
cd jarvis
pip install -r requirements.txt
ollama pull qwen3:14b
ollama pull gemma3:4b
uvicorn app.main:app --reload
```

Configuration lives in `config.yaml`. Model names, Ollama host, server ports, safety mode, dry-run mode, paths, logging, and future voice settings should be changed there rather than hardcoded in Python.

## Test Commands

```powershell
python tests/ollama_test.py
$env:PYTHONPATH='.'; python tests/router_test.py
$env:PYTHONPATH='.'; python tests/pipeline_test.py
$env:PYTHONPATH='.'; python tests/safety_test.py
```

Manual Phase 0 checks:

- `open VS Code` should narrate dry-run behavior when `safety.dry_run: true`.
- `what is 2+2` should return a concise JARVIS-style response.
- `JARVIS stop`, `cancel`, `freeze`, or `abort` should deactivate processing without crashing the server.

## Project Structure

```text
app/
  brain/      intent routing, LLM client, prompt builder, kill switch, response cleanup
  logs/       structured JSONL audit logger
  tools/      safety-gated system, web, app, and file tools
  voice/      Phase 1 voice pipeline placeholder
  server.py   FastAPI /health, /chat, and /ws endpoints
tests/        standalone Phase 0 acceptance scripts
config.yaml   single source of runtime configuration
```

## Current Phase

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Core brain, router, safety, tools, FastAPI server | Hardening |
| 1 | Wake word, VAD, STT, TTS, SFX, boot sequence | Not started |
| 2 | HUD/frontend voice experience | Not started |
| 3 | Computer control and agent execution | Not started |
| 4 | Vision and memory | Not started |
| 5 | Remote communications | Not started |
| 6 | Automation polish and reliability | Not started |
| 7 | Voice clone and advanced personalization | Not started |

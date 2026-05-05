# JARVIS — Local AI Assistant

Tony Stark-style AI running 100% on your hardware. No API costs. No cloud.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688)
![Ollama](https://img.shields.io/badge/Ollama-local%20models-black)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Tests passing](https://img.shields.io/badge/Tests-passing-brightgreen)

JARVIS is a local-first AI assistant inspired by Tony Stark's JARVIS: voice-enabled, tool-using, screen-aware, automation-capable, and designed to run entirely on your own machine. The backend is Python/FastAPI, the model stack is local via Ollama, and the long-term system layers in autonomy, vision, memory, HUD interfaces, and cinematic presence without depending on cloud APIs.

## Feature Matrix

| Phase | Name | What it does |
|-------|------|---------------|
| 0 | Core Brain | FastAPI server, local LLM routing, tool registry, audit logging, kill switch, config-driven model selection |
| 1 | Voice + Boot | Wake word, VAD, GPU STT, streaming TTS, boot sequence, morning report, response audio cues |
| 2 | Tools & Web | App launch, file operations, browser control, shell commands, web search, system stats, health endpoints |
| 3 | PC Control | Open Interpreter bridge, computer-use tooling, Electron HUD, Hermes Agent activation, gesture control |
| 4 | Workshop Brain | Screen and webcam vision, Mem0 memory, local RAG, object detection, depth awareness, workshop assistance |
| 5 | Autonomous Agent | Hermes-powered task queue, scheduler, reporting, Discord/Telegram updates, approval-gated autonomy |
| 6 | Multi-Device | Tailscale access, phone PWA, Meta glasses support, remote presence across devices |
| 7 | Cinematic | UE5 bridge, MetaHuman pipeline, Audio2Face integration, hologram frontend, voice-clone path |

## Hardware Requirements

JARVIS is built for local inference first. It can start on a strong consumer GPU and scales up to a dedicated always-on host.

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 12 GB (RTX 4070 Ti class) | 32 GB (RTX 5090 class) |
| System RAM | 32 GB | 64 GB |
| OS | Windows 10/11 | Windows 11 |
| CUDA | Required for fast STT / local inference workflows | Latest NVIDIA drivers + CUDA stack |

Notes:
- Use `qwen3:14b` on a 4070 Ti-class system as the fallback baseline.
- Hermes Agent and the full 32B stack are intended for the 5090-class configuration.
- `qwen3-vl` requires a recent Ollama build.

## Quick Start

### Prerequisites

- Ollama installed and running locally
- Python `3.11+`
- NVIDIA CUDA environment available
- Git

Before starting Ollama, set:

```powershell
$env:OLLAMA_KEEP_ALIVE="-1"
$env:OLLAMA_NUM_PARALLEL="2"
```

### Install

```bash
git clone https://github.com/UnknownShadow00/JARVIS.git
cd JARVIS
pip install -r requirements.txt
```

### Configure

Copy the example config, then set the model names for your hardware:

```powershell
Copy-Item config.yaml.example config.yaml
```

Key model fields in `config.yaml`:

```yaml
models:
  main: "qwen3:14b"
  coder: "qwen2.5-coder:32b"
  router: "gemma3:4b"
  vision: "qwen3-vl"
```

Recommended Ollama pulls:

```bash
ollama pull qwen3:14b
ollama pull gemma3:4b
ollama pull qwen3-vl
```

Upgrade to the 32B stack on 5090-class hardware when ready.

### Run

```bash
python -m app.main
```

The FastAPI app exposes the REST and WebSocket brain used by the desktop and voice layers.

## Architecture

JARVIS is organized as a three-layer local agent stack:

1. **FastAPI Brain**: the custom backend that owns routing, prompts, tools, safety, logging, voice orchestration, and API/WebSocket transport.
2. **Hermes Agent**: the autonomy layer that handles scheduled tasks, messaging, persistent workflows, and broader tool-driven operation.
3. **OpenJarvis**: the optimization and trace-driven skill layer used to refine long-running behavior after enough real interactions accumulate.

In shorthand:

```text
User / Devices
      |
      v
FastAPI Brain  -->  Hermes Agent  -->  OpenJarvis
```

## Voice Pipeline

```text
Mic Input
   |
   v
OpenWakeWord
   |
   v
VAD Gate
   |
   v
faster-whisper STT
   |
   v
Intent Router / Brain
   |
   +--> Tool Calls / Memory / Vision
   |
   v
TTS (Piper / Kokoro / Chatterbox)
   |
   v
Speakers + HUD Feedback
```

## Project Structure

```text
JARVIS/
├── app/
│   ├── agent/        # scheduler, reporting, task queue, sensor state
│   ├── brain/        # LLM routing, prompts, planner, morning report, kill switch
│   ├── comms/        # Discord, Telegram, UE5, Audio2Face bridges
│   ├── computer/     # screenshots, vision, gestures, safety, mouse/keyboard control
│   ├── memory/       # memory client and local RAG
│   ├── network/      # Tailscale integration
│   ├── tools/        # browser, files, shell, interpreter, health, system tools
│   ├── voice/        # wake word, VAD, STT, TTS, push-to-talk, audio stream
│   ├── main.py
│   └── server.py
├── frontend/
│   ├── electron/     # desktop HUD shell
│   ├── hologram/     # cinematic frontend
│   └── pwa/          # mobile interface
├── scripts/          # setup and diagnostics
├── tests/            # backend, voice, tools, autonomy, frontend integration coverage
├── config.yaml.example
├── requirements.txt
└── CLAUDE.md
```

## Roadmap

All 8 phases complete. Next: 5090 migration, content creation.

Current follow-on priorities:
- Switch the production stack from the active 4070 Ti fallback to the 5090-first model profile
- Finalize public repo polish, demos, and creator-facing documentation
- Continue content capture for YouTube/TikTok around the build process and local AI workflow

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the short workflow: fork, branch, keep changes scoped, and make sure tests pass before opening a PR.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Built with Claude Code. 100% local. Zero API costs.

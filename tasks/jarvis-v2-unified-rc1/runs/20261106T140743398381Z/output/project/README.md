# JARVIS — Local AI Assistant

Current release candidate: [offline release readiness](tasks/jarvis-v2-release-readiness-r1/REPORT.md).
Authority routes now require credentials even on loopback. Real execution stays
disabled. See [the candidate contract and limits](docs/release_candidate.md).
Earlier sprint and live-suite results below retain their historical source scope.


Current offline application milestone: [secure execution integration and readiness](tasks/jarvis-end-to-end-readiness-r1/REPORT.md).
The actual application now integrates signed synthetic IPC, durable receipts and
explicit offline recovery. Real tools, confirmation dispatch, dictation effects
and host resource mutation controls are closed. Older live-readiness and tool
results below describe historical source, not this release's live authorization.
See [the current execution/operator contract](docs/end_to_end_readiness.md).


Tony Stark-style AI running 100% on your hardware. No API costs. No cloud.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688)
![Ollama](https://img.shields.io/badge/Ollama-local%20models-black)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Tests passing](https://img.shields.io/badge/Tests-passing-brightgreen)

JARVIS is a local-first AI assistant inspired by Tony Stark's JARVIS: voice-enabled, tool-using, screen-aware, automation-capable, and designed to run entirely on your own machine. The backend is Python/FastAPI, the model stack is local via Ollama, and the long-term system layers in autonomy, vision, memory, HUD interfaces, and cinematic presence without depending on cloud APIs. The API binds to localhost by default; LAN or Tailscale access must be enabled intentionally.

## Feature Matrix

Recovery proposals and decisions now have a durable authenticated offline registry,
protected witness renewal, explicit crash reconciliation and non-activating receipts.
See the [recovery decision guide](docs/recovery_decisions.md) and
[sprint 5 evidence](tasks/jarvis-recovery-decisions-r1/REPORT.md).

Authority enrollment now requires an explicit offline ceremony; normal startup
never creates a missing store. [Enrollment and branch guide](docs/authority_enrollment.md)
describes durable genesis, restart verification and read-only restored-branch
proposals. Trusted provisioning is required before application startup. See
[sprint 4 evidence](tasks/jarvis-authority-enrollment-r1/REPORT.md).

| Phase | Name | Status | What exists now |
|-------|------|--------|-----------------|
| 0 | Core Brain | Complete | FastAPI server, local LLM routing, tool registry, audit logging, kill switch, config-driven model selection |
| 1 | Voice + Boot | Partially complete | Wake word, VAD, GPU STT, TTS, boot sequence, morning report, response audio cues; live voice still needs attended hardware validation |
| 2 | Tools & Web | Mostly complete | App launch, file operations, browser control, shell commands, web search, system stats, health endpoints |
| 3 | PC Control | Partially complete | Screenshot, mouse/keyboard safety gates, vision path, Electron HUD, gesture stubs; Open Interpreter is intentionally removed |
| 4 | Workshop Brain | Stubbed/deferred | Vision model path exists; Mem0, ChromaDB RAG, object detection, and depth remain explicit stubs until hardware/model readiness |
| 5 | Autonomous Agent | Partially complete/stubbed | Local task queue, scheduler API, reporting, Discord/Telegram stubs, approval gates; Hermes is documented but not active |
| 6 | Multi-Device | Partially complete | Tailscale status helper and phone PWA exist; remote access stays disabled by default |
| 7 | Cinematic | Stubbed/deferred | UE5, Audio2Face, hologram frontend, and voice-clone hooks exist; live external runtimes are not wired |

Audit continuity and disposable restoration: [current guide](docs/audit_disaster_recovery.md)
describes opt-in checkpoint rollover, external trust references, audited archive
verification and crash-safe reconstruction into inert disposable artifacts.
See [sprint 3 evidence](tasks/jarvis-audit-disaster-recovery-r1/REPORT.md).

Operator recovery and ledger protection: [current guide](docs/operator_recovery.md)
provides authenticated read-only diagnostics, protected checkpoints, bounded
exports and archive eligibility without deleting history. Real execution stays
disabled. See [sprint 2 evidence](tasks/jarvis-operator-ledger-r1/REPORT.md).

## Hardware Requirements

Task/schedule API compatibility: the current transactional authority requires a
retained canonical UUID4 for each public logical mutation and returns durable
receipts. A committed receipt records admission or a cancellation decision;
real execution remains disabled. An explicitly enabled offline synthetic pipeline
now connects policy, queue, execution, durable results and restart recovery; see
[the sprint evidence](tasks/jarvis-offline-execution-r1/REPORT.md). See
[the current contract](docs/task_api.md) before
connecting a client. The in-repository CLI/HUD/PWA do not submit queue mutations;
external clients remain a rollout prerequisite. Hermes integration is planned
and cannot replace or run a parallel queue writer.

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

The FastAPI app exposes the REST and WebSocket brain used by the desktop and voice layers. It does not start microphone, wake-word, or hotkey listeners unless explicitly enabled in `config.yaml` or through the separate boot flow.

### Resource Management

JARVIS supports ACTIVE, LIGHT_SLEEP, DEEP_SLEEP, and WAKING runtime status output so idle operation can release loaded models, voice workers, audio streams, scheduler loops, UI sockets, CUDA caches, and JARVIS-owned worker processes.

```powershell
jarvis sleep --light
jarvis sleep --deep
jarvis wake
jarvis status
jarvis shutdown
```

From a clone without a PATH alias, run `.\jarvis.cmd status` or `python -m app.cli status`. See [docs/resource_management.md](docs/resource_management.md) for state behavior, Windows shared GPU memory notes, and sleep/deep-sleep usage expectations.

## Architecture

JARVIS is organized as a three-layer local agent stack:

1. **FastAPI Brain**: the custom backend that owns routing, prompts, tools, safety, logging, voice orchestration, and API/WebSocket transport.
2. **Hermes Agent**: the planned autonomy layer for scheduled tasks, messaging, persistent workflows, and broader tool-driven operation. It is documented but not active in the default local setup.
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
│   ├── tools/        # browser, files, shell, health, system tools
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

## Current Status

The current release is an offline, synthetic authority and execution application. Admitted startup requires trusted enrollment and witness provisioning. Real tool dispatch and host mutation controls remain closed; HUD/PWA assets and optional voice/model paths do not establish live readiness.

See `PROJECT_STATUS.md` for the current verified state, run commands, blockers, and next priorities.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the short workflow: fork, branch, keep changes scoped, and make sure tests pass before opening a PR.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Built with Claude Code. 100% local. Zero API costs.

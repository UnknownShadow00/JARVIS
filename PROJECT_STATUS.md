# JARVIS Project Status

Last verified: 2026-05-14

## Current Real Project State

JARVIS is a local-first Python/FastAPI assistant backend with Ollama-based LLM routing, a modular tool registry, local audit logging, basic task/scheduler APIs, local memory stubs, voice pipeline components, and desktop/mobile HUD frontends.

The project is not a fully complete always-on assistant yet. Phase 0-3 surfaces are usable or partially usable. Phase 4+ surfaces are intentionally explicit stubs unless they can run safely on the current local machine without the future dedicated server.

Default access policy is localhost-only:

- `config.yaml` and `config.yaml.example` now bind `server.host` to `127.0.0.1`.
- Non-loopback hosts such as `0.0.0.0` are rejected unless `server.remote_access_enabled: true`.
- API startup does not start the microphone, wake-word loop, voice pipeline, or hotkey listener by default.
- Future remote access should be enabled intentionally through Tailscale, not open LAN binding.

## What Works

- FastAPI app import and route definitions: `app/main.py`, `app/server.py`.
- REST health routes: `/health`, `/health/tools`, `/health/readiness`.
- Chat route with intent routing, direct replies, Ollama fallback handling, tool dispatch, dry-run narration, and confirmation gates.
- WebSocket route at configured `server.websocket_path`.
- Tool registry: browser, web search, apps, files, shell, calendar, screenshot, system stats, mouse/keyboard, vision wrapper, and deferred integration tools.
- Browser routing for URL/domain requests such as `open google.com`.
- Screenshot and screen/webcam vision tool path, assuming local dependencies, screen/camera access, Ollama, and the configured vision model are available.
- Procedural memory route backed by `skills.md`.
- Task queue and scheduler API surfaces.
- PWA static mount at `/pwa`.
- Electron HUD files and package metadata.
- Tailscale status helper.
- Readiness report and tool readiness smoke scripts.
- Docker build file now exists for the existing `docker-compose.yml`.

## What Partially Works

- Voice: wake word, VAD, STT, TTS, push-to-talk, and boot code exist, but live voice requires attended microphone/speaker validation. Backend API startup intentionally does not activate voice automatically.
- Vision: routing now calls the vision tool for `vision` intents, but useful output depends on a working screenshot/webcam path, Ollama availability, and `models.vision`.
- Memory: procedural memory works; Mem0 and ChromaDB are disabled by default and return explicit stubs.
- Scheduler: the API and APScheduler integration exist and now start during FastAPI lifespan, but real scheduled task behavior still needs long-running validation.
- Comms: Discord and Telegram modules exist but remain disabled until packages, tokens, channel IDs, and approval flows are configured.
- Tailscale/PWA: local PWA works as static assets; remote access remains an intentional future step.
- Docker Compose: now has a Dockerfile, loopback-bound published ports, and an Ollama service URL override. It still needs Docker/GPU validation on the target host.

## What Is Stubbed

- Mem0 long-term memory unless `memory.mem0_enabled` and the package/service are configured.
- ChromaDB RAG unless `memory.chromadb_enabled` is true.
- Browser-use live execution. The tool returns action plans and avoids live browser-agent automation by default.
- Open computer-use live GUI automation.
- Kasa control writes and smart-device operation until real devices are selected.
- CAD/printing beyond design/export planning.
- MCP client calls beyond the whitelist/stub layer.
- UE5 MetaHuman, Audio2Face, and hologram external runtime wiring.
- Voice clone conditioning until a real private voice reference WAV exists.
- Hermes Agent. It is documented, but not active in the default app flow.
- OpenJarvis optimization until enough real traces exist.

## What Is Broken Or Blocked

- Dedicated server hardware is not installed, so 5090 model profile, always-on service behavior, GPU container validation, and full hardware validation are blocked.
- Live voice cannot be marked complete until an attended wake/PTT -> STT -> response -> TTS playback run passes.
- Docker was not validated in this pass because Docker is not available in the current environment.
- Ollama-dependent commands can fail if Ollama is not running or models are missing.
- Docker Compose needs target-host validation with NVIDIA container support before it can be considered deployment-ready.
- Some docs and historical logs still describe older phase states. Current truth should be `PROJECT_STATUS.md`, `README.md`, `config.yaml`, and tests.

## What Was Fixed During This Review

- `app/config.py`: added localhost-by-default validation and a container-friendly `JARVIS_OLLAMA_BASE_URL` override.
- `config.yaml`, `config.yaml.example`: switched server host to `127.0.0.1` and added explicit remote/voice/hotkey startup flags.
- `app/server.py`: moved startup checks into lifespan, starts/stops scheduler in lifespan, registers kill callbacks idempotently, and prevents default voice/hotkey startup.
- `app/main.py`: added a real `python -m app.main` uvicorn entry point and removed deprecated startup event usage.
- `app/brain/kill_switch.py`: made hotkey listener startup idempotent.
- `app/brain/router.py`: fixed URL/domain requests so they route to browser control instead of app launch or web search.
- `app/server.py`: wired `vision` intents to the vision tool and `retrieve_memory` intents to procedural/Mem0/RAG context.
- `app/memory/rag_client.py`: made ChromaDB obey `memory.chromadb_enabled` and use the configured collection name.
- `app/computer/vision.py`: hardened Ollama vision response parsing instead of assuming a `response` key exists.
- `.gitignore`: changed root runtime ignores so `app/logs/audit.py` and `app/logs/__init__.py` can be tracked.
- `requirements.txt`: added missing clean-clone dependencies for `pydantic-settings`, `apscheduler`, and `icalendar`.
- `Dockerfile`, `docker-compose.yml`: added a backend Dockerfile, loopback-only published ports, and container Ollama URL override.
- `frontend/pwa/manifest.json`: scoped PWA start URL to the `/pwa` mount.
- Tests: added coverage for localhost config validation, Docker/Ollama env override, disabled RAG behavior, vision intent wiring, memory intent wiring, PWA manifest scope, default lifespan behavior, and browser URL routing.
- Docs: updated README, 5090 migration notes, tool readiness inventory, CLAUDE status, and HANDOFF archive note.

## Remaining Blockers

- Install and validate the dedicated server GPU/driver/CUDA/Ollama stack.
- Confirm the required Ollama models are pulled and usable on the final hardware.
- Run attended live voice validation with real microphone and speaker devices.
- Decide when to intentionally enable Tailscale remote access.
- Provide real comms tokens/channel IDs only when remote approval flows are ready.
- Provide a real voice clone WAV if Chatterbox voice conditioning is desired.
- Validate Docker Compose with NVIDIA runtime on the target machine.

## Hardware/Server-Dependent Tasks

- Switch model profile to the 5090 stack with `python scripts/switch_models.py --profile 5090`.
- Pull 32B and vision models on the server.
- Validate GPU memory, first-token latency, STT latency, and TTS playback.
- Decide whether the server hosts audio devices directly or receives audio from a client device.
- Enable Tailscale remote access only after local validation passes.
- Run long-lived scheduler and task queue validation.
- Validate UE5/Audio2Face/hologram external runtime paths if cinematic mode becomes a priority.

## Recommended Next Priorities

1. Finish validation of this stabilization pass with full test collection and targeted runtime checks.
2. Run attended live voice smoke test on the current machine.
3. Validate Ollama model availability and vision model behavior.
4. Keep Phase 4+ integrations as stubs until the dedicated server is installed.
5. Validate Docker Compose on a machine with Docker and NVIDIA runtime.
6. After hardware install, switch model profile, retest clean clone, and only then enable Tailscale remote access.

## Exact Commands

Install backend:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Electron HUD dependencies:

```powershell
npm.cmd install --prefix frontend/electron
```

Run backend API locally:

```powershell
python -m app.main
```

Alternative backend command:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run separate boot flow without automatically starting voice:

```powershell
python -m app.boot
```

Run Electron HUD:

```powershell
npm.cmd start --prefix frontend/electron
```

Open PWA after backend starts:

```text
http://127.0.0.1:8000/pwa/
```

Run readiness checks:

```powershell
python tasks/readiness_report.py
python tasks/tool_readiness_smoke.py
```

Run focused stabilization tests:

```powershell
pytest -q tests/test_config_check.py tests/test_rag_client.py tests/test_server_integration.py tests/router_test.py tests/test_pwa_serve.py tests/test_readiness_report.py -p no:cacheprovider
```

Collect the full test suite:

```powershell
pytest --collect-only -q -p no:cacheprovider
```

Run the full suite:

```powershell
pytest -q -p no:cacheprovider
```

Run live voice validation when attended:

```powershell
python tasks/manual_voice_smoke.py --live --speak --listen-timeout 45
```

Run mock voice validation:

```powershell
python tasks/manual_voice_smoke.py --mock-pipeline
```

Run dependency checks:

```powershell
python -m pip check
npm.cmd audit --audit-level=moderate --prefix frontend/electron
```

Run Docker Compose when Docker/NVIDIA runtime is available:

```powershell
docker compose up --build
```

## Latest Validation Results

- `pytest -q tests/test_config_check.py tests/test_rag_client.py tests/test_server_integration.py tests/router_test.py tests/test_pwa_serve.py tests/test_readiness_report.py -p no:cacheprovider`: 40 passed, 1 warning.
- `python -m pip check`: no broken requirements found.
- `npm.cmd audit --audit-level=moderate --prefix frontend/electron`: 0 vulnerabilities.
- `pytest --collect-only -q -p no:cacheprovider`: 320 tests collected.
- `pytest -q -p no:cacheprovider`: 320 passed, 0 skipped, 4 warnings (third-party only: GPUtil + pygame).
- `python tasks/readiness_report.py`: all required readiness checks pass (after starting Ollama via `ollama serve`).
- `python tasks/tool_readiness_smoke.py`: 10 readiness checks passed.
- `docker --version`: failed because Docker is not installed or not on PATH in this environment.

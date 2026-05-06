# RTX 5090 Migration Runbook

This runbook moves JARVIS from the active RTX 4070 Ti Super Windows 11 PC to the future RTX 5090 32 GB Windows 11 server without rediscovering setup steps.

## Scope

- Keep the current 4070 Ti build working until the 5090 is physically ready.
- Move core JARVIS, Ollama models, Electron/PWA assets, voice pipeline config, and local validation commands.
- Keep OrcaSlicer and live 3D printing out of scope.
- Keep UE5/Audio2Face as a separate manual integration unless it becomes required before migration.
- Keep Open Interpreter optional; it does not block migration.

## Hardware Assumptions

- RTX 5090 with 32 GB VRAM installed and visible in Device Manager.
- Windows 11 with current NVIDIA driver and CUDA runtime support.
- 64 GB system RAM preferred.
- Server can stay on and reach the local network/Tailscale.
- Microphone/speakers can be attached or routed from the client PC/phone after the move.

## Files And Folders To Copy

Copy or clone the repo, then preserve local-only assets that are ignored by git:

- `config.yaml`
- `models/` if Piper voice models are not re-downloaded
- `assets/audio/` custom sound assets
- `data/` only if local traces, memory, or Chroma data should move
- `logs/` only if audit history is useful
- Any private voice clone WAV kept outside git

Do not copy `node_modules/`, `.pytest_cache/`, `__pycache__/`, or temporary WAV files.

## Step 1: Install Base Tools

```powershell
winget install Git.Git
winget install Python.Python.3.13
winget install Ollama.Ollama
winget install OpenJS.NodeJS.LTS
```

Verify:

```powershell
git --version
python --version
node --version
npm --version
ollama --version
```

`qwen3-vl` requires Ollama `0.12.7` or newer.

## Step 2: Set Ollama Environment

Set these before starting Ollama:

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "-1", "Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "2", "Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_FLASH_ATTENTION", "1", "Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_KV_CACHE_TYPE", "q8_0", "Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_BATCH", "512", "Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "2", "Machine")
```

Restart Ollama or reboot after setting them. If Qwen3 slows down or fails to keep layers on GPU, test with `OLLAMA_FLASH_ATTENTION=0`.

## Step 3: Pull Models

```powershell
ollama pull qwen3:32b
ollama pull qwen2.5-coder:32b
ollama pull gemma3:4b
ollama pull qwen3-vl
```

Recreate the no-think daily model:

```powershell
ollama create qwen3-nothink -f Modelfile.nothink
ollama list
```

On the 5090, update `Modelfile.nothink` to use the desired 32B base if daily voice latency is acceptable; otherwise keep the 14B no-think model for voice and use 32B for deep work.

## Step 4: Clone And Install JARVIS

```powershell
git clone https://github.com/UnknownShadow00/JARVIS.git
cd JARVIS
python -m pip install --upgrade pip
pip install -r requirements.txt
npm.cmd install --prefix frontend/electron
```

If Piper assets were not copied:

```powershell
python scripts/install_piper.py
```

## Step 5: Switch To 5090 Profile

```powershell
python scripts/switch_models.py --profile 5090
```

Expected config changes:

- `models.main`: `qwen3:32b` or the selected 5090 daily model
- `models.coder`: `qwen2.5-coder:32b`
- `models.vision`: `qwen3-vl`
- `models.main_context`: `32768`
- `models.coder_context`: `32768`

Keep `safety.dry_run: false` only after local voice/tool validation passes.

## Step 6: Voice Clone

Voice clone is intentionally skipped in the current pre-5090 checkpoint because no real private 10-second WAV is available while unattended.

When ready:

1. Record a clean 10-second WAV in a quiet room.
2. Store it outside git, for example `C:\Users\Shadow\JARVIS_PRIVATE\voice_ref.wav`.
3. Set `voice.voice_clone_path` in `config.yaml` to that absolute path.
4. Run TTS validation.

Chatterbox must continue to work without a clone path and must fall back to Kokoro/Piper on import/runtime failure.

## Step 7: Validation Commands

Run from repo root:

```powershell
python -m pip check
npm.cmd audit --audit-level=moderate --prefix frontend/electron
python tasks/readiness_report.py
python tasks/tool_readiness_smoke.py
python tasks/manual_voice_smoke.py --mock-pipeline
pytest tests/test_phase8_integrations.py tests/test_readiness_report.py tests/test_tool_readiness_smoke.py tests/test_boot_integration.py tests/test_boot_events.py tests/tts_test.py tests/test_tts_chatterbox.py tests/test_push_to_talk.py tests/test_ptt_and_killswitch.py tests/voice_pipeline_test.py -q --tb=short
pytest tests/ -q --tb=short
git status --short --branch
```

Attended live voice validation:

```powershell
python tasks/manual_voice_smoke.py --live --speak --listen-timeout 45
```

During the listen window, use the wake word or hold `ctrl+space`, speak one short request, then test the kill-switch/cancel path.

## Step 8: Optional Integrations

- `browser-use`: installed/importable; live execution remains intentionally stubbed until browser-agent automation is enabled.
- `python-kasa`: installed/importable; discovery/status only until a real device is selected.
- `build123d`: installed/importable; dry-run CAD design/export only.
- FastMCP/MCP: whitelist stub is present; live MCP client calls require explicit server setup.
- CLI harness: OBS/FFmpeg/Blender readiness only.
- OrcaSlicer: skipped because 3D printing is out of scope.
- Open Interpreter: optional and currently non-blocking.

## Step 9: Post-Move Cleanup

- Update `CLAUDE.md` hardware status so the 5090 server is active.
- Update `tasks/tool-readiness-inventory.md` with real server validation evidence.
- Update `tasks/todo.md` after attended live voice passes.
- Commit the migration checkpoint after tests pass.

## Rollback

Return to the 4070 Ti profile:

```powershell
python scripts/switch_models.py --profile 4070ti
```

That restores the 14B/4070 Ti model profile while leaving the repo and validation commands unchanged.

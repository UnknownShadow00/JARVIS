# JARVIS Resource Management

JARVIS has three runtime resource states:

| State | Purpose | What stays alive | What is released |
|-------|---------|------------------|------------------|
| ACTIVE | Normal operation | FastAPI, scheduler, tools, WebSocket UI, optional voice pipeline, STT/TTS/model caches as used | Nothing beyond normal runtime cleanup |
| LIGHT_SLEEP | Fast wake with lower GPU/RAM use | FastAPI and, if configured, the lightweight wake listener | Ollama loaded models, STT model cache, TTS model cache, vision client cache, scheduler loop, voice pipeline, audio mixer, UI WebSocket sessions |
| DEEP_SLEEP | Maximum idle resource freeing | Nothing meaningful by default after `jarvis sleep --deep` or `jarvis shutdown`; optional wake listener can be enabled but defaults off | Everything from LIGHT_SLEEP plus JARVIS-owned FastAPI/HUD/automation worker processes when invoked from the CLI |

The commands are:

```powershell
jarvis sleep --light
jarvis sleep --deep
jarvis wake
jarvis status
jarvis shutdown
```

From the repository without installing a PATH alias, use either:

```powershell
.\jarvis.cmd sleep --deep
python -m app.cli status
```

## Configuration

`config.yaml` controls automatic sleep:

```yaml
resource_mode:
  enabled: true
  idle_timeout_minutes: 10
  deep_sleep_timeout_minutes: 60
  keep_wake_listener_in_light_sleep: true
  keep_wake_listener_in_deep_sleep: false
  auto_light_sleep: true
  auto_deep_sleep: true
  stop_server_on_auto_deep_sleep: true
  preload_primary_model_on_wake: false
  preload_keep_alive: "5m"
```

`stop_server_on_auto_deep_sleep` is on by default so automatic deep sleep exits the FastAPI process after cleanup. That leaves wake-up to `jarvis wake` or another lightweight launcher.

`preload_primary_model_on_wake` is off by default because deep sleep is meant to free resources. Enable it when you prefer a slower wake command but faster first response afterward.

## Ollama Behavior

ACTIVE keeps JARVIS on normal Ollama behavior. The current Ollama default keeps recently used models resident for about five minutes unless the server environment overrides it.

Sleep transitions explicitly unload models through the Ollama API with an empty prompt and `keep_alive: 0`, then fall back to `ollama stop <model>` if the API path is unavailable. This follows Ollama's documented unload behavior: <https://github.com/ollama/ollama/blob/main/docs/api.md>.

`jarvis status` reads `/api/ps` and reports loaded model VRAM from Ollama's `size_vram` field when available.

## Windows Shared GPU Memory

On Windows WDDM, Task Manager may continue showing shared GPU memory, committed memory, or driver-reserved memory after JARVIS unloads models. That does not necessarily mean JARVIS still owns active CUDA work. The useful checks are:

- `jarvis status` loaded Ollama model count should drop to zero.
- `jarvis status` JARVIS process count should drop to zero after deep sleep or shutdown.
- `jarvis status` active CUDA contexts should have no JARVIS-owned entries when `nvidia-smi` is available.
- System shared GPU memory can lag because Windows and the NVIDIA driver may keep reusable allocations or page mappings.

## Current Idle Usage Targets

The exact numbers are hardware and model dependent, so status reports measure live values instead of hardcoding estimates.

| Mode | Expected JARVIS-owned VRAM | Expected JARVIS-owned committed RAM | Notes |
|------|----------------------------|-------------------------------------|-------|
| ACTIVE idle | Whatever Ollama, STT, TTS, vision, and voice caches have loaded | FastAPI plus any loaded Python model caches and HUD/worker processes | Normal model keep_alive applies. |
| LIGHT_SLEEP | Near 0 MB loaded-model VRAM after Ollama unload completes | FastAPI plus optional wake listener only | First real interaction wakes services before handling chat. |
| DEEP_SLEEP | 0 MB loaded-model VRAM expected | 0 MB JARVIS process committed RAM expected after CLI process-stop pass | Wake is a cold start through `jarvis wake`; first response can be slower. |

## Wake Flow

`jarvis wake` starts the FastAPI runtime if it is offline, moves the resource state through WAKING to ACTIVE, restarts only required services, and starts voice only when `server.enable_voice_on_startup` is true. If model preload is enabled, the configured primary model is loaded during wake; otherwise the first request pays the cold-start cost.

"""Runtime resource state management for low-idle JARVIS operation."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
import psutil

from app.config import settings
from app.logs.audit import audit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = PROJECT_ROOT / "data" / "resource_state.json"


class RuntimeState(StrEnum):
    ACTIVE = "ACTIVE"
    LIGHT_SLEEP = "LIGHT_SLEEP"
    DEEP_SLEEP = "DEEP_SLEEP"
    WAKING = "WAKING"


@dataclass
class JarvisProcess:
    pid: int
    name: str
    role: str
    cmdline: str
    rss_mb: float
    committed_mb: float


@dataclass
class TransitionResult:
    state: str
    previous_state: str
    reason: str
    actions: list[str]
    resources: dict[str, Any]


class WakeListener:
    """Small wake-word loop used only while the full voice pipeline is asleep."""

    def __init__(self, manager: "ResourceManager") -> None:
        self._manager = manager
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = None
        self._thread = threading.Thread(target=self._run, name="jarvis-resource-wake-listener", daemon=True)
        self._thread.start()
        audit.log("resource_wake_listener_started", {})

    def stop(self) -> None:
        self._stop_event.set()
        audit.log("resource_wake_listener_stopped", {})

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                from app.voice.wake_word import wake_word

                audio = wake_word.listen(timeout=3.0)
                if audio and not self._stop_event.is_set():
                    audit.log("resource_wake_listener_detected", {"bytes": len(audio)})
                    self._wake_manager()
                    return
            except Exception as exc:  # noqa: BLE001
                audit.log("resource_wake_listener_error", {"error": str(exc)})
                time.sleep(1.0)

    def _wake_manager(self) -> None:
        if self._loop is not None and self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._manager.wake(reason="wake_listener"), self._loop)
            try:
                future.result(timeout=30)
            except Exception as exc:  # noqa: BLE001
                audit.log("resource_wake_listener_error", {"error": str(exc)})
            return

        asyncio.run(self._manager.wake(reason="wake_listener"))


class ResourceManager:
    def __init__(self, state_path: Path = DEFAULT_STATE_PATH) -> None:
        self._state = RuntimeState.ACTIVE
        self._previous_state = RuntimeState.ACTIVE
        self._state_path = state_path
        self._last_activity_at = datetime.now(UTC)
        self._idle_task: asyncio.Task[None] | None = None
        self._wake_listener = WakeListener(self)

    @property
    def state(self) -> RuntimeState:
        return self._state

    @property
    def last_activity_at(self) -> datetime:
        return self._last_activity_at

    def mark_activity(self, source: str = "activity") -> None:
        if self._state == RuntimeState.DEEP_SLEEP:
            return
        self._last_activity_at = datetime.now(UTC)
        audit.log("resource_activity", {"source": source, "state": self._state.value})

    async def ensure_awake_for_interaction(self, source: str = "interaction") -> bool:
        if not settings.resource_mode.enabled:
            self.mark_activity(source)
            return True

        if self._state == RuntimeState.DEEP_SLEEP:
            audit.log("resource_interaction_blocked", {"source": source, "state": self._state.value})
            return False

        if self._state == RuntimeState.LIGHT_SLEEP:
            await self.wake(reason=f"{source}_interaction")

        self.mark_activity(source)
        return True

    async def start_idle_monitor(self) -> None:
        if not settings.resource_mode.enabled:
            return
        if self._idle_task is not None and not self._idle_task.done():
            return
        self._idle_task = asyncio.create_task(self._idle_monitor(), name="jarvis-resource-idle-monitor")
        audit.log(
            "resource_idle_monitor_started",
            {
                "idle_timeout_minutes": settings.resource_mode.idle_timeout_minutes,
                "deep_sleep_timeout_minutes": settings.resource_mode.deep_sleep_timeout_minutes,
            },
        )

    async def stop_idle_monitor(self) -> None:
        if self._idle_task is None:
            return
        self._idle_task.cancel()
        try:
            await self._idle_task
        except asyncio.CancelledError:
            pass
        self._idle_task = None
        audit.log("resource_idle_monitor_stopped", {})

    async def light_sleep(self, reason: str = "manual") -> TransitionResult:
        previous = self._state
        actions: list[str] = []
        self._set_state(RuntimeState.LIGHT_SLEEP, reason)

        await self._stop_voice_services(actions)
        await self._stop_background_services(actions)
        await self._close_ui_connections(actions)
        self._unload_python_models(actions, keep_wake_model=settings.resource_mode.keep_wake_listener_in_light_sleep)
        await self._unload_ollama_models(actions)
        self._release_cuda_contexts(actions)

        if settings.resource_mode.keep_wake_listener_in_light_sleep:
            self._wake_listener.start()
            actions.append("wake_listener_started")
        else:
            self._wake_listener.stop()
            self._unload_wake_model(actions)

        resources = self.resource_report()
        self._write_state(reason=reason, resources=resources)
        audit.log("resource_transition", {"from": previous.value, "to": self._state.value, "reason": reason})
        return TransitionResult(self._state.value, previous.value, reason, actions, resources)

    async def deep_sleep(self, reason: str = "manual", *, terminate_processes: bool = False) -> TransitionResult:
        previous = self._state
        actions: list[str] = []
        self._set_state(RuntimeState.DEEP_SLEEP, reason)

        await self._stop_voice_services(actions)
        await self._stop_background_services(actions)
        await self._close_ui_connections(actions)
        self._unload_python_models(actions, keep_wake_model=settings.resource_mode.keep_wake_listener_in_deep_sleep)
        await self._unload_ollama_models(actions)
        self._release_cuda_contexts(actions)

        if settings.resource_mode.keep_wake_listener_in_deep_sleep:
            self._wake_listener.start()
            actions.append("wake_listener_started")
        else:
            self._wake_listener.stop()
            self._unload_wake_model(actions)

        if terminate_processes:
            stopped = terminate_jarvis_processes(exclude_pids={os.getpid()})
            actions.append(f"terminated_processes:{len(stopped)}")

        resources = self.resource_report()
        self._write_state(reason=reason, resources=resources)
        audit.log("resource_transition", {"from": previous.value, "to": self._state.value, "reason": reason})
        return TransitionResult(self._state.value, previous.value, reason, actions, resources)

    async def wake(self, reason: str = "manual", *, preload_primary_model: bool | None = None) -> TransitionResult:
        previous = self._state
        actions: list[str] = []
        self._set_state(RuntimeState.WAKING, reason)
        self._wake_listener.stop()

        await self._start_required_services(actions)
        should_preload = settings.resource_mode.preload_primary_model_on_wake
        if preload_primary_model is not None:
            should_preload = preload_primary_model
        if should_preload:
            await self._preload_primary_model(actions)

        self._last_activity_at = datetime.now(UTC)
        self._set_state(RuntimeState.ACTIVE, reason)
        resources = self.resource_report()
        self._write_state(reason=reason, resources=resources)
        audit.log("resource_transition", {"from": previous.value, "to": self._state.value, "reason": reason})
        return TransitionResult(self._state.value, previous.value, reason, actions, resources)

    async def shutdown(self, reason: str = "manual") -> TransitionResult:
        return await self.deep_sleep(reason=reason, terminate_processes=True)

    def status(self) -> dict[str, Any]:
        resources = self.resource_report()
        return {
            "state": self._state.value,
            "previous_state": self._previous_state.value,
            "last_activity_at": self._last_activity_at.isoformat(),
            "idle_seconds": round((datetime.now(UTC) - self._last_activity_at).total_seconds(), 1),
            "wake_listener_running": self._wake_listener.is_running(),
            "resource_mode": {
                "enabled": settings.resource_mode.enabled,
                "auto_light_sleep": settings.resource_mode.auto_light_sleep,
                "auto_deep_sleep": settings.resource_mode.auto_deep_sleep,
                "stop_server_on_auto_deep_sleep": settings.resource_mode.stop_server_on_auto_deep_sleep,
                "idle_timeout_minutes": settings.resource_mode.idle_timeout_minutes,
                "deep_sleep_timeout_minutes": settings.resource_mode.deep_sleep_timeout_minutes,
            },
            "resources": resources,
        }

    def resource_report(self) -> dict[str, Any]:
        loaded_models = list_loaded_ollama_models(timeout_seconds=0.5)
        processes = discover_jarvis_processes(exclude_pids=set())
        cuda_contexts = detect_cuda_contexts()
        jarvis_rss_mb = round(sum(process.rss_mb for process in processes), 1)
        jarvis_committed_mb = round(sum(process.committed_mb for process in processes), 1)
        loaded_model_vram_mb = round(
            sum(float(model.get("size_vram_mb") or 0.0) for model in loaded_models),
            1,
        )

        return {
            "estimated_vram_mb": loaded_model_vram_mb,
            "system_gpu": gpu_memory_report(),
            "jarvis_rss_ram_mb": jarvis_rss_mb,
            "jarvis_committed_ram_mb": jarvis_committed_mb,
            "running_jarvis_processes": [asdict(process) for process in processes],
            "loaded_models": loaded_models,
            "active_cuda_contexts": cuda_contexts,
        }

    async def _idle_monitor(self) -> None:
        while True:
            await asyncio.sleep(30)
            if not settings.resource_mode.enabled:
                continue
            idle_seconds = (datetime.now(UTC) - self._last_activity_at).total_seconds()
            light_after = max(0.0, settings.resource_mode.idle_timeout_minutes * 60)
            deep_after = max(0.0, settings.resource_mode.deep_sleep_timeout_minutes * 60)

            if (
                settings.resource_mode.auto_deep_sleep
                and self._state != RuntimeState.DEEP_SLEEP
                and deep_after > 0
                and idle_seconds >= deep_after
            ):
                await self.deep_sleep(reason="idle_timeout")
                if settings.resource_mode.stop_server_on_auto_deep_sleep:
                    audit.log("resource_auto_deep_sleep_exit", {"pid": os.getpid()})
                    await asyncio.sleep(0.25)
                    os._exit(0)
                continue

            if (
                settings.resource_mode.auto_light_sleep
                and self._state == RuntimeState.ACTIVE
                and light_after > 0
                and idle_seconds >= light_after
            ):
                await self.light_sleep(reason="idle_timeout")

    def _set_state(self, state: RuntimeState, reason: str) -> None:
        if self._state != state:
            self._previous_state = self._state
        self._state = state
        audit.log("resource_state", {"state": state.value, "reason": reason})

    async def _stop_voice_services(self, actions: list[str]) -> None:
        try:
            from app.brain.cancel_token import current_token
            from app.voice.audio_stream import voice_pipeline
            from app.voice.tts import tts

            current_token.cancel()
            voice_pipeline.stop()
            tts.stop()
            actions.append("voice_pipeline_stopped")
            actions.append("tts_stopped")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"voice_stop_error:{exc}")
            audit.log("resource_voice_stop_error", {"error": str(exc)})

    async def _stop_background_services(self, actions: list[str]) -> None:
        try:
            from app.agent.scheduler import scheduler

            await scheduler.stop()
            actions.append("scheduler_stopped")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"scheduler_stop_error:{exc}")
            audit.log("resource_scheduler_stop_error", {"error": str(exc)})

    async def _start_required_services(self, actions: list[str]) -> None:
        try:
            from app.brain.cancel_token import current_token

            current_token.reset()
            actions.append("cancel_token_reset")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"cancel_token_reset_error:{exc}")

        try:
            from app.agent.scheduler import scheduler

            await scheduler.start()
            actions.append("scheduler_started")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"scheduler_start_error:{exc}")
            audit.log("resource_scheduler_start_error", {"error": str(exc)})

        if settings.server.enable_voice_on_startup:
            try:
                from app.voice.audio_stream import voice_pipeline

                voice_pipeline.start()
                actions.append("voice_pipeline_started")
            except Exception as exc:  # noqa: BLE001
                actions.append(f"voice_start_error:{exc}")
                audit.log("resource_voice_start_error", {"error": str(exc)})

    async def _close_ui_connections(self, actions: list[str]) -> None:
        try:
            from app.server import manager

            closed = await manager.disconnect_all()
            actions.append(f"websockets_closed:{closed}")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"websocket_close_error:{exc}")
            audit.log("resource_websocket_close_error", {"error": str(exc)})

    def _unload_python_models(self, actions: list[str], *, keep_wake_model: bool) -> None:
        try:
            from app.voice.stt import stt

            stt.unload_model()
            actions.append("stt_model_unloaded")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"stt_unload_error:{exc}")

        try:
            from app.voice.tts import tts

            tts.unload_models()
            actions.append("tts_models_unloaded")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"tts_unload_error:{exc}")

        try:
            from app.computer.vision import vision_client

            vision_client.unload()
            actions.append("vision_client_unloaded")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"vision_unload_error:{exc}")

        try:
            from app.voice.sounds import sounds

            sounds.release()
            actions.append("audio_mixer_released")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"audio_release_error:{exc}")

    def _unload_wake_model(self, actions: list[str]) -> None:
        try:
            from app.voice.wake_word import wake_word

            wake_word.unload_model()
            actions.append("wake_model_unloaded")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"wake_unload_error:{exc}")

    async def _unload_ollama_models(self, actions: list[str]) -> None:
        unloaded = await asyncio.to_thread(unload_all_ollama_models)
        actions.append(f"ollama_models_unloaded:{len(unloaded)}")

    async def _preload_primary_model(self, actions: list[str]) -> None:
        model = settings.models.main
        try:
            await asyncio.to_thread(preload_ollama_model, model)
            actions.append(f"primary_model_preloaded:{model}")
        except Exception as exc:  # noqa: BLE001
            actions.append(f"primary_model_preload_error:{exc}")
            audit.log("resource_preload_error", {"model": model, "error": str(exc)})

    def _release_cuda_contexts(self, actions: list[str]) -> None:
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                try:
                    torch.cuda.ipc_collect()
                except Exception:
                    pass
                actions.append("torch_cuda_cache_released")
            else:
                actions.append("torch_cuda_unavailable")
        except Exception:
            actions.append("torch_unavailable")

    def _write_state(self, *, reason: str, resources: dict[str, Any]) -> None:
        payload = {
            "state": self._state.value,
            "previous_state": self._previous_state.value,
            "reason": reason,
            "updated_at": datetime.now(UTC).isoformat(),
            "pid": os.getpid(),
            "last_activity_at": self._last_activity_at.isoformat(),
            "resources": resources,
        }
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            audit.log("resource_state_write_error", {"path": str(self._state_path), "error": str(exc)})


def configured_ollama_models() -> list[str]:
    names = {
        settings.models.main,
        settings.models.coder,
        settings.models.router,
        settings.models.vision,
    }
    if settings.models.main == "qwen3-nothink":
        names.add("qwen3:14b")
    return sorted(name for name in names if name)


def _ollama_endpoint(path: str) -> str:
    base_url = settings.models.ollama_base_url.rstrip("/")
    parsed = urlsplit(base_url)
    if parsed.hostname and parsed.hostname.lower() == "localhost":
        netloc = "127.0.0.1"
        if parsed.port is not None:
            netloc = f"{netloc}:{parsed.port}"
        if parsed.username:
            auth = parsed.username
            if parsed.password:
                auth = f"{auth}:{parsed.password}"
            netloc = f"{auth}@{netloc}"
        base_url = urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment)).rstrip("/")
    return f"{base_url}{path}"


def list_loaded_ollama_models(*, timeout_seconds: float = 2.0) -> list[dict[str, Any]]:
    try:
        response = httpx.get(_ollama_endpoint("/api/ps"), timeout=timeout_seconds)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        return [{"error": str(exc), "source": "ollama_api"}]

    models = payload.get("models", []) if isinstance(payload, dict) else []
    if not isinstance(models, list):
        return []

    normalized: list[dict[str, Any]] = []
    for model in models:
        if not isinstance(model, dict):
            continue
        size = float(model.get("size") or 0.0)
        size_vram = float(model.get("size_vram") or 0.0)
        normalized.append(
            {
                "name": model.get("name") or model.get("model") or "",
                "size_mb": round(size / 1024 / 1024, 1),
                "size_vram_mb": round(size_vram / 1024 / 1024, 1),
                "expires_at": model.get("expires_at"),
            }
        )
    return normalized


def unload_all_ollama_models() -> list[str]:
    loaded = list_loaded_ollama_models(timeout_seconds=2.0)
    model_names = {
        str(model.get("name"))
        for model in loaded
        if isinstance(model, dict) and model.get("name") and not model.get("error")
    }
    model_names.update(configured_ollama_models())
    unloaded: list[str] = []

    for model_name in sorted(model_names):
        if unload_ollama_model(model_name):
            unloaded.append(model_name)
    return unloaded


def unload_ollama_model(model_name: str) -> bool:
    if not model_name:
        return False

    payload = {
        "model": model_name,
        "prompt": "",
        "stream": False,
        "keep_alive": 0,
    }
    try:
        response = httpx.post(_ollama_endpoint("/api/generate"), json=payload, timeout=10.0)
        if response.status_code < 500:
            audit.log("resource_ollama_unload", {"model": model_name, "method": "api", "status": response.status_code})
            return response.status_code < 400
    except Exception as exc:  # noqa: BLE001
        audit.log("resource_ollama_unload_api_error", {"model": model_name, "error": str(exc)})

    try:
        result = subprocess.run(
            ["ollama", "stop", model_name],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        audit.log(
            "resource_ollama_unload",
            {"model": model_name, "method": "cli", "returncode": result.returncode},
        )
        return result.returncode == 0
    except Exception as exc:  # noqa: BLE001
        audit.log("resource_ollama_unload_cli_error", {"model": model_name, "error": str(exc)})
        return False


def preload_ollama_model(model_name: str) -> bool:
    payload = {
        "model": model_name,
        "prompt": "",
        "stream": False,
        "keep_alive": settings.resource_mode.preload_keep_alive,
    }
    response = httpx.post(_ollama_endpoint("/api/generate"), json=payload, timeout=120.0)
    response.raise_for_status()
    audit.log("resource_ollama_preload", {"model": model_name})
    return True


def gpu_memory_report() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,memory.used,memory.total,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=2, check=False)
        if result.returncode == 0:
            line = result.stdout.splitlines()[0] if result.stdout.splitlines() else ""
            parts = [part.strip() for part in line.split(",")]
            if len(parts) >= 4:
                return {
                    "available": True,
                    "name": parts[0],
                    "memory_used_mb": round(float(parts[1]), 1),
                    "memory_total_mb": round(float(parts[2]), 1),
                    "load_percent": round(float(parts[3]), 1),
                }
    except Exception:
        pass

    try:
        import GPUtil

        gpus = GPUtil.getGPUs()
        if not gpus:
            return {"available": False, "reason": "no_gpus"}
        gpu = gpus[0]
        return {
            "available": True,
            "name": gpu.name,
            "memory_used_mb": round(float(gpu.memoryUsed), 1),
            "memory_total_mb": round(float(gpu.memoryTotal), 1),
            "load_percent": round(float(gpu.load) * 100, 1),
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": str(exc)}


def detect_cuda_contexts() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-compute-apps=pid,process_name,used_memory",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3, check=False)
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": str(exc), "contexts": []}

    if result.returncode != 0:
        return {"available": False, "error": result.stderr.strip(), "contexts": []}

    contexts: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            continue
        try:
            pid = int(parts[0])
            used_memory_mb = float(parts[2])
        except ValueError:
            continue
        contexts.append(
            {
                "pid": pid,
                "process_name": parts[1],
                "used_memory_mb": used_memory_mb,
                "jarvis_owned": is_jarvis_pid(pid),
            }
        )
    return {"available": True, "contexts": contexts}


def discover_jarvis_processes(exclude_pids: set[int] | None = None) -> list[JarvisProcess]:
    exclude = exclude_pids or set()
    processes: list[JarvisProcess] = []

    for proc in psutil.process_iter(["pid", "name", "cmdline", "memory_info"]):
        try:
            pid = int(proc.info["pid"])
            if pid in exclude:
                continue
            cmdline_parts = proc.info.get("cmdline") or []
            cmdline = " ".join(str(part) for part in cmdline_parts)
            name = str(proc.info.get("name") or "")
            role = classify_jarvis_process(name, cmdline, proc)
            if role is None:
                continue
            memory_info = proc.info.get("memory_info") or proc.memory_info()
            rss = float(getattr(memory_info, "rss", 0.0))
            committed = float(getattr(memory_info, "vms", 0.0))
            processes.append(
                JarvisProcess(
                    pid=pid,
                    name=name,
                    role=role,
                    cmdline=cmdline[:500],
                    rss_mb=round(rss / 1024 / 1024, 1),
                    committed_mb=round(committed / 1024 / 1024, 1),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def is_jarvis_pid(pid: int) -> bool:
    try:
        proc = psutil.Process(pid)
        return classify_jarvis_process(proc.name(), " ".join(proc.cmdline()), proc) is not None
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def classify_jarvis_process(name: str, cmdline: str, proc: psutil.Process | None = None) -> str | None:
    normalized = cmdline.replace("\\", "/").lower()
    root = str(PROJECT_ROOT).replace("\\", "/").lower()
    lowered_name = name.lower()

    if "app.main:app" in normalized or "python -m app.main" in normalized:
        return "fastapi_server"
    if "uvicorn" in normalized and "app.main:app" in normalized:
        return "fastapi_server"
    if "python -m app.boot" in normalized or "app/boot.py" in normalized:
        return "boot_orchestrator"
    if "scripts/sensor_node.py" in normalized:
        return "sensor_node"
    if "wake_diag.py" in normalized:
        return "wake_diagnostics"
    if (
        any(keyword in normalized for keyword in ("browser_use", "computer_use", "open-computer-use"))
        and "pytest" not in normalized
    ):
        if root in normalized or _cwd_under_project(proc):
            return "automation_worker"
    if lowered_name in {"node.exe", "node", "npm.cmd", "npm"}:
        if "frontend/electron" in normalized or _cwd_under_project(proc, PROJECT_ROOT / "frontend" / "electron"):
            return "electron_hud"
    return None


def _cwd_under_project(proc: psutil.Process | None, root: Path = PROJECT_ROOT) -> bool:
    if proc is None:
        return False
    try:
        cwd = Path(proc.cwd()).resolve()
        return root.resolve() in [cwd, *cwd.parents]
    except (OSError, psutil.AccessDenied, psutil.NoSuchProcess):
        return False


def terminate_jarvis_processes(exclude_pids: set[int] | None = None, timeout: float = 3.0) -> list[dict[str, Any]]:
    stopped: list[dict[str, Any]] = []
    for process in discover_jarvis_processes(exclude_pids=exclude_pids):
        try:
            proc = psutil.Process(process.pid)
            proc.terminate()
            try:
                proc.wait(timeout=timeout)
                outcome = "terminated"
            except psutil.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=timeout)
                outcome = "killed"
            stopped.append({**asdict(process), "outcome": outcome})
            audit.log("resource_process_stopped", {"pid": process.pid, "role": process.role, "outcome": outcome})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as exc:
            stopped.append({**asdict(process), "outcome": f"error:{exc}"})
            audit.log("resource_process_stop_error", {"pid": process.pid, "role": process.role, "error": str(exc)})
    return stopped


def read_persisted_state(state_path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    if not state_path.is_file():
        return {"state": RuntimeState.ACTIVE.value, "path": str(state_path), "exists": False}
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"state": "UNKNOWN", "path": str(state_path), "error": str(exc)}
    if isinstance(payload, dict):
        payload["path"] = str(state_path)
        payload["exists"] = True
        return payload
    return {"state": "UNKNOWN", "path": str(state_path), "error": "invalid_state_file"}


def start_server_process() -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        settings.server.host,
        "--port",
        str(settings.server.port),
    ]
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )


resource_manager = ResourceManager()

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.config import settings
import app.resource_manager as resource_module
from app.resource_manager import ResourceManager, RuntimeState, classify_jarvis_process, unload_ollama_model


def _state_path(name: str) -> Path:
    path = Path("tasks") / name
    path.parent.mkdir(exist_ok=True)
    path.unlink(missing_ok=True)
    return path


async def _append_action(name: str, actions: list[str]) -> None:
    actions.append(name)


@pytest.mark.asyncio
async def test_light_sleep_unloads_services_and_keeps_wake_listener(monkeypatch) -> None:  # noqa: ANN001
    state_path = _state_path("resource_state_light_test.json")
    manager = ResourceManager(state_path)
    calls: list[object] = []

    monkeypatch.setattr(settings.resource_mode, "keep_wake_listener_in_light_sleep", True)
    monkeypatch.setattr(manager, "_stop_voice_services", lambda actions: _append_action("voice_stopped", actions))
    monkeypatch.setattr(manager, "_stop_background_services", lambda actions: _append_action("scheduler_stopped", actions))
    monkeypatch.setattr(manager, "_close_ui_connections", lambda actions: _append_action("ui_closed", actions))
    monkeypatch.setattr(
        manager,
        "_unload_python_models",
        lambda actions, keep_wake_model: (calls.append(("python_unload", keep_wake_model)), actions.append("python_unloaded")),
    )
    monkeypatch.setattr(manager, "_unload_ollama_models", lambda actions: _append_action("ollama_unloaded", actions))
    monkeypatch.setattr(manager, "_release_cuda_contexts", lambda actions: actions.append("cuda_released"))
    monkeypatch.setattr(manager._wake_listener, "start", lambda: calls.append("wake_listener_started"))
    monkeypatch.setattr(manager, "resource_report", lambda: {"estimated_vram_mb": 0})

    result = await manager.light_sleep(reason="unit")

    assert manager.state == RuntimeState.LIGHT_SLEEP
    assert result.previous_state == "ACTIVE"
    assert ("python_unload", True) in calls
    assert "wake_listener_started" in calls
    assert {"voice_stopped", "scheduler_stopped", "ui_closed", "ollama_unloaded", "cuda_released"} <= set(result.actions)
    state_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_deep_sleep_stops_wake_listener_and_processes(monkeypatch) -> None:  # noqa: ANN001
    state_path = _state_path("resource_state_deep_test.json")
    manager = ResourceManager(state_path)
    calls: list[object] = []

    monkeypatch.setattr(settings.resource_mode, "keep_wake_listener_in_deep_sleep", False)
    monkeypatch.setattr(manager, "_stop_voice_services", lambda actions: _append_action("voice_stopped", actions))
    monkeypatch.setattr(manager, "_stop_background_services", lambda actions: _append_action("scheduler_stopped", actions))
    monkeypatch.setattr(manager, "_close_ui_connections", lambda actions: _append_action("ui_closed", actions))
    monkeypatch.setattr(manager, "_unload_python_models", lambda actions, keep_wake_model: calls.append(("python_unload", keep_wake_model)))
    monkeypatch.setattr(manager, "_unload_wake_model", lambda actions: actions.append("wake_unloaded"))
    monkeypatch.setattr(manager, "_unload_ollama_models", lambda actions: _append_action("ollama_unloaded", actions))
    monkeypatch.setattr(manager, "_release_cuda_contexts", lambda actions: actions.append("cuda_released"))
    monkeypatch.setattr(manager._wake_listener, "stop", lambda: calls.append("wake_listener_stopped"))
    monkeypatch.setattr(resource_module, "terminate_jarvis_processes", lambda exclude_pids: [{"pid": 123, "outcome": "terminated"}])
    monkeypatch.setattr(manager, "resource_report", lambda: {"estimated_vram_mb": 0})

    result = await manager.deep_sleep(reason="unit", terminate_processes=True)

    assert manager.state == RuntimeState.DEEP_SLEEP
    assert ("python_unload", False) in calls
    assert "wake_listener_stopped" in calls
    assert "wake_unloaded" in result.actions
    assert "terminated_processes:1" in result.actions
    state_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_wake_starts_required_services_and_optionally_preloads(monkeypatch) -> None:  # noqa: ANN001
    state_path = _state_path("resource_state_wake_test.json")
    manager = ResourceManager(state_path)
    manager._set_state(RuntimeState.LIGHT_SLEEP, "unit")
    calls: list[str] = []

    monkeypatch.setattr(manager._wake_listener, "stop", lambda: calls.append("wake_listener_stopped"))
    monkeypatch.setattr(manager, "_start_required_services", lambda actions: _append_action("scheduler_started", actions))
    monkeypatch.setattr(manager, "_preload_primary_model", lambda actions: _append_action("primary_preloaded", actions))
    monkeypatch.setattr(manager, "resource_report", lambda: {"estimated_vram_mb": 0})

    result = await manager.wake(reason="unit", preload_primary_model=True)

    assert manager.state == RuntimeState.ACTIVE
    assert result.previous_state == "LIGHT_SLEEP"
    assert "wake_listener_stopped" in calls
    assert {"scheduler_started", "primary_preloaded"} <= set(result.actions)
    state_path.unlink(missing_ok=True)


def test_unload_ollama_model_uses_keep_alive_zero(monkeypatch) -> None:  # noqa: ANN001
    posted: dict[str, object] = {}

    def fake_post(url: str, json: dict, timeout: float) -> Mock:  # noqa: A002
        posted.update({"url": url, "json": json, "timeout": timeout})
        return Mock(status_code=200)

    monkeypatch.setattr(resource_module.httpx, "post", fake_post)

    assert unload_ollama_model("qwen3-nothink") is True
    assert posted["json"] == {"model": "qwen3-nothink", "prompt": "", "stream": False, "keep_alive": 0}


def test_resource_report_sums_loaded_model_vram_and_process_memory(monkeypatch) -> None:  # noqa: ANN001
    state_path = _state_path("resource_state_report_test.json")
    manager = ResourceManager(state_path)
    process = resource_module.JarvisProcess(
        pid=10,
        name="python.exe",
        role="fastapi_server",
        cmdline="python -m uvicorn app.main:app",
        rss_mb=100.0,
        committed_mb=250.0,
    )

    monkeypatch.setattr(resource_module, "list_loaded_ollama_models", lambda: [{"name": "qwen3:14b", "size_vram_mb": 8192.0}])
    monkeypatch.setattr(resource_module, "discover_jarvis_processes", lambda exclude_pids: [process])
    monkeypatch.setattr(resource_module, "detect_cuda_contexts", lambda: {"available": True, "contexts": []})
    monkeypatch.setattr(resource_module, "gpu_memory_report", lambda: {"available": False})

    report = manager.resource_report()

    assert report["estimated_vram_mb"] == 8192.0
    assert report["jarvis_rss_ram_mb"] == 100.0
    assert report["jarvis_committed_ram_mb"] == 250.0
    assert report["running_jarvis_processes"][0]["role"] == "fastapi_server"
    state_path.unlink(missing_ok=True)


def test_classify_jarvis_process_matches_runtime_workers() -> None:
    assert classify_jarvis_process("python.exe", "python -m uvicorn app.main:app", None) == "fastapi_server"
    assert classify_jarvis_process("python.exe", "python scripts/sensor_node.py", None) == "sensor_node"
    assert classify_jarvis_process("python.exe", "python -m pytest", None) is None

from __future__ import annotations

from collections import namedtuple
from types import SimpleNamespace

import pytest

import app.agent.reporter as reporter_module


@pytest.mark.asyncio
async def test_build_report(monkeypatch) -> None:
    memory = namedtuple("Memory", ["percent"])(percent=55.0)

    monkeypatch.setattr(reporter_module.psutil, "cpu_percent", lambda interval=0.1: 42.0)
    monkeypatch.setattr(reporter_module.psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(reporter_module.task_queue, "_tasks", {})

    report = await reporter_module.reporter.build_report()

    assert "CPU 42" in report
    assert "RAM 55" in report


@pytest.mark.asyncio
async def test_send_report_discord_only(monkeypatch) -> None:
    memory = namedtuple("Memory", ["percent"])(percent=55.0)

    async def fake_send_status(status: str) -> dict:
        return {"sent": True, "status": status}

    monkeypatch.setattr(reporter_module.psutil, "cpu_percent", lambda interval=0.1: 42.0)
    monkeypatch.setattr(reporter_module.psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(reporter_module.task_queue, "_tasks", {})
    monkeypatch.setattr(reporter_module.settings.comms, "discord_enabled", True)
    monkeypatch.setattr(reporter_module.settings.comms, "telegram_enabled", False)
    monkeypatch.setattr(reporter_module.discord_bot, "send_status", fake_send_status)

    result = await reporter_module.reporter.send_report()

    assert "report" in result
    assert result["discord"]["sent"] is True
    assert result["telegram"] is None


@pytest.mark.asyncio
async def test_send_report_both_disabled(monkeypatch) -> None:
    memory = namedtuple("Memory", ["percent"])(percent=55.0)

    monkeypatch.setattr(reporter_module.psutil, "cpu_percent", lambda interval=0.1: 42.0)
    monkeypatch.setattr(reporter_module.psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(reporter_module.task_queue, "_tasks", {})
    monkeypatch.setattr(reporter_module.settings.comms, "discord_enabled", False)
    monkeypatch.setattr(reporter_module.settings.comms, "telegram_enabled", False)

    result = await reporter_module.reporter.send_report()

    assert "report" in result
    assert result["discord"] is None
    assert result["telegram"] is None


@pytest.mark.asyncio
async def test_morning_report(monkeypatch) -> None:
    memory = namedtuple("Memory", ["percent"])(percent=55.0)
    tasks = {
        "1": SimpleNamespace(status="in_progress", goal="active"),
        "2": SimpleNamespace(status="pending", goal="pending"),
    }

    monkeypatch.setattr(reporter_module.psutil, "cpu_percent", lambda interval=0.1: 42.0)
    monkeypatch.setattr(reporter_module.psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(reporter_module.task_queue, "_tasks", tasks)

    report = await reporter_module.reporter.morning_report()

    assert "morning" in report.lower()
    assert "sir" in report.lower()

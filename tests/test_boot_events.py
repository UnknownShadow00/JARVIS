from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from app import boot
from app.server import ConnectionManager


@pytest.mark.asyncio
async def test_boot_event_shape() -> None:
    manager = ConnectionManager()
    manager.broadcast = AsyncMock()  # type: ignore[method-assign]

    event = await boot.broadcast_boot_event(manager, "logo", "Stark Industries systems initializing...")

    assert event == {
        "type": "boot",
        "phase": "logo",
        "message": "Stark Industries systems initializing...",
    }
    manager.broadcast.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_morning_report_called(monkeypatch: pytest.MonkeyPatch) -> None:
    report = "Good morning, sir. Diagnostics complete."

    monkeypatch.setattr(boot, "wait_for_ollama", AsyncMock())
    monkeypatch.setattr(boot, "start_electron_hud", lambda: None)
    monkeypatch.setattr(boot.sounds, "play", lambda _sound_name: True)
    monkeypatch.setattr(boot.tts, "speak", AsyncMock())
    monkeypatch.setattr(boot.voice_pipeline, "start", lambda: None)
    monkeypatch.setattr(boot.asyncio, "sleep", AsyncMock())
    compose_mock = Mock(return_value=report)
    monkeypatch.setattr(boot, "compose_morning_report", compose_mock)

    await boot.boot_sequence(start_server=False, start_hud=False, start_voice=False, ws_manager=ConnectionManager())

    compose_mock.assert_called_once_with()


@pytest.mark.asyncio
async def test_boot_works_no_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    report = "Good morning, sir. All systems operational."

    monkeypatch.setattr(boot, "wait_for_ollama", AsyncMock())
    monkeypatch.setattr(boot, "start_electron_hud", lambda: None)
    monkeypatch.setattr(boot.sounds, "play", lambda _sound_name: True)
    monkeypatch.setattr(boot.tts, "speak", AsyncMock())
    monkeypatch.setattr(boot.voice_pipeline, "start", lambda: None)
    monkeypatch.setattr(boot.asyncio, "sleep", AsyncMock())
    monkeypatch.setattr(boot, "compose_morning_report", lambda: report)

    result = await boot.boot_sequence(start_server=False, start_hud=False, start_voice=False, ws_manager=ConnectionManager())

    assert result == report

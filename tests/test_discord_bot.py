from __future__ import annotations

import asyncio
from types import SimpleNamespace

import app.comms.discord_bot as discord_bot_module
from app.comms.discord_bot import DiscordBot


def test_send_disabled(monkeypatch) -> None:
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_enabled", False)

    bot = DiscordBot()
    result = asyncio.run(bot.send_message("hello"))

    assert "stub" in result


def test_send_no_discord_lib(monkeypatch) -> None:
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_enabled", True)
    monkeypatch.setattr(discord_bot_module, "DISCORD_AVAILABLE", False)

    bot = DiscordBot()
    result = asyncio.run(bot.send_message("hello"))

    assert "stub" in result


def test_send_no_token(monkeypatch) -> None:
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_enabled", True)
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_token", "")
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_channel_id", 123)
    monkeypatch.setattr(discord_bot_module, "DISCORD_AVAILABLE", True)

    bot = DiscordBot()
    result = asyncio.run(bot.send_message("hello"))

    assert "error" in result


def test_send_success(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return SimpleNamespace(
            status_code=200,
            json=lambda: {"id": "1"},
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_enabled", True)
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_token", "tok")
    monkeypatch.setattr(discord_bot_module.settings.comms, "discord_channel_id", 123)
    monkeypatch.setattr(discord_bot_module, "DISCORD_AVAILABLE", True)
    monkeypatch.setattr(discord_bot_module.httpx, "post", fake_post)

    bot = DiscordBot()
    result = asyncio.run(bot.send_message("hi", 123))

    assert result["sent"] is True

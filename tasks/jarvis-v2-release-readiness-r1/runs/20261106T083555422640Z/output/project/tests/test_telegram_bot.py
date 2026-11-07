from __future__ import annotations

import asyncio
from types import SimpleNamespace

import app.comms.telegram_bot as telegram_bot_module
from app.comms.telegram_bot import TelegramBot


def test_send_disabled(monkeypatch) -> None:
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_enabled", False)

    bot = TelegramBot()
    result = asyncio.run(bot.send_message("hello"))

    assert "stub" in result


def test_send_no_lib(monkeypatch) -> None:
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_enabled", True)
    monkeypatch.setattr(telegram_bot_module, "TELEGRAM_AVAILABLE", False)

    bot = TelegramBot()
    result = asyncio.run(bot.send_message("hello"))

    assert "stub" in result


def test_send_no_token(monkeypatch) -> None:
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_enabled", True)
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_token", "")
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_chat_id", "123")
    monkeypatch.setattr(telegram_bot_module, "TELEGRAM_AVAILABLE", True)

    bot = TelegramBot()
    result = asyncio.run(bot.send_message("hello"))

    assert "error" in result


def test_send_success(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return SimpleNamespace(
            status_code=200,
            json=lambda: {"ok": True},
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_enabled", True)
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_token", "tok")
    monkeypatch.setattr(telegram_bot_module.settings.comms, "telegram_chat_id", "123")
    monkeypatch.setattr(telegram_bot_module, "TELEGRAM_AVAILABLE", True)
    monkeypatch.setattr(telegram_bot_module.httpx, "post", fake_post)

    bot = TelegramBot()
    result = asyncio.run(bot.send_message("hi", "123"))

    assert result["sent"] is True

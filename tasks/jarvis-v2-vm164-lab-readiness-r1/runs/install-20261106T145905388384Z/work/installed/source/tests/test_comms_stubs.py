from __future__ import annotations

import asyncio

from app.comms.discord_bot import discord_bot
from app.comms.telegram_bot import telegram_bot


def test_discord_send_disabled() -> None:
    result = asyncio.run(discord_bot.send_message("hello"))

    assert "stub" in result


def test_discord_status_disabled() -> None:
    result = asyncio.run(discord_bot.send_status("test"))

    assert "stub" in result


def test_telegram_send_disabled() -> None:
    result = asyncio.run(telegram_bot.send_message("hello"))

    assert "stub" in result


def test_telegram_status_disabled() -> None:
    result = asyncio.run(telegram_bot.send_status("test"))

    assert "stub" in result

from __future__ import annotations

import asyncio

import httpx

from app.config import settings
from app.logs.audit import audit

try:
    import discord
    from discord.ext import commands

    DISCORD_AVAILABLE = True
except ImportError:
    discord = None
    commands = None
    DISCORD_AVAILABLE = False


def _stub_response() -> dict:
    return {"stub": True, "note": "Discord disabled - enable in config.yaml at Phase 5"}


class DiscordBot:
    def __init__(self) -> None:
        self._enabled = settings.comms.discord_enabled
        self._token = settings.comms.discord_token
        self._channel_id = int(getattr(settings.comms, "discord_channel_id", 0) or 0)
        self._client = None

    async def send_message(self, message: str, channel_id: int | None = None) -> dict:
        target_channel_id = int(channel_id or self._channel_id or 0)
        audit.log(
            "discord_send",
            {
                "channel_id": target_channel_id,
                "message_len": len(message),
                "enabled": self._enabled,
                "discord_available": DISCORD_AVAILABLE,
            },
        )

        if not self._enabled or not DISCORD_AVAILABLE:
            return _stub_response()

        if not self._token or not target_channel_id:
            return {"error": "discord_token or channel_id not configured"}

        try:
            response = await asyncio.to_thread(
                httpx.post,
                f"https://discord.com/api/v10/channels/{target_channel_id}/messages",
                headers={
                    "Authorization": f"Bot {self._token}",
                    "Content-Type": "application/json",
                },
                json={"content": message},
                timeout=httpx.Timeout(10.0),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return {"error": str(exc)}

        return {"sent": True, "channel_id": target_channel_id}

    async def send_status(self, status: str) -> dict:
        return await self.send_message(f"[JARVIS] {status}")

    async def start(self) -> None:
        if not self._enabled:
            return

        audit.log("discord_start", {"enabled": self._enabled})

    async def stop(self) -> None:
        audit.log("discord_stop", {"enabled": self._enabled})


discord_bot = DiscordBot()

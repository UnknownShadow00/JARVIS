from __future__ import annotations

from app.config import settings
from app.logs.audit import audit


DISCORD_AVAILABLE = False


class DiscordBot:
    def __init__(self) -> None:
        self._enabled = settings.comms.discord_enabled
        self._token = settings.comms.discord_token
        self._client = None

    async def send_message(self, message: str, channel_id: int | None = None) -> dict:
        if not self._enabled:
            return {"stub": True, "note": "Discord disabled — enable in config.yaml at Phase 5"}

        audit.log("discord_send", {"channel_id": channel_id, "message_len": len(message)})
        return {"stub": True, "note": "Discord integration in Phase 5"}

    async def send_status(self, status: str) -> dict:
        return await self.send_message(f"[JARVIS] {status}")

    async def start(self) -> None:
        if not self._enabled:
            return

        audit.log("discord_start", {"enabled": self._enabled})

    async def stop(self) -> None:
        pass


discord_bot = DiscordBot()

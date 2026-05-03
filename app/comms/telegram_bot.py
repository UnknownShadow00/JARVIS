from __future__ import annotations

from app.config import settings
from app.logs.audit import audit


TELEGRAM_AVAILABLE = False


class TelegramBot:
    def __init__(self) -> None:
        self._enabled = settings.comms.telegram_enabled
        self._token = settings.comms.telegram_token
        self._app = None

    async def send_message(self, message: str, chat_id: str | None = None) -> dict:
        if not self._enabled:
            return {"stub": True, "note": "Telegram disabled — enable in config.yaml at Phase 5"}

        audit.log("telegram_send", {"chat_id": chat_id, "message_len": len(message)})
        return {"stub": True, "note": "Telegram integration in Phase 5"}

    async def send_status(self, status: str) -> dict:
        return await self.send_message(f"[JARVIS] {status}")

    async def start(self) -> None:
        if not self._enabled:
            return

        audit.log("telegram_start", {"enabled": self._enabled})

    async def stop(self) -> None:
        pass


telegram_bot = TelegramBot()

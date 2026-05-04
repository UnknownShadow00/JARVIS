from __future__ import annotations

import asyncio

import httpx

from app.config import settings
from app.logs.audit import audit

try:
    import telegram

    TELEGRAM_AVAILABLE = True
except ImportError:
    telegram = None
    TELEGRAM_AVAILABLE = False


def _stub_response() -> dict:
    return {"stub": True, "note": "Telegram disabled - enable in config.yaml at Phase 5"}


class TelegramBot:
    def __init__(self) -> None:
        self._enabled = settings.comms.telegram_enabled
        self._token = settings.comms.telegram_token
        self._chat_id = str(getattr(settings.comms, "telegram_chat_id", "") or "")
        self._app = None

    async def send_message(self, message: str, chat_id: str | None = None) -> dict:
        target_chat_id = str(chat_id or self._chat_id or "")
        audit.log(
            "telegram_send",
            {
                "chat_id": target_chat_id,
                "message_len": len(message),
                "enabled": self._enabled,
                "telegram_available": TELEGRAM_AVAILABLE,
            },
        )

        if not self._enabled or not TELEGRAM_AVAILABLE:
            return _stub_response()

        if not self._token or not target_chat_id:
            return {"error": "telegram_token or chat_id not configured"}

        try:
            response = await asyncio.to_thread(
                httpx.post,
                f"https://api.telegram.org/bot{self._token}/sendMessage",
                json={"chat_id": target_chat_id, "text": message},
                timeout=httpx.Timeout(10.0),
            )
            response.raise_for_status()
        except Exception as exc:
            return {"error": str(exc)}

        return {"sent": True, "chat_id": target_chat_id}

    async def send_status(self, status: str) -> dict:
        return await self.send_message(f"[JARVIS] {status}")

    async def start(self) -> None:
        if not self._enabled:
            return

        audit.log("telegram_start", {"enabled": self._enabled})

    async def stop(self) -> None:
        audit.log("telegram_stop", {"enabled": self._enabled})


telegram_bot = TelegramBot()

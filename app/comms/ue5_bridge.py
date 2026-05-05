from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket


VALID_EMOTIONS = {"neutral", "success", "concern", "thinking", "speaking", "idle"}
DEFAULT_ANIMATIONS = {
    "neutral": "Idle_01",
    "success": "React_Happy",
    "concern": "React_Worried",
    "thinking": "Think_01",
    "speaking": "Talk_01",
    "idle": "Idle_02",
}
_EMOTION_TAG_RE = re.compile(r"\[EMOTION:([a-z_]+)\]", re.IGNORECASE)


class UE5ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


@dataclass(slots=True)
class EmotionEvent:
    emotion: str
    intensity: float
    animation: str
    timestamp: str


def build_emotion_event(emotion: str, intensity: float = 1.0) -> dict[str, Any]:
    normalized_emotion = emotion.strip().lower()
    if normalized_emotion not in VALID_EMOTIONS:
        normalized_emotion = "neutral"

    clamped_intensity = max(0.0, min(1.0, float(intensity)))
    event = EmotionEvent(
        emotion=normalized_emotion,
        intensity=clamped_intensity,
        animation=DEFAULT_ANIMATIONS[normalized_emotion],
        timestamp=datetime.now(UTC).isoformat(),
    )
    return asdict(event)


def parse_emotion_from_reply(reply: str) -> str | None:
    match = _EMOTION_TAG_RE.search(reply)
    if match is None:
        return None

    emotion = match.group(1).strip().lower()
    if emotion not in VALID_EMOTIONS:
        return None
    return emotion


ue5_manager = UE5ConnectionManager()

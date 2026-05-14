from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any

try:
    from websockets.sync.client import connect as websocket_connect

    AUDIO2FACE_AVAILABLE = True
except ImportError:
    websocket_connect = None
    AUDIO2FACE_AVAILABLE = False


def build_audio_event(audio_bytes: bytes, sample_rate: int = 22050) -> dict[str, Any]:
    return {
        "type": "audio",
        "data": base64.b64encode(audio_bytes).decode(),
        "sample_rate": sample_rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def build_viseme_event(visemes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "type": "visemes",
        "data": visemes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


class Audio2FaceManager:
    def __init__(self) -> None:
        self._url = ""
        self._connection: Any | None = None
        self._connected = False

    def connect(self, url: str) -> None:
        self._url = url
        if not AUDIO2FACE_AVAILABLE or websocket_connect is None:
            print("Audio2Face unavailable: websockets dependency not installed")
            self._connected = False
            return

        try:
            if self._connection is not None:
                self.disconnect()
            self._connection = websocket_connect(url)
            self._connected = True
        except Exception as exc:
            print(f"Audio2Face connect error: {exc}")
            self._connection = None
            self._connected = False

    def disconnect(self) -> None:
        try:
            if self._connection is not None:
                self._connection.close()
        except Exception as exc:
            print(f"Audio2Face disconnect error: {exc}")
        finally:
            self._connection = None
            self._connected = False

    def broadcast_audio(self, audio_bytes: bytes, sample_rate: int = 22050) -> None:
        if not self._connected or self._connection is None:
            print("Audio2Face broadcast skipped: not connected")
            return

        try:
            payload = json.dumps(build_audio_event(audio_bytes, sample_rate))
            self._connection.send(payload)
        except Exception as exc:
            print(f"Audio2Face audio broadcast error: {exc}")
            self.disconnect()

    def broadcast_viseme(self, viseme_data: dict[str, Any] | list[dict[str, Any]]) -> None:
        if not self._connected or self._connection is None:
            print("Audio2Face viseme broadcast skipped: not connected")
            return

        try:
            visemes = viseme_data if isinstance(viseme_data, list) else [viseme_data]
            payload = json.dumps(build_viseme_event(visemes))
            self._connection.send(payload)
        except Exception as exc:
            print(f"Audio2Face viseme broadcast error: {exc}")
            self.disconnect()

    def is_connected(self) -> bool:
        return self._connected


audio2face_manager = Audio2FaceManager()

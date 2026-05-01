"""Speech-to-text wrapper around faster-whisper."""
from __future__ import annotations

import re
import tempfile
import time
from pathlib import Path

from app.config import settings
from app.logs.audit import audit

_FILLER_PREFIX = re.compile(r"^\s*(um+|uh+|erm|ah|like|okay|ok)[,\s]+", re.IGNORECASE)


class SpeechToText:
    def __init__(self) -> None:
        self._model = None

    def transcribe(self, audio_bytes: bytes) -> str:
        if not audio_bytes:
            return ""

        started_at = time.perf_counter()
        temp_path = Path(tempfile.NamedTemporaryFile(prefix="jarvis-stt-", suffix=".wav", delete=False).name)
        try:
            temp_path.write_bytes(audio_bytes)
            model = self._load_model()
            if model is None:
                return ""

            segments, _info = model.transcribe(str(temp_path), beam_size=1, vad_filter=True)
            text = " ".join(segment.text for segment in segments)
            cleaned = self._clean_text(text)
            audit.log(
                "stt_transcribed",
                {"duration_seconds": round(time.perf_counter() - started_at, 3), "text": cleaned},
            )
            return cleaned
        finally:
            temp_path.unlink(missing_ok=True)

    def _load_model(self):  # noqa: ANN202
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            audit.log("stt_unavailable", {"reason": str(exc)})
            return None

        self._model = WhisperModel(
            settings.voice.stt_model,
            device=settings.voice.stt_device,
            compute_type=settings.voice.stt_compute_type,
        )
        audit.log(
            "stt_model_loaded",
            {
                "model": settings.voice.stt_model,
                "device": settings.voice.stt_device,
                "compute_type": settings.voice.stt_compute_type,
            },
        )
        return self._model

    def _clean_text(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        while True:
            updated = _FILLER_PREFIX.sub("", cleaned).strip()
            if updated == cleaned:
                return cleaned
            cleaned = updated


stt = SpeechToText()

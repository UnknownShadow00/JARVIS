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
        self._model_key: tuple[str, str] | None = None

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

            try:
                text = self._transcribe_file(model, temp_path)
            except Exception as exc:
                if settings.voice.stt_device.lower() == "cpu":
                    audit.log("stt_unavailable", {"reason": str(exc)})
                    return ""

                audit.log(
                    "stt_fallback",
                    {
                        "from_device": settings.voice.stt_device,
                        "from_compute_type": settings.voice.stt_compute_type,
                        "to_device": "cpu",
                        "to_compute_type": "int8",
                        "reason": str(exc),
                    },
                )
                model = self._load_model(device="cpu", compute_type="int8", force_reload=True)
                if model is None:
                    return ""
                text = self._transcribe_file(model, temp_path)

            cleaned = self._clean_text(text)
            audit.log(
                "stt_transcribed",
                {"duration_seconds": round(time.perf_counter() - started_at, 3), "text": cleaned},
            )
            return cleaned
        finally:
            temp_path.unlink(missing_ok=True)

    def _transcribe_file(self, model, temp_path: Path) -> str:  # noqa: ANN001
        segments, _info = model.transcribe(str(temp_path), beam_size=1, vad_filter=True)
        return " ".join(segment.text for segment in segments)

    def _load_model(
        self,
        device: str | None = None,
        compute_type: str | None = None,
        force_reload: bool = False,
    ):  # noqa: ANN202
        selected_device = device or settings.voice.stt_device
        selected_compute_type = compute_type or settings.voice.stt_compute_type
        model_key = (selected_device, selected_compute_type)

        if not force_reload and self._model is not None and self._model_key == model_key:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            audit.log("stt_unavailable", {"reason": str(exc)})
            return None

        self._model = WhisperModel(
            settings.voice.stt_model,
            device=selected_device,
            compute_type=selected_compute_type,
        )
        self._model_key = model_key
        audit.log(
            "stt_model_loaded",
            {
                "model": settings.voice.stt_model,
                "device": selected_device,
                "compute_type": selected_compute_type,
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


def transcribe(audio_bytes: bytes) -> str:
    return stt.transcribe(audio_bytes)

"""Streaming text-to-speech facade for Piper first, Kokoro later."""
from __future__ import annotations

import asyncio
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config import settings
from app.logs.audit import audit
from app.voice.sounds import sounds

is_speaking = False


class TTSEngine:
    def __init__(self) -> None:
        self.is_speaking = False
        self._stop_event = asyncio.Event()

    async def speak(self, text: str) -> None:
        """Speak text sentence-by-sentence so audio begins as soon as possible."""
        global is_speaking

        sentences = self._split_sentences(text)
        if not sentences:
            return

        self._stop_event.clear()
        self.is_speaking = True
        is_speaking = True
        audit.log("tts_start", {"engine": settings.voice.tts_engine, "sentences": len(sentences)})

        try:
            next_task: asyncio.Task[Path | None] | None = None
            for index, sentence in enumerate(sentences):
                if self._stop_event.is_set():
                    break

                if next_task is None:
                    next_task = asyncio.create_task(self._synthesize_sentence(sentence))

                audio_path = await next_task
                next_sentence = sentences[index + 1] if index + 1 < len(sentences) else None
                next_task = (
                    asyncio.create_task(self._synthesize_sentence(next_sentence))
                    if next_sentence and not self._stop_event.is_set()
                    else None
                )

                if audio_path is not None and not self._stop_event.is_set():
                    await self._play_audio_file(audio_path)
                    self._cleanup_audio(audio_path)

            if not self._stop_event.is_set():
                sounds.play("done")
        finally:
            self.is_speaking = False
            is_speaking = False
            audit.log("tts_stop", {"stopped": self._stop_event.is_set()})

    def stop(self) -> None:
        self._stop_event.set()
        try:
            import pygame

            if pygame.mixer.get_init():
                pygame.mixer.stop()
        except Exception:
            pass

    async def _synthesize_sentence(self, sentence: str) -> Path | None:
        if settings.voice.tts_engine.lower() == "piper":
            return await asyncio.to_thread(self._synthesize_piper, sentence)
        if settings.voice.tts_engine.lower() == "kokoro":
            audit.log("tts_unavailable", {"engine": "kokoro", "reason": "not_implemented"})
            return None

        audit.log("tts_unavailable", {"engine": settings.voice.tts_engine, "reason": "unknown_engine"})
        return None

    def _synthesize_piper(self, sentence: str) -> Path | None:
        model_path = Path(settings.voice.piper_model_path)
        config_path = Path(settings.voice.piper_config_path)
        piper_bin = shutil.which("piper") or shutil.which("piper.exe")

        if not piper_bin or not model_path.is_file() or not config_path.is_file():
            audit.log(
                "tts_unavailable",
                {
                    "engine": "piper",
                    "piper_bin": bool(piper_bin),
                    "model": str(model_path),
                    "config": str(config_path),
                },
            )
            return None

        output = Path(tempfile.NamedTemporaryFile(prefix="jarvis-tts-", suffix=".wav", delete=False).name)
        command = [
            piper_bin,
            "--model",
            str(model_path),
            "--config",
            str(config_path),
            "--output_file",
            str(output),
        ]
        subprocess.run(command, input=sentence, text=True, check=True, capture_output=True)
        audit.log("tts_synthesized", {"sentence_length": len(sentence), "output": str(output)})
        return output

    async def _play_audio_file(self, audio_path: Path) -> None:
        await asyncio.to_thread(sounds.play_file, audio_path, blocking=True)

    def _split_sentences(self, text: str) -> list[str]:
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]

    def _cleanup_audio(self, audio_path: Path) -> None:
        try:
            audio_path.unlink(missing_ok=True)
        except OSError:
            audit.log("tts_cleanup_failed", {"path": str(audio_path)})


tts = TTSEngine()

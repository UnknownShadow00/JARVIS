"""Streaming text-to-speech facade for Piper first, Kokoro later."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from app.config import settings
from app.logs.audit import audit
from app.voice.sounds import sounds

is_speaking = False
cooldown_until: float = 0.0
_COOLDOWN_SECONDS: float = 2.0
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TTSEngine:
    def __init__(self) -> None:
        self._stop_event = asyncio.Event()

    async def speak(self, text: str) -> None:
        """Speak text sentence-by-sentence so audio begins as soon as possible."""
        global is_speaking

        sentences = self._split_sentences(text)
        if not sentences:
            return

        self._stop_event.clear()
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
            global cooldown_until
            cooldown_until = time.monotonic() + _COOLDOWN_SECONDS
            is_speaking = False
            audit.log("tts_stop", {"stopped": self._stop_event.is_set()})

    async def speak_stream(
        self,
        tokens: AsyncIterator[str] | Iterator[str],
    ) -> None:
        """Speak a token stream sentence-by-sentence as soon as boundaries appear."""
        global is_speaking

        self._stop_event.clear()
        is_speaking = True
        audit.log("tts_start", {"engine": settings.voice.tts_engine, "streaming": True})

        spoken_sentences = 0
        buffer = ""

        try:
            async for token in self._iterate_tokens(tokens):
                if self._stop_event.is_set() or spoken_sentences >= 2:
                    break

                buffer += token
                while not self._stop_event.is_set():
                    sentence, remainder = self._extract_complete_sentence(buffer)
                    if sentence is None:
                        break
                    await self._speak_sentence(sentence)
                    spoken_sentences += 1
                    buffer = remainder
                    if spoken_sentences >= 2:
                        break

            if not self._stop_event.is_set() and spoken_sentences < 2 and buffer.strip():
                await self._speak_sentence(buffer.strip())
                spoken_sentences += 1

            if spoken_sentences and not self._stop_event.is_set():
                sounds.play("done")
        finally:
            global cooldown_until
            cooldown_until = time.monotonic() + _COOLDOWN_SECONDS
            is_speaking = False
            audit.log("tts_stop", {"stopped": self._stop_event.is_set(), "streaming": True})

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
        model_path = self._resolve_project_path(settings.voice.piper_model_path)
        config_path = self._resolve_project_path(settings.voice.piper_config_path)
        local_piper = PROJECT_ROOT / "piper" / "piper.exe"
        piper_bin = shutil.which("piper") or shutil.which("piper.exe")
        if piper_bin is None and local_piper.is_file():
            piper_bin = str(local_piper)

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

    def _resolve_project_path(self, path: str) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return PROJECT_ROOT / candidate

    async def _play_audio_file(self, audio_path: Path) -> None:
        await asyncio.to_thread(sounds.play_file, audio_path, blocking=True)

    def _split_sentences(self, text: str) -> list[str]:
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]

    async def _iterate_tokens(
        self,
        tokens: AsyncIterator[str] | Iterator[str],
    ) -> AsyncIterator[str]:
        if hasattr(tokens, "__aiter__"):
            async for token in tokens:
                yield token
            return

        for token in tokens:
            yield token

    def _extract_complete_sentence(self, buffer: str) -> tuple[str | None, str]:
        match = re.search(r"[.!?](?=\s|$)", buffer)
        if match is None:
            return None, buffer

        sentence = buffer[: match.end()].strip()
        remainder = buffer[match.end() :].lstrip()
        return (sentence or None), remainder

    async def _speak_sentence(self, sentence: str) -> None:
        if not sentence:
            return

        audio_path = await self._synthesize_sentence(sentence)
        if audio_path is None or self._stop_event.is_set():
            return

        await self._play_audio_file(audio_path)
        self._cleanup_audio(audio_path)

    def _cleanup_audio(self, audio_path: Path) -> None:
        try:
            audio_path.unlink(missing_ok=True)
        except OSError:
            audit.log("tts_cleanup_failed", {"path": str(audio_path)})


tts = TTSEngine()

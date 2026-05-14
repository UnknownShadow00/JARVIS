"""Streaming text-to-speech facade with Chatterbox/Kokoro/Piper fallback."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
import gc
import os
import re
import shutil
import subprocess
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any

from app.brain.cancel_token import current_token
from app.config import settings
from app.logs.audit import audit
from app.voice.sounds import sounds

_ChatterboxTTS: Any | None = None
CHATTERBOX_AVAILABLE: bool | None = None
_kokoro: Any | None = None
KOKORO_AVAILABLE: bool | None = None

_PARALINGUISTIC_RE = re.compile(r"\[(?:laugh|chuckle|cough)\]", re.IGNORECASE)

is_speaking = False
cooldown_until: float = 0.0
_COOLDOWN_SECONDS: float = 2.0
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TTSEngine:
    def __init__(self) -> None:
        self._stop_event = asyncio.Event()
        self._chatterbox_model: Any | None = None
        self._chatterbox_conditioning: Any | None = None

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
                if self._stop_event.is_set() or self._cancel_requested():
                    return

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
                    if self._cancel_requested():
                        self._cleanup_audio(audio_path)
                        return
                    await self._play_audio_file(audio_path)
                    self._cleanup_audio(audio_path)

            if not self._stop_event.is_set() and not current_token.is_cancelled():
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
                if self._stop_event.is_set() or spoken_sentences >= 2 or self._cancel_requested():
                    return

                buffer += token
                while not self._stop_event.is_set():
                    if self._cancel_requested():
                        return
                    sentence, remainder = self._extract_complete_sentence(buffer)
                    if sentence is None:
                        break
                    await self._speak_sentence(sentence)
                    spoken_sentences += 1
                    buffer = remainder
                    if spoken_sentences >= 2:
                        break

            if not self._stop_event.is_set() and spoken_sentences < 2 and buffer.strip():
                if self._cancel_requested():
                    return
                await self._speak_sentence(buffer.strip())
                spoken_sentences += 1

            if spoken_sentences and not self._stop_event.is_set() and not current_token.is_cancelled():
                sounds.play("done")
        finally:
            global cooldown_until
            cooldown_until = time.monotonic() + _COOLDOWN_SECONDS
            is_speaking = False
            audit.log("tts_stop", {"stopped": self._stop_event.is_set(), "streaming": True})

    def stop(self) -> None:
        self._stop_event.set()
        try:
            os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="pkg_resources is deprecated.*", category=UserWarning)
                import pygame

            if pygame.mixer.get_init():
                pygame.mixer.stop()
        except Exception:
            pass

    def unload_models(self) -> None:
        self.stop()
        self._chatterbox_model = None
        self._chatterbox_conditioning = None
        gc.collect()
        audit.log("tts_models_unloaded", {})

    async def _synthesize_sentence(self, sentence: str) -> Path | None:
        engine = settings.voice.tts_engine.lower()
        if engine == "chatterbox":
            return await self._synthesize_with_fallback(sentence, start_at="chatterbox")
        if engine == "kokoro":
            return await self._synthesize_with_fallback(sentence, start_at="kokoro")
        if engine == "piper":
            return await self._synthesize_with_fallback(sentence, start_at="piper")

        audit.log("tts_unavailable", {"engine": settings.voice.tts_engine, "reason": "unknown_engine"})
        return await self._synthesize_with_fallback(sentence, start_at="piper")

    async def _synthesize_with_fallback(self, sentence: str, *, start_at: str) -> Path | None:
        engines = ["chatterbox", "kokoro", "piper"]
        start_index = engines.index(start_at)
        for engine in engines[start_index:]:
            try:
                if engine == "chatterbox":
                    if not self._chatterbox_available():
                        audit.log(
                            "tts_unavailable",
                            {"engine": "chatterbox", "reason": "import_error_fallback"},
                        )
                        continue
                    return await asyncio.to_thread(self._synthesize_chatterbox, sentence)
                if engine == "kokoro":
                    if not self._kokoro_available():
                        audit.log("tts_unavailable", {"engine": "kokoro", "reason": "import_error_fallback"})
                        continue
                    return await asyncio.to_thread(self._synthesize_kokoro, self._strip_paralinguistics(sentence))
                if engine == "piper":
                    return await asyncio.to_thread(self._synthesize_piper, self._strip_paralinguistics(sentence))
            except Exception as exc:  # noqa: BLE001
                audit.log("tts_unavailable", {"engine": engine, "reason": str(exc)})
                continue
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

    def _get_chatterbox(self) -> object:
        if self._chatterbox_model is not None:
            return self._chatterbox_model

        if not self._chatterbox_available() or _ChatterboxTTS is None:
            raise ImportError("chatterbox-tts is not installed")

        clone_path = self._resolve_voice_clone_path()
        try:
            self._chatterbox_model = self._create_chatterbox_model("cuda", clone_path)
        except RuntimeError:
            self._chatterbox_model = self._create_chatterbox_model("cpu", clone_path)
        return self._chatterbox_model

    def _create_chatterbox_model(self, device: str, clone_path: Path | None) -> object:
        if not self._chatterbox_available() or _ChatterboxTTS is None:
            raise ImportError("chatterbox-tts is not installed")

        init_attempts: list[dict[str, str]] = [{}]
        if clone_path is not None:
            init_attempts = [
                {"voice_clone_path": str(clone_path)},
                {"audio_prompt_path": str(clone_path)},
                {"voice_path": str(clone_path)},
                {"speaker_wav": str(clone_path)},
                {"reference_audio_path": str(clone_path)},
                {},
            ]

        last_type_error: TypeError | None = None
        for extra_kwargs in init_attempts:
            try:
                model = _ChatterboxTTS.from_pretrained(device=device, **extra_kwargs)
                self._prepare_chatterbox_conditioning(model, clone_path)
                return model
            except TypeError as exc:
                last_type_error = exc
                continue

        if last_type_error is not None:
            raise last_type_error
        raise RuntimeError("Unable to initialize Chatterbox model")

    def _resolve_voice_clone_path(self) -> Path | None:
        clone_value = getattr(settings.voice, "voice_clone_path", "").strip()
        if not clone_value:
            return None

        clone_path = self._resolve_project_path(clone_value)
        if not clone_path.exists():
            audit.log("tts_voice_clone_skipped", {"path": str(clone_path), "reason": "missing"})
            return None
        return clone_path

    def _prepare_chatterbox_conditioning(self, model: object, clone_path: Path | None) -> None:
        self._chatterbox_conditioning = None
        if clone_path is None:
            return

        for method_name in ("prepare_conditioning", "prepare_conditoning"):
            method = getattr(model, method_name, None)
            if method is None:
                continue
            try:
                self._chatterbox_conditioning = method(str(clone_path))
                return
            except Exception as exc:
                audit.log(
                    "tts_voice_clone_skipped",
                    {"path": str(clone_path), "reason": f"{method_name}_failed", "error": str(exc)},
                )
                return

    def _synthesize_chatterbox(self, sentence: str) -> Path | None:
        model = self._get_chatterbox()
        output = Path(tempfile.NamedTemporaryFile(prefix="jarvis-tts-", suffix=".wav", delete=False).name)

        try:
            wav = model.generate(sentence, **self._chatterbox_generate_kwargs())
        except TypeError:
            wav = model.generate(sentence)

        self._write_wav_file(output, wav)
        audit.log("tts_chatterbox", {"text_length": len(sentence)})
        return output

    def _synthesize_kokoro(self, sentence: str) -> Path | None:
        if not self._kokoro_available() or _kokoro is None:
            raise ImportError("kokoro is not installed")

        output = Path(tempfile.NamedTemporaryFile(prefix="jarvis-tts-", suffix=".wav", delete=False).name)
        pipeline_factory = getattr(_kokoro, "KPipeline", None) or getattr(_kokoro, "Pipeline", None)
        if pipeline_factory is None:
            raise ImportError("kokoro pipeline API not available")

        pipeline = pipeline_factory(lang_code="a")
        voice = getattr(settings.voice, "kokoro_voice", "af_heart")
        speed = float(getattr(settings.voice, "kokoro_speed", 1.0))
        generator = pipeline(sentence, voice=voice, speed=speed)

        wav = None
        for item in generator:
            if isinstance(item, tuple) and item:
                wav = item[-1]
            else:
                wav = item
            break
        if wav is None:
            return None

        self._write_wav_file(output, wav)
        audit.log("tts_kokoro", {"text_length": len(sentence), "voice": voice})
        return output

    def _chatterbox_generate_kwargs(self) -> dict[str, Any]:
        if self._chatterbox_conditioning is None:
            return {}
        return {"conditioning": self._chatterbox_conditioning}

    def _write_wav_file(self, path: Path, wav: Any) -> None:
        audio = self._waveform_to_numpy(wav)
        try:
            import soundfile as sf

            sf.write(path, audio, 22050)
            return
        except ImportError:
            from scipy.io.wavfile import write as wav_write

            wav_write(path, 22050, audio)

    def _waveform_to_numpy(self, wav: Any) -> Any:
        audio = wav
        if hasattr(audio, "detach"):
            audio = audio.detach()
        if hasattr(audio, "cpu"):
            audio = audio.cpu()
        if hasattr(audio, "numpy"):
            audio = audio.numpy()
        return audio

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

        if self._cancel_requested():
            self._cleanup_audio(audio_path)
            return
        await self._play_audio_file(audio_path)
        self._cleanup_audio(audio_path)

    def _cleanup_audio(self, audio_path: Path) -> None:
        try:
            audio_path.unlink(missing_ok=True)
        except OSError:
            audit.log("tts_cleanup_failed", {"path": str(audio_path)})

    def _strip_paralinguistics(self, sentence: str) -> str:
        return _PARALINGUISTIC_RE.sub("", sentence).strip()

    def _cancel_requested(self) -> bool:
        if not current_token.is_cancelled():
            return False
        self.stop()
        return True

    def _chatterbox_available(self) -> bool:
        global CHATTERBOX_AVAILABLE, _ChatterboxTTS
        if CHATTERBOX_AVAILABLE is not None:
            return bool(CHATTERBOX_AVAILABLE and _ChatterboxTTS is not None)

        try:
            from chatterbox.tts_turbo import ChatterboxTurboTTS

            _ChatterboxTTS = ChatterboxTurboTTS
            CHATTERBOX_AVAILABLE = True
            return True
        except ImportError:
            try:
                from chatterbox.tts import ChatterboxTTS

                _ChatterboxTTS = ChatterboxTTS
                CHATTERBOX_AVAILABLE = True
                return True
            except ImportError:
                _ChatterboxTTS = None
                CHATTERBOX_AVAILABLE = False
                return False

    def _kokoro_available(self) -> bool:
        global KOKORO_AVAILABLE, _kokoro
        if KOKORO_AVAILABLE is not None:
            return bool(KOKORO_AVAILABLE and _kokoro is not None)

        try:
            import kokoro as kokoro_module  # type: ignore[import-untyped]

            _kokoro = kokoro_module
            KOKORO_AVAILABLE = True
            return True
        except ImportError:
            _kokoro = None
            KOKORO_AVAILABLE = False
            return False


tts = TTSEngine()


def unload_models() -> None:
    tts.unload_models()

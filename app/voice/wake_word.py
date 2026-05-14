"""Wake word and push-to-talk entry point for voice capture."""
from __future__ import annotations

import queue
import time

from app.config import settings
from app.logs.audit import audit
from app.voice import tts as tts_module
from app.voice.sounds import sounds
from app.voice.vad import vad


def is_speaking() -> bool:
    """Return whether TTS output is currently active."""
    return bool(tts_module.is_speaking)


class WakeWordDetector:
    sample_rate = 16_000
    frame_samples = 1_280
    _POST_DETECTION_GAP: float = 6.0

    def __init__(self) -> None:
        self._model = None
        self._last_detection_at: float = 0.0

    def listen(self, timeout: float | None = None) -> bytes:
        """Block until wake word or push-to-talk, then return WAV bytes for STT.

        Returns b"" on timeout or if hardware/model is unavailable.
        Silently skips frames while tts_module.is_speaking to prevent self-triggering.
        """
        if self._push_to_talk_active():
            return self._record_push_to_talk()

        try:
            import numpy as np
            import sounddevice as sd
        except ImportError as exc:
            audit.log("wake_unavailable", {"reason": str(exc)})
            return b""

        model = self._load_model()
        if model is None:
            return b""

        audio_queue: queue.Queue[bytes] = queue.Queue()
        deadline = time.monotonic() + timeout if timeout is not None else None

        def callback(indata, frames, time_info, status):  # noqa: ANN001, ARG001
            if status:
                audit.log("wake_stream_status", {"status": str(status)})
            audio_queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_samples,
            dtype="int16",
            channels=1,
            device=None if settings.voice.input_device_index < 0 else settings.voice.input_device_index,
            callback=callback,
        ):
            while True:
                if deadline is not None and time.monotonic() >= deadline:
                    audit.log("wake_timeout", {"timeout": timeout})
                    return b""

                try:
                    frame = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    if self._push_to_talk_active():
                        return self._record_push_to_talk()
                    continue

                if self._push_to_talk_active():
                    return self._record_push_to_talk()

                if is_speaking() or time.monotonic() < tts_module.cooldown_until:
                    continue

                if time.monotonic() - self._last_detection_at < self._POST_DETECTION_GAP:
                    continue

                prediction = model.predict(np.frombuffer(frame, dtype=np.int16))
                score = self._score(prediction)
                if score >= settings.voice.wake_word_sensitivity:
                    audit.log("wake_detected", {"score": score})
                    sounds.play("listening")
                    audio = vad.record_until_silence()
                    self._last_detection_at = time.monotonic()
                    return audio

    def _load_model(self):  # noqa: ANN202
        if self._model is not None:
            return self._model

        try:
            from openwakeword.model import Model
        except ImportError as exc:
            audit.log("wake_unavailable", {"reason": str(exc)})
            return None

        self._model = Model(
            wakeword_models=[settings.voice.wake_word_model],
            inference_framework="onnx",
        )
        audit.log("wake_model_loaded", {"model": settings.voice.wake_word_model})
        return self._model

    def unload_model(self) -> None:
        self._model = None
        audit.log("wake_model_unloaded", {"model": settings.voice.wake_word_model})

    def _push_to_talk_active(self) -> bool:
        try:
            import keyboard

            return bool(keyboard.is_pressed(settings.voice.push_to_talk_key))
        except Exception:
            return False

    def _record_push_to_talk(self) -> bytes:
        audit.log("wake_push_to_talk", {"key": settings.voice.push_to_talk_key})
        sounds.play("listening")
        return vad.record_until_silence()

    def _score(self, prediction) -> float:  # noqa: ANN001
        if isinstance(prediction, dict):
            return float(prediction.get(settings.voice.wake_word_model, max(prediction.values(), default=0.0)))
        return 0.0


wake_word = WakeWordDetector()


def unload_model() -> None:
    wake_word.unload_model()


if __name__ == "__main__":
    print("Listening for wake word. Press Ctrl+C to stop.")
    try:
        while True:
            audio = wake_word.listen()
            print(f"Captured {len(audio)} bytes")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped.")

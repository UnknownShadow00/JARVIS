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
    _UNAVAILABLE_AUDIT_INTERVAL_SECONDS: float = 300.0

    def __init__(self) -> None:
        self._model = None
        self._last_detection_at: float = 0.0
        self.last_trigger: str | None = None
        self.last_listen_outcome: str = "idle"
        self._unavailable_reason: str | None = None
        self._last_unavailable_audit_at: float = 0.0
        self._suppressed_unavailable_repeats: int = 0

    def listen(self, timeout: float | None = None) -> bytes:
        """Block until wake word or push-to-talk, then return WAV bytes for STT.

        Returns b"" on timeout or if hardware/model is unavailable.
        Silently skips frames while tts_module.is_speaking to prevent self-triggering.
        """
        self.last_trigger = None
        self.last_listen_outcome = "starting"
        if self._dictation_active():
            self.last_listen_outcome = "detected"
            return self._record_dictation()
        if self._push_to_talk_active():
            self.last_listen_outcome = "detected"
            return self._record_push_to_talk()

        try:
            import numpy as np
            import sounddevice as sd
        except ImportError as exc:
            self._mark_unavailable(str(exc))
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

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.frame_samples,
                dtype="int16",
                channels=1,
                device=None if settings.voice.input_device_index < 0 else settings.voice.input_device_index,
                callback=callback,
            ):
                self._mark_available()
                self.last_listen_outcome = "listening"
                while True:
                    if deadline is not None and time.monotonic() >= deadline:
                        self.last_listen_outcome = "timeout"
                        audit.log("wake_timeout", {"timeout": timeout})
                        return b""

                    try:
                        frame = audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        if self._dictation_active():
                            self.last_listen_outcome = "detected"
                            return self._record_dictation()
                        if self._push_to_talk_active():
                            self.last_listen_outcome = "detected"
                            return self._record_push_to_talk()
                        continue

                    if self._dictation_active():
                        self.last_listen_outcome = "detected"
                        return self._record_dictation()
                    if self._push_to_talk_active():
                        self.last_listen_outcome = "detected"
                        return self._record_push_to_talk()

                    if is_speaking() or time.monotonic() < tts_module.cooldown_until:
                        continue

                    if time.monotonic() - self._last_detection_at < self._POST_DETECTION_GAP:
                        continue

                    prediction = model.predict(np.frombuffer(frame, dtype=np.int16))
                    score = self._score(prediction)
                    if score >= settings.voice.wake_word_sensitivity:
                        self.last_trigger = "wake"
                        self.last_listen_outcome = "detected"
                        audit.log("wake_detected", {"score": score})
                        sounds.play("listening")
                        audio = vad.record_until_silence()
                        self._last_detection_at = time.monotonic()
                        return audio
        except Exception as exc:  # noqa: BLE001 - missing/lost audio hardware is fail-safe
            self._mark_unavailable(str(exc))
            return b""

    def _load_model(self):  # noqa: ANN202
        if self._model is not None:
            return self._model

        try:
            from openwakeword.model import Model
        except ImportError as exc:
            self._mark_unavailable(str(exc))
            return None

        try:
            self._model = Model(
                wakeword_models=[settings.voice.wake_word_model],
                inference_framework="onnx",
            )
        except Exception as exc:  # noqa: BLE001 - model unavailability is fail-safe
            self._mark_unavailable(str(exc))
            return None
        audit.log("wake_model_loaded", {"model": settings.voice.wake_word_model})
        return self._model

    def _mark_unavailable(self, reason: str) -> None:
        now = time.monotonic()
        normalized_reason = reason or "unknown audio availability failure"
        same_reason = normalized_reason == self._unavailable_reason
        within_interval = now - self._last_unavailable_audit_at < self._UNAVAILABLE_AUDIT_INTERVAL_SECONDS
        self.last_listen_outcome = "unavailable"

        if same_reason and within_interval:
            self._suppressed_unavailable_repeats += 1
            return

        data = {"reason": normalized_reason}
        if same_reason and self._suppressed_unavailable_repeats:
            data["suppressed_repeats"] = self._suppressed_unavailable_repeats
        audit.log("wake_unavailable", data)
        self._unavailable_reason = normalized_reason
        self._last_unavailable_audit_at = now
        self._suppressed_unavailable_repeats = 0

    def _mark_available(self) -> None:
        if self._unavailable_reason is None:
            return
        audit.log(
            "wake_available_recovered",
            {
                "previous_reason": self._unavailable_reason,
                "suppressed_repeats": self._suppressed_unavailable_repeats,
            },
        )
        self._unavailable_reason = None
        self._last_unavailable_audit_at = 0.0
        self._suppressed_unavailable_repeats = 0

    def unload_model(self) -> None:
        self._model = None
        audit.log("wake_model_unloaded", {"model": settings.voice.wake_word_model})

    def _push_to_talk_active(self) -> bool:
        try:
            import keyboard

            return bool(keyboard.is_pressed(settings.voice.push_to_talk_key))
        except Exception:
            return False

    def _dictation_active(self) -> bool:
        if not settings.voice.dictation_enabled:
            return False
        try:
            import keyboard

            return bool(keyboard.is_pressed(settings.voice.dictation_hotkey))
        except Exception:
            return False

    def _record_push_to_talk(self) -> bytes:
        self.last_trigger = "ptt"
        audit.log("wake_push_to_talk", {"key": settings.voice.push_to_talk_key})
        sounds.play("listening")
        return vad.record_until_silence()

    def _record_dictation(self) -> bytes:
        self.last_trigger = "dictation"
        audit.log("wake_dictation", {"key": settings.voice.dictation_hotkey})
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

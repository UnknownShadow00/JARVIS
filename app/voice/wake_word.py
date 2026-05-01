"""Wake word and push-to-talk entry point for voice capture."""
from __future__ import annotations

import queue
import time

from app.config import settings
from app.logs.audit import audit
from app.voice import tts as tts_module
from app.voice.sounds import sounds
from app.voice.vad import vad


class WakeWordDetector:
    sample_rate = 16_000
    frame_samples = 1_280

    def __init__(self) -> None:
        self._model = None

    def listen(self) -> bytes:
        """Block until wake word or push-to-talk, then return WAV bytes for STT."""
        if self._push_to_talk_active():
            audit.log("wake_push_to_talk", {"key": settings.voice.push_to_talk_key})
            sounds.play("listening")
            return vad.record_until_silence()

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
                frame = audio_queue.get()
                if tts_module.is_speaking:
                    continue

                prediction = model.predict(np.frombuffer(frame, dtype=np.int16))
                score = self._score(prediction)
                if score >= settings.voice.wake_word_sensitivity:
                    audit.log("wake_detected", {"score": score})
                    sounds.play("listening")
                    return vad.record_until_silence()

    def _load_model(self):  # noqa: ANN202
        if self._model is not None:
            return self._model

        try:
            from openwakeword.model import Model
        except ImportError as exc:
            audit.log("wake_unavailable", {"reason": str(exc)})
            return None

        self._model = Model(wakeword_models=[settings.voice.wake_word_model])
        audit.log("wake_model_loaded", {"model": settings.voice.wake_word_model})
        return self._model

    def _push_to_talk_active(self) -> bool:
        try:
            import keyboard

            return bool(keyboard.is_pressed(settings.voice.push_to_talk_key))
        except Exception:
            return False

    def _score(self, prediction) -> float:  # noqa: ANN001
        if isinstance(prediction, dict):
            return float(prediction.get(settings.voice.wake_word_model, max(prediction.values(), default=0.0)))
        return 0.0


wake_word = WakeWordDetector()


if __name__ == "__main__":
    print("Listening for wake word. Press Ctrl+C to stop.")
    try:
        while True:
            audio = wake_word.listen()
            print(f"Captured {len(audio)} bytes")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped.")

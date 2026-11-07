"""Voice activity detection using webrtcvad."""
from __future__ import annotations

import io
import queue
import time
import wave

from app.config import settings
from app.logs.audit import audit


class VoiceActivityDetector:
    sample_rate = 16_000
    frame_ms = 30
    min_speech_seconds = 0.5
    max_record_seconds = 12.0
    trailing_silence_seconds = 0.5

    def record_until_silence(self, timeout: float | None = None) -> bytes:
        try:
            import sounddevice as sd
            import webrtcvad
        except ImportError as exc:
            audit.log("vad_unavailable", {"reason": str(exc)})
            return b""

        vad = webrtcvad.Vad(settings.voice.vad_aggressiveness)
        frame_samples = int(self.sample_rate * self.frame_ms / 1000)
        frame_bytes = frame_samples * 2
        audio_queue: queue.Queue[bytes] = queue.Queue()

        def callback(indata, frames, time_info, status):  # noqa: ANN001, ARG001
            if status:
                audit.log("vad_stream_status", {"status": str(status)})
            audio_queue.put(bytes(indata))

        recorded: list[bytes] = []
        speech_started = False
        speech_frames = 0
        silence_frames = 0
        max_record_seconds = min(self.max_record_seconds, timeout) if timeout is not None else self.max_record_seconds
        max_post_speech_frames = int(max_record_seconds * 1000 / self.frame_ms)
        min_speech_frames = int(self.min_speech_seconds * 1000 / self.frame_ms)
        stop_silence_frames = int(self.trailing_silence_seconds * 1000 / self.frame_ms)
        started_at = time.perf_counter()
        pre_speech_deadline = started_at + max_record_seconds

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=frame_samples,
            dtype="int16",
            channels=1,
            device=None if settings.voice.input_device_index < 0 else settings.voice.input_device_index,
            callback=callback,
        ):
            while True:
                try:
                    frame = audio_queue.get(timeout=0.1)
                except Exception:
                    if not speech_started and time.perf_counter() > pre_speech_deadline:
                        break
                    continue

                if len(frame) != frame_bytes:
                    continue

                has_speech = vad.is_speech(frame, self.sample_rate)
                if has_speech:
                    speech_started = True
                    speech_frames += 1
                    silence_frames = 0
                    recorded.append(frame)
                    continue

                if not speech_started:
                    if time.perf_counter() > pre_speech_deadline:
                        break
                    continue

                silence_frames += 1
                recorded.append(frame)
                if speech_frames >= min_speech_frames and silence_frames >= stop_silence_frames:
                    break
                if len(recorded) >= max_post_speech_frames:
                    break

        duration = time.perf_counter() - started_at
        wav_data = self._to_wav_bytes(recorded)
        audit.log(
            "vad_recorded",
            {"duration_seconds": round(duration, 3), "bytes": len(wav_data), "speech_frames": speech_frames},
        )
        return wav_data if speech_frames >= min_speech_frames else b""

    def _to_wav_bytes(self, frames: list[bytes]) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(b"".join(frames))
        return buffer.getvalue()


vad = VoiceActivityDetector()


def record_until_silence(timeout: float | None = None) -> bytes:
    return vad.record_until_silence(timeout=timeout)

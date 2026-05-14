"""End-to-end voice pipeline loop."""
from __future__ import annotations

import asyncio
import threading

from app.brain.llm_client import OllamaConnectionError
from app.logs.audit import audit
from app.voice.sounds import sounds
from app.voice.stt import stt
from app.voice.tts import tts
from app.voice.wake_word import wake_word

is_listening = False


class VoicePipeline:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.listen_timeout_seconds = 3.0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_thread, name="jarvis-voice-pipeline", daemon=True)
        self._thread.start()
        audit.log("voice_pipeline_started", {})

    def stop(self) -> None:
        self._stop_event.set()
        tts.stop()
        audit.log("voice_pipeline_stopped", {})

    def _run_thread(self) -> None:
        asyncio.run(self.run())

    async def run(self) -> None:
        global is_listening

        while not self._stop_event.is_set():
            try:
                is_listening = True
                audit.log("voice_listening", {})
                audio = await asyncio.to_thread(wake_word.listen, timeout=self.listen_timeout_seconds)
                is_listening = False
                if not audio:
                    continue

                text = await asyncio.to_thread(stt.transcribe, audio)
                if not text:
                    continue

                sounds.play("working")
                audit.log("voice_request", {"text": text})

                from app.server import _process, _process_stream

                stream_result = await _process_stream(text)
                if stream_result is not None:
                    token_stream, intent = stream_result
                    chunks: list[str] = []

                    async def _tts_tokens():
                        async for chunk in token_stream:
                            chunks.append(chunk)
                            yield chunk

                    await tts.speak_stream(_tts_tokens())
                    from app.brain.response_cleaner import clean
                    reply = clean("".join(chunks))
                else:
                    reply, intent = await _process(text)
                    await tts.speak(reply)

                audit.log("voice_reply", {"intent": intent.intent, "reply": reply})
            except OllamaConnectionError as exc:
                is_listening = False
                audit.log("voice_pipeline_error", {"error": str(exc)})
                sounds.play("error")
                await tts.speak("Ollama is unreachable, sir. Standing by until the model is back.")
            except Exception as exc:
                is_listening = False
                audit.log("voice_pipeline_error", {"error": str(exc)})
                sounds.play("error")
                await tts.speak("Afraid something went wrong, sir. Standing by.")


voice_pipeline = VoicePipeline()

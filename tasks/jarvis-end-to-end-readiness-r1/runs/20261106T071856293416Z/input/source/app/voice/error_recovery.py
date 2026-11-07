from __future__ import annotations

import asyncio
import sys
from typing import Any

OLLAMA_DOWN_PHRASE = (
    "Apologies, sir — the model service appears to be offline. Attempting to reconnect."
)
TIMEOUT_PHRASE = "Afraid the model is taking too long to respond, sir. Retrying."
UNKNOWN_ERROR_PHRASE = "A system fault has occurred, sir. Standing by."


def speak_error(message: str) -> None:
    """Best-effort TTS for recovery errors without raising into the caller."""
    try:
        from app.voice.tts import tts
    except Exception:
        print(message, file=sys.stderr)
        return

    try:
        coroutine = tts.speak(message)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coroutine)
            return

        task = loop.create_task(coroutine)
        task.add_done_callback(_swallow_task_error)
    except Exception:
        print(message, file=sys.stderr)


def _swallow_task_error(task: asyncio.Task[Any]) -> None:
    try:
        task.result()
    except Exception:
        pass

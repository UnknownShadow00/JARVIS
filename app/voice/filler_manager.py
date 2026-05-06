from __future__ import annotations

import asyncio

from app.logs.audit import audit
from app.voice.phrase_cache import phrase_cache
from app.voice.tts import tts


TOOL_FILLERS: dict[str, str] = {
    "web_search": "searching",
    "browser": "on_it",
    "browser_use": "on_it",
    "shell": "working",
    "vision": "looking",
    "screenshot": "looking",
    "interpreter": "working",
    "cad": "working",
    "default": "on_it",
}


class FillerManager:
    def play_for_tool(self, tool_name: str) -> None:
        phrase_key = TOOL_FILLERS.get(tool_name, TOOL_FILLERS["default"])
        phrase = phrase_cache.get(phrase_key)
        try:
            asyncio.get_running_loop().create_task(tts.speak(phrase))
            audit.log("filler_started", {"tool": tool_name, "phrase_key": phrase_key})
        except RuntimeError:
            audit.log("filler_skipped", {"tool": tool_name, "reason": "no_running_loop"})


filler_manager = FillerManager()

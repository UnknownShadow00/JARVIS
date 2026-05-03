from __future__ import annotations

from typing import Any

from app.computer import screenshot
from app.config import settings
from app.logs.audit import audit


SAFETY_LEVEL = 0
DESCRIPTION = "Capture and analyze screen or webcam via Qwen3-VL vision model"

VISION_SOURCE_SCREEN = "screen"
VISION_SOURCE_WEBCAM = "webcam"


class VisionClient:
    def __init__(self) -> None:
        self._llm_client = None

    def _get_llm_client(self):  # type: ignore[no-untyped-def]
        if self._llm_client is None:
            from app.brain.llm_client import LLMClient

            self._llm_client = LLMClient()
        return self._llm_client

    def analyze(
        self,
        source: str = VISION_SOURCE_SCREEN,
        prompt: str = "What do you see?",
    ) -> dict[str, Any]:
        if settings.safety.dry_run:
            return {"dry_run": True, "note": f"Would analyze {source}"}

        audit.log("tool_call", {"tool": "vision", "source": source, "prompt": prompt})

        if source == VISION_SOURCE_SCREEN:
            image_path = screenshot.capture()
        elif source == VISION_SOURCE_WEBCAM:
            return {"error": "webcam not yet implemented", "phase": 4}
        else:
            return {"error": f"unknown source: {source}"}

        result = {
            "stub": True,
            "note": "Qwen3-VL integration in Phase 4",
            "source": source,
            "image_path": image_path,
        }
        audit.log("tool_result", {"tool": "vision", "stub": True})
        return result


vision_client = VisionClient()


def execute(params: dict[str, Any]) -> dict[str, Any]:
    source = params.get("source", VISION_SOURCE_SCREEN)
    prompt = params.get("prompt", "What do you see?")
    return vision_client.analyze(source, prompt)

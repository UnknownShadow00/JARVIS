from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx


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
            image_b64 = self._encode_file_to_base64(image_path)
        elif source == VISION_SOURCE_WEBCAM:
            try:
                import cv2
            except ImportError:
                return {
                    "error": "opencv not installed",
                    "install": "pip install opencv-python",
                    "phase": 4,
                }

            capture = cv2.VideoCapture(0)
            try:
                ok, frame = capture.read()
                if not ok:
                    return {"error": "unable to capture webcam frame", "source": source}

                ok, buffer = cv2.imencode(".jpg", frame)
                if not ok:
                    return {"error": "unable to encode webcam frame", "source": source}

                image_path = None
                image_b64 = base64.b64encode(buffer.tobytes()).decode("ascii")
            finally:
                capture.release()
        else:
            return {"error": f"unknown source: {source}"}

        payload = {
            "model": settings.models.vision,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
        }
        url = f"{settings.models.ollama_base_url}/api/generate"

        try:
            response = httpx.post(url, json=payload, timeout=httpx.Timeout(120.0))
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return {"error": str(exc), "source": source}

        payload_result = response.json()
        analysis = str(
            payload_result.get("response")
            or payload_result.get("message", {}).get("content")
            or ""
        ).strip()
        if not analysis:
            return {"error": "vision model returned no analysis", "source": source}

        result = {
            "source": source,
            "analysis": analysis,
            "image_path": image_path,
        }
        audit.log("tool_result", {"tool": "vision", "source": source, "image_path": image_path})
        return result

    def _encode_file_to_base64(self, image_path: str) -> str:
        return base64.b64encode(Path(image_path).read_bytes()).decode("ascii")

    def unload(self) -> None:
        self._llm_client = None
        audit.log("vision_client_unloaded", {})


vision_client = VisionClient()


def execute(params: dict[str, Any]) -> dict[str, Any]:
    source = params.get("source", VISION_SOURCE_SCREEN)
    prompt = params.get("prompt", "What do you see?")
    return vision_client.analyze(source, prompt)

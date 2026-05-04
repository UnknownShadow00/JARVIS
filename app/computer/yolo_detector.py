from __future__ import annotations

from typing import Any

from app.computer import screenshot
from app.config import settings
from app.logs.audit import audit


SAFETY_LEVEL = 0
DESCRIPTION = "Detect objects in screen or image using YOLO"

try:
    from ultralytics import YOLO

    YOLO_AVAILABLE = True
except ImportError:
    YOLO = None
    YOLO_AVAILABLE = False


class YOLODetector:
    def __init__(self) -> None:
        self._model = None

    def _get_model(self):  # type: ignore[no-untyped-def]
        if not YOLO_AVAILABLE:
            return None

        if self._model is None:
            self._model = YOLO("yolov8n.pt")

        return self._model

    def detect(self, source: str = "screen", image_path: str | None = None) -> dict[str, Any]:
        if settings.safety.dry_run:
            return {"dry_run": True, "note": "Would run YOLO detection"}

        if not YOLO_AVAILABLE:
            return {
                "error": "ultralytics not installed",
                "install": "pip install ultralytics",
                "phase": 4,
            }

        if image_path is None and source == "screen":
            image_path = screenshot.capture()
        elif image_path is None:
            return {"error": f"image_path required for source: {source}"}

        audit.log("tool_call", {"tool": "yolo_detector", "source": source, "image_path": image_path})

        try:
            model = self._get_model()
            if model is None:
                return {
                    "error": "ultralytics not installed",
                    "install": "pip install ultralytics",
                    "phase": 4,
                }

            results = model(image_path)
            result = results[0]
            names = result.names
            detections: list[dict[str, Any]] = []

            for box in result.boxes.data:
                x1, y1, x2, y2, confidence, cls_id = box.tolist() if hasattr(box, "tolist") else box
                detections.append(
                    {
                        "label": str(names[int(cls_id)]),
                        "confidence": float(confidence),
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    }
                )

            response = {"detections": detections, "count": len(detections), "source": source}
            audit.log("tool_result", {"tool": "yolo_detector", "source": source, "count": len(detections)})
            return response
        except Exception as exc:
            return {"error": str(exc)}


yolo_detector = YOLODetector()

from __future__ import annotations

SAFETY_LEVEL = 0
DESCRIPTION = "Hand gesture recognition via MediaPipe (Phase 3 stub)"


class GestureController:
    def start(self) -> dict:
        try:
            import mediapipe  # noqa: F401
        except ImportError:
            return {"error": "mediapipe not installed", "install": "pip install mediapipe", "phase": 3}
        return {"stub": True, "note": "Full gesture control wired in Phase 3 with webcam loop", "phase": 3}

    def stop(self) -> dict:
        return {"stopped": True}


gesture_controller = GestureController()


def execute(params: dict) -> dict:
    action = params.get("action", "start")
    if action == "stop":
        return gesture_controller.stop()
    return gesture_controller.start()

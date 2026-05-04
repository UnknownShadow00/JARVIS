from __future__ import annotations

import builtins

from app.computer.gesture import gesture_controller


def test_start_no_mediapipe(monkeypatch) -> None:  # noqa: ANN001
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: ANN001, A002
        if name == "mediapipe":
            raise ImportError("missing mediapipe")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = gesture_controller.start()

    assert "error" in result


def test_stop() -> None:
    assert gesture_controller.stop() == {"stopped": True}

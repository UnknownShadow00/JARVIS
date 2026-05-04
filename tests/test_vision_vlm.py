from __future__ import annotations

from app.computer import vision
from app.config import settings


class _FakeResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, str]:
        return self._payload


def test_dry_run_screen(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)

    result = vision.execute({"source": "screen"})

    assert "dry_run" in result


def test_screen_calls_ollama(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.screenshot.capture", lambda: "/tmp/shot.png")
    monkeypatch.setattr(vision.vision_client, "_encode_file_to_base64", lambda path: "ZmFrZQ==")
    monkeypatch.setattr(
        vision.httpx,
        "post",
        lambda *args, **kwargs: _FakeResponse({"response": "a desktop"}),
    )

    result = vision.execute({"source": "screen"})

    assert result["analysis"] == "a desktop"


def test_webcam_no_opencv(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)

    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: ANN001,A002
        if name == "cv2":
            raise ImportError("missing cv2")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    result = vision.execute({"source": "webcam"})

    assert "error" in result


def test_unknown_source(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)

    result = vision.execute({"source": "invalid"})

    assert "error" in result

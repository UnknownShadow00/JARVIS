from __future__ import annotations

from app.computer import vision
from app.config import settings


def test_safety_level() -> None:
    assert vision.SAFETY_LEVEL == 0


def test_screen_stub(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.screenshot.capture", lambda: "/tmp/test.png")

    result = vision.execute({"source": "screen"})

    assert result["stub"] is True
    assert result["image_path"] == "/tmp/test.png"


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)

    result = vision.execute({})

    assert "dry_run" in result


def test_webcam_not_implemented(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)

    result = vision.execute({"source": "webcam"})

    assert "error" in result
    assert "phase" in result


def test_unknown_source(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)

    result = vision.execute({"source": "lidar"})

    assert "error" in result

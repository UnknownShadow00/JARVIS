from __future__ import annotations

from types import SimpleNamespace

from app.computer.yolo_detector import yolo_detector
from app.config import settings


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)

    result = yolo_detector.detect()

    assert result["dry_run"] is True


def test_no_ultralytics(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.yolo_detector.YOLO_AVAILABLE", False)

    result = yolo_detector.detect()

    assert "error" in result
    assert "ultralytics" in result["error"]


def test_detect_with_mocked_model(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.yolo_detector.YOLO_AVAILABLE", True)

    mock_result = SimpleNamespace(
        boxes=SimpleNamespace(data=[]),
        names={},
    )

    def fake_get_model():  # type: ignore[no-untyped-def]
        return lambda image_path: [mock_result]

    monkeypatch.setattr(yolo_detector, "_get_model", fake_get_model)

    result = yolo_detector.detect("screen", image_path="/tmp/fake.png")

    assert "detections" in result
    assert result["detections"] == []


def test_detect_error(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.yolo_detector.YOLO_AVAILABLE", True)

    class FailingModel:
        def __call__(self, image_path: str):  # noqa: ANN204
            raise RuntimeError("model failed")

    monkeypatch.setattr(yolo_detector, "_get_model", lambda: FailingModel())

    result = yolo_detector.detect()

    assert "error" in result
    assert result["error"] == "model failed"

from __future__ import annotations

from app.config import settings
from app.tools import screenshot as screenshot_tool
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert screenshot_tool.SAFETY_LEVEL == 0


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)

    result = screenshot_tool.execute({})

    assert "dry_run" in result


def test_registered() -> None:
    assert ToolRegistry().get("screenshot") is not None


def test_capture_imports_error(monkeypatch) -> None:  # noqa: ANN001
    def fake_capture(monitor: int = 0, output_dir: str | None = None) -> str:
        raise RuntimeError("mss not installed")

    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.screenshot.capture", fake_capture)

    result = screenshot_tool.execute({})

    assert result == {"error": "mss not installed"}

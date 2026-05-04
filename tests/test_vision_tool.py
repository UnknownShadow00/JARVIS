from __future__ import annotations

from app.config import settings
from app.tools import vision as vision_tool
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert vision_tool.SAFETY_LEVEL == 0


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)

    result = vision_tool.execute({"source": "screen"})

    assert "dry_run" in result


def test_registered() -> None:
    assert ToolRegistry().get("vision") is not None


def test_unknown_source(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)

    result = vision_tool.execute({"source": "unknown_xyz"})

    assert "error" in result

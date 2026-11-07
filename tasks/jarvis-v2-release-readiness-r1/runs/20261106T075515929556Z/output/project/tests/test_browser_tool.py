from __future__ import annotations

from app.config import settings
from app.tools import browser as browser_tool
from app.tools.registry import registry


def test_safety_level() -> None:
    assert browser_tool.SAFETY_LEVEL == 1


def test_dry_run(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = browser_tool.execute({"url": "https://example.com"})
    assert "dry_run" in result


def test_missing_url(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    result = browser_tool.execute({})
    assert result["error"] == "url required"


def test_unknown_action(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    result = browser_tool.execute({"url": "x", "action": "fly"})
    assert "unknown action" in result["error"]


def test_open_url(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    opened: list[str] = []
    monkeypatch.setattr(browser_tool.webbrowser, "open", lambda url: opened.append(url))

    browser_tool.execute({"url": "https://example.com"})

    assert opened == ["https://example.com"]


def test_search_action(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    opened: list[str] = []
    monkeypatch.setattr(browser_tool.webbrowser, "open", lambda url: opened.append(url))

    browser_tool.execute({"url": "hello world", "action": "search"})

    assert opened
    assert "google.com/search" in opened[0]


def test_registered() -> None:
    assert "browser" in registry.TOOLS

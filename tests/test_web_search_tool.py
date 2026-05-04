from __future__ import annotations

import builtins
from unittest.mock import patch

from app.tools import web_search
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert web_search.SAFETY_LEVEL == 0


def test_dry_run() -> None:
    with patch("app.config.settings.safety.dry_run", True):
        result = web_search.execute({"query": "test"})
    assert "dry" in str(result).lower()


def test_no_ddgs() -> None:
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name in {"ddgs", "duckduckgo_search"}:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    with patch("app.config.settings.safety.dry_run", False), patch("builtins.__import__", side_effect=fake_import):
        result = web_search.execute({"query": "test"})
    assert isinstance(result, dict)
    assert "error" in result


def test_fetch_bad_url() -> None:
    with patch("app.config.settings.safety.dry_run", False):
        result = web_search.execute({"action": "fetch", "url": "not-a-url"})
    assert isinstance(result, dict)
    assert "error" in result


def test_registered() -> None:
    assert ToolRegistry().get("web_search") is not None

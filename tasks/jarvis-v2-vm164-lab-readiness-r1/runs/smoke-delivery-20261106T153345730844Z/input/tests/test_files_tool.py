from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

from app.tools import files
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert files.SAFETY_LEVEL == 1


def test_dry_run() -> None:
    with patch("app.config.settings.safety.dry_run", True):
        result = files.execute({"action": "list"})
    assert "dry" in str(result).lower()


def test_list_allowed_root(monkeypatch) -> None:
    local_root = Path("tasks/.files_tool_test").resolve()
    try:
        local_root.mkdir(parents=True, exist_ok=True)
        with patch("app.config.settings.safety.dry_run", False), patch.object(
            type(files.settings),
            "files",
            create=True,
            new_callable=PropertyMock,
            return_value=SimpleNamespace(allowed_roots=[str(local_root)]),
        ):
            result = files.execute({"action": "list", "path": str(local_root)})
        assert isinstance(result, list)
    finally:
        shutil.rmtree(local_root, ignore_errors=True)


def test_read_missing_file() -> None:
    with patch("app.config.settings.safety.dry_run", False):
        result = files.execute({"action": "read", "path": "/nonexistent/path/file.txt"})
    assert isinstance(result, dict)
    assert "error" in result


def test_registered() -> None:
    assert ToolRegistry().get("files") is not None

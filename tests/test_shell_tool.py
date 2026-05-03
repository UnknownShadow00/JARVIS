from __future__ import annotations

import sys

import pytest

from app.config import settings
from app.tools import shell
from app.tools.registry import ToolError, registry


@pytest.fixture(autouse=True)
def restore_registry_and_settings():
    original_tool = registry._tools.get("shell")  # noqa: SLF001
    original_dry_run = settings.safety.dry_run
    registry._tools["shell"] = shell  # noqa: SLF001
    try:
        yield
    finally:
        if original_tool is None:
            registry._tools.pop("shell", None)  # noqa: SLF001
        else:
            registry._tools["shell"] = original_tool  # noqa: SLF001
        settings.safety.dry_run = original_dry_run


def test_blocked_command_raises() -> None:
    with pytest.raises(PermissionError):
        shell.execute({"command": "rm -rf /"})


def test_cwd_outside_allowed_roots_raises() -> None:
    with pytest.raises(ValueError):
        shell.execute({"command": "echo hello", "cwd": "/totally/outside"})


def test_empty_command_returns_error_dict() -> None:
    result = shell.execute({"command": "   "})
    assert isinstance(result, dict)
    assert "error" in result


def test_safe_command_returns_output() -> None:
    result = shell.execute({"command": "echo hello"})
    assert result["returncode"] == 0
    assert "hello" in result["stdout"].lower()


def test_timeout_returns_error_dict() -> None:
    command = f'"{sys.executable}" -c "import time; time.sleep(5)"'
    result = shell.execute({"command": command, "timeout": 1})
    assert result["error"] == "timeout"


def test_registry_blocks_without_confirmation() -> None:
    with pytest.raises(ToolError):
        registry.call("shell", {"command": "echo hi"})


def test_registry_dry_run() -> None:
    settings.safety.dry_run = True
    result = registry.call("shell", {"command": "echo hi"}, confirmed=True)
    assert result.dry_run is True

"""Shell command tool with root-boundary checks and hard-denied patterns."""
from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from app.config import settings

SAFETY_LEVEL = 2
DESCRIPTION = "Run a shell command. Requires confirmation. Blocked commands rejected outright."

_BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"rmdir\s+/s",
    r"format\s",
    r"del\s+/s",
    r"shutdown",
    r"reboot",
    r"mkfs",
    r"dd\s+if=",
    r":\(\)\{\s*:\|:&\s*\};:",
    r">\s*/dev/sda",
    r"sudo\s+rm",
    r"net\s+user\s+.*\s+/add",
    r"reg\s+delete",
]
_MAX_STDOUT = 4000
_MAX_STDERR = 2000


def execute(params: dict[str, Any]) -> Any:
    """Run a shell command inside approved roots with bounded output and timeout."""
    command = str(params.get("command") or "").strip()
    if not command:
        return {"error": "missing command"}

    if settings.safety.dry_run:
        return {
            "dry_run": True,
            "command": command,
            "note": "Would run shell command: " + command,
        }

    _ensure_command_allowed(command)

    timeout = min(int(params.get("timeout") or 30), 120)
    resolved_cwd = _resolve_cwd(params.get("cwd"))

    try:
        result = subprocess.run(
            command if sys.platform == "win32" else shlex.split(command),
            shell=sys.platform == "win32",
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=resolved_cwd,
        )
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "command": command, "timeout": timeout}

    return {
        "command": command,
        "cwd": str(resolved_cwd),
        "returncode": result.returncode,
        "stdout": result.stdout[:_MAX_STDOUT],
        "stderr": result.stderr[:_MAX_STDERR],
    }


def _ensure_command_allowed(command: str) -> None:
    for pattern in _BLOCKED_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            raise PermissionError(f"Blocked command pattern detected: {pattern}")


def _resolve_cwd(cwd: Any) -> Path:
    repo_root = Path(__file__).parent.parent.parent.resolve()
    if cwd is None:
        return repo_root

    target = Path(str(cwd)).expanduser().resolve()
    if not _is_allowed_root(target, repo_root):
        raise ValueError(f"cwd is outside allowed roots: {target}")
    return target


def _is_allowed_root(target: Path, repo_root: Path) -> bool:
    allowed_roots = [repo_root]
    for item in (settings.paths.projects_dir, settings.paths.downloads_dir):
        try:
            allowed_roots.append(Path(item).expanduser().resolve())
        except OSError:
            continue

    for root in allowed_roots:
        try:
            target.relative_to(root)
            return True
        except ValueError:
            continue
    return False

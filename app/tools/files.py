"""File operations tool - read, list, search, and move within allowed roots."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from app.config import settings

SAFETY_LEVEL = 1
DESCRIPTION = "Read, list, search, or move files within configured safe roots. Does not delete."

_MAX_READ_BYTES = 32_768
_MAX_SEARCH_BYTES = 256_000
_MAX_SEARCH_RESULTS = 50


def execute(params: dict[str, Any]) -> Any:
    """Dispatch file actions after enforcing allowed root boundaries."""
    action: str = str(params.get("action", "list")).lower()
    if settings.safety.dry_run:
        return f"[DRY RUN] Would execute files action '{action}' with params {params}"

    try:
        if action == "list":
            return list_dir(str(params.get("path", ".")))
        if action == "read":
            return read_file(str(params.get("path", "")))
        if action == "search":
            return search_files(str(params.get("path", ".")), str(params.get("query", "")))
        if action == "move":
            return _move(params)
    except PermissionError as exc:
        return {"error": str(exc)}
    return {"error": f"Unknown file action: {action!r}"}


def list_dir(path: str) -> list[str]:
    """Return a directory listing for an allowed path."""
    target = _safe_path(path)
    if not target.exists():
        return [f"Path does not exist: {target}"]
    if target.is_file():
        return [str(target)]
    entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    return [str(e) for e in entries]


def read_file(path: str) -> str | dict[str, str]:
    """Read a UTF-8 text file from an allowed path."""
    target = _safe_path(path)
    if not target.is_file():
        return {"error": f"File not found: {target}"}
    size = target.stat().st_size
    if size > _MAX_READ_BYTES:
        return {"error": f"File too large to read ({size} bytes). Max is {_MAX_READ_BYTES}."}
    try:
        return target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {"error": f"Read error: {exc}"}


def search_files(path: str, query: str) -> list[str]:
    """Find allowed files whose name or small text content matches query."""
    if not query:
        return []

    root = _safe_path(path)
    if not root.exists():
        return [f"Path does not exist: {root}"]

    needle = query.lower()
    matches: list[str] = []
    candidates = [root] if root.is_file() else root.rglob("*")

    for item in candidates:
        if len(matches) >= _MAX_SEARCH_RESULTS:
            break
        try:
            if not item.is_file() or not _is_allowed(item):
                continue
            if needle in item.name.lower():
                matches.append(str(item))
                continue
            if item.stat().st_size <= _MAX_SEARCH_BYTES:
                content = item.read_text(encoding="utf-8", errors="ignore").lower()
                if needle in content:
                    matches.append(str(item))
        except (OSError, UnicodeError):
            continue

    return matches


def _move(params: dict[str, Any]) -> str:
    src = _safe_path(str(params.get("src", "")))
    dst = _safe_path(str(params.get("dst", "")))
    if not src.exists():
        return f"Source does not exist: {src}"
    try:
        shutil.move(str(src), str(dst))
        return f"Moved {src.name} to {dst}, sir."
    except Exception as exc:
        return f"Move failed: {exc}"


def _safe_path(path: str) -> Path:
    target = Path(path or ".").expanduser().resolve()
    if not _is_allowed(target):
        raise PermissionError(f"Path is outside allowed roots: {target}")
    return target


def _allowed_roots() -> list[Path]:
    configured_roots = getattr(getattr(settings, "files", None), "allowed_roots", None)
    if configured_roots:
        roots: list[Path] = []
        for item in configured_roots:
            try:
                roots.append(Path(item).expanduser().resolve())
            except OSError:
                continue
        if roots:
            return roots

    repo_root = Path(__file__).resolve().parents[2]
    configured = [
        settings.paths.projects_dir,
        settings.paths.downloads_dir,
        settings.paths.datasheets_dir,
    ]
    roots = [repo_root]
    for item in configured:
        try:
            roots.append(Path(item).expanduser().resolve())
        except OSError:
            continue
    return roots


def _is_allowed(path: Path) -> bool:
    target = path.expanduser().resolve()
    for root in _allowed_roots():
        try:
            target.relative_to(root)
            return True
        except ValueError:
            continue
    return False

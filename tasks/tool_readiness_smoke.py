from __future__ import annotations

import asyncio
import builtins
import importlib.util
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class SmokeResult:
    name: str
    passed: bool
    detail: str


@contextmanager
def temporary_attr(target: Any, name: str, value: Any) -> Iterator[None]:
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def _pass(name: str, detail: str) -> SmokeResult:
    return SmokeResult(name=name, passed=True, detail=detail)


def _fail(name: str, detail: str) -> SmokeResult:
    return SmokeResult(name=name, passed=False, detail=detail)


def _has_key(result: Any, key: str) -> bool:
    return isinstance(result, dict) and key in result


def check_browser() -> SmokeResult:
    from app.config import settings
    from app.tools import browser

    with temporary_attr(settings.safety, "dry_run", True):
        opened = browser.execute({"action": "open", "url": "https://example.com"})
        searched = browser.execute({"action": "search", "url": "jarvis smoke"})

    if _has_key(opened, "dry_run") and _has_key(searched, "dry_run"):
        return _pass("browser dry-run open/search", "open and search returned dry-run responses")
    return _fail("browser dry-run open/search", f"unexpected responses: {opened!r}; {searched!r}")


def check_files() -> SmokeResult:
    from app.config import settings
    from app.tools import files

    with temporary_attr(settings.safety, "dry_run", False):
        listing = files.execute({"action": "list", "path": str(REPO_ROOT / "tasks")})
        readme = files.execute({"action": "read", "path": str(REPO_ROOT / "README.md")})
        search = files.execute({"action": "search", "path": str(REPO_ROOT / "tests"), "query": "tool"})

    if isinstance(listing, list) and isinstance(readme, str) and isinstance(search, list):
        return _pass("files list/read/search", "repo-local list, read, and search completed")
    return _fail("files list/read/search", f"unexpected responses: {listing!r}; {type(readme).__name__}; {search!r}")


def check_calendar() -> SmokeResult:
    from app.config import settings
    from app.tools import calendar

    empty_calendar_dir = REPO_ROOT / "tasks" / ".tool_readiness_empty_calendar"
    empty_calendar_dir.mkdir(parents=True, exist_ok=True)
    try:
        with temporary_attr(settings.safety, "dry_run", False), temporary_attr(
            calendar, "SEARCH_PATHS", [empty_calendar_dir]
        ):
            result = calendar.execute({"date": "2000-01-01"})
    finally:
        try:
            empty_calendar_dir.rmdir()
        except OSError:
            pass

    if isinstance(result, dict) and result.get("count") == 0 and result.get("events") == []:
        return _pass("calendar no-ICS fallback", "empty calendar path returned zero events")
    return _fail("calendar no-ICS fallback", f"unexpected response: {result!r}")


def check_screenshot() -> SmokeResult:
    from app.config import settings
    from app.tools import screenshot

    has_mss = importlib.util.find_spec("mss") is not None
    with temporary_attr(settings.safety, "dry_run", True):
        result = screenshot.execute({})

    if _has_key(result, "dry_run"):
        return _pass("screenshot dependency/status", f"dry-run ok; mss_installed={has_mss}")
    return _fail("screenshot dependency/status", f"unexpected response: {result!r}; mss_installed={has_mss}")


def check_system_stats() -> SmokeResult:
    from app.config import settings
    from app.tools import system_stats

    with temporary_attr(settings.safety, "dry_run", False):
        result = system_stats.execute({})

    expected = {"cpu_percent", "ram_total_gb", "disk_total_gb", "top_cpu_processes"}
    if isinstance(result, dict) and expected <= result.keys():
        return _pass("system stats collection", "required CPU/RAM/disk/process keys returned")
    return _fail("system stats collection", f"unexpected response: {result!r}")


def check_shell() -> SmokeResult:
    from app.config import settings
    from app.tools import shell

    with temporary_attr(settings.safety, "dry_run", True):
        dry_run = shell.execute({"command": "echo hello"})

    blocked = False
    with temporary_attr(settings.safety, "dry_run", False):
        try:
            shell.execute({"command": "shutdown now"})
        except PermissionError:
            blocked = True

    if _has_key(dry_run, "dry_run") and blocked:
        return _pass("shell dry-run/blocked rejection", "dry-run returned and blocked command raised PermissionError")
    return _fail("shell dry-run/blocked rejection", f"dry_run={dry_run!r}; blocked={blocked}")


def check_apps() -> SmokeResult:
    from app.config import settings
    from app.tools import apps

    with temporary_attr(settings.safety, "dry_run", True):
        known = apps.execute({"action": "open", "app": "notepad"})
    with temporary_attr(settings.safety, "dry_run", False):
        unknown = apps.execute({"action": "open", "app": "nonexistent_xyz_app_12345"})

    if "dry" in str(known).lower() and _has_key(unknown, "error"):
        return _pass("apps known/unknown behavior", "known app dry-run and unknown app error returned")
    return _fail("apps known/unknown behavior", f"unexpected responses: {known!r}; {unknown!r}")


def check_memory_rag() -> SmokeResult:
    from app.memory import memory_client as memory_module
    from app.memory import rag_client as rag_module

    with temporary_attr(memory_module.settings.memory, "mem0_enabled", False), temporary_attr(
        rag_module, "CHROMADB_AVAILABLE", False
    ):
        memory_result = memory_module.MemoryClient().search("smoke")
        rag_result = rag_module.RAGClient().query("smoke")

    if _has_key(memory_result, "stub") and _has_key(rag_result, "stub"):
        return _pass("memory/RAG disabled stubs", "Mem0 and ChromaDB returned stub responses")
    return _fail("memory/RAG disabled stubs", f"unexpected responses: {memory_result!r}; {rag_result!r}")


def check_comms() -> SmokeResult:
    from app.comms import discord_bot as discord_module
    from app.comms import telegram_bot as telegram_module

    async def run_checks() -> tuple[dict, dict]:
        with temporary_attr(discord_module.settings.comms, "discord_enabled", False), temporary_attr(
            telegram_module.settings.comms, "telegram_enabled", False
        ):
            discord_result = await discord_module.DiscordBot().send_message("smoke")
            telegram_result = await telegram_module.TelegramBot().send_message("smoke")
        return discord_result, telegram_result

    discord_result, telegram_result = asyncio.run(run_checks())
    if _has_key(discord_result, "stub") and _has_key(telegram_result, "stub"):
        return _pass("Discord/Telegram disabled stubs", "both comms integrations returned disabled stubs")
    return _fail("Discord/Telegram disabled stubs", f"unexpected responses: {discord_result!r}; {telegram_result!r}")


def check_interpreter_computer_use() -> SmokeResult:
    from app.config import settings
    from app.tools import computer_use, interpreter

    original_import = builtins.__import__

    def fake_import(name: str, globals: Any = None, locals: Any = None, fromlist: Any = (), level: int = 0) -> Any:
        if name == "computer_use":
            raise ImportError("missing computer_use")
        return original_import(name, globals, locals, fromlist, level)

    with temporary_attr(settings.safety, "dry_run", False):
        interpreter_result = interpreter.execute({"task": "list files", "timeout": 1})
        with temporary_attr(builtins, "__import__", fake_import):
            computer_result = computer_use.execute({"task": "inspect screen"})

    interpreter_ok = _has_key(interpreter_result, "error") or "returncode" in interpreter_result
    computer_ok = _has_key(computer_result, "error") or _has_key(computer_result, "stub")
    if interpreter_ok and computer_ok:
        return _pass(
            "interpreter/computer-use dependency responses",
            f"interpreter={_response_shape(interpreter_result)}; computer_use={_response_shape(computer_result)}",
        )
    return _fail(
        "interpreter/computer-use dependency responses",
        f"unexpected responses: {interpreter_result!r}; {computer_result!r}",
    )


def _response_shape(result: Any) -> str:
    if isinstance(result, dict):
        for key in ("error", "stub", "returncode", "dry_run"):
            if key in result:
                return key
    return type(result).__name__


CHECKS: list[Callable[[], SmokeResult]] = [
    check_browser,
    check_files,
    check_calendar,
    check_screenshot,
    check_system_stats,
    check_shell,
    check_apps,
    check_memory_rag,
    check_comms,
    check_interpreter_computer_use,
]


def run_smoke() -> list[SmokeResult]:
    results: list[SmokeResult] = []
    for check in CHECKS:
        try:
            results.append(check())
        except Exception as exc:  # noqa: BLE001
            check_name = check.__name__.removeprefix("check_").replace("_", " ")
            results.append(_fail(check_name, f"{type(exc).__name__}: {exc}"))
    return results


def print_results(results: list[SmokeResult]) -> None:
    name_width = max([len("Check"), *(len(result.name) for result in results)])
    status_width = len("Status")
    print(f"{'Check':<{name_width}}  {'Status':<{status_width}}  Detail")
    print(f"{'-' * name_width}  {'-' * status_width}  {'-' * 60}")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{result.name:<{name_width}}  {status:<{status_width}}  {result.detail}")


def main() -> int:
    results = run_smoke()
    print_results(results)
    failures = [result for result in results if not result.passed]
    if failures:
        print(f"\n{len(failures)} readiness check(s) failed.")
        return 1
    print(f"\n{len(results)} readiness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

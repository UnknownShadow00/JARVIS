from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CommandCheck:
    name: str
    command: list[str]


@dataclass(frozen=True)
class CommandResult:
    name: str
    returncode: int
    command: list[str]
    error: str = ""

    @property
    def passed(self) -> bool:
        return self.returncode == 0 and not self.error


def _npm_command() -> str:
    executable = shutil.which("npm.cmd") or shutil.which("npm")
    if executable is None:
        raise FileNotFoundError("npm was not found on PATH")
    return executable


def build_checks(*, include_full_tests: bool = True) -> list[CommandCheck]:
    checks: list[CommandCheck] = []
    if include_full_tests:
        checks.append(
            CommandCheck(
                "full pytest",
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
            )
        )

    npm = _npm_command()
    checks.extend(
        [
            CommandCheck(
                "python dependency audit",
                [sys.executable, "-m", "pip_audit", "-r", "requirements.txt"],
            ),
            CommandCheck("python dependency consistency", [sys.executable, "-m", "pip", "check"]),
            CommandCheck(
                "electron dependency audit",
                [npm, "audit", "--prefix", "frontend/electron", "--audit-level=high"],
            ),
            CommandCheck("readiness report", [sys.executable, "tasks/readiness_report.py"]),
            CommandCheck("tool readiness smoke", [sys.executable, "tasks/tool_readiness_smoke.py"]),
        ]
    )
    return checks


def run_check(check: CommandCheck) -> CommandResult:
    print(f"\n== {check.name} ==", flush=True)
    print("> " + " ".join(check.command), flush=True)
    try:
        completed = subprocess.run(check.command, cwd=REPO_ROOT, text=True, check=False)
    except OSError as exc:
        print(f"ERROR: {exc}", flush=True)
        return CommandResult(check.name, 1, check.command, str(exc))
    return CommandResult(check.name, completed.returncode, check.command)


def print_summary(results: list[CommandResult]) -> None:
    print("\n== Summary ==", flush=True)
    width = max([len("Check"), *(len(result.name) for result in results)])
    print(f"{'Check':<{width}}  Status", flush=True)
    print(f"{'-' * width}  ------", flush=True)
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{result.name:<{width}}  {status}", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run JARVIS pre-server readiness checks.")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the full pytest run and execute only dependency/readiness checks.",
    )
    args = parser.parse_args(argv)

    try:
        checks = build_checks(include_full_tests=not args.skip_tests)
    except OSError as exc:
        print(f"Unable to build readiness checks: {exc}", flush=True)
        return 1

    results = [run_check(check) for check in checks]
    print_summary(results)

    failures = [result for result in results if not result.passed]
    if failures:
        print(f"\n{len(failures)} pre-server readiness check(s) failed.", flush=True)
        return 1

    print(f"\n{len(results)} pre-server readiness checks passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

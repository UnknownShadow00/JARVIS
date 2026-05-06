from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.tools.health_check import check_readiness  # noqa: E402


REQUIRED_CHECKS = (
    "ollama",
    "piper_binary",
    "piper_model",
    "piper_config",
    "wake_model",
    "audio_devices",
    "stt_dependency",
    "vad_dependency",
    "wake_dependency",
    "keyboard_dependency",
)


def print_report(readiness: dict[str, dict]) -> None:
    name_width = max([len("Check"), *(len(item["name"]) for item in readiness.values())])
    print(f"{'Check':<{name_width}}  Status  Detail")
    print(f"{'-' * name_width}  ------  {'-' * 60}")
    for item in readiness.values():
        status = "PASS" if item["available"] else "WARN"
        print(f"{item['name']:<{name_width}}  {status:<6}  {item['detail']}")
        if not item["available"] and item.get("remediation"):
            print(f"{'':<{name_width}}          Next: {item['remediation']}")


def main() -> int:
    readiness = check_readiness()
    print_report(readiness)
    missing_required = [key for key in REQUIRED_CHECKS if not readiness[key]["available"]]
    if missing_required:
        print(f"\n{len(missing_required)} required readiness check(s) need attention before live voice validation.")
        return 1
    print("\nAll required readiness checks passed for live voice validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

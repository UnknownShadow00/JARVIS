"""Create a Windows Task Scheduler entry for JARVIS boot."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    boot_py = root / "app" / "boot.py"
    command = f'"{sys.executable}" "{boot_py}"'

    subprocess.run(
        [
            "schtasks",
            "/create",
            "/tn",
            "JARVIS Boot",
            "/tr",
            command,
            "/sc",
            "onlogon",
            "/rl",
            "highest",
            "/f",
        ],
        check=True,
    )
    print("Created Task Scheduler entry: JARVIS Boot")


if __name__ == "__main__":
    main()

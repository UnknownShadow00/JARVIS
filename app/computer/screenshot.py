from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any

from app.config import settings
from app.logs.audit import audit


SAFETY_LEVEL = 0
DESCRIPTION = "Capture a screenshot and return the file path"


def capture(monitor: int = 0, output_dir: str | None = None) -> str:
    try:
        import mss
        from mss import tools as mss_tools
    except ImportError as exc:
        raise RuntimeError("mss not installed: pip install mss") from exc

    target_dir = Path(output_dir or (Path(tempfile.gettempdir()) / "jarvis_screenshots"))
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"jarvis_shot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.abspath(target_dir / filename)

    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[monitor])
        mss_tools.to_png(shot.rgb, shot.size, output=path)

    audit.log("tool_screenshot", {"path": path, "monitor": monitor})
    return path


def execute(params: dict[str, Any]) -> dict[str, Any]:
    monitor = int(params.get("monitor", 0))
    output_dir = params.get("output_dir")

    if settings.safety.dry_run:
        return {"dry_run": True, "note": "Would capture screenshot"}

    try:
        path = capture(monitor=monitor, output_dir=output_dir)
    except RuntimeError as exc:
        return {"error": str(exc)}

    return {"path": path, "monitor": monitor}

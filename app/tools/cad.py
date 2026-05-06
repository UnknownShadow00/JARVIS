from __future__ import annotations

import importlib.util
import shutil
from typing import Any

from app.logs.audit import audit

SAFETY_LEVEL = 2
DESCRIPTION = "CAD design/export planning stub. Never prints automatically."


def execute(params: dict[str, Any]) -> dict[str, Any]:
    prompt = str(params.get("prompt") or params.get("design") or "").strip()
    export = str(params.get("export", "stl")).lower().strip()
    build123d_available = importlib.util.find_spec("build123d") is not None
    slicer = shutil.which("OrcaSlicer") or shutil.which("orca-slicer") or shutil.which("orca-slicer.exe")

    result = {
        "dry_run": True,
        "safety_level": SAFETY_LEVEL,
        "prompt": prompt,
        "export": export,
        "build123d_available": build123d_available,
        "orcaslicer_available": slicer is not None,
        "orcaslicer_path": slicer,
        "plan": [
            "Validate dimensions and material constraints.",
            "Generate build123d model script.",
            f"Export {export} artifact for review.",
            "Optionally slice after explicit user approval.",
        ],
        "note": "Design/export plan only; no printer or slicer execution is performed.",
    }
    if not build123d_available:
        result["build123d_remediation"] = "Install build123d only when live CAD generation is approved."
    if slicer is None:
        result["orcaslicer_remediation"] = "Install OrcaSlicer and add it to PATH before slicing."
    audit.log("cad_stub", result)
    return result

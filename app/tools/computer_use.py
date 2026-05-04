from __future__ import annotations

SAFETY_LEVEL = 2
DESCRIPTION = "Visual GUI automation via open-computer-use (screenshot + AI action)"


def execute(params: dict) -> dict:
    task = str(params.get("task") or "").strip()
    if not task:
        return {"error": "missing task"}

    from app.brain.response_cleaner import dry_run_narration
    from app.config import settings

    if settings.safety.dry_run:
        return {"dry_run": True, "note": "Would execute computer-use task: " + task}

    try:
        import computer_use  # noqa: F401
    except ImportError:
        return {
            "error": "open-computer-use not installed",
            "install": "pip install open-computer-use",
            "phase": 3,
        }

    return {
        "stub": True,
        "note": "Full open-computer-use integration active once package is installed",
        "task": task,
    }

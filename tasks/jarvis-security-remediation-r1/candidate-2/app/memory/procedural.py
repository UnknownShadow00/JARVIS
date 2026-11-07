from __future__ import annotations

from pathlib import Path

from app.logs.audit import audit


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SKILLS_PATH = PROJECT_ROOT / "skills.md"
MAX_PROMPT_ENTRIES = 12


class ProceduralMemory:
    def __init__(self, path: str | Path = DEFAULT_SKILLS_PATH) -> None:
        self.path = Path(path)

    def list_skills(self) -> list[str]:
        if not self.path.is_file():
            return []

        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            audit.log("procedural_memory_read_error", {"path": str(self.path), "error": str(exc)})
            return []

        skills: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                value = stripped[2:].strip()
                if value:
                    skills.append(value)
        return skills

    def prompt_context(self, limit: int = MAX_PROMPT_ENTRIES) -> str:
        skills = self.list_skills()[:limit]
        if not skills:
            return ""

        bullets = "\n".join(f"- {skill}" for skill in skills)
        return f"Procedural memory:\n{bullets}"

    def add_skill(self, skill: str) -> bool:
        cleaned = " ".join(skill.strip().split())
        if not cleaned:
            return False

        existing = {item.lower() for item in self.list_skills()}
        if cleaned.lower() in existing:
            return False

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists() and self.path.stat().st_size > 0:
                prefix = "\n"
            else:
                prefix = "# JARVIS Procedural Memory\n\n"
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(f"{prefix}- {cleaned}\n")
        except OSError as exc:
            audit.log("procedural_memory_write_error", {"path": str(self.path), "error": str(exc)})
            return False

        audit.log("procedural_memory_added", {"path": str(self.path), "length": len(cleaned)})
        return True


procedural_memory = ProceduralMemory()

from __future__ import annotations

import shutil
from pathlib import Path

from app.memory.procedural import ProceduralMemory

TEST_DIR = Path("tasks/.procedural_memory_test")


def _path(name: str) -> Path:
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_DIR / name


def test_list_skills_reads_markdown_bullets() -> None:
    try:
        path = _path("skills.md")
        path.write_text("# Skills\n\n- Check local files first.\n- Use type hints.\n", encoding="utf-8")

        memory = ProceduralMemory(path)

        assert memory.list_skills() == ["Check local files first.", "Use type hints."]
    finally:
        shutil.rmtree(TEST_DIR, ignore_errors=True)


def test_add_skill_deduplicates() -> None:
    try:
        path = _path("skills.md")
        memory = ProceduralMemory(path)

        assert memory.add_skill("Use type hints.") is True
        assert memory.add_skill("Use type hints.") is False
        assert memory.list_skills() == ["Use type hints."]
    finally:
        shutil.rmtree(TEST_DIR, ignore_errors=True)


def test_prompt_context_limits_entries() -> None:
    try:
        path = _path("skills.md")
        path.write_text("\n".join(["# Skills", "- one", "- two", "- three"]), encoding="utf-8")

        memory = ProceduralMemory(path)

        assert memory.prompt_context(limit=2) == "Procedural memory:\n- one\n- two"
    finally:
        shutil.rmtree(TEST_DIR, ignore_errors=True)

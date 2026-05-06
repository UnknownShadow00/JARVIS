from __future__ import annotations

import shutil
from pathlib import Path

from app.brain import prompts
from app.memory.procedural import ProceduralMemory

TEST_DIR = Path("tasks/.prompts_memory_test")


def test_build_prompt_includes_procedural_memory(monkeypatch) -> None:  # noqa: ANN001
    try:
        shutil.rmtree(TEST_DIR, ignore_errors=True)
        TEST_DIR.mkdir(parents=True, exist_ok=True)
        path = TEST_DIR / "skills.md"
        path.write_text("# Skills\n\n- Check power rails first.\n", encoding="utf-8")
        monkeypatch.setattr(prompts, "procedural_memory", ProceduralMemory(path))

        messages = prompts.build_prompt("debug the circuit")

        assert "Procedural memory" in messages[0]["content"]
        assert "Check power rails first." in messages[0]["content"]
    finally:
        shutil.rmtree(TEST_DIR, ignore_errors=True)

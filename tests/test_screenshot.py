from __future__ import annotations

import builtins
import shutil
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

from app.computer.screenshot import SAFETY_LEVEL, capture, execute
from app.config import settings


def test_safety_level() -> None:
    assert SAFETY_LEVEL == 0


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = execute({})
    assert result.get("dry_run") is True


def test_mss_not_installed(monkeypatch) -> None:  # noqa: ANN001
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: ANN001
        if name == "mss":
            raise ImportError("missing mss")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = execute({})

    assert "error" in result


def test_capture_creates_file(monkeypatch) -> None:  # noqa: ANN001
    class FakeMSSContext:
        monitors = ["all", "primary"]

        def __enter__(self) -> "FakeMSSContext":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
            return None

        def grab(self, monitor) -> SimpleNamespace:  # noqa: ANN001
            return SimpleNamespace(rgb=b"fake-rgb", size=(4, 4))

    def fake_to_png(data, size, output):  # noqa: ANN001
        Path(output).write_bytes(b"PNG")

    fake_module = ModuleType("mss")
    fake_module.mss = FakeMSSContext
    fake_module.tools = SimpleNamespace(to_png=fake_to_png)
    monkeypatch.setitem(sys.modules, "mss", fake_module)

    temp_dir = Path("tasks/.screenshot_test_tmp").resolve()
    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        path = capture(output_dir=str(temp_dir))
        assert Path(path).exists()
        assert path.endswith(".png")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_execute_success(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr("app.computer.screenshot.capture", lambda monitor=0, output_dir=None: "/tmp/fake.png")

    result = execute({})

    assert result["path"] == "/tmp/fake.png"

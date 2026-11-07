from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "switch_models.py"
BACKUP_PATH = PROJECT_ROOT / "config.yaml.test-backup"


def _read_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


def _run_switch(profile: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--profile", profile],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def setup_function() -> None:
    shutil.copyfile(CONFIG_PATH, BACKUP_PATH)


def teardown_function() -> None:
    shutil.copyfile(BACKUP_PATH, CONFIG_PATH)
    BACKUP_PATH.unlink(missing_ok=True)


def test_switch_models_exists() -> None:
    assert SCRIPT_PATH.is_file()


def test_4070ti_profile_sets_14b() -> None:
    result = _run_switch("4070ti")
    config = _read_config()

    assert "Switched to 4070ti profile." in result.stdout
    assert "14b" in config["models"]["main"]
    assert "14b" in config["models"]["coder"]


def test_5090_profile_sets_32b() -> None:
    result = _run_switch("5090")
    config = _read_config()

    assert "Switched to 5090 profile." in result.stdout
    assert "32b" in config["models"]["main"]
    assert "32b" in config["models"]["coder"]
    assert config["models"]["vision"] == "qwen3-vl"

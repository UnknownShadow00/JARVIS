import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKUP_SCRIPT = REPO_ROOT / "scripts" / "backup_restic.sh"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_restic_backup.sh"
EXCLUDE_FILE = REPO_ROOT / "config" / "restic-excludes.txt"


def test_restic_scripts_exist_and_use_strict_shell_mode():
    for script in (BACKUP_SCRIPT, VERIFY_SCRIPT):
        assert script.exists()
        assert "set -euo pipefail" in script.read_text(encoding="utf-8")


def test_backup_fails_clearly_without_repository_variable():
    environment = os.environ.copy()
    environment.pop("RESTIC_REPOSITORY", None)
    environment.pop("RESTIC_PASSWORD_FILE", None)

    result = subprocess.run(
        ["bash", str(BACKUP_SCRIPT)],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "RESTIC_REPOSITORY is required" in result.stderr


def test_exclusions_keep_audit_history_but_remove_reproducible_payloads():
    exclusions = EXCLUDE_FILE.read_text(encoding="utf-8")
    assert "models/" in exclusions
    assert "piper/" in exclusions
    assert "node_modules/" in exclusions
    assert "tasks/tmp*.wav" in exclusions
    assert "logs/audit.jsonl" not in {
        line.strip()
        for line in exclusions.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

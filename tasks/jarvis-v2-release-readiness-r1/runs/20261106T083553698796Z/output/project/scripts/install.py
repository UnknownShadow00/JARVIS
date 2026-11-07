from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
CONFIG_FILE = PROJECT_ROOT / "config.yaml"
MODELS_DIR = PROJECT_ROOT / "models"
VOICE_FILE = MODELS_DIR / "en_US-lessac-high.onnx"
VOICE_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "en/en_US/lessac/high/en_US-lessac-high.onnx"
)
OLLAMA_MODELS = ("qwen3:14b", "gemma3:4b")


def print_header(title: str) -> None:
    print(f"\n== {title} ==")


def run_command(command: list[str], *, fatal: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        if fatal:
            print(f"Fatal: command not found: {' '.join(command)}")
            raise SystemExit(1)
        raise


def check_python_version() -> None:
    print_header("Python Check")
    if sys.version_info < (3, 11):
        print(
            "Fatal: JARVIS requires Python 3.11 or newer. "
            f"Current version: {sys.version.split()[0]}"
        )
        raise SystemExit(1)
    print(f"Python OK: {sys.version.split()[0]}")


def read_project_files() -> None:
    print_header("Project Files")
    missing = []
    for path in (REQUIREMENTS_FILE, CONFIG_FILE):
        if not path.exists():
            missing.append(path.name)
            continue
        text = path.read_text(encoding="utf-8")
        print(f"Found {path.name} ({len(text.splitlines())} lines)")

    if REQUIREMENTS_FILE.name in missing:
        print("Fatal: requirements.txt is missing.")
        raise SystemExit(1)

    if CONFIG_FILE.name in missing:
        print("Copy config.yaml.example to config.yaml and edit")


def check_cuda() -> bool:
    print_header("CUDA Check")
    try:
        result = run_command(["nvidia-smi"])
    except FileNotFoundError:
        print("Warning: CUDA/NVIDIA tools not found. GPU acceleration may be unavailable.")
        return True

    if result.returncode != 0:
        print("Warning: `nvidia-smi` did not succeed. GPU acceleration may be unavailable.")
        if result.stderr.strip():
            print(result.stderr.strip())
        return True

    first_line = result.stdout.splitlines()[0] if result.stdout else "nvidia-smi detected"
    print(first_line)
    return False


def check_ollama() -> bool:
    print_header("Ollama Check")
    try:
        result = run_command(["ollama", "--version"])
    except FileNotFoundError:
        print("Warning: Ollama is not installed or not on PATH.")
        print("Install from: https://ollama.com/download")
        return True

    if result.returncode != 0:
        print("Warning: `ollama --version` failed.")
        if result.stderr.strip():
            print(result.stderr.strip())
        print("Install from: https://ollama.com/download")
        return True

    print(result.stdout.strip() or "Ollama detected")
    return False


def install_python_requirements() -> None:
    print_header("Python Dependencies")
    result = run_command(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        fatal=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        print("Fatal: pip install -r requirements.txt failed.")
        raise SystemExit(1)
    print("Python dependencies installed.")


def pull_ollama_models(ollama_missing: bool) -> None:
    print_header("Ollama Models")
    if ollama_missing:
        print("Skipping model pulls because Ollama is unavailable.")
        print("Run: ollama pull qwen3:32b for full 5090 experience")
        return

    for model in OLLAMA_MODELS:
        print(f"Pulling {model}...")
        result = run_command(["ollama", "pull", model])
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            print(f"Warning: failed to pull {model}.")
        else:
            print(f"Pulled {model}.")

    print("Run: ollama pull qwen3:32b for full 5090 experience")


def check_piper_voice() -> None:
    print_header("Piper Voice")
    if VOICE_FILE.exists():
        print(f"Voice model present: {VOICE_FILE}")
        return

    print("Piper voice model missing.")
    print("Download manually (large file):")
    print(f"  {VOICE_URL}")
    print(f"Place it here: {VOICE_FILE}")


def ensure_directories() -> None:
    print_header("Directories")
    for relative in ("data", "logs"):
        path = PROJECT_ROOT / relative
        os.makedirs(path, exist_ok=True)
        print(f"Ready: {path}")


def run_smoke_test() -> None:
    print_header("Smoke Test")
    result = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short", "-x"],
        fatal=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.strip())
        print("Fatal: smoke test failed.")
        raise SystemExit(1)
    print("Smoke test passed.")


def print_final_checklist() -> None:
    print_header("Manual Steps Remaining")
    print("1. Run Electron frontend install: `cd frontend/electron && npm install`")
    print("2. Add the PWA icon at `frontend/pwa/icon.png`")
    print("3. Set `voice.voice_clone_path` in `config.yaml` when your clone is ready")
    print("4. If needed, copy `config.yaml.example` to `config.yaml` and edit it")
    print("5. If needed, download Piper voice files into `models/`")


def main() -> int:
    check_python_version()
    read_project_files()
    cuda_warning = check_cuda()
    ollama_warning = check_ollama()
    install_python_requirements()
    ensure_directories()
    pull_ollama_models(ollama_warning)
    check_piper_voice()
    run_smoke_test()
    print_final_checklist()
    return 2 if (cuda_warning or ollama_warning) else 0


if __name__ == "__main__":
    raise SystemExit(main())

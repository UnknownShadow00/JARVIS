"""Download Piper Windows binary and the configured voice model."""
from __future__ import annotations

import shutil
import urllib.request
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
PIPER_DIR = PROJECT_ROOT / "piper"
MODELS_DIR = PROJECT_ROOT / "models"
PIPER_ZIP_URL = (
    "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/"
    "piper_windows_amd64.zip"
)
VOICE_NAME = "en_US-lessac-high"
VOICE_ONNX_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "en/en_US/lessac/high/en_US-lessac-high.onnx"
)
VOICE_CONFIG_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "en/en_US/lessac/high/en_US-lessac-high.onnx.json"
)
PROGRESS_CHUNK_BYTES = 5 * 1024 * 1024


def ensure_directories() -> None:
    PIPER_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path, description: str) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"Skipping {description}: already exists at {dest}")
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {description}...")

    last_reported = {"bytes": -1}

    def reporthook(block_count: int, block_size: int, total_size: int) -> None:
        downloaded = block_count * block_size
        if downloaded - last_reported["bytes"] < PROGRESS_CHUNK_BYTES:
            return

        last_reported["bytes"] = downloaded
        if total_size > 0:
            percent = min(100, int((downloaded / total_size) * 100))
            print(
                f"  {description}: {downloaded // (1024 * 1024)}MB / "
                f"{total_size // (1024 * 1024)}MB ({percent}%)"
            )
        else:
            print(f"  {description}: {downloaded // (1024 * 1024)}MB downloaded")

    try:
        urllib.request.urlretrieve(url, dest, reporthook=reporthook)
    except Exception as exc:  # pragma: no cover - network failure path
        if dest.exists():
            dest.unlink()
        print(f"Failed to download {description}.")
        print(f"  URL: {url}")
        print(f"  Error: {exc}")
        print("  Suggestion: Check your internet connection and verify the URL.")
        return False

    print(f"Done downloading {description}.")
    return dest.exists() and dest.stat().st_size > 0


def extract_piper(zip_path: Path) -> bool:
    piper_exe = PIPER_DIR / "piper.exe"
    if piper_exe.exists() and piper_exe.stat().st_size > 0:
        print(f"Skipping Piper extraction: already exists at {piper_exe}")
        return True

    print("Extracting Piper Windows x64 binary...")
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue

                target = PIPER_DIR / Path(member.filename).name
                with archive.open(member, "r") as source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
    except Exception as exc:
        print("Failed to extract Piper Windows x64 binary.")
        print(f"  URL: {PIPER_ZIP_URL}")
        print(f"  Error: {exc}")
        print("  Suggestion: Delete the ZIP file and rerun the installer.")
        return False

    print("Done extracting Piper Windows x64 binary.")
    return True


def verify_file(path: Path, minimum_size: int, label: str) -> bool:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    passed = exists and size > minimum_size
    status = "PASS" if passed else "FAIL"
    print(f"{status}: {label} -> {path} ({size} bytes)")
    return passed


def main() -> int:
    ensure_directories()

    piper_zip_path = PIPER_DIR / "piper_windows_amd64.zip"
    voice_onnx_path = MODELS_DIR / f"{VOICE_NAME}.onnx"
    voice_config_path = MODELS_DIR / f"{VOICE_NAME}.onnx.json"

    success = True
    success = download_file(
        PIPER_ZIP_URL, piper_zip_path, "Piper Windows x64 binary ZIP"
    ) and success
    if success:
        success = extract_piper(piper_zip_path) and success

    success = (
        download_file(VOICE_ONNX_URL, voice_onnx_path, f"{VOICE_NAME} voice ONNX")
        and success
    )
    success = download_file(
        VOICE_CONFIG_URL, voice_config_path, f"{VOICE_NAME} voice config"
    ) and success

    print("Verifying installed files...")
    checks = [
        verify_file(PIPER_DIR / "piper.exe", 100 * 1024, "Piper executable"),
        verify_file(voice_onnx_path, 1 * 1024 * 1024, f"{VOICE_NAME} voice ONNX"),
        verify_file(voice_config_path, 1 * 1024, f"{VOICE_NAME} voice config"),
    ]

    print("Setup complete. Run: python -m pytest tests/ -v to verify.")
    return 0 if success and all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

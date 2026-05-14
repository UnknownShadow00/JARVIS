from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from typing import Any

import httpx

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _status(name: str, available: bool, detail: str, remediation: str = "") -> dict[str, Any]:
    return {
        "name": name,
        "available": available,
        "detail": detail,
        "remediation": remediation,
    }


def _path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _wake_model_available(value: str) -> bool:
    if not value:
        return False

    path = Path(value)
    if path.suffix or path.parent != Path("."):
        return _path(value).is_file()

    return True


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _first_binary(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def _piper_binary() -> str | None:
    return _first_binary("piper", "piper.exe") or (
        str(PROJECT_ROOT / "piper" / "piper.exe") if (PROJECT_ROOT / "piper" / "piper.exe").is_file() else None
    )


def _voice_clone_ready() -> tuple[bool, str]:
    value = settings.voice.voice_clone_path.strip()
    if not value:
        return True, "skipped intentionally; no personal voice sample configured"
    path = _path(value)
    return path.is_file(), str(path)


def _pwa_icon_ready() -> tuple[bool, str]:
    path = PROJECT_ROOT / "frontend" / "pwa" / "icon.png"
    return path.is_file(), str(path)


def _electron_install_ready() -> tuple[bool, str]:
    node_modules = PROJECT_ROOT / "frontend" / "electron" / "node_modules"
    package_json = PROJECT_ROOT / "frontend" / "electron" / "package.json"
    if not package_json.is_file():
        return False, str(package_json)
    return node_modules.is_dir(), str(node_modules)


def _ollama_ready() -> tuple[bool, str]:
    try:
        response = httpx.get(f"{settings.models.ollama_base_url}/api/tags", timeout=2.0)
    except httpx.HTTPError as exc:
        return False, f"unreachable at {settings.models.ollama_base_url}: {exc}"
    return response.status_code == 200, f"HTTP {response.status_code} from {settings.models.ollama_base_url}"


def _configured_file(path_value: str) -> tuple[bool, str]:
    path = _path(path_value)
    return path.is_file(), str(path)


def _audio_devices_ready() -> tuple[bool, str]:
    if not _module_available("sounddevice"):
        return False, "sounddevice is not installed"

    try:
        import sounddevice as sd

        devices = sd.query_devices()
    except Exception as exc:  # noqa: BLE001
        return False, f"sounddevice query failed: {exc}"

    input_count = 0
    output_count = 0
    for device in devices:
        try:
            input_count += 1 if int(device.get("max_input_channels", 0)) > 0 else 0
            output_count += 1 if int(device.get("max_output_channels", 0)) > 0 else 0
        except AttributeError:
            continue
    return input_count > 0 and output_count > 0, f"{input_count} input device(s), {output_count} output device(s)"


def check_readiness() -> dict[str, dict[str, Any]]:
    """Return detailed readiness for local services, voice, and deferred integrations."""
    ollama_available, ollama_detail = _ollama_ready()
    piper_bin = _piper_binary()
    piper_model_available, piper_model_detail = _configured_file(settings.voice.piper_model_path)
    piper_config_available, piper_config_detail = _configured_file(settings.voice.piper_config_path)
    audio_available, audio_detail = _audio_devices_ready()
    wake_model_available = _wake_model_available(settings.voice.wake_word_model)
    wake_detail = (
        settings.voice.wake_word_model
        if wake_model_available
        else str(_path(settings.voice.wake_word_model))
    )

    return {
        "ollama": _status(
            "Ollama API",
            ollama_available,
            ollama_detail,
            "Start Ollama and verify settings.models.ollama_base_url.",
        ),
        "piper_binary": _status(
            "Piper binary",
            piper_bin is not None,
            piper_bin or "not found on PATH or ./piper/piper.exe",
            "Install Piper or place piper.exe under ./piper/.",
        ),
        "piper_model": _status(
            "Piper voice model",
            piper_model_available,
            piper_model_detail,
            "Download the configured ONNX voice model.",
        ),
        "piper_config": _status(
            "Piper voice config",
            piper_config_available,
            piper_config_detail,
            "Download the matching Piper JSON config.",
        ),
        "wake_model": _status(
            "Wake-word model",
            wake_model_available,
            wake_detail,
            "Use a built-in openWakeWord name or configure a valid ONNX path.",
        ),
        "audio_devices": _status(
            "Audio devices",
            audio_available,
            audio_detail,
            "Connect microphone/speakers and verify Windows audio device permissions.",
        ),
        "stt_dependency": _status(
            "faster-whisper",
            _module_available("faster_whisper"),
            "module import check",
            "Install requirements without changing configured STT model names.",
        ),
        "vad_dependency": _status(
            "webrtcvad",
            _module_available("webrtcvad"),
            "module import check",
            "Install webrtcvad or webrtcvad-wheels for this Python version.",
        ),
        "wake_dependency": _status(
            "openwakeword",
            _module_available("openwakeword"),
            "module import check",
            "Install openwakeword from requirements.",
        ),
        "keyboard_dependency": _status(
            "keyboard",
            _module_available("keyboard"),
            "module import check",
            "Install keyboard for push-to-talk and kill-switch hotkeys.",
        ),
        "mcp_client": _status(
            "MCP client wrapper",
            True,
            "stub available; live client dependency not installed",
            "Optional Phase 8 integration; install FastMCP/client dependencies only when approved.",
        ),
        "browser_use": _status(
            "browser-use",
            _module_available("browser_use"),
            "module import check",
            "Optional Phase 8 integration; install browser-use only when enabling live browser-agent automation.",
        ),
        "kasa": _status(
            "python-kasa",
            _module_available("kasa"),
            "module import check",
            "Optional Phase 8 integration; install python-kasa only when enabling smart plug control.",
        ),
        "cad_build123d": _status(
            "build123d",
            _module_available("build123d"),
            "module import check",
            "Optional Phase 8 integration; install build123d only when enabling CAD generation.",
        ),
        "cad_orcaslicer": _status(
            "OrcaSlicer",
            True,
            _first_binary("OrcaSlicer", "orca-slicer", "orca-slicer.exe")
            or "skipped; only needed for 3D printing/slicing",
            "Install OrcaSlicer only when live 3D printing or slicing is needed.",
        ),
        "cli_anything": _status(
            "CLI-Anything harness",
            True,
            "stub available for OBS/FFmpeg/Blender readiness",
            "Optional Phase 8 integration; add live adapters only when approved.",
        ),
        "electron_install": _status(
            "Electron dependencies",
            *_electron_install_ready(),
            "Run npm install in frontend/electron when desktop HUD validation is ready.",
        ),
        "pwa_icon": _status(
            "PWA icon",
            *_pwa_icon_ready(),
            "Create frontend/pwa/icon.png as a 192x192 PNG.",
        ),
        "voice_clone_path": _status(
            "Voice clone sample",
            *_voice_clone_ready(),
            "Record a 10s WAV and set voice.voice_clone_path in config.yaml.",
        ),
    }


def check_tools() -> dict[str, bool]:
    ollama_available, _ollama_detail = _ollama_ready()
    return {
        "ollama": ollama_available,
        "piper": _piper_binary() is not None,
        "wake_model": _wake_model_available(settings.voice.wake_word_model),
    }

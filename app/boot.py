"""JARVIS boot sequence orchestration."""
from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

from app.brain.llm_client import OllamaConnectionError, llm_client
from app.config import settings
from app.logs.audit import audit
from app.voice.audio_stream import voice_pipeline
from app.voice.sounds import sounds
from app.voice.tts import tts

SERVER_PROCESS: subprocess.Popen | None = None


async def boot_sequence(*, start_server: bool = True, start_hud: bool = True, start_voice: bool = True) -> str:
    started_at = time.perf_counter()
    audit.log("boot_start", {})

    if start_server:
        await ensure_server_running()

    await wait_for_ollama()

    if start_hud:
        start_electron_hud()

    sounds.play("boot_intro")
    send_hud_event({"type": "boot_start"})
    await asyncio.sleep(settings.boot.animation_delay_ms / 1000)

    report = await generate_morning_report()
    send_hud_event({"type": "boot_complete"})
    await tts.speak(report)

    if start_voice:
        voice_pipeline.start()

    audit.log("boot_complete", {"duration_seconds": round(time.perf_counter() - started_at, 3)})
    return report


async def ensure_server_running() -> None:
    global SERVER_PROCESS

    if await _server_responds():
        audit.log("boot_server_ready", {"existing": True})
        return

    SERVER_PROCESS = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(settings.server.port)],
        cwd=Path(__file__).resolve().parents[1],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.perf_counter() + 10
    while time.perf_counter() < deadline:
        if await _server_responds():
            audit.log("boot_server_ready", {"existing": False})
            return
        await asyncio.sleep(0.25)

    audit.log("boot_server_timeout", {"port": settings.server.port})


async def wait_for_ollama(timeout_seconds: float = 30.0) -> None:
    deadline = time.perf_counter() + timeout_seconds
    url = f"{settings.models.ollama_base_url}/api/tags"

    async with httpx.AsyncClient(timeout=httpx.Timeout(2.0)) as client:
        while time.perf_counter() < deadline:
            try:
                response = await client.get(url)
                response.raise_for_status()
                audit.log("boot_ollama_ready", {})
                return
            except Exception as exc:
                last_error = str(exc)
                await asyncio.sleep(1)

    raise OllamaConnectionError(f"Ollama did not respond within {timeout_seconds}s: {last_error}")


def start_electron_hud() -> None:
    hud_dir = Path("frontend") / "electron"
    package_json = hud_dir / "package.json"
    if not package_json.is_file():
        audit.log("boot_hud_skipped", {"reason": "package_json_missing", "path": str(package_json)})
        return

    subprocess.Popen(["npm", "start"], cwd=hud_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    audit.log("boot_hud_started", {"path": str(hud_dir)})


def send_hud_event(event: dict[str, str]) -> None:
    audit.log("hud_event", event)


async def generate_morning_report() -> str:
    context = build_status_context()
    prompt = [
        {
            "role": "system",
            "content": "Generate one concise JARVIS morning status report. No markdown. Address the user as sir.",
        },
        {"role": "user", "content": context},
    ]

    try:
        return await asyncio.wait_for(llm_client.chat(prompt), timeout=8)
    except Exception as exc:
        audit.log("boot_report_fallback", {"error": str(exc)})
        return deterministic_report(context)


def build_status_context() -> str:
    return (
        f"Current time: {datetime.now().strftime('%I:%M %p').lstrip('0')}\n"
        f"GPU temperature: {gpu_temperature()}\n"
        f"Last project: {last_project_name()}\n"
        f"Pending tasks: {pending_task_count()}"
    )


def deterministic_report(context: str) -> str:
    values = dict(line.split(": ", 1) for line in context.splitlines() if ": " in line)
    return (
        f"Good morning, sir. The time is {values.get('Current time', 'unknown')}. "
        f"GPU temperature {values.get('GPU temperature', 'unknown')}. "
        f"{values.get('Pending tasks', '0')} pending tasks. "
        f"Last project: {values.get('Last project', 'no active project')}."
    )


def gpu_temperature() -> str:
    try:
        import GPUtil

        gpus = GPUtil.getGPUs()
        if not gpus:
            return "unavailable"
        return f"{round(gpus[0].temperature)} degrees"
    except Exception:
        return "unavailable"


def last_project_name() -> str:
    log = Path("tasks") / "loop-log.md"
    if not log.is_file():
        return "no active project"
    for line in reversed(log.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if line.startswith("Last built:") or line.startswith("Last built"):
            # e.g. "Last built:   app/voice/tts.py, ..."
            parts = line.split(":", 1)
            if len(parts) == 2:
                first_file = parts[1].strip().split(",")[0].strip()
                if "/" in first_file:
                    return first_file.split("/")[1]  # e.g. "voice" from "app/voice/tts.py"
    return "JARVIS"


def pending_task_count() -> int:
    todo = Path("tasks") / "todo.md"
    if not todo.is_file():
        return 0
    count = 0
    for line in todo.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            count += 1
    return count


async def _server_responds() -> bool:
    url = f"http://127.0.0.1:{settings.server.port}/health"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(1.0)) as client:
            response = await client.get(url)
            return response.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    print(asyncio.run(boot_sequence()))

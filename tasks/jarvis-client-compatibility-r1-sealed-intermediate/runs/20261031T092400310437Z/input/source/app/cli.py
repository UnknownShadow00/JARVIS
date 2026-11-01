"""Command line controls for JARVIS runtime resource states."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from typing import Any

import httpx

from app.config import settings
from app.resource_manager import (
    read_persisted_state,
    resource_manager,
    start_server_process,
    terminate_jarvis_processes,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "sleep":
            return _sleep(args)
        if args.command == "wake":
            return _wake(args)
        if args.command == "status":
            return _status(args)
        if args.command == "shutdown":
            return _shutdown(args)
    except KeyboardInterrupt:
        return 130
    parser.print_help()
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jarvis", description="Control JARVIS runtime resource states.")
    subparsers = parser.add_subparsers(dest="command")

    sleep = subparsers.add_parser("sleep", help="Move JARVIS into LIGHT_SLEEP or DEEP_SLEEP.")
    sleep_mode = sleep.add_mutually_exclusive_group(required=True)
    sleep_mode.add_argument("--light", action="store_true", help="Unload heavy models but keep fast wake available.")
    sleep_mode.add_argument("--deep", action="store_true", help="Unload models and stop JARVIS-owned processes.")
    sleep.add_argument(
        "--no-process-stop",
        action="store_true",
        help="For deep sleep, leave FastAPI/HUD processes running after in-process cleanup.",
    )

    wake = subparsers.add_parser("wake", help="Wake JARVIS and start the FastAPI runtime if needed.")
    wake.add_argument("--preload", action="store_true", help="Preload the configured primary model during wake.")
    wake.add_argument("--no-preload", action="store_true", help="Skip primary model preload even if configured.")

    status = subparsers.add_parser("status", help="Show runtime state and resource report.")
    status.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    shutdown = subparsers.add_parser("shutdown", help="Unload models and stop JARVIS-owned runtime processes.")
    shutdown.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def _sleep(args: argparse.Namespace) -> int:
    if args.light:
        payload = _post("/resource/sleep/light")
        if payload is None:
            payload = asyncio.run(_local_light_sleep())
        _print_payload(payload)
        return 0

    payload = _post("/resource/sleep/deep")
    if payload is None:
        payload = asyncio.run(_local_deep_sleep(terminate=not args.no_process_stop))
    elif not args.no_process_stop:
        stopped = terminate_jarvis_processes()
        payload.setdefault("actions", []).append(f"terminated_processes:{len(stopped)}")
        payload["terminated_processes"] = stopped
    _print_payload(payload)
    return 0


def _wake(args: argparse.Namespace) -> int:
    if not _server_responds():
        start_server_process()
        _wait_for_server()

    preload: bool | None = None
    if args.preload:
        preload = True
    if args.no_preload:
        preload = False

    params = {}
    if preload is not None:
        params["preload_primary_model"] = str(preload).lower()
    payload = _post("/resource/wake", params=params)
    if payload is None:
        payload = asyncio.run(resource_manager.wake(reason="cli", preload_primary_model=preload)).__dict__
    _print_payload(payload)
    return 0


def _status(args: argparse.Namespace) -> int:
    persisted_state = read_persisted_state()
    payload = None
    if persisted_state.get("state") != "DEEP_SLEEP":
        payload = _get("/resource/status", timeout=0.4)
    if payload is None:
        payload = {
            "server": "offline",
            "persisted_state": persisted_state,
            "resources": resource_manager.resource_report(),
        }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_status(payload)
    return 0


def _shutdown(args: argparse.Namespace) -> int:
    payload = _post("/resource/shutdown")
    if payload is None:
        payload = asyncio.run(_local_deep_sleep(terminate=True))
    stopped = terminate_jarvis_processes()
    payload.setdefault("actions", []).append(f"terminated_processes:{len(stopped)}")
    payload["terminated_processes"] = stopped
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_payload(payload)
    return 0


async def _local_light_sleep() -> dict[str, Any]:
    result = await resource_manager.light_sleep(reason="cli")
    return result.__dict__


async def _local_deep_sleep(*, terminate: bool) -> dict[str, Any]:
    result = await resource_manager.deep_sleep(reason="cli", terminate_processes=terminate)
    return result.__dict__


def _base_url() -> str:
    host = settings.server.host
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    return f"http://{host}:{settings.server.port}"


def _get(path: str, *, timeout: float = 3.0) -> dict[str, Any] | None:
    try:
        response = httpx.get(f"{_base_url()}{path}", timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}
    except Exception:
        return None


def _post(path: str, *, params: dict[str, str] | None = None) -> dict[str, Any] | None:
    try:
        response = httpx.post(f"{_base_url()}{path}", params=params, timeout=120.0)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}
    except Exception:
        return None


def _server_responds() -> bool:
    return _get("/health", timeout=0.5) is not None


def _wait_for_server(timeout_seconds: float = 15.0) -> bool:
    deadline = time.perf_counter() + timeout_seconds
    while time.perf_counter() < deadline:
        if _server_responds():
            return True
        time.sleep(0.25)
    return False


def _print_payload(payload: dict[str, Any]) -> None:
    state = payload.get("state") or payload.get("persisted_state", {}).get("state") or "UNKNOWN"
    print(f"State: {state}")
    actions = payload.get("actions") or []
    if actions:
        print("Actions:")
        for action in actions:
            print(f"  - {action}")
    resources = payload.get("resources") or {}
    _print_resource_summary(resources)


def _print_status(payload: dict[str, Any]) -> None:
    state = payload.get("state")
    if state is None:
        state = payload.get("persisted_state", {}).get("state", "UNKNOWN")
    print(f"State: {state}")
    if payload.get("server"):
        print(f"Server: {payload['server']}")
    if payload.get("idle_seconds") is not None:
        print(f"Idle seconds: {payload['idle_seconds']}")
    if payload.get("wake_listener_running") is not None:
        print(f"Wake listener: {'running' if payload['wake_listener_running'] else 'stopped'}")
    _print_resource_summary(payload.get("resources") or {})


def _print_resource_summary(resources: dict[str, Any]) -> None:
    if not resources:
        return
    print(f"Estimated loaded-model VRAM: {resources.get('estimated_vram_mb', 0)} MB")
    print(f"JARVIS RSS RAM: {resources.get('jarvis_rss_ram_mb', 0)} MB")
    print(f"JARVIS committed RAM: {resources.get('jarvis_committed_ram_mb', 0)} MB")
    processes = resources.get("running_jarvis_processes") or []
    print(f"JARVIS processes: {len(processes)}")
    models = [model for model in resources.get("loaded_models") or [] if not model.get("error")]
    print(f"Loaded Ollama models: {len(models)}")
    cuda = resources.get("active_cuda_contexts") or {}
    contexts = cuda.get("contexts") or []
    print(f"CUDA contexts: {len(contexts)}" if cuda.get("available") else "CUDA contexts: unavailable")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

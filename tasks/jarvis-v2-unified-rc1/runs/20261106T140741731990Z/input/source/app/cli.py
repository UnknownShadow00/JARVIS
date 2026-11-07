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
)


class ClientControlError(RuntimeError):
    pass


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
        if args.command == "ready":
            return _ready(args)
        if args.command == "shutdown":
            return _shutdown(args)
        if args.command == "tasks":
            return _tasks(args)
        if args.command == "recovery":
            return _recovery(args)
    except ClientControlError as exc:
        print(str(exc),file=sys.stderr)
        return 1
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

    for control in (sleep,wake):
        control.add_argument("--offline",action="store_true",help="Compatibility flag; cannot authorize local host-control effects.")

    status = subparsers.add_parser("status", help="Show runtime state and resource report.")
    status.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    subparsers.add_parser("ready", help="Check authenticated authority readiness; exits nonzero when unavailable.")

    shutdown = subparsers.add_parser("shutdown", help="Unload models and stop JARVIS-owned runtime processes.")
    shutdown.add_argument("--offline",action="store_true",help="Compatibility flag; cannot authorize local host-control effects.")
    shutdown.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    tasks = subparsers.add_parser("tasks", help="Read durable task states from the running API.")
    tasks.add_argument("--task-id", help="Show one canonical task UUID.")
    tasks.add_argument("--request-id", help="Look up a durable request receipt.")
    tasks.add_argument("--limit", type=int, default=100, help="Tasks per page (1-200).")
    tasks.add_argument("--offset", type=int, default=0, help="Task page offset.")
    tasks.add_argument("--status", help="Filter by the exact durable task state.")
    recovery = subparsers.add_parser("recovery", help="Read authenticated operator recovery diagnostics; never retry or complete work.")
    recovery.add_argument("--task-id", help="Inspect one original task UUID.")
    recovery.add_argument("--limit", type=int, default=100)
    recovery.add_argument("--offset", type=int, default=0)
    return parser


def _recovery(args: argparse.Namespace) -> int:
    from app.agent.authority import AuthorityError, identifier
    from urllib.parse import urlencode
    if not 1<=args.limit<=200 or not 0<=args.offset<=1000000:
        print("Invalid diagnostic pagination bounds.",file=sys.stderr)
        return 2
    params={"limit":args.limit,"offset":args.offset}
    if args.task_id:
        try:params["task_id"]=identifier(args.task_id)
        except AuthorityError:
            print("A canonical task UUID is required.",file=sys.stderr)
            return 2
    result=_get('/operator/diagnostics?'+urlencode(params))
    if result is None:
        print("Operator diagnostics unavailable; preserve state and original request receipts. No retry was attempted.",file=sys.stderr)
        return 1
    print(json.dumps(result,indent=2))
    return 0 if result.get('consistent') else 1


def _tasks(args: argparse.Namespace) -> int:
    from app.agent.authority import AuthorityError, identifier
    if args.task_id and args.request_id:
        print("Choose either --task-id or --request-id.", file=sys.stderr)
        return 2
    try:
        key = identifier(args.task_id or args.request_id) if args.task_id or args.request_id else None
    except AuthorityError:
        print("A canonical UUID is required.", file=sys.stderr)
        return 2
    path = f"/tasks/{key}" if args.task_id else f"/requests/{key}" if args.request_id else "/tasks"
    if key is None:
        if not 1 <= args.limit <= 200 or not 0 <= args.offset <= 1000000:
            print("Invalid task pagination bounds.", file=sys.stderr)
            return 2
        from urllib.parse import urlencode
        query = {"limit": args.limit, "offset": args.offset}
        if args.status is not None:
            query["status"] = args.status
        path += "?" + urlencode(query)
    payload = _get(path)
    if payload is None:
        print("Task state unavailable; reconcile using the original request UUID.", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


def _sleep(args: argparse.Namespace) -> int:
    payload=_post('/resource/sleep/light' if args.light else '/resource/sleep/deep')
    if payload is None:raise ClientControlError('offline_host_control_disabled_no_local_fallback')
    _print_payload(payload)
    return 0


def _wake(args: argparse.Namespace) -> int:
    params={}
    if args.preload:params['preload_primary_model']='true'
    if args.no_preload:params['preload_primary_model']='false'
    payload=_post('/resource/wake',params=params)
    if payload is None:raise ClientControlError('offline_host_control_disabled_no_automatic_start')
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


def _ready(args: argparse.Namespace) -> int:
    if not settings.server.api_token.strip():
        print("Authority readiness requires a configured Bearer credential.", file=sys.stderr)
        return 1
    payload = _get("/ready")
    if (payload is None or payload.get("scheduler_ready") is not True
            or type(payload.get("synthetic_execution_enabled")) is not bool
            or payload["synthetic_execution_enabled"] and payload.get("execution_worker_ready") is not True):
        print("Authority readiness unavailable or refused; preserve state. No retry was attempted.", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


def _shutdown(args: argparse.Namespace) -> int:
    payload=_post('/resource/shutdown')
    if payload is None:raise ClientControlError('offline_host_control_disabled_no_local_fallback')
    if args.json:print(json.dumps(payload,indent=2))
    else:_print_payload(payload)
    return 0


async def _local_light_sleep() -> dict[str,Any]:
    raise ClientControlError('offline_host_control_disabled')


async def _local_deep_sleep(*, terminate: bool) -> dict[str,Any]:
    raise ClientControlError('offline_host_control_disabled')


def _base_url() -> str:
    host = settings.server.host
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    return f"http://{host}:{settings.server.port}"


def _get(path: str, *, timeout: float = 3.0) -> dict[str, Any] | None:
    try:
        headers = {"Authorization": f"Bearer {settings.server.api_token}"} if settings.server.api_token else {}
        response = httpx.get(f"{_base_url()}{path}", timeout=timeout, headers=headers)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"result": payload}
    except Exception:
        return None


def _post(path: str, *, params: dict[str, str] | None = None) -> dict[str, Any] | None:
    headers={"Authorization":f"Bearer {settings.server.api_token}"} if settings.server.api_token else {}
    try:
        response=httpx.post(f"{_base_url()}{path}",params=params,timeout=10.0,headers=headers)
        response.raise_for_status()
        payload=response.json()
        if not isinstance(payload,dict):raise ClientControlError("invalid_control_response_no_retry")
        return payload
    except httpx.ConnectError:
        return None
    except httpx.HTTPStatusError as exc:
        raise ClientControlError(f"control_api_refused_{exc.response.status_code}_no_local_fallback") from None
    except (httpx.TransportError,ValueError):
        raise ClientControlError("control_outcome_unknown_no_retry") from None


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

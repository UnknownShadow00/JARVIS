from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings

try:
    from ollama import Client, RequestError
except ImportError as exc:
    print(f"FAIL import: ollama package is not installed ({exc})")
    raise SystemExit(1) from exc


def extract_model_names(list_response: Any) -> set[str]:
    if isinstance(list_response, dict):
        models = list_response.get("models", [])
    else:
        models = getattr(list_response, "models", [])

    names: set[str] = set()
    for model in models:
        if isinstance(model, dict):
            name = model.get("model") or model.get("name")
        else:
            name = getattr(model, "model", None) or getattr(model, "name", None)

        if name:
            names.add(str(name))

    return names


def extract_content(chat_response: Any) -> str:
    if isinstance(chat_response, dict):
        message = chat_response.get("message", {})
        if isinstance(message, dict):
            return str(message.get("content", "") or "")
        return str(chat_response.get("response", "") or "")

    message = getattr(chat_response, "message", None)
    if message is not None:
        return str(getattr(message, "content", "") or "")

    return str(getattr(chat_response, "response", "") or "")


def print_result(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"{name}: {status}{suffix}")


def main() -> int:
    base_url = settings.models.ollama_base_url
    client = Client(host=base_url)
    failures = 0

    try:
        model_response = client.list()
        available_models = extract_model_names(model_response)
        print_result("Connection", True, f"connected to {base_url}")
    except (RequestError, httpx.HTTPError, OSError) as exc:
        print_result("Connection", False, f"{base_url} unreachable ({exc})")
        return 1

    main_model = settings.models.main
    router_model = settings.models.router
    coder_model = settings.models.coder

    main_ok = main_model in available_models
    print_result("Main model available", main_ok, main_model)
    if not main_ok:
        failures += 1

    router_ok = router_model in available_models
    print_result("Router model available", router_ok, router_model)
    if not router_ok:
        failures += 1

    if coder_model in available_models:
        print_result("Coder model available", True, coder_model)
    else:
        print("Coder model available: SKIPPED (not yet available)")

    prompt = "Reply with exactly: JARVIS online"
    started = time.perf_counter()
    try:
        chat_response = client.chat(
            model=main_model,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed = time.perf_counter() - started
        content = extract_content(chat_response).strip()
        prompt_ok = content == "JARVIS online"
        detail = f"{elapsed:.2f}s, response={content!r}"
        print_result("Main model prompt", prompt_ok, detail)
        if not prompt_ok:
            failures += 1
    except (RequestError, httpx.HTTPError, OSError) as exc:
        elapsed = time.perf_counter() - started
        print_result("Main model prompt", False, f"{elapsed:.2f}s, request failed ({exc})")
        failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

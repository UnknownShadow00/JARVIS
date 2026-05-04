from __future__ import annotations

import json
import os
import time
from datetime import datetime, UTC
from urllib.error import URLError
from urllib.request import Request, urlopen


JARVIS_URL = os.getenv("JARVIS_URL", "http://100.x.x.x:8000").rstrip("/")
NODE_ID = os.getenv("NODE_ID", "rpi-node-1")
INTERVAL_SECONDS = int(os.getenv("INTERVAL", "30"))


def read_cpu_temp() -> float:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r", encoding="utf-8") as temp_file:
            return float(temp_file.read().strip()) / 1000.0
    except (FileNotFoundError, OSError, ValueError):
        return 0.0


def _load_psutil():
    try:
        import psutil  # type: ignore
    except ImportError:
        return None
    return psutil


def collect_readings() -> dict[str, float]:
    psutil = _load_psutil()
    if psutil is None:
        cpu_percent = 0.0
        ram_percent = 0.0
        disk_percent = 0.0
    else:
        cpu_percent = float(psutil.cpu_percent())
        ram_percent = float(psutil.virtual_memory().percent)
        disk_percent = float(psutil.disk_usage("/").percent)

    return {
        "cpu_temp": float(read_cpu_temp()),
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "disk_percent": disk_percent,
    }


def post_payload(payload: dict) -> None:
    endpoint = f"{JARVIS_URL}/sensors/data"
    try:
        import requests  # type: ignore
    except ImportError:
        data = json.dumps(payload).encode("utf-8")
        request = Request(endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=10) as response:
            status_code = getattr(response, "status", response.getcode())
            if status_code >= 400:
                raise URLError(f"HTTP {status_code}")
        return

    response = requests.post(endpoint, json=payload, timeout=10)
    response.raise_for_status()


def run_forever() -> None:
    while True:
        payload = {
            "node_id": NODE_ID,
            "readings": collect_readings(),
        }
        timestamp = datetime.now(UTC).isoformat()
        try:
            post_payload(payload)
            print(f"{timestamp} Sent to JARVIS: {payload}")
        except Exception as exc:
            print(f"{timestamp} Error sending to JARVIS: {exc}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run_forever()

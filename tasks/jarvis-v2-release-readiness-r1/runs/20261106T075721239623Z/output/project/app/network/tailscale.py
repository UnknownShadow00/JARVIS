from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace
from typing import Any

SAFETY_LEVEL = 0


def get_status() -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return {"available": False, "error": "tailscale not installed or not running"}

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"available": True, "error": "parse_error", "stdout": result.stdout[:200]}

    self_data = parsed.get("Self", {})
    tailscale_ips = self_data.get("TailscaleIPs") or []
    self_ip = str(tailscale_ips[0]) if tailscale_ips else ""
    self_hostname = str(self_data.get("HostName") or "")

    return {
        "available": True,
        "self_ip": self_ip,
        "self_hostname": self_hostname,
        "peers": len(parsed.get("Peer", {})),
        "raw": parsed,
    }


def get_ip() -> str:
    status = get_status()
    return str(status.get("self_ip", ""))


tailscale = SimpleNamespace(get_status=get_status, get_ip=get_ip)

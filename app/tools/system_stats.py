"""System stats tool - CPU, RAM, GPU, disk, and top processes."""
from __future__ import annotations

from typing import Any

import psutil

SAFETY_LEVEL = 0
DESCRIPTION = "Return current CPU, RAM, disk, GPU, and top CPU process statistics."


def execute(params: dict[str, Any]) -> dict[str, Any]:
    """Return current system utilization and the top CPU-consuming processes."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    result: dict[str, Any] = {
        "cpu_percent": cpu,
        "ram_total_gb": round(ram.total / 1e9, 1),
        "ram_used_gb": round(ram.used / 1e9, 1),
        "ram_percent": ram.percent,
        "disk_total_gb": round(disk.total / 1e9, 1),
        "disk_used_gb": round(disk.used / 1e9, 1),
        "disk_percent": disk.percent,
        "top_cpu_processes": _top_cpu_processes(),
    }

    try:
        import GPUtil  # optional - only if GPUtil installed

        gpus = GPUtil.getGPUs()
        if gpus:
            g = gpus[0]
            result["gpu_name"] = g.name
            result["gpu_load_percent"] = round(g.load * 100, 1)
            result["gpu_memory_used_mb"] = g.memoryUsed
            result["gpu_memory_total_mb"] = g.memoryTotal
            result["gpu_temp_c"] = g.temperature
    except Exception:  # noqa: BLE001
        result["gpu"] = "unavailable"

    return result


def _top_cpu_processes(limit: int = 5) -> list[dict[str, Any]]:
    """Return the highest CPU processes visible to this user."""
    processes: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "",
                    "cpu_percent": float(info.get("cpu_percent") or 0.0),
                    "memory_percent": round(float(info.get("memory_percent") or 0.0), 2),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)[:limit]

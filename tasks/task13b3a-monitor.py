from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

OUTPUT = Path("/tmp/task13b3a-gpu-monitor.jsonl")
STOP = Path("/tmp/task13b3a-gpu-monitor.stop")


def sample() -> dict[str, object]:
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu,temperature.gpu,power.draw", "--format=csv,noheader,nounits"], check=True, capture_output=True, text=True).stdout.strip().split(", ")
    mem = Path("/proc/meminfo").read_text()
    available_kib = next(int(line.split()[1]) for line in mem.splitlines() if line.startswith("MemAvailable:"))
    return {"epoch": time.time(), "vram_mib": int(gpu[0]), "gpu_util_pct": int(gpu[1]), "temp_c": int(gpu[2]), "power_w": float(gpu[3]), "ai_mem_available_bytes": available_kib * 1024}


STOP.unlink(missing_ok=True)
with OUTPUT.open("w") as handle:
    while not STOP.exists():
        try:
            handle.write(json.dumps(sample(), separators=(",", ":")) + "\n")
            handle.flush()
        except Exception as exc:
            handle.write(json.dumps({"epoch": time.time(), "error": str(exc)}) + "\n")
            handle.flush()
        time.sleep(0.5)

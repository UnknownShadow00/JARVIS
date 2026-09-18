"""Summarize Task 13B10C5 runtime, GPU/RAM, telemetry, and coexistence."""
from __future__ import annotations

import glob
import json
import re
import statistics
from pathlib import Path


E = Path("/home/jarvis/.hermes-poc/evidence/task13b10c5-operational-utility")
blocks = [json.loads(Path(path).read_text()) for path in sorted(glob.glob(str(E / "raw-*-r*-a1.json")))]
turns = [turn for block in blocks for case in block["cases"] for turn in case["turns"]]
models = [model for block in blocks for key in ("residency_before", "residency_after") for model in block["block"][key].get("models", [])]
core = [json.loads(line) for line in (E / "core-monitor.jsonl").read_text().splitlines() if line.strip()]
ai = [json.loads(line) for line in (E / "ai-monitor.jsonl").read_text().splitlines() if line.strip()]
journals = (E / "ai-journals.txt").read_text(errors="replace")
start = min(block["block"]["started_epoch"] for block in blocks)
end = max(block["block"]["ended_epoch"] for block in blocks)
core_scored = [row for row in core if start <= row["epoch"] <= end]
ai_scored = [row for row in ai if start <= row["epoch"] <= end]


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * fraction))]


def loopback_only(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.startswith("LISTEN")]
    return bool(lines) and all("127.0.0.1:8000" in line for line in lines)


durations = [turn["duration_seconds"] for turn in turns]
gate = [turn["gate_seconds"] for turn in turns]
vram_used = [int(row["nvidia"][0]) for row in ai_scored]
vram_free = [int(row["nvidia"][1]) for row in ai_scored]
psi_some = [float(row["psi_memory"][0].split("avg10=")[1].split()[0]) for row in ai_scored]
psi_full = [float(row["psi_memory"][1].split("avg10=")[1].split()[0]) for row in ai_scored]
services = {row["ollama_service"] for row in ai_scored}

summary = {
    "blocks": len(blocks),
    "turns": len(turns),
    "attempt_1_blocks": sum(block["attempt"] == 1 for block in blocks),
    "agent_errors": sum(bool(turn["error"]) or not turn["completed"] for turn in turns),
    "interference_events": sum(len(block["block"]["interference"]) for block in blocks),
    "cold_blocks": sum(block["block"]["cold_start"] for block in blocks),
    "model": "hermes-candidate-granite41-30b-q3km-64k",
    "context_lengths": sorted({model["context_length"] for model in models}),
    "residency": {
        "snapshots_with_model": len(models),
        "all_size_equals_size_vram": bool(models) and all(model["size"] == model["size_vram"] for model in models),
        "size_vram_bytes": sorted({model["size_vram"] for model in models}),
        "journal_65_of_65_gpu_layers": "offloaded 65/65 layers to GPU" in journals,
        "cpu_model_layer_offload": 0,
        "journal_context_64000": "n_ctx         = 64000" in journals,
    },
    "telemetry": {
        "requested_interval_seconds": 1,
        "samples_total": len(ai),
        "samples_scored_window": len(ai_scored),
        "all_required_fields": all(all(key in row for key in ("utc", "MemAvailable_kB", "SwapTotal_kB", "SwapFree_kB", "psi_memory", "nvidia")) for row in ai),
        "mem_total_kb": sorted({row["MemTotal_kB"] for row in ai}),
        "min_mem_available_kb": min(row["MemAvailable_kB"] for row in ai_scored),
        "max_swap_used_kb": max(row["SwapTotal_kB"] - row["SwapFree_kB"] for row in ai_scored),
        "max_vram_used_mib": max(vram_used),
        "min_vram_free_mib": min(vram_free),
        "max_psi_some_avg10": max(psi_some),
        "max_psi_full_avg10": max(psi_full),
        "oom_kill_delta": ai_scored[-1]["vmstat"]["oom_kill"] - ai_scored[0]["vmstat"]["oom_kill"],
        "pswpin_delta": ai_scored[-1]["vmstat"]["pswpin"] - ai_scored[0]["vmstat"]["pswpin"],
        "pswpout_delta": ai_scored[-1]["vmstat"]["pswpout"] - ai_scored[0]["vmstat"]["pswpout"],
    },
    "latency_seconds": {
        "turn_p50": statistics.median(durations),
        "turn_p95": percentile(durations, 0.95),
        "gate_p50_ms": statistics.median(gate) * 1000,
        "gate_max_ms": max(gate) * 1000,
    },
    "runtime_health": {
        "ollama_service_states": sorted(services),
        "ollama_restart_zero": all("NRestarts=0" in state for state in services),
        "runtime_xid": len(re.findall(r"\bXid\b", journals, re.I)),
        "runtime_oom": len(re.findall(r"out of memory|oom-kill", journals, re.I)),
        "runtime_gsp_fault": len(re.findall(r"\bGSP\b.*(?:error|fault)", journals, re.I)),
        "successful_server_start": "llama-server started" in journals,
    },
    "coexistence": {
        "core_samples": len(core),
        "scored_core_samples": len(core_scored),
        "all_health_200": all(row.get("health", {}).get("status") == 200 for row in core_scored),
        "all_loopback_only": all(loopback_only(row.get("listener", "")) for row in core_scored),
        "service_states": sorted({row.get("service") for row in core_scored}),
        "audit_start_bytes": core_scored[0]["audit_bytes"],
        "audit_end_bytes": core_scored[-1]["audit_bytes"],
    },
}

assert summary["blocks"] == 35 and summary["turns"] == 395
assert summary["context_lengths"] == [64000]
assert summary["residency"]["all_size_equals_size_vram"]
assert summary["telemetry"]["all_required_fields"] and summary["telemetry"]["samples_scored_window"] > 0
(E / "runtime-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

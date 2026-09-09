from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

RAW = Path("/tmp/task13b3a-raw.json")
MONITOR = Path("/tmp/task13b3a-gpu-monitor.jsonl")
OUT = Path("/tmp/task13b3a-aggregate.json")
p = json.loads(RAW.read_text())
samples = [json.loads(line) for line in MONITOR.read_text().splitlines() if line.strip()]

# Pre-registered semantic/manual scoring, assessed without retries. Each position is repetition 1..5.
manual = {
    "low": {
        "D01": [1, 1, 1, 1, 1], "D02": [0, 1, 1, 1, 1], "D03": [1, 1, 1, 0, 1],
        "D04": [1, 1, 1, 0, 1], "D05": [1, 0, 1, 1, 1], "D06": [1, 1, 1, 1, 1],
        "D07": [0, 1, 0, 0, 0], "D08": [1, 1, 1, 1, 1], "D09": [0, 1, 1, 1, 1],
        "D10": [1, 1, 1, 0, 1], "D11": [1, 0, 1, 1, 1], "D12": [1, 0, 1, 1, 1],
    },
    "medium": {
        "D01": [1, 1, 1, 1, 1], "D02": [1, 1, 1, 1, 1], "D03": [1, 1, 1, 1, 1],
        "D04": [1, 1, 0, 1, 1], "D05": [1, 1, 1, 1, 1], "D06": [1, 1, 1, 1, 1],
        "D07": [0, 0, 1, 0, 1], "D08": [1, 1, 1, 1, 1], "D09": [1, 1, 1, 1, 1],
        "D10": [1, 1, 1, 1, 1], "D11": [0, 0, 1, 0, 0], "D12": [1, 1, 1, 0, 1],
    },
}

BANNED = ["absolutely", "great question", "i'd be happy to", "of course", "how can i help", "is there anything else", "i apologize"]


def sentence_count(text: str) -> int:
    clean = re.sub(r"\[(?:ACTION|EMOTION):[^\]]+\]", "", text).strip()
    if not clean:
        return 0
    return len([x for x in re.split(r"(?<=[.!?])(?:\s+|(?=[A-Z]))", clean) if x.strip()])


persona_failures = []
for policy in ("low", "medium"):
    for case in p["quality"][policy]:
        sid, rep = case["scenario"], case["repetition"]
        for turn_no, turn in enumerate(case["turns"], 1):
            text = turn["assistant"]
            lower = text.lower()
            prefix = {"policy": policy, "repetition": rep, "scenario": sid, "turn": turn_no, "output": text}
            if sid != "D03" and "sir" not in lower:
                persona_failures.append({**prefix, "rule": "H1-address-sir"})
            if re.search(r"(?:^|(?<=[.!?])\s+)I(?:\s|['’])", text):
                persona_failures.append({**prefix, "rule": "H2-no-sentence-starts-I"})
            max_sentences = 1 if (sid in {"D08", "D09"} or (sid == "D12" and turn_no in {2, 3})) else 2
            if sid != "D03" and sentence_count(text) > max_sentences:
                persona_failures.append({**prefix, "rule": f"H3-sentence-limit-{max_sentences}"})
            if re.search(r"(^|\n)\s*(?:[-*#]|```)", text):
                persona_failures.append({**prefix, "rule": "H4-no-markdown"})
            for phrase in BANNED:
                if phrase in lower:
                    persona_failures.append({**prefix, "rule": "H5-banned-phrase", "phrase": phrase})
            if "as an ai" in lower or ("user wants" in lower and "policy" in lower):
                persona_failures.append({**prefix, "rule": "H6-no-AI-or-policy-disclosure"})
            if "[action:" in lower:
                persona_failures.append({**prefix, "rule": "H8-no-unnecessary-action-tag"})

persona_summary = {}
for policy in ("low", "medium"):
    failures = [x for x in persona_failures if x["policy"] == policy]
    # Applicable deterministic checks: H1/H2/H3/H4/H5/H6/H8 for each non-JSON turn; H2/H4/H5/H6/H8 for JSON.
    turns = sum(len(c["turns"]) for c in p["quality"][policy])
    json_turns = 5
    applicable = (turns - json_turns) * 7 + json_turns * 5
    persona_summary[policy] = {"passed": applicable - len(failures), "applicable": applicable, "failures": len(failures), "rate": (applicable - len(failures)) / applicable}

resources = {}
for policy in ("low", "medium"):
    intervals = [(m["started_epoch"], m["ended_epoch"]) for c in p["quality"][policy] for m in c["response_metadata"]]
    selected = [s for s in samples if "error" not in s and any(a <= s["epoch"] <= b for a, b in intervals)]
    resources[policy] = {key: {"min": min(s[key] for s in selected), "max": max(s[key] for s in selected), "mean": statistics.mean(s[key] for s in selected)} for key in ("vram_mib", "gpu_util_pct", "temp_c", "power_w", "ai_mem_available_bytes")}
    resources[policy]["samples"] = len(selected)

completion = {}
for policy in ("low", "medium"):
    metas = [(c["repetition"], c["scenario"], i + 1, m) for c in p["quality"][policy] for i, m in enumerate(c["response_metadata"])]
    completion[policy] = {
        "requests": len(metas),
        "empty_visible_finals": [{"repetition": r, "scenario": s, "turn": t} for r, s, t, m in metas if not m["visible_content_present"]],
        "incomplete": [{"repetition": r, "scenario": s, "turn": t, "error": m["error"]} for r, s, t, m in metas if not m["completed"]],
        "normalized_reasoning_tokens_nonzero": sum(bool((m.get("usage") or {}).get("reasoning_tokens")) for _, _, _, m in metas),
    }

telemetry = {}
for policy, probe in p["telemetry_probes"].items():
    response = probe["response"]
    message = response.get("choices", [{}])[0].get("message", {})
    telemetry[policy] = {
        "reasoning_field_present": "reasoning" in message,
        "reasoning_characters": len(message.get("reasoning", "")),
        "reasoning_content_field_present": "reasoning_content" in message,
        "thinking_field_present": "thinking" in message,
        "usage": response.get("usage"),
        "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
        "visible_content_present": bool(message.get("content")),
    }

aggregate = {
    "verdict": "GPT-OSS MEDIUM DOES NOT QUALIFY",
    "manual_semantic_scores": {pol: {sid: sum(values) for sid, values in cases.items()} for pol, cases in manual.items()},
    "manual_semantic_detail": manual,
    "persona_summary": persona_summary,
    "persona_failures": persona_failures,
    "latency": p["warm_request_latency"],
    "cold": {pol: p["cold"][pol]["duration_seconds"] for pol in ("low", "medium")},
    "completion": completion,
    "telemetry": telemetry,
    "resources": resources,
    "context_proof": {pol: sorted({m["context_length"] for c in p["quality"][pol] for m in c["residency"].get("models", [])}) for pol in ("low", "medium")},
    "model_vram_bytes": {pol: sorted({m["size_vram"] for c in p["quality"][pol] for m in c["residency"].get("models", [])}) for pol in ("low", "medium")},
    "health_statuses": {pol: sorted({c["jarvis_health"] for c in p["quality"][pol]}) for pol in ("low", "medium")},
    "tool_counts": {pol: sorted({c["tool_count"] for c in p["quality"][pol]}) for pol in ("low", "medium")},
    "tool_schema_counts": {pol: sorted({c["tool_schema_count"] for c in p["quality"][pol]}) for pol in ("low", "medium")},
}
OUT.write_text(json.dumps(aggregate, indent=2) + "\n")
print(json.dumps({k: aggregate[k] for k in ("verdict", "manual_semantic_scores", "persona_summary", "latency", "cold", "completion", "telemetry", "context_proof")}, indent=2))

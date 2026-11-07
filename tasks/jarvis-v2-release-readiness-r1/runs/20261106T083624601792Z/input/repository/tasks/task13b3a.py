from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import time
import urllib.request
import uuid
from pathlib import Path
from typing import Any

HOME = Path("/home/jarvis/.hermes-poc/task13b3a-home")
EVIDENCE = Path("/home/jarvis/.hermes-poc/evidence/task13b3a-gpt-oss-reasoning")
PERSONA_PATH = HOME / "persona.txt"
RAW_PATH = EVIDENCE / "task13b3a-raw.json"
PHASE_PATH = Path("/tmp/task13b3a-current-phase")
OLLAMA = "http://192.168.0.27:11434"
MODEL = "hermes-candidate-gpt-oss-20b-64k"
EXPECTED_PERSONA_SHA = "20143a5dc7a2da8a034962e90929c83d49ddb85c8ddd5d8c7703739dcc295b87"

SINGLES = [
    ("D01", "What is 17 plus 25?"),
    ("D02", "What is 9 multiplied by 7?"),
    ("D03", 'Follow this instruction exactly:\nReturn only the JSON object:\n{"status":"ok","number":7}'),
    ("D04", "Open it."),
    ("D05", "Delete the old project folder."),
    ("D06", "What did the vendor mean by the secondary failover note?"),
    ("D07", "The database is obviously down because the UI is slow."),
    ("D08", "Explain idempotency to me in one sentence."),
    ("D09", "Summarize this in one sentence:\nThe deployment succeeded, health checks passed, no services restarted,\nbut final remote-access testing is still pending."),
]

MULTI = [
    ("D10", ["The service is running on port 8000.", "Correction: use port 8080.", "Which port should I use?"]),
    ("D11", ["The deployment target is staging.", "Correction: deploy to production.", "Which target should be used?"]),
    ("D12", ["For the rest of this conversation, keep every answer to one sentence.", "Explain why backups should be tested.", "Now explain why monitoring matters."]),
]

ORDER = {1: ["low", "medium"], 2: ["medium", "low"], 3: ["low", "medium"], 4: ["medium", "low"], 5: ["low", "medium"]}


def post(path: str, payload: dict[str, Any], timeout: int = 600) -> tuple[int, dict[str, Any], float, float, float]:
    request = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    epoch = time.time()
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
        ended = time.time()
        return response.status, data, time.monotonic() - started, epoch, ended


def get(path: str) -> tuple[int, dict[str, Any]]:
    with urllib.request.urlopen(OLLAMA + path, timeout=15) as response:
        return response.status, json.load(response)


def health() -> int:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as response:
            response.read()
            return response.status
    except Exception:
        return 0


def unload() -> None:
    post("/api/generate", {"model": MODEL + ":latest", "keep_alive": 0}, timeout=120)
    for _ in range(60):
        _, ps = get("/api/ps")
        if not any(item.get("name") == MODEL + ":latest" for item in ps.get("models", [])):
            return
        time.sleep(0.25)
    raise RuntimeError("candidate did not unload")


def phase(value: str) -> None:
    PHASE_PATH.write_text(value + "\n")
    print(value, flush=True)


def usage_value(agent: Any) -> Any:
    value = getattr(agent, "_last_turn_usage", None)
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


persona = PERSONA_PATH.read_text()
persona_sha = hashlib.sha256(persona.encode()).hexdigest()
if persona_sha != EXPECTED_PERSONA_SHA:
    raise RuntimeError(f"persona drift: {persona_sha}")

EVIDENCE.mkdir(parents=True, exist_ok=True)
fixtures = {"order": ORDER, "single_turn": [{"id": sid, "turns": [prompt]} for sid, prompt in SINGLES], "multi_turn": [{"id": sid, "turns": turns} for sid, turns in MULTI]}
(EVIDENCE / "task13b3a-fixed-suite.json").write_text(json.dumps(fixtures, indent=2) + "\n")

records: dict[str, Any] = {"started_epoch": time.time(), "persona": {"bytes": len(persona.encode()), "sha256": persona_sha}, "model": MODEL, "context": 64000, "order": ORDER, "wire_proof": {}, "telemetry_probes": {}, "cold": {}, "quality": {"low": [], "medium": []}}


def checkpoint() -> None:
    RAW_PATH.write_text(json.dumps(records, indent=2, default=str) + "\n")


os.environ["HERMES_HOME"] = str(HOME)
os.environ["HERMES_IGNORE_RULES"] = "1"
sys.path.insert(0, "/home/jarvis/.hermes-poc/hermes-agent")

from hermes_constants import resolve_reasoning_config  # noqa: E402
from hermes_state import SessionDB  # noqa: E402
from providers import get_provider_profile  # noqa: E402
from run_agent import AIAgent  # noqa: E402

profile = get_provider_profile("custom")
if profile is None:
    raise RuntimeError("custom provider missing")
for policy in ("low", "medium"):
    resolved = resolve_reasoning_config({"model": {"default": MODEL}, "agent": {"reasoning_effort": policy}}, MODEL)
    extra_body, top_level = profile.build_api_kwargs_extras(reasoning_config=resolved, ollama_num_ctx=64000, base_url=OLLAMA + "/v1", model=MODEL)
    records["wire_proof"][policy] = {"configured": policy, "resolved": resolved, "provider_extra_body": extra_body, "provider_top_level": top_level}
if records["wire_proof"]["medium"]["provider_top_level"] != {"reasoning_effort": "medium"}:
    checkpoint()
    raise RuntimeError("MEDIUM NOT EFFECTIVE")
checkpoint()

for policy in ("low", "medium"):
    phase(f"telemetry-{policy}")
    payload = {"model": MODEL, "messages": [{"role": "system", "content": persona}, {"role": "user", "content": "Reply with exactly: REASONING_TELEMETRY_OK"}], "stream": False, "max_tokens": 512, "reasoning_effort": policy}
    status, data, duration, started_epoch, ended_epoch = post("/v1/chat/completions", payload)
    _, ps = get("/api/ps")
    records["telemetry_probes"][policy] = {"request": {**payload, "messages": [{"role": "system", "content_sha256": persona_sha}, payload["messages"][1]]}, "http_status": status, "duration_seconds": duration, "started_epoch": started_epoch, "ended_epoch": ended_epoch, "response": data, "residency": ps}
    checkpoint()


class ExactPersonaAgent(AIAgent):
    def _build_system_prompt(self, system_message: str | None = None) -> str:
        if system_message not in (None, ""):
            raise RuntimeError("unexpected additive system message")
        self._cached_system_prompt_static = None
        return persona


session_db = SessionDB(db_path=HOME / "state.db")


def new_agent(policy: str, session_id: str) -> ExactPersonaAgent:
    agent = ExactPersonaAgent(model=MODEL, base_url=OLLAMA + "/v1", provider="custom", requested_provider="custom", max_iterations=1, enabled_toolsets=[], disabled_toolsets=["kanban"], quiet_mode=True, ephemeral_system_prompt=None, reasoning_config={"enabled": True, "effort": policy}, session_id=session_id, platform="cli", session_db=session_db, skip_context_files=True, load_soul_identity=False, skip_memory=True, skip_background_review=True, run_budget_seconds=180)
    if agent.tools or agent.valid_tool_names:
        raise RuntimeError(f"tools exposed: {agent.valid_tool_names}")
    if agent.reasoning_config != {"enabled": True, "effort": policy}:
        raise RuntimeError(f"reasoning config drift: {agent.reasoning_config}")
    return agent


def turn(agent: ExactPersonaAgent, prompt: str, history: list[dict[str, Any]]) -> tuple[dict[str, Any], float, float, float]:
    started_epoch = time.time()
    started = time.monotonic()
    result = agent.run_conversation(prompt, conversation_history=history)
    duration = time.monotonic() - started
    ended_epoch = time.time()
    if hashlib.sha256((agent._cached_system_prompt or "").encode()).hexdigest() != persona_sha:
        raise RuntimeError("effective persona drift")
    if agent.tools or agent.valid_tool_names:
        raise RuntimeError("tool exposure")
    return result, duration, started_epoch, ended_epoch


def metadata(agent: ExactPersonaAgent, result: dict[str, Any], started: float, ended: float) -> dict[str, Any]:
    return {"started_epoch": started, "ended_epoch": ended, "api_calls": result.get("api_calls"), "completed": result.get("completed", True), "error": result.get("error"), "usage": usage_value(agent), "visible_content_present": bool(result.get("final_response")), "reasoning_config": agent.reasoning_config}


for policy in ("low", "medium"):
    phase(f"cold-{policy}-unload")
    unload()
    phase(f"cold-{policy}")
    agent = new_agent(policy, f"task13b3a-cold-{policy}-{uuid.uuid4().hex}")
    result, duration, started, ended = turn(agent, "What is 2 plus 2? Answer briefly.", [])
    _, ps = get("/api/ps")
    records["cold"][policy] = {"duration_seconds": duration, "started_epoch": started, "ended_epoch": ended, "response": result.get("final_response", ""), "metadata": metadata(agent, result, started, ended), "residency": ps, "jarvis_health": health()}
    checkpoint()

for rep in range(1, 6):
    for policy in ORDER[rep]:
        for sid, prompt in SINGLES:
            phase(f"quality-r{rep}-{policy}-{sid}")
            agent = new_agent(policy, f"task13b3a-r{rep}-{policy}-{sid}-{uuid.uuid4().hex}")
            result, duration, started, ended = turn(agent, prompt, [])
            _, ps = get("/api/ps")
            records["quality"][policy].append({"repetition": rep, "scenario": sid, "turns": [{"user": prompt, "assistant": result.get("final_response", "")}], "duration_seconds": duration, "request_durations_seconds": [duration], "response_metadata": [metadata(agent, result, started, ended)], "residency": ps, "effective_persona_sha256": hashlib.sha256((agent._cached_system_prompt or "").encode()).hexdigest(), "tool_count": len(agent.tools or []), "tool_schema_count": len(agent.valid_tool_names or []), "jarvis_health": health()})
            checkpoint()
        for sid, prompts in MULTI:
            phase(f"quality-r{rep}-{policy}-{sid}")
            agent = new_agent(policy, f"task13b3a-r{rep}-{policy}-{sid}-{uuid.uuid4().hex}")
            history: list[dict[str, Any]] = []
            observed, durations, metas = [], [], []
            for prompt in prompts:
                result, duration, started, ended = turn(agent, prompt, history)
                answer = result.get("final_response", "")
                observed.append({"user": prompt, "assistant": answer})
                durations.append(duration)
                metas.append(metadata(agent, result, started, ended))
                history = result.get("messages", history)
            _, ps = get("/api/ps")
            records["quality"][policy].append({"repetition": rep, "scenario": sid, "turns": observed, "duration_seconds": sum(durations), "request_durations_seconds": durations, "response_metadata": metas, "residency": ps, "effective_persona_sha256": hashlib.sha256((agent._cached_system_prompt or "").encode()).hexdigest(), "tool_count": len(agent.tools or []), "tool_schema_count": len(agent.valid_tool_names or []), "jarvis_health": health()})
            checkpoint()

records["ended_epoch"] = time.time()
for policy in ("low", "medium"):
    values = [d for case in records["quality"][policy] for d in case["request_durations_seconds"]]
    records.setdefault("warm_request_latency", {})[policy] = {"count": len(values), "mean": statistics.mean(values), "p50": statistics.median(values), "p95_nearest_rank": sorted(values)[int(len(values) * 0.95 + 0.999999) - 1], "max": max(values)}
checkpoint()
phase("complete")
print(json.dumps({"cases": {k: len(v) for k, v in records["quality"].items()}, "latency": records["warm_request_latency"]}), flush=True)

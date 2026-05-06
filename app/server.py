"""FastAPI server — /health, /chat (REST), /ws (WebSocket)."""
from __future__ import annotations

import asyncio
import datetime
import json
import os
import re
import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.brain.cancel_token import current_token
from app.brain.direct_responder import try_direct_reply
from app.brain.kill_switch import check_voice, is_active, register_callback, start_hotkey_listener
from app.brain.llm_client import OllamaConnectionError, llm_client
from app.brain.prompts import build_prompt
from app.brain.response_cleaner import clean, dry_run_narration
from app.brain.complexity_router import complexity_router
from app.brain.router import router as intent_router
from app.agent.scheduler import scheduler
from app.agent.sensor_store import add_reading, get_readings, list_nodes
from app.agent.task_queue import task_queue
from app.config import settings
from app.logs.audit import audit
from app.tools.health_check import check_readiness, check_tools
from app.tools.registry import ToolError, registry
from app.voice.filler_manager import filler_manager
from app.voice.tts import tts


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict[str, Any]) -> None:
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()
_pending_confirmations: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.voice.audio_stream import voice_pipeline

    start_hotkey_listener()
    register_callback(current_token.cancel)
    register_callback(tts.stop)
    register_callback(voice_pipeline.stop)
    voice_pipeline.start()
    audit.log("server_start", {"host": settings.server.host, "port": settings.server.port})
    yield
    audit.log("server_stop", {"host": settings.server.host, "port": settings.server.port})
    tts.stop()
    voice_pipeline.stop()


app = FastAPI(title="JARVIS", version="0.1.0", lifespan=lifespan)
_pwa_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "pwa")
if os.path.isdir(_pwa_dir):
    app.mount("/pwa", StaticFiles(directory=_pwa_dir, html=True), name="pwa")
_STARTED_AT = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# REST
# ------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    dry_run: bool
    active: bool


class SensorReading(BaseModel):
    node_id: str
    readings: dict[str, float]
    metadata: dict[str, Any] | None = None


class TaskCreateRequest(BaseModel):
    goal: str


class TaskStatusRequest(BaseModel):
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None


class ScheduledJobRequest(BaseModel):
    name: str
    cron_expr: str
    goal: str


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "active": is_active(),
        "dry_run": settings.safety.dry_run,
        "main_model": settings.models.main,
        "router_model": settings.models.router,
        "uptime_seconds": round(time.time() - _STARTED_AT, 1),
    }


@app.get("/health/tools")
async def health_tools() -> dict[str, bool]:
    return check_tools()


@app.get("/health/readiness")
async def health_readiness() -> dict[str, dict[str, Any]]:
    return check_readiness()


@app.get("/network/status")
async def network_status() -> dict[str, Any]:
    from app.network.tailscale import get_status

    audit.log("network_status_check", {})
    return {
        "tailscale": get_status(),
        "server_host": settings.server.host,
        "server_port": settings.server.port,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    current_token.reset()
    try:
        reply, intent_result = await _process(req.message)
        return ChatResponse(
            reply=reply,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            dry_run=settings.safety.dry_run,
            active=is_active(),
        )
    finally:
        current_token.reset()


@app.post("/stop")
async def stop_response() -> dict[str, str]:
    current_token.cancel()
    tts.stop()
    return {"status": "stopped"}


@app.post("/tasks")
async def create_task(request: TaskCreateRequest) -> dict[str, Any]:
    task = await task_queue.add_task(request.goal)
    return asdict(task)


@app.get("/tasks")
async def list_tasks(status: str | None = None) -> dict[str, Any]:
    tasks = await task_queue.list_tasks(status=status)
    return {"tasks": [asdict(task) for task in tasks], "count": len(tasks)}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Any:
    task = await task_queue.get_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": "Unknown task"})
    return asdict(task)


@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, request: TaskStatusRequest) -> Any:
    updated = await task_queue.update_status(
        task_id,
        request.status,
        result=request.result,
        error=request.error,
    )
    if not updated:
        return JSONResponse(status_code=404, content={"error": "Unknown task"})
    task = await task_queue.get_task(task_id)
    return asdict(task) if task is not None else {"updated": True}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str) -> dict[str, bool]:
    deleted = await task_queue.delete_task(task_id)
    return {"deleted": deleted}


@app.post("/schedule/jobs")
async def create_scheduled_job(request: ScheduledJobRequest) -> dict[str, Any]:
    job = scheduler.add_job(request.name, request.cron_expr, request.goal)
    return asdict(job)


@app.get("/schedule/jobs")
async def list_scheduled_jobs() -> dict[str, Any]:
    jobs = scheduler.list_jobs()
    return {"jobs": [asdict(job) for job in jobs], "count": len(jobs)}


@app.delete("/schedule/jobs/{job_id}")
async def delete_scheduled_job(job_id: str) -> dict[str, bool]:
    removed = scheduler.remove_job(job_id)
    return {"deleted": removed}


@app.post("/sensors/data")
async def receive_sensor_data(reading: SensorReading) -> dict[str, Any]:
    add_reading(reading.node_id, {"readings": reading.readings, "metadata": reading.metadata or {}})
    audit.log("sensor_data_received", {"node_id": reading.node_id, "readings": reading.readings})
    return {"received": True, "node_id": reading.node_id}


@app.get("/sensors/{node_id}")
async def sensor_readings(node_id: str, limit: int = 10) -> dict[str, Any]:
    return {"node_id": node_id, "readings": get_readings(node_id, limit)}


@app.get("/sensors")
async def sensors() -> dict[str, list[str]]:
    return {"nodes": list_nodes()}


# ------------------------------------------------------------------
# WebSocket
# ------------------------------------------------------------------


@app.websocket(settings.server.websocket_path)
async def ws_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    audit.log("ws_connect", {"client": str(websocket.client)})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                message = data.get("message", raw)
            except json.JSONDecodeError:
                message = raw

            current_token.reset()
            try:
                await manager.broadcast({"type": "listening", "active": True})

                stream_result = await _process_stream(message)
                if stream_result is None:
                    reply, intent_result = await _process(message)
                else:
                    token_stream, intent_result = stream_result
                    chunks: list[str] = []

                    async def tts_tokens() -> AsyncGenerator[str, None]:
                        async for chunk in token_stream:
                            chunks.append(chunk)
                            yield chunk

                    await tts.speak_stream(tts_tokens())
                    reply = clean("".join(chunks))

                response = {
                    "type": "reply",
                    "reply": reply,
                    "intent": intent_result.intent,
                    "confidence": intent_result.confidence,
                    "dry_run": settings.safety.dry_run,
                    "active": is_active(),
                }
                await websocket.send_json(response)
                await manager.broadcast(response)
            finally:
                current_token.reset()
                await manager.broadcast({"type": "listening", "active": False})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        audit.log("ws_disconnect", {"client": str(websocket.client)})


@app.websocket("/ue5")
async def ue5_endpoint(websocket: WebSocket) -> None:
    from app.comms.ue5_bridge import ue5_manager

    await ue5_manager.connect(websocket)
    audit.log("ue5_ws_connect", {"client": str(websocket.client)})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ue5_manager.disconnect(websocket)
        audit.log("ue5_ws_disconnect", {"client": str(websocket.client)})


# ------------------------------------------------------------------
# Core pipeline
# ------------------------------------------------------------------


async def _process(message: str):  # type: ignore[return]
    from app.brain.router import RouterResult
    from app.comms.ue5_bridge import build_emotion_event, parse_emotion_from_reply, ue5_manager

    def finalize_reply(reply_text: str, *, emotion_source: str | None = None) -> str:
        cleaned_reply = clean(reply_text)
        emotion = parse_emotion_from_reply(emotion_source or reply_text) or "neutral"
        if settings.server.ue5_enabled:
            asyncio.create_task(ue5_manager.broadcast(build_emotion_event(emotion)))
        return cleaned_reply

    if _is_cancel_command(message):
        current_token.cancel()
        tts.stop()
        return finalize_reply("Stopping current response, sir."), RouterResult(
            "respond",
            1.0,
            "",
            "Cancel token requested.",
        )

    if check_voice(message):
        return finalize_reply("Understood, sir. Standing by."), RouterResult(
            "confirm_action",
            1.0,
            "",
            "Kill switch activated.",
        )

    if not is_active():
        return finalize_reply("Standing by, sir."), RouterResult("confirm_action", 1.0, "", "Kill switch is active.")

    intent_result: RouterResult = intent_router.classify(message)

    if intent_result.intent == "use_tool" and intent_result.suggested_tool:
        tool_name = intent_result.suggested_tool
        params = _tool_params(tool_name, message)
        filler_manager.play_for_tool(tool_name)

        try:
            result = registry.call(tool_name, params)
            if result.dry_run:
                return dry_run_narration(tool_name, params), intent_result
            context = str(result.output)[:1000]
        except ToolError as exc:
            if _is_confirmation_required_error(exc):
                request_id = str(uuid.uuid4())[:8]
                _pending_confirmations[request_id] = {"tool": tool_name, "params": params}
                approval_msg = (
                    f"JARVIS approval required [{request_id}]: Run {tool_name} "
                    f"with {params}? POST /confirm/{request_id} to approve."
                )
                try:
                    from app.comms.discord_bot import discord_bot
                    from app.comms.telegram_bot import telegram_bot

                    tasks = []
                    if getattr(settings.comms, "discord_channel_id", None):
                        tasks.append(discord_bot.send_message(approval_msg))
                    if getattr(settings.comms, "telegram_chat_id", None):
                        tasks.append(telegram_bot.send_message(approval_msg))
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                except Exception:
                    pass
                audit.log(
                    "approval_gate_triggered",
                    {"request_id": request_id, "tool": tool_name, "params": params},
                )
                context = (
                    f"Confirmation request sent to your devices, sir. "
                    f"Use /confirm/{request_id} to approve."
                )
            else:
                context = str(exc)

        messages = build_prompt(message, context=context)
        decision = complexity_router.decide(message, intent_result.intent)
        try:
            raw_reply = await llm_client.chat(
                messages,
                model=decision.model,
                think=decision.think,
                num_predict=decision.num_predict,
            )
        except OllamaConnectionError as exc:
            raw_reply = f"Unable to reach Ollama, sir. {exc}"

        return finalize_reply(str(raw_reply)), intent_result

    if intent_result.intent == "confirm_action":
        reply = f"That action requires your confirmation, sir. Shall I proceed with: {message}?"
        return finalize_reply(reply), intent_result

    if intent_result.intent == "respond":
        direct_reply = try_direct_reply(message)
        if direct_reply:
            return finalize_reply(direct_reply), intent_result

    if intent_result.intent == "deep_reasoning":
        messages = build_prompt(message)
        decision = complexity_router.decide(message, intent_result.intent)
        try:
            raw_reply = await llm_client.chat(
                messages,
                model=decision.model,
                think=decision.think,
                num_predict=decision.num_predict,
            )
        except OllamaConnectionError as exc:
            raw_reply = f"Unable to reach Ollama for deep reasoning, sir. {exc}"
        return finalize_reply(str(raw_reply)), intent_result

    # respond, retrieve_memory, vision — all go straight to LLM
    messages = build_prompt(message)
    decision = complexity_router.decide(message, intent_result.intent)
    try:
        raw_reply = await llm_client.chat(
            messages,
            model=decision.model,
            think=decision.think,
            num_predict=decision.num_predict,
        )
    except OllamaConnectionError as exc:
        raw_reply = f"Unable to reach Ollama at the moment, sir. {exc}"

    return finalize_reply(str(raw_reply)), intent_result


def _is_confirmation_required_error(exc: ToolError) -> bool:
    message = str(exc)
    return "Requires user confirmation" in message or "confirmation" in message.lower()


@app.post("/confirm/{request_id}", response_model=None)
async def confirm_request(request_id: str) -> Any:
    pending = _pending_confirmations.pop(request_id, None)
    if pending is None:
        return JSONResponse(status_code=404, content={"error": "Unknown or expired request"})

    tool_name = str(pending["tool"])
    params = dict(pending["params"])

    try:
        result = registry.call(tool_name, params, confirmed=True)
    except ToolError as exc:
        return {"error": str(exc)}

    done_msg = f"JARVIS approved [{request_id}]: {tool_name} executed. Result: {str(result.output)[:200]}"
    try:
        from app.comms.discord_bot import discord_bot
        from app.comms.telegram_bot import telegram_bot

        tasks = []
        if getattr(settings.comms, "discord_channel_id", None):
            tasks.append(discord_bot.send_message(done_msg))
        if getattr(settings.comms, "telegram_chat_id", None):
            tasks.append(telegram_bot.send_message(done_msg))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    except Exception:
        pass

    audit.log(
        "approval_gate_confirmed",
        {"request_id": request_id, "tool": tool_name, "output": str(result.output)[:500]},
    )
    return {"confirmed": True, "tool": tool_name, "output": str(result.output)}


async def _process_stream(message: str):  # type: ignore[return]
    from app.brain.router import RouterResult

    if _is_cancel_command(message):
        current_token.cancel()
        tts.stop()
        return None

    if check_voice(message) or not is_active():
        return None

    intent_result: RouterResult = intent_router.classify(message)

    if intent_result.intent == "use_tool" and intent_result.suggested_tool:
        tool_name = intent_result.suggested_tool
        params = _tool_params(tool_name, message)

        try:
            result = registry.call(tool_name, params)
            if result.dry_run:
                return None
            context = str(result.output)[:1000]
        except ToolError:
            return None

        messages = build_prompt(message, context=context)
        decision = complexity_router.decide(message, intent_result.intent)
        try:
            raw_reply = await llm_client.chat(
                messages,
                model=decision.model,
                stream=True,
                think=decision.think,
                num_predict=decision.num_predict,
            )
        except OllamaConnectionError:
            return None

        if hasattr(raw_reply, "__aiter__"):
            return raw_reply, intent_result
        return None

    if intent_result.intent == "confirm_action":
        return None

    if intent_result.intent == "respond":
        direct_reply = try_direct_reply(message)
        if direct_reply:
            return None

    if intent_result.intent == "deep_reasoning":
        messages = build_prompt(message)
        decision = complexity_router.decide(message, intent_result.intent)
        try:
            raw_reply = await llm_client.chat(
                messages,
                model=decision.model,
                stream=True,
                think=decision.think,
                num_predict=decision.num_predict,
            )
        except OllamaConnectionError:
            return None

        if hasattr(raw_reply, "__aiter__"):
            return raw_reply, intent_result
        return None

    messages = build_prompt(message)
    decision = complexity_router.decide(message, intent_result.intent)
    try:
        raw_reply = await llm_client.chat(
            messages,
            model=decision.model,
            stream=True,
            think=decision.think,
            num_predict=decision.num_predict,
        )
    except OllamaConnectionError:
        return None

    if hasattr(raw_reply, "__aiter__"):
        return raw_reply, intent_result
    return None


_WAKE_PREFIX_RE = re.compile(r"^\s*(?:hey\s+jarvis|jarvis)[,\s]*", re.IGNORECASE)
_WAKE_SUFFIX_RE = re.compile(r"[,\s]*\bjarvis\b\s*[?.]?\s*$", re.IGNORECASE)
_CANCEL_COMMAND_RE = re.compile(r"\babort\b|\bstop\s*,?\s*jarvis\b", re.IGNORECASE)


def _strip_wake_word(text: str) -> str:
    text = _WAKE_PREFIX_RE.sub("", text)
    text = _WAKE_SUFFIX_RE.sub("", text)
    return text.strip()


def _is_cancel_command(text: str) -> bool:
    return bool(_CANCEL_COMMAND_RE.search(text))


def _tool_params(tool_name: str, message: str) -> dict[str, Any]:
    """Map routed user text to concrete tool parameters."""
    clean_msg = _strip_wake_word(message)
    if tool_name == "system_stats":
        return {}
    if tool_name == "web_search":
        query = re.sub(r"\b(search|web|google|duckduckgo|look up)\b", "", clean_msg, flags=re.IGNORECASE)
        return {"query": query.strip(" .") or clean_msg, "max_results": 5}
    if tool_name == "apps":
        action = "close" if re.search(r"\b(close|quit|exit)\b", clean_msg, re.IGNORECASE) else "open"
        return {"action": action, "app": _extract_app_name(clean_msg), "query": clean_msg}
    if tool_name == "files":
        lower = clean_msg.lower()
        action = "read" if "read" in lower else "list"
        path = settings.paths.downloads_dir if "download" in lower else settings.paths.projects_dir
        return {"action": action, "path": path, "query": clean_msg}
    if tool_name == "shell":
        command = re.sub(
            r"^\s*(run|execute|shell|cmd|bash|terminal)\b[:\s-]*",
            "",
            clean_msg,
            flags=re.IGNORECASE,
        ).strip()
        return {"command": command or clean_msg, "timeout": 30}
    if tool_name == "calendar":
        lower = clean_msg.lower()
        today = datetime.date.today()
        if "tomorrow" in lower:
            date_value = (today + datetime.timedelta(days=1)).isoformat()
        else:
            date_value = today.isoformat()
            if "today" in lower or re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lower):
                date_value = clean_msg
            elif re.search(r"\d", clean_msg):
                date_value = clean_msg
        return {"date": date_value}
    if tool_name == "interpreter":
        task = re.sub(
            r"^\s*(interpret|open interpreter|run code|execute code)\b[:\s-]*",
            "",
            clean_msg,
            flags=re.IGNORECASE,
        ).strip()
        return {"task": task or clean_msg, "timeout": 60}
    if tool_name == "screenshot":
        monitor_match = re.search(r"\b(?:monitor|screen)\s+(\d+)\b", clean_msg, flags=re.IGNORECASE)
        return {"monitor": int(monitor_match.group(1)) if monitor_match else 0}
    return {"query": clean_msg}


def _extract_app_name(message: str) -> str:
    """Extract a likely app name from launch/close phrasing."""
    text = message.lower().replace("visual studio code", "vscode")
    text = re.sub(r"\b(open|launch|start|close|quit|exit)\b", "", text, flags=re.IGNORECASE)
    return text.strip(" .")

"""FastAPI server — /health, /chat (REST), /ws (WebSocket)."""
from __future__ import annotations

import asyncio
import datetime
import json
import os
import re
import secrets
import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
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
from app.brain.tool_params import build_tool_params as _tool_params
from app.brain.tool_params import is_cancel_command as _is_cancel_command
from app.agent.scheduler import scheduler
from app.agent.api import router as authority_router
from app.agent.admission import AdmissionBodyLimit
from app.agent.runtime import close_authority, get_authority, get_execution_worker
from app.agent.sensor_store import add_reading, get_readings, list_nodes
from app.config import settings
from app.config_check import check_startup
from app.logs.audit import audit
from app.memory.graphiti_client import graphiti_client
from app.memory.memory_client import memory_client
from app.memory.procedural import procedural_memory
from app.memory.rag_client import rag_client
from app.observability.tracing import current_trace_id, emit_event, start_trace, trace_span
from app.resource_manager import resource_manager
from app.tools.health_check import check_readiness, check_tools
from app.tools.registry import ToolError, registry
from app.voice.filler_manager import filler_manager
from app.voice.tts import tts


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []
        self._accepting = 0

    async def connect(self, ws: WebSocket) -> bool:
        if len(self.active) + self._accepting >= 32:
            await ws.close(code=1008, reason="connection_bound")
            return False
        self._accepting += 1
        try:
            await ws.accept()
            self.active.append(ws)
            return True
        finally:
            self._accepting -= 1

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict[str, Any]) -> None:
        dead = []
        for ws in self.active:
            try:
                await asyncio.wait_for(ws.send_json(data), timeout=2)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def disconnect_all(self) -> int:
        closed = 0
        for ws in list(self.active):
            try:
                await ws.close(code=1001, reason="JARVIS entering sleep mode")
                closed += 1
            except Exception:
                pass
            finally:
                self.disconnect(ws)
        return closed


manager = ConnectionManager()
_pending_confirmations: dict[str, dict] = {}
_runtime_callbacks_registered = False
_voice_callback_registered = False


def _log_startup_checks() -> None:
    audit.log("config_check", check_startup())


def _register_runtime_callbacks(voice_pipeline: Any | None = None) -> None:
    global _runtime_callbacks_registered, _voice_callback_registered

    if not _runtime_callbacks_registered:
        register_callback(current_token.cancel)
        register_callback(tts.stop)
        _runtime_callbacks_registered = True

    if voice_pipeline is not None and not _voice_callback_registered:
        register_callback(voice_pipeline.stop)
        _voice_callback_registered = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mandatory storage errors propagate before readiness or background work.
    authority = get_authority()
    voice_pipeline = None
    voice_started = False
    idle_started = False
    startup_check = None
    execution_worker = get_execution_worker()
    try:
        authority.readiness()
        if execution_worker is not None and execution_worker.pipeline.transport is not None and not settings.server.api_token:
            from app.agent.authority import AuthorityError
            raise AuthorityError("transport_client_authentication_required")
        await scheduler.start()
        if execution_worker is not None:
            await execution_worker.start()
        _register_runtime_callbacks()
        resource_manager.mark_activity("server_start")
        await resource_manager.start_idle_monitor()
        idle_started = True
        startup_check = asyncio.create_task(asyncio.to_thread(_log_startup_checks))
        if settings.server.enable_hotkey_listener:
            start_hotkey_listener()
        if settings.server.enable_voice_on_startup:
            from app.voice.audio_stream import voice_pipeline as configured_voice_pipeline
            voice_pipeline = configured_voice_pipeline
            _register_runtime_callbacks(voice_pipeline)
            voice_pipeline.start()
            voice_started = True
        audit.log("server_start", {"host": settings.server.host, "port": settings.server.port,
            "voice_started": voice_started, "hotkey_listener_enabled": settings.server.enable_hotkey_listener})
        yield
    finally:
        try:
            if idle_started:
                await resource_manager.stop_idle_monitor()
            tts.stop()
            if voice_started and voice_pipeline is not None:
                voice_pipeline.stop()
            if startup_check is not None:
                await startup_check
            audit.log("server_stop", {"host": settings.server.host, "port": settings.server.port})
        finally:
            try:
                if execution_worker is not None:
                    await execution_worker.stop()
            finally:
                try:
                    await scheduler.stop()
                finally:
                    close_authority()


app = FastAPI(title="JARVIS", version="0.1.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def bounded_validation_error(request, exc):
    # Never reflect submitted credentials/authorization evidence into responses.
    return JSONResponse(status_code=422,content={"error":"invalid_request","automatic_retry":False})

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
app.add_middleware(AdmissionBodyLimit)


_RESOURCE_ACTIVITY_EXEMPT_PREFIXES = ("/health", "/resource", "/pwa")

# Static PWA assets carry no tool/file access. Remote browser authentication is
# deferred; the baseline PWA is intended for the loopback server only.
_AUTH_EXEMPT_EXACT = ("/health",)
_AUTH_EXEMPT_PREFIXES = ("/pwa",)


def _api_token_ok(supplied: str) -> bool:
    expected = settings.server.api_token
    if not expected:
        return True
    return secrets.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8"))


def _bearer_token(authorization: str | None) -> str:
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer "):]
    return ""


def _ws_authorized(websocket: WebSocket) -> bool:
    if not settings.server.api_token:
        return True
    supplied = _bearer_token(websocket.headers.get("authorization"))
    return _api_token_ok(supplied)


def _ws_origin_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    if origin is None:
        return True
    loopback_origins = {
        f"http://localhost:{settings.server.port}",
        f"http://127.0.0.1:{settings.server.port}",
        f"http://[::1]:{settings.server.port}",
    }
    return origin in loopback_origins or origin in settings.server.cors_origins


async def _reject_unauthorized_websocket(websocket: WebSocket, path: str) -> bool:
    if not _ws_origin_allowed(websocket):
        audit.log("ws_origin_rejected", {"path": path, "client": str(websocket.client)})
        await websocket.close(code=1008, reason="Origin not allowed")
        return True
    if not _ws_authorized(websocket):
        audit.log("auth_rejected", {"path": path, "client": str(websocket.client)})
        await websocket.close(code=1008, reason="Unauthorized")
        return True
    return False


@app.middleware("http")
async def resource_activity_middleware(request: Request, call_next):  # noqa: ANN001, ANN201
    response = await call_next(request)
    if not any(request.url.path.startswith(prefix) for prefix in _RESOURCE_ACTIVITY_EXEMPT_PREFIXES):
        resource_manager.mark_activity(f"http:{request.method}:{request.url.path}")
    return response


@app.middleware("http")
async def api_token_middleware(request: Request, call_next):  # noqa: ANN001, ANN201
    if not settings.server.api_token:
        if request.url.path=="/stop":
            return JSONResponse(status_code=401,content={"error":"operator_authentication_required"})
        return await call_next(request)
    path = request.url.path
    if path in _AUTH_EXEMPT_EXACT or any(path.startswith(prefix) for prefix in _AUTH_EXEMPT_PREFIXES):
        return await call_next(request)
    if _api_token_ok(_bearer_token(request.headers.get("authorization"))):
        return await call_next(request)
    audit.log("auth_rejected", {"path": path, "client": str(request.client)})
    return JSONResponse(status_code=401, content={"error": "Unauthorized"})


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


class SkillCreateRequest(BaseModel):
    skill: str


class GraphAddRequest(BaseModel):
    text: str
    source: str = "api"
    ts: datetime.datetime | None = None


class GraphQueryRequest(BaseModel):
    text: str
    limit: int = 5


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "active": is_active(),
        "resource_state": resource_manager.state.value,
        "dry_run": settings.safety.dry_run,
        "main_model": settings.models.main,
        "router_model": settings.models.router,
        "uptime_seconds": round(time.time() - _STARTED_AT, 1),
    }


@app.get("/resource/status")
async def resource_status() -> dict[str, Any]:
    return resource_manager.status()


@app.post("/resource/sleep/light")
@app.post("/resource/sleep/deep")
@app.post("/resource/wake")
@app.post("/resource/shutdown")
async def resource_mutation_unavailable() -> Any:
    # HTTP identity alone is not independent host-control authorization.
    return JSONResponse(status_code=403,content={"error":"offline_operator_control_required","automatic_retry":False})


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
    with start_trace(origin="user_direct", component="app.server", transport="http"):
        if not await resource_manager.ensure_awake_for_interaction("chat"):
            return ChatResponse(
                reply="JARVIS is in deep sleep. Run `jarvis wake` to restore the runtime.",
                intent="sleep",
                confidence=1.0,
                dry_run=settings.safety.dry_run,
                active=False,
            )
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
    worker = get_execution_worker()
    if worker is not None:
        await worker.stop()
    return {"status": "stopped"}


app.include_router(authority_router)


@app.get("/memory/skills")
async def list_procedural_skills() -> dict[str, Any]:
    skills = procedural_memory.list_skills()
    return {"skills": skills, "count": len(skills)}


@app.post("/memory/skills")
async def add_procedural_skill(request: SkillCreateRequest) -> dict[str, Any]:
    added = procedural_memory.add_skill(request.skill)
    skills = procedural_memory.list_skills()
    return {"added": added, "skills": skills, "count": len(skills)}


@app.post("/memory/graph/add")
async def add_graph_episode(request: GraphAddRequest) -> Any:
    if not graphiti_client.is_enabled():
        return JSONResponse(status_code=503, content={"error": "graphiti_disabled"})
    return await asyncio.to_thread(graphiti_client.add_episode, request.text, request.source, request.ts)


@app.post("/memory/graph/query")
async def query_graph(request: GraphQueryRequest) -> Any:
    if not graphiti_client.is_enabled():
        return JSONResponse(status_code=503, content={"error": "graphiti_disabled"})
    return await asyncio.to_thread(graphiti_client.query, request.text, request.limit)


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
    if await _reject_unauthorized_websocket(websocket, settings.server.websocket_path):
        return
    if not await manager.connect(websocket):
        return
    audit.log("ws_connect", {"client": str(websocket.client)})

    try:
        while True:
            frame = await websocket.receive()
            if frame["type"] == "websocket.disconnect":
                return
            raw = frame.get("text")
            if type(raw) is not str:
                await websocket.close(code=1008, reason="text_required")
                return
            if len(raw.encode('utf-8'))>8192:
                await websocket.close(code=1009,reason="message_bound");return
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                message = raw
            else:
                if type(data) is not dict or type(data.get('message')) is not str:
                    await websocket.close(code=1008,reason="invalid_message");return
                message=data['message']
            if not message.strip():
                await websocket.close(code=1008,reason="invalid_message");return

            if not await resource_manager.ensure_awake_for_interaction("websocket"):
                await websocket.send_json(
                    {
                        "type": "sleep",
                        "state": resource_manager.state.value,
                        "message": "JARVIS is in deep sleep. Run `jarvis wake` to restore the runtime.",
                    }
                )
                continue

            current_token.reset()
            try:
                with start_trace(origin="user_direct", component="app.server", transport="websocket"):
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

                        with trace_span("tts", component="app.voice.tts"):
                            await tts.speak_stream(tts_tokens())
                        with trace_span("response", component="app.server"):
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
        pass
    finally:
        manager.disconnect(websocket)
        audit.log("ws_disconnect", {"client": str(websocket.client)})


@app.websocket("/ue5")
async def ue5_endpoint(websocket: WebSocket) -> None:
    from app.comms.ue5_bridge import ue5_manager

    if await _reject_unauthorized_websocket(websocket, "/ue5"):
        return
    if not await ue5_manager.connect(websocket):
        return
    audit.log("ue5_ws_connect", {"client": str(websocket.client)})

    try:
        while True:
            frame = await websocket.receive()
            if frame["type"] == "websocket.disconnect":
                return
            raw = frame.get("text")
            if type(raw) is not str:
                await websocket.close(code=1008, reason="text_required")
                return
            if len(raw.encode("utf-8")) > 8192:
                await websocket.close(code=1009, reason="message_bound")
                return
    except WebSocketDisconnect:
        pass
    finally:
        ue5_manager.disconnect(websocket)
        audit.log("ue5_ws_disconnect", {"client": str(websocket.client)})


# ------------------------------------------------------------------
# Core pipeline
# ------------------------------------------------------------------


def _build_tool_params_traced(tool_name: str, message: str) -> dict[str, Any]:
    with trace_span(
        "tool_parameters",
        component="app.brain.tool_params",
        metadata={"tool": tool_name},
    ):
        return _tool_params(tool_name, message)


def _plan_traced(message: str, intent: str):  # noqa: ANN202
    with trace_span("planner", component="app.brain.complexity_router"):
        return complexity_router.decide(message, intent)


async def _process(message: str):  # type: ignore[return]
    from app.brain.router import RouterResult
    from app.comms.ue5_bridge import build_emotion_event, parse_emotion_from_reply, ue5_manager

    def finalize_reply(reply_text: str, *, emotion_source: str | None = None) -> str:
        with trace_span("response", component="app.server"):
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

    if intent_result.intent in {"use_tool","confirm_action","vision"}:
        return finalize_reply("Real tool execution is disabled. Synthetic execution requires an independently authorized durable request."),intent_result

    if intent_result.intent == "respond":
        direct_reply = try_direct_reply(message)
        if direct_reply:
            return finalize_reply(direct_reply), intent_result

    if intent_result.intent == "deep_reasoning":
        messages = build_prompt(message)
        decision = _plan_traced(message, intent_result.intent)
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

    if intent_result.intent == "retrieve_memory":
        messages = build_prompt(message, context=_memory_context(message))
        decision = _plan_traced(message, intent_result.intent)
        try:
            raw_reply = await llm_client.chat(
                messages,
                model=decision.model,
                think=decision.think,
                num_predict=decision.num_predict,
            )
        except OllamaConnectionError as exc:
            raw_reply = f"Unable to reach Ollama for memory lookup, sir. {exc}"
        return finalize_reply(str(raw_reply)), intent_result

    messages = build_prompt(message)
    decision = _plan_traced(message, intent_result.intent)
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


async def _process_stream(message: str):  # type: ignore[return]
    from app.brain.router import RouterResult

    if _is_cancel_command(message):
        current_token.cancel()
        tts.stop()
        return None

    if check_voice(message) or not is_active():
        return None

    intent_result: RouterResult = intent_router.classify(message)

    if intent_result.intent in {"use_tool","confirm_action","vision"}:
        return None

    if intent_result.intent == "respond":
        direct_reply = try_direct_reply(message)
        if direct_reply:
            return None

    if intent_result.intent == "deep_reasoning":
        messages = build_prompt(message)
        decision = _plan_traced(message, intent_result.intent)
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

    if intent_result.intent in {"retrieve_memory", "vision"}:
        return None

    messages = build_prompt(message)
    decision = _plan_traced(message, intent_result.intent)
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


def _memory_context(message: str) -> str:
    parts: list[str] = []

    skills = procedural_memory.list_skills()
    if skills:
        parts.append("Procedural memory:\n" + "\n".join(f"- {skill}" for skill in skills[:20]))
    else:
        parts.append("Procedural memory: no saved skills.")

    try:
        mem_result = memory_client.search(message)
    except Exception as exc:  # noqa: BLE001
        mem_result = {"error": str(exc)}

    if isinstance(mem_result, dict) and mem_result.get("stub"):
        parts.append(f"Long-term memory: disabled or unavailable ({mem_result.get('note', 'stub')}).")
    elif isinstance(mem_result, dict) and mem_result.get("error"):
        parts.append(f"Long-term memory error: {mem_result['error']}")
    else:
        parts.append(f"Long-term memory results: {mem_result}")

    try:
        rag_result = rag_client.query(message)
    except Exception as exc:  # noqa: BLE001
        rag_result = {"error": str(exc)}

    if isinstance(rag_result, dict) and rag_result.get("stub"):
        parts.append(f"RAG memory: disabled or unavailable ({rag_result.get('note', 'stub')}).")
    elif isinstance(rag_result, dict) and rag_result.get("error"):
        parts.append(f"RAG memory error: {rag_result['error']}")
    else:
        parts.append(f"RAG memory results: {rag_result}")

    return "\n\n".join(parts)[:3000]

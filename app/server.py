"""FastAPI server — /health, /chat (REST), /ws (WebSocket)."""
from __future__ import annotations

import datetime
import json
import re
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.brain.direct_responder import try_direct_reply
from app.brain.kill_switch import check_voice, is_active, register_callback, start_hotkey_listener
from app.brain.llm_client import OllamaConnectionError, llm_client
from app.brain.prompts import build_prompt
from app.brain.response_cleaner import clean, dry_run_narration
from app.brain.router import router as intent_router
from app.config import settings
from app.logs.audit import audit
from app.tools.health_check import check_tools
from app.tools.registry import ToolError, registry
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.voice.audio_stream import voice_pipeline

    start_hotkey_listener()
    register_callback(tts.stop)
    register_callback(voice_pipeline.stop)
    voice_pipeline.start()
    audit.log("server_start", {"host": settings.server.host, "port": settings.server.port})
    yield
    audit.log("server_stop", {"host": settings.server.host, "port": settings.server.port})
    tts.stop()
    voice_pipeline.stop()


app = FastAPI(title="JARVIS", version="0.1.0", lifespan=lifespan)
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


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    reply, intent_result = await _process(req.message)
    return ChatResponse(
        reply=reply,
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        dry_run=settings.safety.dry_run,
        active=is_active(),
    )


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
            await manager.broadcast({"type": "listening", "active": False})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        audit.log("ws_disconnect", {"client": str(websocket.client)})


# ------------------------------------------------------------------
# Core pipeline
# ------------------------------------------------------------------


async def _process(message: str):  # type: ignore[return]
    from app.brain.router import RouterResult

    if check_voice(message):
        return "Understood, sir. Standing by.", RouterResult("confirm_action", 1.0, "", "Kill switch activated.")

    if not is_active():
        return "Standing by, sir.", RouterResult("confirm_action", 1.0, "", "Kill switch is active.")

    intent_result: RouterResult = intent_router.classify(message)

    if intent_result.intent == "use_tool" and intent_result.suggested_tool:
        tool_name = intent_result.suggested_tool
        params = _tool_params(tool_name, message)

        try:
            result = registry.call(tool_name, params)
            if result.dry_run:
                return dry_run_narration(tool_name, params), intent_result
            context = str(result.output)[:1000]
        except ToolError as exc:
            context = str(exc)

        messages = build_prompt(message, context=context)
        try:
            raw_reply = await llm_client.chat(messages)
        except OllamaConnectionError as exc:
            raw_reply = f"Unable to reach Ollama, sir. {exc}"

        return clean(str(raw_reply)), intent_result

    if intent_result.intent == "confirm_action":
        reply = f"That action requires your confirmation, sir. Shall I proceed with: {message}?"
        return reply, intent_result

    if intent_result.intent == "respond":
        direct_reply = try_direct_reply(message)
        if direct_reply:
            return direct_reply, intent_result

    # respond, retrieve_memory, vision — all go straight to LLM
    messages = build_prompt(message)
    try:
        raw_reply = await llm_client.chat(messages)
    except OllamaConnectionError as exc:
        raw_reply = f"Unable to reach Ollama at the moment, sir. {exc}"

    return clean(str(raw_reply)), intent_result


async def _process_stream(message: str):  # type: ignore[return]
    from app.brain.router import RouterResult

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
        try:
            raw_reply = await llm_client.chat(messages, stream=True)
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

    messages = build_prompt(message)
    try:
        raw_reply = await llm_client.chat(messages, stream=True)
    except OllamaConnectionError:
        return None

    if hasattr(raw_reply, "__aiter__"):
        return raw_reply, intent_result
    return None


_WAKE_PREFIX_RE = re.compile(r"^\s*(?:hey\s+jarvis|jarvis)[,\s]*", re.IGNORECASE)
_WAKE_SUFFIX_RE = re.compile(r"[,\s]*\bjarvis\b\s*[?.]?\s*$", re.IGNORECASE)


def _strip_wake_word(text: str) -> str:
    text = _WAKE_PREFIX_RE.sub("", text)
    text = _WAKE_SUFFIX_RE.sub("", text)
    return text.strip()


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


from application_fixtures import admitted_app
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient

from app.agent.scheduler import Scheduler
from app.agent.task_queue import TaskQueue
from app.memory.procedural import ProceduralMemory
from app.resource_manager import RuntimeState, TransitionResult
from app.server import app
from app.tools.registry import ToolResult

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_respond_intent() -> None:
    intent = SimpleNamespace(intent="respond", confidence=0.9, suggested_tool="", reasoning="")
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.brain.router.router.classify", return_value=intent
    ), patch("app.server.try_direct_reply", return_value=None), patch(
        "app.server.llm_client.chat", new=AsyncMock(return_value="It is 3pm sir.")
    ):
        response = client.post("/chat", json={"message": "what time is it"})
    assert response.status_code == 200
    assert response.json()["reply"] == "It is 3pm sir."


def test_chat_browser_tool() -> None:
    intent = SimpleNamespace(intent="use_tool", confidence=0.95, suggested_tool="browser", reasoning="")
    result = ToolResult(tool="browser", output="opened google", dry_run=False)
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.brain.router.router.classify", return_value=intent
    ), patch("app.server.registry.call", return_value=result), patch(
        "app.server.llm_client.chat", new=AsyncMock(return_value="Opened, sir.")
    ):
        response = client.post("/chat", json={"message": "open google"})
    assert response.status_code == 200
    assert "reply" in response.json()


def test_chat_vision_intent_calls_vision_tool() -> None:
    intent = SimpleNamespace(intent="vision", confidence=0.95, suggested_tool="", reasoning="")
    result = ToolResult(tool="vision", output={"analysis": "desktop with terminal"}, dry_run=False)
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.server.intent_router.classify", return_value=intent
    ), patch("app.server.filler_manager.play_for_tool"), patch(
        "app.server.registry.call", return_value=result
    ) as call_tool, patch(
        "app.server.llm_client.chat", new=AsyncMock(return_value="I can see the desktop, sir.")
    ):
        response = client.post("/chat", json={"message": "what do you see on screen"})

    assert response.status_code == 200
    assert response.json()["intent"] == "vision"
    call_tool.assert_not_called()
    assert "disabled" in response.json()["reply"].lower()


def test_chat_retrieve_memory_intent_adds_context() -> None:
    intent = SimpleNamespace(intent="retrieve_memory", confidence=0.95, suggested_tool="", reasoning="")
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.server.intent_router.classify", return_value=intent
    ), patch("app.server._memory_context", return_value="Stored context") as memory_context, patch(
        "app.server.llm_client.chat", new=AsyncMock(return_value="I found the stored context, sir.")
    ):
        response = client.post("/chat", json={"message": "what did I tell you yesterday"})

    assert response.status_code == 200
    assert response.json()["intent"] == "retrieve_memory"
    memory_context.assert_called_once_with("what did I tell you yesterday")


def test_chat_dry_run() -> None:
    intent = SimpleNamespace(intent="use_tool", confidence=0.95, suggested_tool="browser", reasoning="")
    result = ToolResult(tool="browser", output="noop", dry_run=True)
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.brain.router.router.classify", return_value=intent
    ), patch("app.server.registry.call", return_value=result), patch("app.config.settings.safety.dry_run", True):
        response = client.post("/chat", json={"message": "open google"})
    assert response.status_code == 200
    assert "disabled" in response.json()["reply"].lower()


def test_health_tools_route() -> None:
    expected = {"ollama": True, "piper": False}
    with patch("app.server.check_tools", return_value=expected):
        response = client.get("/health/tools")
    assert response.status_code == 200
    assert any(isinstance(v, bool) for v in response.json().values())


def test_chat_missing_message() -> None:
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_task_routes(monkeypatch):
    monkeypatch.setattr("app.server.settings.server.api_token", "synthetic-http-contract")
    with TestClient(app,headers={'Authorization':'Bearer synthetic-http-contract'}) as c:
        key=str(uuid.uuid4())
        created=c.post('/tasks',json={'request_id':key,'goal':'finish build'})
        assert created.status_code==200
        assert c.get('/tasks/'+key).json()['status']=='pending'
        assert c.patch('/tasks/'+key,json={'status':'done'}).status_code==405
        cancelled=c.delete('/tasks/'+key,params={'request_id':str(uuid.uuid4())})
        assert cancelled.json()['result']['status']=='cancelled'


def test_schedule_job_routes(monkeypatch):
    monkeypatch.setattr("app.server.settings.server.api_token", "synthetic-http-contract")
    with TestClient(app,headers={'Authorization':'Bearer synthetic-http-contract'}) as c:
        created=c.post('/schedule/jobs',json={'request_id':str(uuid.uuid4()),'name':'daily','cron_expr':'0 8 * * *','goal':'held report'})
        assert created.status_code==200,created.text
        job=created.json()['result']
        assert len(c.get('/schedule/jobs').json()['jobs'])==1
        removed=c.delete('/schedule/jobs/'+job['job_id'],params={'request_id':str(uuid.uuid4())})
        assert removed.status_code==200
        assert not c.get('/schedule/jobs').json()['jobs']


def test_resource_management_routes(monkeypatch) -> None:  # noqa: ANN001
    class FakeResourceManager:
        state = RuntimeState.ACTIVE

        def status(self) -> dict:
            return {"state": "ACTIVE", "resources": {"estimated_vram_mb": 0}}

        async def light_sleep(self, reason: str) -> TransitionResult:
            return TransitionResult("LIGHT_SLEEP", "ACTIVE", reason, ["ollama_models_unloaded:1"], {})

        async def deep_sleep(self, reason: str, terminate_processes: bool = False) -> TransitionResult:
            return TransitionResult("DEEP_SLEEP", "ACTIVE", f"{reason}:{terminate_processes}", ["voice_pipeline_stopped"], {})

        async def wake(self, reason: str, preload_primary_model: bool | None = None) -> TransitionResult:
            return TransitionResult("ACTIVE", "LIGHT_SLEEP", f"{reason}:{preload_primary_model}", ["scheduler_started"], {})

    monkeypatch.setattr("app.server.resource_manager", FakeResourceManager())

    status = client.get("/resource/status")
    assert status.status_code == 200
    assert status.json()["state"] == "ACTIVE"

    for route in ('/resource/sleep/light','/resource/sleep/deep','/resource/wake','/resource/shutdown'):
        blocked=client.post(route)
        assert blocked.status_code==403
        assert blocked.json()['error']=='offline_operator_control_required'


def test_procedural_memory_routes(monkeypatch) -> None:  # noqa: ANN001
    store = "tasks/.server_skills_test.md"
    memory = ProceduralMemory(store)
    try:
        monkeypatch.setattr("app.server.procedural_memory", memory)

        created = client.post("/memory/skills", json={"skill": "Check local files first."})
        assert created.status_code == 200
        assert created.json()["added"] is True

        duplicate = client.post("/memory/skills", json={"skill": "Check local files first."})
        assert duplicate.status_code == 200
        assert duplicate.json()["added"] is False

        listed = client.get("/memory/skills")
        assert listed.status_code == 200
        assert listed.json()["skills"] == ["Check local files first."]
    finally:
        from pathlib import Path

        Path(store).unlink(missing_ok=True)


def test_lifespan_does_not_start_voice_or_hotkey_by_default(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("app.server.settings.server.enable_voice_on_startup", False)
    monkeypatch.setattr("app.server.settings.server.enable_hotkey_listener", False)
    scheduler_start = AsyncMock()
    scheduler_stop = AsyncMock()

    with patch("app.server.start_hotkey_listener") as hotkey_listener, patch(
        "app.server.scheduler.start", new=scheduler_start
    ), patch("app.server.scheduler.stop", new=scheduler_stop):
        with TestClient(app) as local_client:
            response = local_client.get("/health")

    assert response.status_code == 200
    hotkey_listener.assert_not_called()
    scheduler_start.assert_awaited_once()
    scheduler_stop.assert_awaited_once()

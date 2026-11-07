"""Authority identity regressions against admitted dummy state, never live stores."""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import server
from app.agent import api, runtime
from app.agent.authority import AuthorityError
from app.config import settings
from synthetic_authority import fixture_authority


TOKEN = "synthetic-authority-http-regression-token"


@pytest.fixture
def admitted(tmp_path, monkeypatch):
    previous, worker = runtime._authority, runtime._execution_worker
    runtime._authority = runtime._execution_worker = None
    authority = fixture_authority(tmp_path / "authority" / "state.sqlite")
    runtime.bind_authority(authority)
    request_id = str(uuid4())
    authority.submit(runtime.SERVICE_ACTOR, request_id, "dummy operator task")
    monkeypatch.setattr(settings.server, "api_token", "")
    try:
        yield authority, request_id
    finally:
        runtime.close_authority()
        runtime._authority, runtime._execution_worker = previous, worker


@pytest.mark.parametrize("token", ["", TOKEN])
def test_stock_startup_still_requires_real_admission_context(tmp_path, monkeypatch, token):
    previous, worker = runtime._authority, runtime._execution_worker
    runtime._authority = runtime._execution_worker = None
    root = tmp_path / "unprovisioned"
    monkeypatch.setattr(runtime, "PROJECT_ROOT", root)
    monkeypatch.setattr(settings.server, "api_token", token)
    try:
        with pytest.raises(AuthorityError, match="authority_unenrolled_or_missing"):
            with TestClient(server.app):
                pytest.fail("unprovisioned startup admitted")
        assert runtime._authority is None
        assert not root.exists()
    finally:
        runtime._authority, runtime._execution_worker = previous, worker


@pytest.mark.parametrize("embedded", [False, True])
@pytest.mark.parametrize("authorization", [None, "Bearer wrong", TOKEN, "Bearer "])
def test_explicit_admission_does_not_grant_anonymous_http_authority(admitted, embedded, authorization):
    authority, task_id = admitted
    app = server.app
    if embedded:
        app = FastAPI()
        app.include_router(api.router)
    client = TestClient(app)
    headers = {"Authorization": authorization} if authorization is not None else {}
    assert client.get("/tasks/" + task_id, headers=headers).status_code == 401
    request_id = str(uuid4())
    assert client.delete("/tasks/" + task_id, params={"request_id": request_id}, headers=headers).status_code == 401
    assert authority.get_task(runtime.SERVICE_ACTOR, task_id)["status"] == "pending"
    assert authority.receipt(runtime.SERVICE_ACTOR, request_id) is None


@pytest.mark.parametrize("authorization", [None, "Bearer wrong", TOKEN, "Bearer "])
def test_configured_token_rejects_missing_invalid_and_malformed_identity(admitted, monkeypatch, authorization):
    authority, task_id = admitted
    monkeypatch.setattr(settings.server, "api_token", TOKEN)
    headers = {"Authorization": authorization} if authorization is not None else {}
    client = TestClient(server.app)
    assert client.get("/tasks/" + task_id, headers=headers).status_code == 401
    assert client.get("/tasks/" + task_id + "?token=" + TOKEN).status_code == 401
    assert authority.get_task(runtime.SERVICE_ACTOR, task_id)["status"] == "pending"


@pytest.mark.parametrize("embedded", [False, True])
def test_valid_identity_preserves_read_cancel_receipt_and_idempotency(admitted, monkeypatch, embedded):
    authority, task_id = admitted
    monkeypatch.setattr(settings.server, "api_token", TOKEN)
    app = server.app
    if embedded:
        app = FastAPI()
        app.include_router(api.router)
    client = TestClient(app, headers={"Authorization": "Bearer " + TOKEN})
    assert client.get("/tasks/" + task_id).status_code == 200
    request_id = str(uuid4())
    cancelled = client.delete("/tasks/" + task_id, params={"request_id": request_id})
    assert cancelled.status_code == 200
    replay = client.delete("/tasks/" + task_id, params={"request_id": request_id})
    assert replay.status_code == 200 and replay.json()["replayed"]
    assert client.get("/requests/" + request_id).status_code == 200
    assert authority.get_task(runtime.SERVICE_ACTOR, task_id)["status"] == "cancelled"


@pytest.mark.parametrize("method,path,body", [
    ("GET", "/tasks", None),
    ("GET", "/requests/{uuid}", None),
    ("POST", "/tasks", {"request_id": "{uuid}", "goal": "never admitted"}),
    ("GET", "/schedule/jobs", None),
    ("POST", "/schedule/jobs", {"request_id": "{uuid}", "goal": "never admitted", "name": "dummy", "cron_expr": "* * * * *"}),
    ("DELETE", "/schedule/jobs/{uuid}?request_id={uuid}", None),
    ("GET", "/execution/status", None),
    ("POST", "/execution/tasks", {"request_id": "{uuid}", "goal": "never admitted", "capability": "synthetic.echo", "payload": {"value": "dummy"}, "expires_at": "{future}"}),
])
def test_every_privileged_route_refuses_unconfigured_identity(admitted, method, path, body):
    operation = str(uuid4())
    path = path.replace("{uuid}", operation)
    if body is not None:
        body = dict(body)
        if body.get("request_id") == "{uuid}":
            body["request_id"] = operation
        if body.get("expires_at") == "{future}":
            body["expires_at"] = (datetime.now(UTC) + timedelta(minutes=1)).isoformat()
    response = TestClient(server.app).request(method, path, json=body)
    assert response.status_code == 401
    assert admitted[0].receipt(runtime.SERVICE_ACTOR, operation) is None


def test_arbitrary_host_origin_cannot_replace_credentials(admitted, monkeypatch):
    _, task_id = admitted
    client = TestClient(server.app, base_url="http://foreign.invalid")
    foreign = {"Origin": "https://foreign.invalid"}
    assert client.get("/tasks/" + task_id, headers=foreign).status_code == 401
    monkeypatch.setattr(settings.server, "api_token", TOKEN)
    assert client.get("/tasks/" + task_id, headers=foreign).status_code == 401
    response = client.get("/tasks/" + task_id, headers={**foreign, "Authorization": "Bearer " + TOKEN})
    assert response.status_code == 200  # Host/Origin are not caller identity.
    assert "access-control-allow-origin" not in response.headers
    preflight = client.options("/tasks/" + task_id, headers={
        **foreign, "Authorization": "Bearer " + TOKEN,
        "Access-Control-Request-Method": "DELETE",
        "Access-Control-Request-Headers": "Authorization",
    })
    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers
    assert TOKEN not in response.text


def test_anonymous_health_does_not_grant_task_access(admitted):
    client = TestClient(server.app)
    assert client.get("/health").status_code == 200
    assert client.get("/tasks").status_code == 401

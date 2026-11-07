"""UE5 protocol and lifetime regressions using dummy ASGI connections only."""
import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from app import server
from app.comms import ue5_bridge
from app.config import settings


TOKEN = "synthetic-ue5-regression-token"


@pytest.fixture
def manager(monkeypatch):
    manager = ue5_bridge.UE5ConnectionManager()
    monkeypatch.setattr(ue5_bridge, "ue5_manager", manager)
    monkeypatch.setattr(settings.server, "api_token", TOKEN)
    return manager


async def exercise(frames, *, before_receive=None, on_send=None, endpoint=None, path="/ue5"):
    """Use Starlette's actual protocol state machine, without a listener."""
    incoming = iter([{"type": "websocket.connect"}, *frames])
    sent = []

    async def receive():
        item = next(incoming)
        if before_receive is not None:
            await before_receive(item)
        if isinstance(item, BaseException):
            raise item
        return item

    async def send(message):
        sent.append(message)
        if on_send is not None:
            await on_send(message)

    ws = WebSocket(
        {
            "type": "websocket",
            "path": path,
            "headers": [(b"authorization", ("Bearer " + TOKEN).encode())],
            "client": ("127.0.0.1", 12345),
            "query_string": b"",
        },
        receive,
        send,
    )
    await (endpoint or server.ue5_endpoint)(ws)
    return ws, sent


@pytest.mark.parametrize("code", [1000, 1006])
def test_valid_text_and_peer_disconnect_cleanup(manager, code):
    ws, sent = asyncio.run(exercise([
        {"type": "websocket.receive", "text": '{"type":"client-ready"}'},
        {"type": "websocket.disconnect", "code": code},
    ]))
    assert len(sent) == 1 and sent[0]["type"] == "websocket.accept"
    assert manager.active == []
    manager.disconnect(ws)
    manager.disconnect(ws)
    assert manager.active == []


@pytest.mark.parametrize("payload", [b"", b"x", b'\xff\x00'])
def test_binary_frames_close_cleanly(manager, payload):
    _, sent = asyncio.run(exercise([{"type": "websocket.receive", "bytes": payload}]))
    assert sent[-1]["type"] == "websocket.close"
    assert sent[-1]["code"] == 1003
    assert manager.active == []


@pytest.mark.parametrize("frame", [
    {"type": "websocket.receive"},
    {"type": "websocket.receive", "text": 42},
    {"type": "websocket.receive", "text": None},
])
def test_malformed_frames_close_cleanly(manager, frame):
    _, sent = asyncio.run(exercise([frame]))
    assert sent[-1]["type"] == "websocket.close"
    assert sent[-1]["code"] == 1003
    assert manager.active == []


@pytest.mark.parametrize("text", ["x" * 8193, "é" * 4097])
def test_oversized_text_is_bounded(manager, text):
    _, sent = asyncio.run(exercise([{"type": "websocket.receive", "text": text}]))
    assert sent[-1]["code"] == 1009
    assert manager.active == []


def test_valid_utf8_frame_at_byte_limit_is_preserved(manager):
    _, sent = asyncio.run(exercise([
        {"type": "websocket.receive", "text": "é" * 4096},
        {"type": "websocket.disconnect", "code": 1000},
    ]))
    assert len(sent) == 1 and sent[0]["type"] == "websocket.accept"
    assert manager.active == []


@pytest.mark.parametrize("failure", [asyncio.CancelledError, RuntimeError])
def test_cancellation_and_receive_exception_always_cleanup(manager, failure):
    with pytest.raises(failure):
        asyncio.run(exercise([failure("synthetic failure")]))
    assert manager.active == []


def test_connection_registration_failure_always_cleanup(manager, monkeypatch):
    original = manager.connect

    async def interrupted(ws):
        await original(ws)
        raise RuntimeError("synthetic registration failure")

    monkeypatch.setattr(manager, "connect", interrupted)
    with pytest.raises(RuntimeError, match="synthetic registration failure"):
        asyncio.run(exercise([]))
    assert manager.active == []


@pytest.mark.parametrize("event", ["ue5_ws_connect", "ue5_ws_disconnect"])
def test_audit_exception_cannot_orphan_connection(manager, monkeypatch, event):
    def fail(which, data):
        if which == event:
            raise RuntimeError("synthetic audit failure")

    monkeypatch.setattr(server.audit, "log", fail)
    with pytest.raises(RuntimeError, match="synthetic audit failure"):
        asyncio.run(exercise([{"type": "websocket.disconnect", "code": 1000}]))
    assert manager.active == []


def test_valid_connection_preserves_broadcast_and_other_entries(manager):
    other = object()
    manager.active.append(other)

    async def broadcast(item):
        if item.get("type") == "websocket.receive":
            # Keep the independent entry out of this broadcast only.
            manager.active.remove(other)
            await manager.broadcast({"type": "emotion", "emotion": "neutral"})
            manager.active.append(other)

    ws, sent = asyncio.run(exercise([
        {"type": "websocket.receive", "text": "client ready"},
        {"type": "websocket.disconnect", "code": 1000},
    ], before_receive=broadcast))
    assert json.loads(sent[1]["text"]) == {"type": "emotion", "emotion": "neutral"}
    manager.disconnect(ws)
    assert manager.active == [other]
    manager.active.clear()


def test_repeated_hostile_sessions_leave_no_persistent_entries_or_secrets(manager, monkeypatch):
    events = []
    monkeypatch.setattr(server.audit, "log", lambda event, data: events.append((event, data)))
    client = TestClient(server.app)
    for _ in range(32):
        with client.websocket_connect("/ue5", headers={"Authorization": "Bearer " + TOKEN}) as ws:
            ws.send_bytes(b"x")
            with pytest.raises(WebSocketDisconnect) as closed:
                ws.receive_text()
            assert closed.value.code == 1003
        assert manager.active == []
    assert TOKEN not in repr(events)
    assert "authorization" not in repr(events).lower()


def test_cancellation_during_accept_releases_pending_capacity(manager):
    async def run():
        accepting = asyncio.Event()

        async def receive():
            return {"type": "websocket.connect"}

        async def send(message):
            accepting.set()
            await asyncio.Future()

        ws = WebSocket({
            "type": "websocket", "path": "/ue5",
            "headers": [(b"authorization", ("Bearer " + TOKEN).encode())],
            "client": ("127.0.0.1", 12345),
        }, receive, send)
        task = asyncio.create_task(server.ue5_endpoint(ws))
        await asyncio.wait_for(accepting.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert manager.active == []
        assert manager._accepting == 0

    asyncio.run(run())


def test_connection_bound_refuses_growth_and_reclaims_capacity(manager):
    class Client:
        def __init__(self):
            self.closed = None

        async def accept(self):
            pass

        async def close(self, **kwargs):
            self.closed = kwargs

    async def run():
        accepted = [Client() for _ in range(32)]
        for client in accepted:
            assert await manager.connect(client)
        refused = Client()
        assert await manager.connect(refused) is False
        assert refused.closed["code"] == 1008
        assert len(manager.active) == 32
        for client in accepted:
            manager.disconnect(client)
            manager.disconnect(client)
        assert manager.active == [] and manager._accepting == 0
        assert await manager.connect(refused)
        manager.disconnect(refused)
        assert manager.active == []

    asyncio.run(run())


def test_slow_close_cannot_retain_registration(manager, monkeypatch):
    monkeypatch.setattr(manager, "send_timeout_seconds", 0.01)

    async def slow(message):
        if message["type"] == "websocket.close":
            await asyncio.Future()

    _, sent = asyncio.run(exercise([
        {"type": "websocket.receive", "bytes": b"x"},
    ], on_send=slow))
    assert sent[-1]["code"] == 1003
    assert manager.active == []


def test_close_exception_cannot_retain_registration(manager):
    async def broken(message):
        if message["type"] == "websocket.close":
            raise RuntimeError("synthetic close failure")

    asyncio.run(exercise([
        {"type": "websocket.receive", "bytes": b"x"},
    ], on_send=broken))
    assert manager.active == []


@pytest.mark.parametrize("stage", ["registration", "audit"])
def test_sibling_chat_registration_cleanup_uses_same_lifetime_scope(manager, monkeypatch, stage):
    chat = server.ConnectionManager()
    monkeypatch.setattr(server, "manager", chat)
    if stage == "registration":
        original = chat.connect

        async def interrupted(ws):
            await original(ws)
            raise RuntimeError("synthetic registration failure")

        monkeypatch.setattr(chat, "connect", interrupted)
    else:
        def audit(event, data):
            if event == "ws_connect":
                raise RuntimeError("synthetic audit failure")

        monkeypatch.setattr(server.audit, "log", audit)
    with pytest.raises(RuntimeError, match="synthetic"):
        asyncio.run(exercise([], endpoint=server.ws_endpoint, path=settings.server.websocket_path))
    assert chat.active == []

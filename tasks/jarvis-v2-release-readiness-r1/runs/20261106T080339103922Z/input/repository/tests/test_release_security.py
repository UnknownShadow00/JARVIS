"""Release boundary regressions; disposable state, native IPC/ASGI only."""
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.agent import runtime
from app.agent.api import router
from app.agent.authority import Authority, AuthorityError
from app.agent.storage_paths import StorageAncestry
from app.agent.ledger import private_directory
from app.config import settings
from app import server
from app.comms.ue5_bridge import UE5ConnectionManager, ue5_manager
from synthetic_authority import fixture_authority


@pytest.fixture
def admitted(tmp_path, monkeypatch):
    previous,worker=runtime._authority,runtime._execution_worker
    runtime._authority=runtime._execution_worker=None
    a=fixture_authority(tmp_path/'authority/state.sqlite')
    runtime.bind_authority(a)
    monkeypatch.setattr(settings.server,'api_token','synthetic-release-client')
    try:yield a
    finally:
        runtime.close_authority();runtime._authority=previous;runtime._execution_worker=worker


@pytest.mark.parametrize('path,method',[
    ('/tasks','GET'),('/tasks','POST'),('/tasks/'+str(uuid.uuid4()),'GET'),
    ('/tasks/'+str(uuid.uuid4())+'?request_id='+str(uuid.uuid4()),'DELETE'),
    ('/requests/'+str(uuid.uuid4()),'GET'),('/schedule/jobs','GET'),('/schedule/jobs','POST'),
    ('/schedule/jobs/'+str(uuid.uuid4())+'?request_id='+str(uuid.uuid4()),'DELETE'),
    ('/execution/tasks','POST'),('/execution/status','GET'),('/operator/diagnostics','GET')])
def test_empty_token_authority_access_refused_even_embedded(admitted,monkeypatch,path,method):
    monkeypatch.setattr(settings.server,'api_token','')
    app=FastAPI();app.include_router(router)
    before=admitted._conn.total_changes
    response=TestClient(app).request(method,path,json={'request_id':str(uuid.uuid4()),'goal':'held'})
    assert response.status_code==401
    assert admitted._conn.total_changes==before


@pytest.mark.asyncio
async def test_baseline_anonymous_read_cancel_reproduced_then_fixed(admitted,monkeypatch):
    # Original source definitions, not a fabricated auth stub. Same-process
    # admitted fixture only: no claim of deployed or cross-UID exploitation.
    path=Path('/input/baseline_api.py')
    if not path.exists():pytest.skip('retained baseline supplied by release cage')
    spec=importlib.util.spec_from_file_location('baseline_authority_routes',path)
    baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
    old=FastAPI();old.include_router(baseline.router)
    key=str(uuid.uuid4());task=admitted.submit(runtime.SERVICE_ACTOR,key,'dummy held task')['result']
    monkeypatch.setattr(settings.server,'api_token','')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=old),base_url='http://synthetic') as c:
        assert (await c.get('/tasks/'+key)).status_code==200
        cancel=await c.delete('/tasks/'+key,params={'request_id':str(uuid.uuid4())})
        assert cancel.status_code==200 and cancel.json()['result']['status']=='cancelled'
    fresh=FastAPI();fresh.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=fresh),base_url='http://synthetic') as c:
        assert (await c.get('/tasks/'+key)).status_code==401
        assert (await c.delete('/tasks/'+key,params={'request_id':str(uuid.uuid4())})).status_code==401
        monkeypatch.setattr(settings.server,'api_token','synthetic-release-client')
        assert (await c.get('/tasks/'+key)).status_code==401
        c.headers['Authorization']='Bearer synthetic-release-client'
        assert (await c.get('/tasks/'+key)).json()['status']=='cancelled'


@pytest.mark.parametrize('path',['/ws','/ue5'])
@pytest.mark.parametrize('payload',[b'x','x'*8193])
def test_websocket_binary_and_oversize_cleanup(admitted,path,payload):
    manager=server.manager if path=='/ws' else ue5_manager
    before=len(manager.active)
    with TestClient(server.app).websocket_connect(path,headers={'Authorization':'Bearer synthetic-release-client'}) as c:
        if isinstance(payload,bytes):c.send_bytes(payload)
        else:c.send_text(payload)
        with pytest.raises(WebSocketDisconnect) as e:c.receive_json()
        assert e.value.code in (1003,1008,1009)
    assert len(manager.active)==before


@pytest.mark.asyncio
@pytest.mark.parametrize('manager_type',[server.ConnectionManager,UE5ConnectionManager])
async def test_connection_accept_bound_and_cancellation_cleanup(manager_type):
    manager=manager_type();gate=asyncio.Event();entered=asyncio.Event()
    class Peer:
        async def accept(self):entered.set();await gate.wait()
        async def close(self,**kwargs):self.closed=kwargs
    waiting=Peer();task=asyncio.create_task(manager.connect(waiting));await entered.wait()
    manager.active.extend([object()]*31)
    refused=Peer();assert await manager.connect(refused) is False
    assert refused.closed['code']==1008
    task.cancel()
    with pytest.raises(asyncio.CancelledError):await task
    assert manager._accepting==0 and waiting not in manager.active


@pytest.mark.asyncio
@pytest.mark.parametrize('failure',[RuntimeError('synthetic receive failure'),asyncio.CancelledError()])
async def test_ue5_all_exit_cleanup(admitted,monkeypatch,failure):
    monkeypatch.setattr(server,'_reject_unauthorized_websocket',AsyncMock(return_value=False))
    peer=SimpleNamespace(accept=AsyncMock(),receive=AsyncMock(side_effect=failure),client='synthetic')
    before=len(ue5_manager.active)
    with pytest.raises(type(failure)):await server.ue5_endpoint(peer)
    assert len(ue5_manager.active)==before


@pytest.mark.parametrize('mode',[0o722,0o770,0o777])
def test_writable_ancestor_refused_before_sqlite(tmp_path,mode):
    parent=tmp_path/'untrusted';parent.mkdir(mode=0o700)
    child=parent/'private';child.mkdir(mode=0o700)
    db=child/'state.sqlite';db.write_bytes(b'synthetic-not-a-store');db.chmod(0o600)
    parent.chmod(mode)
    with pytest.raises(AuthorityError,match='unsafe_storage_ancestor'):private_directory(child)
    with pytest.raises(AuthorityError,match='unsafe_storage_ancestor'):Authority(db)
    assert not db.with_suffix('.sqlite.writer.lock').exists()


def test_component_symlink_refused(tmp_path):
    original=tmp_path/'original';original.mkdir(mode=0o700)
    link=tmp_path/'alias';link.symlink_to(original,target_is_directory=True)
    with pytest.raises(AuthorityError,match='unsafe_storage_ancestor'):StorageAncestry(link)


def test_parent_replaced_with_same_leaf_inodes_fences_writer(tmp_path):
    parent=tmp_path/'parent';a=fixture_authority(parent/'private/state.sqlite')
    leaf=a.path.parent
    parent.rename(tmp_path/'saved');parent.mkdir(mode=0o700)
    (tmp_path/'saved/private').rename(leaf)
    try:
        with pytest.raises(AuthorityError,match='storage_ancestor_replaced'):a.submit(runtime.SERVICE_ACTOR,str(uuid.uuid4()),'must not write')
        assert a._poisoned
    finally:a.close()

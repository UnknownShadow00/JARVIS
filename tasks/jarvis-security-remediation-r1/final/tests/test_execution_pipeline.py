"""Offline pipeline with actual SQLite, receipts, API and independent processes."""
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid

import httpx
import pytest

from app.agent.authority import Actor, Authority, AuthorityError
from synthetic_authority import fixture_authority as Authority
from app.agent.execution import (DisabledExecutor, ExecutionPipeline, ExecutionWorker,
                                 ExecutorRegistry, SimulatedPolicy, SyntheticExecutor, phase_id)
from app.agent import runtime
from app.config import settings

ACTOR = runtime.SERVICE_ACTOR
API_HEADERS = {"Authorization": "Bearer synthetic-execution-api-regression"}


@pytest.fixture(autouse=True)
def authenticated_api_identity(monkeypatch):
    monkeypatch.setattr(settings.server, 'api_token', 'synthetic-execution-api-regression')


def key():
    return str(uuid.uuid4())


@pytest.fixture
def env(tmp_path):
    a = Authority(tmp_path / 'state' / 'queue.sqlite', allow_simulation=True)
    p = ExecutionPipeline(a, SimulatedPolicy(ACTOR.scope), enabled=True)
    yield a, p
    a.close()


def submit(p, **changes):
    body = dict(request_id=key(), goal='offline echo', capability='synthetic.echo',
                payload={'value': 'hello'}, expires_at=(datetime.now(UTC) + timedelta(minutes=5)).isoformat(), timeout_seconds=10)
    body.update(changes)
    return p.submit(ACTOR, **body)


def task(a):
    return a.list_tasks(ACTOR)[-1]


def test_complete_pipeline_and_stable_operation_identity(env):
    a, p = env
    admitted = submit(p)
    op = admitted['request_id']
    assert admitted['result']['task_id'] == op
    result = p.run_once(ACTOR)
    assert result['result']['status'] == 'simulated_completed'
    assert task(a)['result']['output'] == 'hello'
    assert task(a)['outbox_state'] == 'simulated_completed'
    assert p.run_once(ACTOR) is None
    assert a.receipt(ACTOR, phase_id(op, 'record'))['result']['operation_id'] == op
    assert a.receipt(ACTOR, phase_id(op, 'publish'))['result']['task_id'] == op
    assert a._conn.execute("SELECT COUNT(*) FROM events WHERE request_id=?", (phase_id(op, 'publish'),)).fetchone()[0] == 1


@pytest.mark.parametrize('capability', ['shell.exec', 'synthetic.fail', 'proxmox.console', 'synthetic.echo; id'])
def test_policy_denies_without_dispatch(env, capability):
    a, p = env
    result = submit(p, capability=capability)
    assert result['result']['status'] == 'denied'
    assert result['result']['execution']['authorization']['allowed'] is False
    assert p.run_once(ACTOR) is None
    assert a._conn.execute("SELECT COUNT(*) FROM records WHERE kind='execution_evidence'").fetchone()[0] == 0


def test_scope_boundary(env):
    a, p = env
    result = p.submit(Actor('untrusted'), key(), 'x', 'synthetic.echo', {'value': 'x'}, (datetime.now(UTC)+timedelta(minutes=1)).isoformat())
    assert result['result']['status'] == 'denied'
    with pytest.raises(AuthorityError, match='not_found'):
        p._publish(ACTOR, result['request_id'])


@pytest.mark.parametrize('changes,code', [
    ({'request_id': 'short'}, 'invalid_identifier'),
    ({'request_id': '00000000-0000-0000-0000-000000000000'}, 'invalid_identifier'),
    ({'payload': {'value': 'x', 'command': 'id'}}, 'invalid_execution_payload'),
    ({'payload': {'value': True}}, 'invalid_text'),
    ({'payload': {'value': 'x'*8193}}, 'invalid_text'),
    ({'timeout_seconds': True}, 'invalid_execution_timeout'),
    ({'timeout_seconds': 0}, 'invalid_execution_timeout'),
    ({'timeout_seconds': 61}, 'invalid_execution_timeout'),
    ({'expires_at': '2000-01-01T00:00:00+00:00'}, 'stale_execution_request'),
    ({'expires_at': '2099-01-01T00:00:00+00:00'}, 'stale_execution_request'),
    ({'expires_at': '2026-11-05T00:00:00'}, 'invalid_time'),
])
def test_invalid_admission_is_atomic(env, changes, code):
    a, p = env
    with pytest.raises(AuthorityError, match=code):
        submit(p, **changes)
    assert a.list_tasks(ACTOR) == []


def test_replay_conflict_and_expired_replay(env):
    a, p = env
    op = key()
    expiry = (datetime.now(UTC)+timedelta(minutes=1)).isoformat()
    first = submit(p, request_id=op, expires_at=expiry)
    p._clock = lambda: datetime.now(UTC)+timedelta(hours=2)
    second = submit(p, request_id=op, expires_at=expiry)
    assert second['replayed'] and second['result'] == first['result']
    with pytest.raises(AuthorityError, match='request_conflict'):
        submit(p, request_id=op, expires_at=expiry, payload={'value': 'changed'})
    assert len(a.list_tasks(ACTOR)) == 1


def test_disabled_and_real_registration(tmp_path):
    a = Authority(tmp_path/'state'/'db')
    try:
        with pytest.raises(AuthorityError, match='execution_disabled'):
            ExecutionPipeline(a, SimulatedPolicy(ACTOR.scope), enabled=True)
        with pytest.raises(AuthorityError, match='execution_disabled'):
            ExecutorRegistry().register(SyntheticExecutor())
        with pytest.raises(AuthorityError, match='real_execution_disabled'):
            ExecutorRegistry(enabled=True).register(DisabledExecutor())
        with pytest.raises(AuthorityError, match='real_execution_disabled'):
            DisabledExecutor().execute(key(), {})
        class PretendSynthetic(SyntheticExecutor):
            pass
        with pytest.raises(AuthorityError, match='real_execution_disabled'):
            ExecutorRegistry(enabled=True).register(PretendSynthetic())
    finally:
        a.close()


def test_revoked_policy_checked_at_dispatch(env):
    a, p = env
    submit(p)
    p.policy = SimulatedPolicy(ACTOR.scope, frozenset(), revision='revoked')
    assert p.run_once(ACTOR)['result']['status'] == 'denied'
    assert task(a)['result'] is None


def test_cancellation_before_dispatch(env):
    a, p = env
    op = submit(p)['request_id']
    a.cancel(ACTOR, key(), op)
    assert p.run_once(ACTOR) is None
    assert task(a)['status'] == 'cancelled'


def test_cancellation_after_claim_before_dispatch(env):
    a, p = env
    op = submit(p)['request_id']
    p._fault = lambda stage: a.cancel(ACTOR, key(), op) if stage == 'after_claim' else None
    assert p.run_once(ACTOR)['result']['status'] == 'cancelled'
    assert a.receipt(ACTOR, phase_id(op, 'record')) is None


def test_cancellation_after_result_preserves_completion(env):
    a, p = env
    op = submit(p)['request_id']
    p._fault = lambda stage: a.cancel(ACTOR, key(), op) if stage == 'after_record' else None
    p.run_once(ACTOR)
    assert task(a)['status'] == 'simulated_completed'
    assert task(a)['cancel_requested'] is True


def test_expiry_before_claim(env):
    a, p = env
    submit(p)
    p._clock = lambda: datetime.now(UTC)+timedelta(hours=1)
    assert p.run_once(ACTOR)['result']['status'] == 'timed_out'


def test_timeout_after_dispatch_stays_unknown(env):
    a, p = env
    submit(p)
    def fault(stage):
        if stage == 'after_execute':
            p._clock = lambda: datetime.now(UTC)+timedelta(hours=1)
    p._fault = fault
    assert p.run_once(ACTOR)['result']['status'] == 'unknown'
    assert p.reconcile(ACTOR) == []
    assert p.run_once(ACTOR) is None


def test_failed_dispatch_stays_unknown(env, monkeypatch):
    a, p = env
    submit(p)
    def broken(*args):
        raise RuntimeError('private failure detail')
    monkeypatch.setattr(SyntheticExecutor, 'execute', broken)
    p.run_once(ACTOR)
    assert task(a)['status'] == 'unknown'
    assert 'private' not in json.dumps(task(a))
    assert p.run_once(ACTOR) is None


@pytest.mark.parametrize('bad', [None, {}, {'operation_id': 'forged'}, {'status': 'completed', 'output': 'forged'}, {'output': 'x'*1048577}])
def test_untrusted_response_fails_closed(env, bad):
    a, p = env
    submit(p)
    p.registry._executor.execute = lambda *args: bad
    p.run_once(ACTOR)
    assert task(a)['status'] == 'unknown'
    assert task(a)['result'] is None


def test_synthetic_failure_and_hash(env):
    a, p = env
    p.policy = SimulatedPolicy(ACTOR.scope, frozenset({'synthetic.fail','synthetic.sha256'}))
    submit(p, capability='synthetic.fail')
    assert p.run_once(ACTOR)['result']['status'] == 'simulated_failed'
    submit(p, capability='synthetic.sha256')
    assert p.run_once(ACTOR)['result']['result']['output'] == '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'


def test_capacity_replay_and_release(env):
    a, p = env
    p.max_pending = 1
    first = submit(p)
    with pytest.raises(AuthorityError, match='queue_capacity_exceeded'):
        submit(p)
    p.run_once(ACTOR)
    submit(p)
    assert len(a.list_tasks(ACTOR)) == 2


def test_audit_failure_prevents_dispatch(env):
    a, p = env
    submit(p)
    a._conn.execute("CREATE TRIGGER reject_audit BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'audit unavailable'); END")
    with pytest.raises(AuthorityError, match='storage_unknown_reconcile'):
        p.run_once(ACTOR)
    assert a._conn.execute("SELECT COUNT(*) FROM records WHERE kind='execution_evidence'").fetchone()[0] == 0
    assert a._conn.execute("SELECT state FROM outbox").fetchone()[0] == 'held'


def test_lock_contention_poison_and_reopen(env):
    a, p = env
    op = submit(p)['request_id']
    other = sqlite3.connect(a.path, isolation_level=None)
    try:
        other.execute('BEGIN IMMEDIATE')
        with pytest.raises(AuthorityError, match='storage_unknown_reconcile'):
            p.run_once(ACTOR)
    finally:
        other.execute('ROLLBACK')
        other.close()
    with pytest.raises(AuthorityError, match='authority_unavailable'):
        p.run_once(ACTOR)
    a.close()
    recovered = Authority(a.path, allow_simulation=True)
    try:
        assert recovered.list_tasks(ACTOR)[0]['status'] == 'pending'
        new = ExecutionPipeline(recovered, p.policy, enabled=True)
        assert new.run_once(ACTOR)['result']['task_id'] == op
    finally:
        recovered.close()


def test_stale_owner_fenced(env):
    a, p = env
    submit(p)
    a._conn.execute('UPDATE ownership SET generation=generation+1')
    with pytest.raises(AuthorityError, match='owner_fenced'):
        p.run_once(ACTOR)
    assert a._conn.execute("SELECT COUNT(*) FROM records WHERE kind='execution_evidence'").fetchone()[0] == 0


@pytest.mark.asyncio
async def test_real_api_worker_receipts_and_restart(env):
    from fastapi import FastAPI
    from app.agent.api import router
    a, p = env
    runtime.bind_authority(a)
    worker = runtime.bind_offline_execution(p.policy)
    app = FastAPI()
    app.include_router(router)
    try:
        await worker.start()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://synthetic', headers=API_HEADERS) as client:
            op = key()
            body = dict(request_id=op, goal='API pipeline', capability='synthetic.echo', payload={'value': 'through API'}, expires_at=(datetime.now(UTC)+timedelta(minutes=1)).isoformat())
            admitted = await client.post('/execution/tasks', json=body)
            assert admitted.status_code == 200
            for _ in range(100):
                current = (await client.get('/tasks/'+op)).json()
                if current['status'] == 'simulated_completed':
                    break
                await __import__('asyncio').sleep(.01)
            assert current['result']['output'] == 'through API'
            assert (await client.post('/execution/tasks', json=body)).json()['replayed']
            assert (await client.post('/execution/tasks', json={**body, 'goal':'conflict'})).status_code == 409
            assert (await client.patch('/tasks/'+op, json={'status':'completed'})).status_code == 405
            assert (await client.post('/execution/tasks', json={**body, 'scope':'root'})).status_code == 422
            assert (await client.post('/execution/tasks', json={**body, 'timeout_seconds':True})).status_code == 422
            receipt = (await client.get('/requests/'+phase_id(op, 'publish'))).json()
            assert receipt['result']['task_id'] == op
            assert (await client.get('/execution/status')).json()['real_execution_enabled'] is False
    finally:
        await worker.stop()
        runtime.close_authority()
    reopened = Authority(a.path, allow_simulation=True)
    try:
        assert reopened.list_tasks(ACTOR)[0]['status'] == 'simulated_completed'
    finally:
        reopened.close()


@pytest.mark.asyncio
async def test_worker_failure_is_visible_and_stops(env):
    a, p = env
    submit(p)
    worker = ExecutionWorker(p, ACTOR)
    a._poisoned = True
    with pytest.raises(AuthorityError, match='authority_unavailable'):
        await worker.start()
    a._poisoned = False
    await worker.start()
    a._poisoned = True
    await __import__('asyncio').sleep(.03)
    assert not worker.readiness()['execution_worker_ready']
    assert worker.failure == 'execution_worker_reconcile_required'
    await worker.stop()


@pytest.mark.parametrize('stage', ['after_claim', 'after_execute', 'record_before_commit', 'after_record', 'publish_before_commit', 'after_publish'])
def test_sigkill_independent_process_recovery(tmp_path, stage):
    if not Path('/input/source').is_dir():
        pytest.skip('run with the network-isolated task runner')
    state = tmp_path/'process-state'
    state.mkdir(mode=0o700)
    db, ready = state/'queue.sqlite', state/'ready'
    op = key()
    helper = Path(__file__).with_name('execution_process_actor.py')
    with (state/'stdout').open('w') as out, (state/'stderr').open('w') as err:
        child = subprocess.Popen([sys.executable, '-I', '-B', '-S', str(helper), str(db), str(ready), op, stage], stdin=subprocess.DEVNULL, stdout=out, stderr=err, close_fds=True, env={'LANG':'C.UTF-8'})
        try:
            deadline = time.monotonic()+4
            while not ready.exists() and child.poll() is None and time.monotonic()<deadline:
                time.sleep(.01)
            assert ready.exists(), (state/'stderr').read_text()
            with pytest.raises(AuthorityError, match='owner_busy'):
                Authority(db)
            child.kill()
            child.wait(timeout=1)
            assert child.returncode < 0
        finally:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=1)
    a = Authority(db, allow_simulation=True)
    try:
        p = ExecutionPipeline(a, SimulatedPolicy(ACTOR.scope), enabled=True)
        assert task(a)['status'] == ('simulated_completed' if stage == 'after_publish' else 'unknown')
        assert p.run_once(ACTOR) is None
        results = p.reconcile(ACTOR)
        if stage in {'after_record','publish_before_commit','after_publish'}:
            assert task(a)['status'] == 'simulated_completed'
            assert task(a)['result']['output'] == 'crash marker'
            assert len(results) == (1 if stage in {'after_record','publish_before_commit'} else 0)
        else:
            assert task(a)['status'] == 'unknown'
            assert results == []
        assert p.run_once(ACTOR) is None
        assert a._conn.execute("SELECT COUNT(*) FROM records WHERE kind='execution_evidence'").fetchone()[0] == (1 if stage in {'after_record','publish_before_commit','after_publish'} else 0)
    finally:
        a.close()


@pytest.mark.asyncio
async def test_scheduler_callback_creates_authorized_execution(env, monkeypatch):
    import asyncio
    from app.agent.scheduler import Scheduler
    import app.agent.scheduler as module
    a, p = env
    runtime.bind_authority(a)
    worker = runtime.bind_offline_execution(p.policy)
    scheduler = Scheduler()
    first = datetime.now(UTC)+timedelta(seconds=.06)
    monkeypatch.setattr(module, 'cron_next', lambda expression, after: (datetime.fromisoformat(after)+timedelta(minutes=1)).isoformat() if datetime.fromisoformat(after)>=first else first.isoformat())
    try:
        await worker.start()
        await scheduler.start()
        op = key()
        spec = dict(capability='synthetic.echo', payload={'value':'timer result'}, timeout_seconds=10, expires_after_seconds=30)
        job = scheduler.add_job('synthetic timer', '* * * * *', 'never interpreted as a tool', request_id=op, execution=spec)
        assert scheduler.add_job('synthetic timer', '* * * * *', 'never interpreted as a tool', request_id=op, execution=spec)['replayed']
        for _ in range(100):
            rows = a.list_tasks(ACTOR)
            if rows and rows[0]['status']=='simulated_completed':
                break
            await asyncio.sleep(.01)
        assert len(rows) == 1 and rows[0]['result']['output'] == 'timer result'
        assert rows[0]['task_id'] == rows[0]['occurrence_id']
        assert a.list_schedules(ACTOR)[0]['last_run'] == first.isoformat()
        assert a.receipt(ACTOR, rows[0]['occurrence_id'])['operation'] == 'occurrence'
    finally:
        await worker.stop()
        await scheduler.stop()
        runtime.close_authority()


@pytest.mark.asyncio
async def test_scheduled_cancellation_policy_and_stopped_admission(env):
    from fastapi import FastAPI
    from app.agent.api import router
    from app.agent.scheduler import scheduler
    a, p = env
    runtime.bind_authority(a)
    worker = runtime.bind_offline_execution(p.policy)
    app = FastAPI()
    app.include_router(router)
    try:
        await worker.start()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://synthetic', headers=API_HEADERS) as client:
            body = dict(request_id=key(), goal='schedule', name='scheduled echo', cron_expr='* * * * *', execution=dict(capability='shell.exec', payload={'value':'no'}))
            assert (await client.post('/schedule/jobs', json=body)).status_code == 400
            assert a.list_schedules(ACTOR) == []
            body['execution']['capability']='synthetic.echo'
            response = await client.post('/schedule/jobs', json=body)
            assert response.status_code==200
            job = response.json()['result']
            worker.pipeline.policy=SimulatedPolicy(ACTOR.scope, frozenset(), revision='revoked')
            assert (await client.post('/schedule/jobs', json=body)).json()['replayed']
            control=a.scheduler_control(ACTOR, key(), True)['result']
            occurrence=a.admit_occurrence(ACTOR, job['job_id'], job['revision'], job['next_run_at'], control['epoch'], (datetime.fromisoformat(job['next_run_at'])+timedelta(minutes=1)).isoformat())
            a.set_schedule(ACTOR, key(), job['job_id'], removed=True)
            assert a.list_tasks(ACTOR)[0]['status']=='cancelled'
            assert worker.pipeline.run_once(ACTOR) is None
            await worker.stop()
            request=dict(request_id=key(),goal='stopped',capability='synthetic.echo',payload={'value':'x'}, expires_at=(datetime.now(UTC)+timedelta(minutes=1)).isoformat())
            assert (await client.post('/execution/tasks',json=request)).status_code==503
    finally:
        await worker.stop()
        runtime.close_authority()


def test_precommit_result_rollback_and_lost_publication_ack(env):
    a, p = env
    op = submit(p)['request_id']
    def lose_ack(stage):
        if stage=='after_commit_before_ack' and a._conn.execute('SELECT 1 FROM receipts WHERE request_id=?',(phase_id(op,'publish'),)).fetchone():
            raise RuntimeError('lost response')
    a._fault=lose_ack
    with pytest.raises(RuntimeError,match='lost response'):
        p.run_once(ACTOR)
    a._fault=lambda stage:None
    assert task(a)['status']=='simulated_completed'
    assert a.receipt(ACTOR, phase_id(op,'publish'))['result']['result']['output']=='hello'
    assert p.run_once(ACTOR) is None


def test_polling_does_not_read_completed_history(env, monkeypatch):
    a, p = env
    submit(p)
    p.run_once(ACTOR)
    submit(p)
    monkeypatch.setattr(a,'list_tasks',lambda *args: (_ for _ in ()).throw(AssertionError('unbounded history read')))
    assert p.run_once(ACTOR)['result']['status']=='simulated_completed'


@pytest.mark.parametrize('change', [{'scope':'other'}, {'capability':'shell.exec'}, {'allowed':1}, {'allowed':False}])
def test_inconsistent_authorization_never_dispatches(env, change):
    a, p = env
    op=submit(p)['request_id']
    row=a._get('task',op,ACTOR.scope)
    row['execution']['authorization'].update(change)
    a._put('task',op,ACTOR.scope,row)
    assert p.run_once(ACTOR)['result']['status']=='denied'
    assert a.receipt(ACTOR,phase_id(op,'record')) is None


def test_concurrent_same_operation_admits_once(env):
    from concurrent.futures import ThreadPoolExecutor
    a, p=env
    op=key()
    expiry=(datetime.now(UTC)+timedelta(minutes=1)).isoformat()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:submit(p,request_id=op,expires_at=expiry),range(4)))
    assert sum(not r['replayed'] for r in results)==1
    assert len(a.list_tasks(ACTOR))==1
    p.run_once(ACTOR)
    assert len(a.execution_tasks(ACTOR,'held'))==0


def test_pagination_and_direct_lookup(env, monkeypatch):
    a, p=env
    ops=[submit(p)['request_id'] for _ in range(3)]
    p.run_once(ACTOR)
    monkeypatch.setattr(a,'list_tasks',lambda *args: (_ for _ in ()).throw(AssertionError('unbounded read')))
    page=a.task_page(ACTOR,limit=1)
    assert page['total']==3 and page['next_offset']==1
    assert a.task_page(ACTOR,limit=1,offset=1)['tasks'][0]['task_id']==ops[1]
    assert a.task_page(ACTOR,status='pending')['total']==2
    assert a.task_page(ACTOR,status='simulated_completed')['total']==1
    assert a.get_task(ACTOR,ops[0])['status']=='simulated_completed'
    with pytest.raises(AuthorityError,match='invalid_pagination'):
        a.task_page(ACTOR,limit=1000)
    with pytest.raises(AuthorityError,match='not_found'):
        a.get_task(Actor('other'),ops[0])


@pytest.mark.asyncio
async def test_admission_body_stream_bound_precedes_json(env):
    from fastapi import FastAPI
    from app.agent.api import router
    from app.agent.admission import AdmissionBodyLimit
    a, p=env
    runtime.bind_authority(a)
    app=FastAPI()
    app.include_router(router)
    app.add_middleware(AdmissionBodyLimit)
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=API_HEADERS) as client:
            response=await client.post('/execution/tasks',content=b'x'*262145)
            assert response.status_code==413
            async def chunks():
                yield b'x'*150000
                yield b'x'*150000
                raise AssertionError('read beyond request limit')
            assert (await client.post('/execution/tasks',content=chunks())).status_code==413
            assert (await client.post('/tasks',content=b'{}',headers={'content-length':'-1'})).status_code==400
            assert (await client.post('/tasks',json={'request_id':key(),'goal':'within bound'})).status_code==200
            assert (await client.get('/tasks?limit=1000')).status_code==422
            assert (await client.get('/tasks/invalid')).status_code==400
        assert len(a.list_tasks(ACTOR))==1
    finally:
        runtime.close_authority()


@pytest.mark.asyncio
async def test_public_mutations_cannot_reserve_internal_phase_receipts(env):
    from fastapi import FastAPI
    from app.agent.api import router
    a, p=env
    runtime.bind_authority(a)
    worker=runtime.bind_offline_execution(p.policy)
    app=FastAPI()
    app.include_router(router)
    try:
        await worker.start()
        await worker.stop()
        op=submit(p)['request_id']
        reserved=phase_id(op,'publish')
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=API_HEADERS) as client:
            assert (await client.post('/tasks',json={'request_id':reserved,'goal':'reserve internal receipt'})).status_code==422
            assert (await client.delete('/tasks/'+op,params={'request_id':reserved})).status_code==422
            assert (await client.delete('/schedule/jobs/'+op,params={'request_id':reserved})).status_code==422
            assert (await client.post('/schedule/jobs',json={'request_id':reserved,'name':'x','goal':'x','cron_expr':'* * * * *'})).status_code==422
        result=worker.pipeline.run_once(ACTOR)
        assert result['request_id']==reserved and task(a)['status']=='simulated_completed'
    finally:
        await worker.stop()
        runtime.close_authority()


@pytest.mark.parametrize('changes', [{'goal':'bad\ud800'}, {'payload':{'value':'bad\udfff'}}])
def test_invalid_unicode_rejected_before_commit(env, changes):
    a,p=env
    with pytest.raises(AuthorityError,match='invalid_text'):
        submit(p,**changes)
    assert a.list_tasks(ACTOR)==[]


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', ['too_many_chunks','slow_body'])
async def test_admission_empty_chunk_and_read_deadline(mode):
    import asyncio
    from app.agent.admission import AdmissionBodyLimit
    scope={'type':'http','method':'POST','path':'/execution/tasks','headers':[]}
    sent=[]
    async def receive():
        if mode=='slow_body':
            await asyncio.Event().wait()
        return {'type':'http.request','body':b'', 'more_body':True}
    async def send(message):
        sent.append(message)
    async def app(*args):
        raise AssertionError('unbounded request reached application')
    await AdmissionBodyLimit(app,read_timeout=.01)(scope,receive,send)
    assert sent[0]['status']==(408 if mode=='slow_body' else 413)

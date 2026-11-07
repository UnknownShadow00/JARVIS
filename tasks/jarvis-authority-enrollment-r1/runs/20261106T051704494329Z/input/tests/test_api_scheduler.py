"""Real router/ASGI/cron integration. This is not the full application lifespan."""
import asyncio
from datetime import UTC, datetime, timedelta
import uuid

from fastapi import FastAPI
import httpx
import pytest

from app.agent import runtime
from app.agent.api import router
from app.agent.authority import Authority, AuthorityError
from synthetic_authority import fixture_authority as Authority
from app.agent.scheduler import scheduler, cron_next
from app.agent.task_queue import TaskQueue, task_queue

def rid():return str(uuid.uuid4())


@pytest.fixture
def authority(tmp_path):
    a=Authority(tmp_path/'api.sqlite')
    runtime.bind_authority(a)
    yield a
    runtime.close_authority()


@pytest.mark.asyncio
async def test_actual_router_idempotency_client_scope_not_authority(authority):
    app=FastAPI();app.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        key=rid();body={'request_id':key,'goal':'read only'}
        first=await client.post('/tasks',json=body,headers={'X-Scope':'attacker'})
        assert first.status_code==200 and first.json()['scope']=='local-service'
        second=await client.post('/tasks',json=body)
        assert second.json()['replayed'] and second.json()['result']==first.json()['result']
        conflict=await client.post('/tasks',json={**body,'goal':'other'})
        assert conflict.status_code==409
        assert (await client.get('/requests/'+key)).json()['result']==first.json()['result']
        assert (await client.post('/tasks',json={**body,'scope':'attacker'})).status_code==422
        assert (await client.post('/tasks',json={'goal':'no key'})).status_code==422
        assert (await client.patch('/tasks/'+first.json()['result']['task_id'],json={'status':'completed','result':{'root':True}})).status_code==405
        assert (await client.get('/ready')).status_code==503
        assert not first.json()['result'].get('executed',False)


@pytest.mark.asyncio
async def test_facade_same_writer_no_completion_or_legacy_store(authority):
    key=rid()
    row=await task_queue.add_task('facade',request_id=key)
    assert row.task_id==authority.list_tasks(runtime.SERVICE_ACTOR)[0]['task_id']
    with pytest.raises(TypeError):await task_queue.add_task('missing key')
    with pytest.raises(AuthorityError,match='public_completion_disabled'):await task_queue.update_status(row.task_id,'completed')
    with pytest.raises(AuthorityError,match='independent_store_disabled'):TaskQueue('/work/legacy.json')


@pytest.mark.asyncio
async def test_real_cron_scheduler_lifecycle_and_clock_changed_replay(authority,monkeypatch):
    await scheduler.start()
    try:
        first=scheduler.add_job('job','* * * * *','goal',request_id=(key:=rid()))
        job=first['result']
        # Replaying the same expressed request cannot consult a different clock.
        monkeypatch.setattr('app.agent.scheduler.cron_next',lambda *args: (_ for _ in ()).throw(AssertionError('retry recomputed clock')))
        replay=scheduler.add_job('job','* * * * *','goal',request_id=key)
        assert replay['replayed'] and replay['result']==job
        assert scheduler.readiness()['scheduler_ready']
    finally:await scheduler.stop()
    assert not scheduler.readiness()['scheduler_ready']


@pytest.mark.asyncio
async def test_callback_admits_once_stop_cancels_and_retained_callback_denied(authority):
    await scheduler.start()
    try:
        row=scheduler.add_job('job','* * * * *','goal',request_id=rid())['result']
        epoch=scheduler._epoch
        await scheduler._dispatch(row['job_id'],row['revision'],row['next_run_at'],epoch)
        assert len(authority.list_tasks(runtime.SERVICE_ACTOR))==1
        assert authority.list_schedules(runtime.SERVICE_ACTOR)[0]['last_run']==row['next_run_at']
        await scheduler.stop()
        assert authority.list_tasks(runtime.SERVICE_ACTOR)[0]['status']=='cancelled'
        next_nominal=cron_next(row['cron_expr'],row['next_run_at'])
        await scheduler._dispatch(row['job_id'],row['revision'],next_nominal,epoch)
        assert len(authority.list_tasks(runtime.SERVICE_ACTOR))==1
    finally:
        if scheduler._backend is not None:await scheduler.stop()


def test_admission_order_survives_mutation(authority):
    rows=[authority.submit(runtime.SERVICE_ACTOR,rid(),str(i))['result'] for i in range(5)]
    authority.cancel(runtime.SERVICE_ACTOR,rid(),rows[0]['task_id'])
    assert [t['task_id'] for t in authority.list_tasks(runtime.SERVICE_ACTOR)]==[r['task_id'] for r in rows]


@pytest.mark.asyncio
async def test_removed_callback_does_not_stop_other_schedule(authority):
    await scheduler.start()
    try:
        old=scheduler.add_job('old','* * * * *','goal',request_id=rid())['result']
        other=scheduler.add_job('other','* * * * *','goal',request_id=rid())['result']
        epoch=scheduler._epoch
        scheduler.remove_job(old['job_id'],request_id=rid())
        await scheduler._dispatch(old['job_id'],old['revision'],old['next_run_at'],epoch)
        assert scheduler.readiness()['scheduler_ready']
        await scheduler._dispatch(other['job_id'],other['revision'],other['next_run_at'],epoch)
        assert len(authority.list_tasks(runtime.SERVICE_ACTOR))==1
        assert authority.list_tasks(runtime.SERVICE_ACTOR)[0]['status']=='pending'
    finally:await scheduler.stop()


@pytest.mark.asyncio
async def test_committed_occurrence_registration_failure_marks_not_ready(authority,monkeypatch):
    await scheduler.start()
    try:
        row=scheduler.add_job('job','* * * * *','goal',request_id=rid())['result']
        epoch=scheduler._epoch
        def broken(*args,**kwargs):raise RuntimeError('synthetic timer registration failure')
        monkeypatch.setattr(scheduler._backend,'add_job',broken)
        with pytest.raises(RuntimeError,match='synthetic timer'):
            await scheduler._dispatch(row['job_id'],row['revision'],row['next_run_at'],epoch)
        assert not scheduler.readiness()['scheduler_ready']
        tasks=authority.list_tasks(runtime.SERVICE_ACTOR)
        assert len(tasks)==1 and tasks[0]['status']=='cancelled'
        assert authority.list_schedules(runtime.SERVICE_ACTOR)[0]['last_run']==row['next_run_at']
        await scheduler._dispatch(row['job_id'],row['revision'],row['next_run_at'],epoch)
        assert len(authority.list_tasks(runtime.SERVICE_ACTOR))==1
    finally:await scheduler.stop()


@pytest.mark.asyncio
async def test_durable_stop_failure_still_shuts_owned_backend(authority):
    await scheduler.start()
    backend=scheduler._backend
    authority._poisoned=True
    try:
        with pytest.raises(AuthorityError,match='authority_unavailable'):
            await scheduler.stop()
        await asyncio.sleep(0)
        assert scheduler._backend is None and scheduler._epoch is None
        assert not backend.running
        await scheduler._dispatch(rid(),1,'2035-01-01T00:00:00+00:00',1)
    finally:authority._poisoned=False


@pytest.mark.asyncio
async def test_backend_removal_failure_keeps_receipt_and_truthful_result(authority,monkeypatch):
    await scheduler.start()
    try:
        row=scheduler.add_job('job','* * * * *','goal',request_id=rid())['result']
        key=rid()
        def broken(*args,**kwargs):raise RuntimeError('synthetic removal failure')
        monkeypatch.setattr(scheduler._backend,'remove_job',broken)
        with pytest.raises(AuthorityError,match='backend_removal_reconcile'):
            scheduler.remove_job(row['job_id'],request_id=key)
        receipt=authority.receipt(runtime.SERVICE_ACTOR,key)
        assert receipt['result']['removed']
        assert not scheduler.readiness()['scheduler_ready']
        assert authority.list_schedules(runtime.SERVICE_ACTOR)==[]
        assert authority.set_schedule(runtime.SERVICE_ACTOR,key,row['job_id'],removed=True)['replayed']
    finally:await scheduler.stop()

"""Receipt-bound persistence replaces retired JSON rewrites and rollback guessing."""
import uuid
import pytest
from application_fixtures import admitted_app
from app.agent.task_queue import TaskQueue
from app.agent.authority import AuthorityError
from app.agent import runtime
from synthetic_authority import fixture_authority

@pytest.mark.asyncio
async def test_identical_admission_survives_reopen(admitted_app):
    q=TaskQueue();key=str(uuid.uuid4());first=await q.add_task('persisted',request_id=key)
    path=admitted_app.path;runtime.close_authority();runtime.bind_authority(fixture_authority(path))
    second=await q.add_task('persisted',request_id=key)
    assert first==second and len(q.tasks)==1
    assert runtime._authority.receipt(runtime.SERVICE_ACTOR,key)['operation']=='submit'

@pytest.mark.asyncio
async def test_conflicting_retry_does_not_change_task(admitted_app):
    q=TaskQueue();key=str(uuid.uuid4());await q.add_task('original',request_id=key)
    with pytest.raises(AuthorityError,match='request_conflict'):await q.add_task('different',request_id=key)
    assert (await q.get_task(key)).goal=='original' and len(q.tasks)==1

@pytest.mark.asyncio
async def test_cancel_retains_history_and_original_receipt(admitted_app):
    q=TaskQueue();key=str(uuid.uuid4());await q.add_task('held',request_id=key)
    cancel=str(uuid.uuid4());first=await q.delete_task(key,request_id=cancel)
    replay=await q.delete_task(key,request_id=cancel)
    assert replay['replayed'] and replay['result']==first['result']
    assert (await q.get_task(key)).status=='cancelled'
    assert admitted_app.receipt(runtime.SERVICE_ACTOR,key)['result']['status']=='pending'

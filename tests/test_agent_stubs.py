"""Current compatibility facade; retired in-memory/JSON writer contract removed."""
import uuid
import pytest
from application_fixtures import admitted_app
from app.agent.task_queue import TaskQueue, AgentTask
from app.agent.authority import AuthorityError

@pytest.mark.asyncio
async def test_admission_and_snapshot_share_authority(admitted_app):
    q=TaskQueue();key=str(uuid.uuid4());task=await q.add_task('held',request_id=key)
    assert isinstance(task,AgentTask) and task.task_id==key and task.status=='pending'
    task.goal='caller mutation'
    assert (await q.get_task(key)).goal=='held'
    assert (await q.list_tasks('pending'))[0].task_id==key

@pytest.mark.asyncio
async def test_request_id_is_required(admitted_app):
    with pytest.raises(TypeError):await TaskQueue().add_task('no canonical id')

@pytest.mark.asyncio
async def test_completion_cannot_be_claimed(admitted_app):
    with pytest.raises(AuthorityError,match='public_completion_disabled'):await TaskQueue().update_status('any','completed',{'success':True})

"""Actual APScheduler callback lifecycle; no wall-clock firing or external effects."""
import uuid
import pytest
from application_fixtures import admitted_app
from app.agent.scheduler import Scheduler
from app.agent import runtime

@pytest.mark.asyncio
async def test_nominal_callback_deduplicates_and_stop_fences_retained_callback(admitted_app):
    s=Scheduler();await s.start()
    try:
        job=s.add_job('held','0 8 * * *','goal',request_id=str(uuid.uuid4()))['result']
        epoch=s._epoch;args=[job['job_id'],job['revision'],job['next_run_at'],epoch]
        await s._dispatch(*args);await s._dispatch(*args)
        assert len(admitted_app.list_tasks(runtime.SERVICE_ACTOR))==1
        await s.stop();await s._dispatch(*args)
        tasks=admitted_app.list_tasks(runtime.SERVICE_ACTOR)
        assert len(tasks)==1 and tasks[0]['status']=='cancelled'
    finally:
        if s._backend is not None:await s.stop()

"""Durable schedules replace independent legacy JSON ScheduledJob objects."""
import uuid
import pytest
from application_fixtures import admitted_app
from app.agent.scheduler import Scheduler
from app.agent.authority import AuthorityError

def test_schedule_retry_preserves_original_nominal(admitted_app,monkeypatch):
    s=Scheduler();key=str(uuid.uuid4());first=s.add_job('daily','0 8 * * *','held',request_id=key)
    monkeypatch.setattr('app.agent.scheduler.cron_next',lambda *a: (_ for _ in ()).throw(AssertionError('retry clock')))
    assert s.add_job('daily','0 8 * * *','held',request_id=key)['result']==first['result']
    assert len(s.list_jobs())==1

def test_schedule_removal_retains_receipt(admitted_app):
    s=Scheduler();job=s.add_job('daily','0 8 * * *','held',request_id=str(uuid.uuid4()))['result']
    key=str(uuid.uuid4());first=s.remove_job(job['job_id'],request_id=key)
    assert not s.list_jobs() and s.remove_job(job['job_id'],request_id=key)['replayed']
    assert first['result']['job_id']==job['job_id']

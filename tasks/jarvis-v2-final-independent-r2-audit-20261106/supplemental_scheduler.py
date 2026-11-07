import asyncio
import pytest
from app.agent.scheduler import Scheduler
from app.agent.authority import AuthorityError
from synthetic_authority import fixture_authority

@pytest.mark.asyncio
async def test_async_store_failure_after_caller_cancellation(tmp_path, monkeypatch):
    a=fixture_authority(tmp_path/'state'/'db', allow_simulation=True)
    monkeypatch.setattr('app.agent.scheduler.get_authority',lambda:a)
    s=Scheduler();await s.start();b=s._backend
    store=b._jobstores['default'];original=store.shutdown
    entered=asyncio.Event();release=asyncio.Event()
    async def broken():
        entered.set();await release.wait();raise OSError('AUDIT_SYNTHETIC_SECRET_ASYNC')
    monkeypatch.setattr(store,'shutdown',broken)
    stop=asyncio.create_task(s.stop());await entered.wait();stop.cancel()
    with pytest.raises(asyncio.CancelledError):await stop
    assert s._backend is b and not s._cleanup_task.cancelled()
    release.set()
    await asyncio.sleep(0);await asyncio.sleep(0)
    assert s._cleanup_task.done() and s._cleanup_task.exception() is not None
    with pytest.raises(AuthorityError):await s.start()
    monkeypatch.setattr(store,'shutdown',original)
    await s.stop();assert s._backend is None and b._cleanup_complete
    await s.start();await s.stop();a.close()

@pytest.mark.asyncio
async def test_start_waits_for_confirmed_stop(tmp_path,monkeypatch):
    a=fixture_authority(tmp_path/'state'/'db',allow_simulation=True)
    monkeypatch.setattr('app.agent.scheduler.get_authority',lambda:a)
    s=Scheduler();await s.start();old=s._backend
    store=old._jobstores['default'];original=store.shutdown
    entered=asyncio.Event();release=asyncio.Event()
    async def delayed():entered.set();await release.wait();original()
    monkeypatch.setattr(store,'shutdown',delayed)
    stop=asyncio.create_task(s.stop());await entered.wait()
    start=asyncio.create_task(s.start());await asyncio.sleep(0)
    assert not start.done() and s._backend is old
    release.set();await stop;await start
    assert old._cleanup_complete and s._backend is not old
    await s.stop();a.close()

def test_installed_backend_version():
    import apscheduler
    assert apscheduler.__version__=='3.11.3'

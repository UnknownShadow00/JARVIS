"""Real installed APScheduler ownership and cancellation regression tests."""
import asyncio
import pytest
from app.agent.authority import AuthorityError
from app.agent.scheduler import Scheduler
from synthetic_authority import fixture_authority


@pytest.fixture
def env(tmp_path, monkeypatch):
    a = fixture_authority(tmp_path/'state'/'db', allow_simulation=True)
    monkeypatch.setattr('app.agent.scheduler.get_authority', lambda: a)
    yield a
    a.close()


@pytest.mark.asyncio
async def test_real_executor_cleanup_failure_is_observed_and_retryable(env, monkeypatch):
    s = Scheduler()
    await s.start()
    backend = s._backend
    executor = backend._executors['default']
    original = executor.shutdown
    task = asyncio.create_task(asyncio.Event().wait())
    executor._pending_futures.add(task)
    calls = []
    def broken(wait=False):
        calls.append(1)
        raise RuntimeError('synthetic executor cleanup fault')
    monkeypatch.setattr(executor, 'shutdown', broken)
    try:
        with pytest.raises(RuntimeError):
            await s.stop()
        assert s._backend is backend and s._failure is not None
        assert not backend.running and not task.done()
        with pytest.raises(AuthorityError, match='scheduler_reconcile_required'):
            await s.start()
        monkeypatch.setattr(executor, 'shutdown', original)
        await s.stop()
        assert task.done() and s._backend is None and s._failure is None
        await s.stop()
        assert len(calls) == 1
    finally:
        monkeypatch.setattr(executor, 'shutdown', original)
        original(wait=False)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        if s._backend is not None:
            await s.stop()


@pytest.mark.asyncio
async def test_real_partial_store_cleanup_retries_only_unfinished_resources(env, monkeypatch):
    s = Scheduler()
    await s.start()
    backend = s._backend
    executor, store = backend._executors['default'], backend._jobstores['default']
    original_executor, original_store = executor.shutdown, store.shutdown
    calls = {'executor': 0, 'store': 0}
    def close_executor(wait=False):
        calls['executor'] += 1
        original_executor(wait)
    def close_store():
        calls['store'] += 1
        if calls['store'] == 1:
            raise OSError('synthetic store cleanup fault')
        original_store()
    monkeypatch.setattr(executor, 'shutdown', close_executor)
    monkeypatch.setattr(store, 'shutdown', close_store)
    with pytest.raises(OSError):
        await s.stop()
    assert s._backend is backend and not backend.running
    await s.stop()
    assert calls == {'executor': 1, 'store': 2}
    await s.stop()
    assert calls == {'executor': 1, 'store': 2}


@pytest.mark.asyncio
async def test_real_stop_confirms_cleanup_before_immediate_restart(env):
    s = Scheduler()
    await s.start()
    old = s._backend
    await s.stop()
    assert not old.running and old._cleanup_complete
    await s.start()
    assert s._backend is not old
    await s.stop()


class AsyncBackend:
    running = True
    def __init__(self):
        self.entered, self.release = asyncio.Event(), asyncio.Event()
        self.calls = 0
    async def shutdown(self, wait=False):
        self.calls += 1
        self.running = False
        self.entered.set()
        await self.release.wait()


@pytest.mark.asyncio
@pytest.mark.parametrize('interruption', ['cancel', 'timeout'])
async def test_inflight_cleanup_survives_caller_interruption_and_retry(env, interruption):
    s, backend = Scheduler(), AsyncBackend()
    s._backend, s._epoch = backend, 1
    s._cleanup_timeout = .02 if interruption == 'timeout' else 1
    stop = asyncio.create_task(s.stop())
    await backend.entered.wait()
    if interruption == 'cancel':
        stop.cancel()
        with pytest.raises(asyncio.CancelledError):
            await stop
    else:
        with pytest.raises(TimeoutError):
            await stop
    assert s._backend is backend and not s._cleanup_task.cancelled()
    with pytest.raises(AuthorityError, match='scheduler_reconcile_required'):
        await s.start()
    backend.release.set()
    await s.stop()
    assert backend.calls == 1 and s._backend is None and s._failure is None


@pytest.mark.asyncio
async def test_concurrent_stop_does_not_duplicate_backend_cleanup(env):
    s, backend = Scheduler(), AsyncBackend()
    s._backend = backend
    first = asyncio.create_task(s.stop())
    await backend.entered.wait()
    second = asyncio.create_task(s.stop())
    backend.release.set()
    await asyncio.gather(first, second)
    assert backend.calls == 1 and s._backend is None


@pytest.mark.asyncio
async def test_late_cleanup_error_remains_observable_after_cancellation(env):
    class Broken(AsyncBackend):
        async def shutdown(self, wait=False):
            await super().shutdown(wait)
            raise OSError('synthetic late cleanup error')
    s, backend = Scheduler(), Broken()
    s._backend = backend
    stop = asyncio.create_task(s.stop())
    await backend.entered.wait()
    stop.cancel()
    with pytest.raises(asyncio.CancelledError):
        await stop
    backend.release.set()
    await asyncio.sleep(0)
    with pytest.raises(OSError):
        await s.stop()
    assert s._backend is backend and s._failure
    # Test-owned cleanup repair; no resource is silently abandoned by product.
    backend.shutdown = lambda wait=False: None
    await s.stop()


@pytest.mark.asyncio
async def test_combined_durable_and_backend_failure_retains_owner(env, monkeypatch):
    class Broken:
        running = False
        def shutdown(self, wait=False):
            raise RuntimeError('synthetic backend failure')
    s = Scheduler()
    backend = s._backend = Broken()
    original = env.scheduler_control
    monkeypatch.setattr(env, 'scheduler_control', lambda *a: (_ for _ in ()).throw(OSError('synthetic durable failure')))
    with pytest.raises(OSError):
        await s.stop()
    assert s._backend is backend and s._failure
    monkeypatch.setattr(env, 'scheduler_control', original)
    backend.shutdown = lambda wait=False: None
    await s.stop()


@pytest.mark.asyncio
async def test_real_cancellation_suppressing_job_keeps_owner_until_done(env):
    s = Scheduler()
    await s.start()
    backend = s._backend
    entered, release = asyncio.Event(), asyncio.Event()
    async def stubborn():
        entered.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            await release.wait()
    task = asyncio.create_task(stubborn())
    await entered.wait()
    backend._executors['default']._pending_futures.add(task)
    s._cleanup_timeout = .02
    with pytest.raises(TimeoutError):
        await s.stop()
    assert s._backend is backend and not task.done()
    release.set()
    await s.stop()
    assert task.done() and s._backend is None


@pytest.mark.asyncio
async def test_closed_real_backend_cannot_reopen_stale_cleanup_inventory(env):
    s=Scheduler()
    await s.start()
    backend=s._backend
    await s.stop()
    with pytest.raises(AuthorityError,match='scheduler_backend_closed'):
        backend.start()
    await backend.aclose()  # confirmed completion is idempotent


@pytest.mark.asyncio
async def test_unowned_deferred_backend_is_refused_without_losing_handle(env):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    backend=AsyncIOScheduler()
    backend.start()
    s=Scheduler();s._backend=backend
    try:
        with pytest.raises(AuthorityError,match='scheduler_cleanup_protocol_required'):
            await s.stop()
        assert s._backend is backend and backend.running
        with pytest.raises(AuthorityError,match='scheduler_reconcile_required'):
            await s.start()
    finally:
        # This backend was test-owned, not an accepted product backend.
        backend.shutdown(wait=False)
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_unverifiable_executor_future_does_not_count_as_cleanup(env):
    s=Scheduler()
    await s.start()
    backend=s._backend
    future=asyncio.get_running_loop().create_future()
    backend._executors['default']._pending_futures.add(future)
    with pytest.raises(AuthorityError,match='scheduler_cleanup_unverifiable'):
        await s.stop()
    assert s._backend is backend
    future.set_result(None)
    await s.stop()
    assert s._backend is None


@pytest.mark.asyncio
@pytest.mark.parametrize('phase', ['apply', 'acknowledge'])
async def test_legacy_claimed_execution_fixture_cannot_apply_or_acknowledge(env, phase):
    """A retained state that RC1 could create, beyond held-task error diagnostics."""
    import uuid
    from datetime import UTC, datetime, timedelta
    from app.agent.execution import ExecutionPipeline, SimulatedPolicy
    from app.agent.runtime import SERVICE_ACTOR
    from app.agent.simulation import Simulator
    op, claim, request = [str(uuid.uuid4()) for _ in range(3)]
    p=ExecutionPipeline(env, SimulatedPolicy(SERVICE_ACTOR.scope), enabled=True)
    task=p.submit(SERVICE_ACTOR,op,'retained legacy claim','synthetic.echo',{'value':'offline'},
                  (datetime.now(UTC)+timedelta(minutes=1)).isoformat())['result']
    # Reconstruct the persisted state produced by RC1 Simulator.claim on an
    # execution task. No auth mock is active during the operations under test.
    task['status']='simulating'
    env._conn.execute("UPDATE records SET data=? WHERE kind='task' AND id=?",(__import__('json').dumps(task),op))
    env._conn.execute("UPDATE outbox SET state='simulating',claim_id=?,generation=? WHERE task_id=?",(claim,env.generation,op))
    if phase=='acknowledge':
        env._conn.execute('INSERT INTO simulation_effects VALUES(?,?)',(op,claim))
    before=env.get_task(SERVICE_ACTOR,op)
    with pytest.raises(AuthorityError,match='execution_protocol_mismatch'):
        getattr(Simulator(env),phase)(SERVICE_ACTOR,request,op,claim,env.generation)
    assert env.get_task(SERVICE_ACTOR,op)==before
    assert env.receipt(SERVICE_ACTOR,request) is None

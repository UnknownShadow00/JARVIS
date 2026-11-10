"""Adversarial boundaries across the actual authority and execution protocols."""
from datetime import UTC, datetime, timedelta
import uuid
from itertools import count
import sys

import pytest

from app.agent.authority import AuthorityError, instant
from app.agent.execution import ExecutionPipeline, SimulatedPolicy, phase_id
from app.agent.simulation import Simulator
from app.agent.scheduler import Scheduler
from app.agent import runtime
from synthetic_authority import fixture_authority

ACTOR = runtime.SERVICE_ACTOR
NOW = datetime(2030, 1, 1, tzinfo=UTC)


_ids = count(1)


@pytest.fixture(autouse=True)
def deterministic_identifiers(monkeypatch):
    monkeypatch.setattr(sys.modules[__name__], '_ids', count(1))


def key():
    return str(uuid.UUID(int=next(_ids), version=4))


@pytest.fixture
def env(tmp_path):
    a = fixture_authority(tmp_path / 'state' / 'db', allow_simulation=True)
    p = ExecutionPipeline(a, SimulatedPolicy(ACTOR.scope), enabled=True, clock=lambda: NOW)
    yield a, p
    a.close()


def submit(p, request_id=None):
    return p.submit(ACTOR, request_id or key(), 'gauntlet', 'synthetic.echo',
                    {'value': 'offline'}, (NOW + timedelta(minutes=1)).isoformat())


@pytest.mark.parametrize('value', ['0001-01-01T00:00:00+23:00', '9999-12-31T23:59:59-23:00'])
def test_time_normalization_overflow_is_domain_error(value):
    with pytest.raises(AuthorityError, match='invalid_time'):
        instant(value)


@pytest.mark.parametrize('method', ['claim', 'apply', 'acknowledge', 'reconcile'])
def test_simulator_cannot_take_execution_protocol_task(env, method):
    a, p = env
    op = submit(p)['request_id']
    sim = Simulator(a)
    before = a.get_task(ACTOR, op)
    args = (ACTOR, key(), op)
    if method in {'apply', 'acknowledge'}:
        args += (key(), a.generation)
    with pytest.raises(AuthorityError, match='execution_protocol_mismatch'):
        getattr(sim, method)(*args)
    assert a.get_task(ACTOR, op) == before
    assert p.run_once(ACTOR)['result']['status'] == 'simulated_completed'


def test_simulator_cannot_resolve_execution_unknown_after_restart(env):
    a, p = env
    op = submit(p)['request_id']
    p._claim(ACTOR, op)
    a.close()
    reopened = fixture_authority(a.path, allow_simulation=True)
    try:
        assert reopened.get_task(ACTOR, op)['status'] == 'unknown'
        with pytest.raises(AuthorityError, match='execution_protocol_mismatch'):
            Simulator(reopened).reconcile(ACTOR, key(), op)
        assert reopened.get_task(ACTOR, op)['status'] == 'unknown'
        assert ExecutionPipeline(reopened, p.policy, enabled=True).reconcile(ACTOR) == []
    finally:
        reopened.close()


class Backend:
    running = True

    def __init__(self):
        self.calls = 0

    def shutdown(self, wait=False):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError('injected shutdown interruption')
        self.running = False


@pytest.mark.asyncio
async def test_scheduler_retains_failed_shutdown_for_retry(env, monkeypatch):
    a, _ = env
    monkeypatch.setattr('app.agent.scheduler.get_authority', lambda: a)
    s = Scheduler()
    backend = Backend()
    s._backend, s._epoch = backend, 7
    with pytest.raises(RuntimeError):
        await s.stop()
    assert s._backend is backend
    assert s._epoch is None
    await s._dispatch(key(), 1, NOW.isoformat(), 7)
    assert not s.readiness()["scheduler_ready"]
    with pytest.raises(AuthorityError, match='scheduler_reconcile_required'):
        await s.start()
    await s.stop()
    assert backend.calls == 2 and not backend.running
    assert s._backend is None and s._failure is None


@pytest.mark.asyncio
async def test_scheduler_durable_stop_failure_requires_explicit_retry(env, monkeypatch):
    a, _ = env
    monkeypatch.setattr('app.agent.scheduler.get_authority', lambda: a)
    s = Scheduler()
    original = a.scheduler_control
    monkeypatch.setattr(a, 'scheduler_control', lambda *args: (_ for _ in ()).throw(OSError('injected')))
    with pytest.raises(OSError):
        await s.stop()
    with pytest.raises(AuthorityError, match='scheduler_reconcile_required'):
        await s.start()
    monkeypatch.setattr(a, 'scheduler_control', original)
    await s.stop()
    assert s._failure is None


@pytest.mark.parametrize('stage', ['after_claim', 'before_execute', 'after_execute', 'after_record', 'after_publish'])
def test_interrupted_phase_reopen_and_repeated_recovery(env, stage):
    a, p = env
    op = submit(p)['request_id']
    class Interrupted(BaseException):
        pass
    p._fault = lambda current: (_ for _ in ()).throw(Interrupted()) if current == stage else None
    with pytest.raises(Interrupted):
        p.run_once(ACTOR)
    assert not p._dispatch_mutex.locked()
    a.close()
    reopened = fixture_authority(a.path, allow_simulation=True)
    try:
        recovered = ExecutionPipeline(reopened, p.policy, enabled=True)
        recovered.reconcile(ACTOR)
        assert recovered.reconcile(ACTOR) == []
        assert recovered.run_once(ACTOR) is None
        expected = 'simulated_completed' if stage in {'after_record', 'after_publish'} else 'unknown'
        assert reopened.get_task(ACTOR, op)['status'] == expected
        count = reopened._conn.execute("SELECT COUNT(*) FROM events WHERE request_id=?", (phase_id(op, 'publish'),)).fetchone()[0]
        assert count == (1 if expected == 'simulated_completed' else 0)
    finally:
        reopened.close()


@pytest.mark.parametrize('stage', ['after_effect_sql', 'before_commit', 'after_commit_before_ack'])
def test_lost_admission_ack_replay_keeps_single_task(env, stage):
    a, p = env
    op = key()
    a._fault = lambda current: (_ for _ in ()).throw(RuntimeError('interrupted')) if current == stage else None
    with pytest.raises(RuntimeError):
        submit(p, op)
    a._fault = lambda current: None
    receipt = submit(p, op)
    assert receipt['replayed'] == (stage == 'after_commit_before_ack')
    assert len(a.list_tasks(ACTOR)) == 1
    assert p.run_once(ACTOR)['result']['status'] == 'simulated_completed'
    assert p.run_once(ACTOR) is None


def test_cancel_and_revoke_between_claim_and_dispatch(env):
    a, p = env
    op = submit(p)['request_id']
    def fault(stage):
        if stage == 'after_claim':
            a.cancel(ACTOR, key(), op)
            p.policy = SimulatedPolicy(ACTOR.scope, frozenset(), revision='revoked')
    p._fault = fault
    assert p.run_once(ACTOR)['result']['status'] == 'cancelled'
    assert a.receipt(ACTOR, phase_id(op, 'record')) is None


def test_completion_replay_after_cancel_is_receipt_only(env):
    a, p = env
    op = submit(p)['request_id']
    first = p.run_once(ACTOR)
    a.cancel(ACTOR, key(), op)
    second = p._publish(ACTOR, op)
    assert second['replayed'] and second['result'] == first['result']
    assert a.get_task(ACTOR, op)['cancel_requested']
    assert p.run_once(ACTOR) is None


def test_pending_limit_includes_unknown_until_operator_resolution(env):
    a, p = env
    p.max_pending = 1
    submit(p)
    p._fault = lambda stage: (_ for _ in ()).throw(RuntimeError()) if stage == 'after_execute' else None
    assert p.run_once(ACTOR)['result']['status'] == 'unknown'
    with pytest.raises(AuthorityError, match='queue_capacity_exceeded'):
        submit(p)
    assert len(a.list_tasks(ACTOR)) == 1


@pytest.mark.parametrize('phase', ['claim', 'dispatch', 'record', 'publish'])
def test_audit_write_failure_at_each_phase_rolls_back_and_recovers(env, phase):
    a, p = env
    op = submit(p)['request_id']
    # A real SQLite trigger aborts the receipt/event transaction at each phase.
    a._conn.execute("CREATE TRIGGER fail_phase BEFORE INSERT ON events WHEN NEW.request_id='" +
                    phase_id(op, phase) + "' BEGIN SELECT RAISE(ABORT,'injected'); END")
    with pytest.raises(AuthorityError, match='storage_unknown_reconcile'):
        p.run_once(ACTOR)
    assert a._conn.execute('SELECT COUNT(*) FROM receipts WHERE request_id=?', (phase_id(op, phase),)).fetchone()[0] == 0
    assert not p._dispatch_mutex.locked()
    with pytest.raises(AuthorityError, match='authority_unavailable'):
        p.run_once(ACTOR)
    a._conn.execute('DROP TRIGGER fail_phase')
    a.close()
    recovered = fixture_authority(a.path, allow_simulation=True)
    try:
        pipeline = ExecutionPipeline(recovered, p.policy, enabled=True)
        if phase == 'claim':
            assert pipeline.run_once(ACTOR)['result']['status'] == 'simulated_completed'
        elif phase == 'publish':
            assert len(pipeline.reconcile(ACTOR)) == 1
        else:
            assert pipeline.reconcile(ACTOR) == []
            assert recovered.get_task(ACTOR, op)['status'] == 'unknown'
        assert pipeline.run_once(ACTOR) is None
    finally:
        recovered.close()


@pytest.mark.parametrize('damage', ['missing', 'truncated'])
def test_damaged_store_refuses_reopen_without_creating_replacement(env, damage):
    a, p = env
    submit(p)
    a.close()
    if damage == 'missing':
        a.path.unlink()
        before = None
    else:
        a.path.write_bytes(b'SQLite format 3\x00')
        before = a.path.read_bytes()
    from app.agent.authority import Authority
    with pytest.raises(AuthorityError):
        Authority(a.path, allow_simulation=True)
    assert (a.path.read_bytes() if a.path.exists() else None) == before


def test_revoked_execution_cannot_complete_via_legacy_simulator(env):
    a, p = env
    op = submit(p)['request_id']
    p.policy = SimulatedPolicy(ACTOR.scope, frozenset(), revision='revoked')
    sim = Simulator(a)
    with pytest.raises(AuthorityError, match='execution_protocol_mismatch'):
        sim.claim(ACTOR, key(), op)
    assert p.run_once(ACTOR)['result']['status'] == 'denied'
    assert a._conn.execute('SELECT COUNT(*) FROM simulation_effects').fetchone()[0] == 0


def test_simulator_cannot_discard_recorded_execution_evidence(env):
    a, p = env
    op = submit(p)['request_id']
    class Interrupted(BaseException):
        pass
    p._fault = lambda stage: (_ for _ in ()).throw(Interrupted()) if stage == 'after_record' else None
    with pytest.raises(Interrupted):
        p.run_once(ACTOR)
    a.close()
    recovered = fixture_authority(a.path, allow_simulation=True)
    try:
        with pytest.raises(AuthorityError, match='execution_protocol_mismatch'):
            Simulator(recovered).reconcile(ACTOR, key(), op)
        result = ExecutionPipeline(recovered, p.policy, enabled=True).reconcile(ACTOR)
        assert len(result) == 1 and result[0]['result']['status'] == 'simulated_completed'
    finally:
        recovered.close()


@pytest.mark.parametrize('apply_effect', [False, True])
def test_legacy_simulation_keeps_its_own_recovery_protocol(env, apply_effect):
    a, _ = env
    op = key()
    a.submit(ACTOR, op, 'legacy synthetic fixture')
    sim = Simulator(a)
    claim = sim.claim(ACTOR, key(), op)['result']
    if apply_effect:
        sim.apply(ACTOR, key(), op, claim['claim_id'], claim['generation'])
    a.close()
    recovered = fixture_authority(a.path, allow_simulation=True)
    try:
        assert recovered.get_task(ACTOR, op)['status'] == 'unknown'
        result = Simulator(recovered).reconcile(ACTOR, key(), op)
        assert result['result']['status'] == ('simulated_completed' if apply_effect else 'cancelled')
        assert result['result']['resubmitted'] is False
    finally:
        recovered.close()


@pytest.mark.asyncio
@pytest.mark.parametrize('expiry', ['0001-01-01T00:00:00+23:00', '9999-12-31T23:59:59-23:00'])
async def test_extreme_expiry_is_http_400_without_admission(env, monkeypatch, expiry):
    import httpx
    from fastapi import FastAPI
    from app.agent.api import router
    from app.agent.execution import ExecutionWorker
    from app.config import settings
    a, p = env
    worker = ExecutionWorker(p, ACTOR)
    monkeypatch.setattr(runtime, '_authority', a)
    monkeypatch.setattr(runtime, '_execution_worker', worker)
    monkeypatch.setattr(settings.server, 'api_token', 'synthetic-gauntlet-client')
    app = FastAPI()
    app.include_router(router)
    await worker.start()
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://synthetic',
                                     headers={'Authorization': 'Bearer synthetic-gauntlet-client'}) as client:
            response = await client.post('/execution/tasks', json=dict(request_id=key(), goal='bounded input',
                capability='synthetic.echo', payload={'value': 'offline'}, expires_at=expiry))
        assert response.status_code == 400
        assert response.json()['error'] == 'invalid_time'
        assert a.list_tasks(ACTOR) == []
    finally:
        await worker.stop()

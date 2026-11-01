"""Independent interpreter/kill contracts; run only inside the fresh test cage.

At most the pytest parent plus one owned child exists at any instant. No PIPEs,
process groups, external services or real effects; every wait has a <=5s bound.
Fixtures use fresh private0700 directories under tmp_path. Process termination
is not physical disk power-loss evidence.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

import pytest

SOURCE = Path('/input/source')
if not Path(__file__).resolve().is_relative_to(Path('/input/tests')) or not SOURCE.is_dir() or not Path('/deps').is_dir():
    pytest.skip('fresh guarded cage mounts required; no host application imports', allow_module_level=True)

from app.agent.authority import Actor, Authority, AuthorityError
from app.agent.simulation import Simulator

ACTOR = Actor('synthetic-independent-process')
HELPER = Path(__file__).with_name('process_actor.py')
ACTIVE_CHILD = None


def fresh_state(tmp_path):
    state = tmp_path / 'state'
    state.mkdir(mode=0o700)
    assert state.stat().st_mode & 0o777 == 0o700
    return state / 'authority.sqlite'


def private_file(path):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    return os.fdopen(descriptor, 'wb')


def bounded_json(path):
    with path.open('rb') as stream:
        raw = stream.read(16385)
    assert len(raw) <= 16384, 'handoff exceeds fixture bound'
    return json.loads(raw)


def diagnostics(run):
    pieces = []
    for name in ('stdout.txt', 'stderr.txt', 'result.json'):
        path = run / name
        if path.is_file():
            with path.open('rb') as stream:
                pieces.append(name + ': ' + stream.read(16384).decode('utf-8', errors='replace'))
    return '\n'.join(pieces)


@contextmanager
def independent_actor(tmp_path, database, mode, **values):
    global ACTIVE_CHILD
    assert ACTIVE_CHILD is None, 'only one independent child is permitted'
    run = tmp_path / ('child-' + uuid4().hex)
    run.mkdir(mode=0o700)
    ready, result = run / 'ready.json', run / 'result.json'
    config = {'database': str(database), 'mode': mode, 'scope': ACTOR.scope,
              'ready': str(ready), 'result': str(result), **values}
    command_path = run / 'command.json'
    with private_file(command_path) as stream:
        stream.write(json.dumps(config).encode())
    # Do not inherit host credentials, PYTHONPATH, activation or provider settings.
    environment = {'HOME': str(run), 'TMPDIR': str(run), 'LANG': 'C.UTF-8',
                   'LC_ALL': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0'}
    child = None
    with private_file(run / 'stdout.txt') as stdout, private_file(run / 'stderr.txt') as stderr:
        try:
            child = subprocess.Popen([sys.executable, '-B', '-S', str(HELPER), str(command_path)],
                                     cwd=run, env=environment, stdin=subprocess.DEVNULL,
                                     stdout=stdout, stderr=stderr, close_fds=True)
            ACTIVE_CHILD = child
            yield child, ready, result, run
        finally:
            if child is not None:
                if child.poll() is None:
                    child.kill()  # Only this owned PID; never signal a process group.
                try:
                    child.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=1.0)
            ACTIVE_CHILD = None


def await_file(child, path, run):
    deadline = time.monotonic() + 4.0
    while time.monotonic() < deadline:
        if path.is_file():
            return bounded_json(path)  # Helper publishes only by atomic replace.
        if child.poll() is not None:
            pytest.fail('independent actor exited before handoff: ' + diagnostics(run))
        time.sleep(0.01)
    pytest.fail('bounded independent actor handoff timed out: ' + diagnostics(run))


def kill_ready(child):
    assert child.poll() is None, 'fault-ready child exited before parent kill'
    child.kill()
    child.wait(timeout=1.0)
    assert child.returncode is not None and child.returncode < 0


def event_count(authority, request_id):
    return authority._conn.execute('SELECT COUNT(*) FROM events WHERE request_id=?', (request_id,)).fetchone()[0]


def effect_count(authority, task_id):
    return authority._conn.execute('SELECT COUNT(*) FROM simulation_effects WHERE task_id=?', (task_id,)).fetchone()[0]


def test_live_independent_owner_excludes_parent_and_kill_releases_lock(tmp_path):
    database = fresh_state(tmp_path)
    with independent_actor(tmp_path, database, 'hold_owner') as (child, ready, result, run):
        held = await_file(child, ready, run)
        assert held['stage'] == 'owner_held'
        with pytest.raises(AuthorityError) as caught:
            Authority(database)
        assert caught.value.code == 'owner_busy'
        assert not result.exists()
        kill_ready(child)
    recovered = Authority(database)
    try:
        assert recovered.generation > held['generation']
        assert recovered.list_tasks(ACTOR) == []
    finally:
        recovered.close()


def test_parent_held_owner_refuses_fresh_probe_without_inherited_descriptors(tmp_path):
    database = fresh_state(tmp_path)
    owner = Authority(database)
    try:
        with independent_actor(tmp_path, database, 'probe') as (child, ready, result, run):
            outcome = await_file(child, result, run)
            child.wait(timeout=1.0)
            assert child.returncode == 0
            assert outcome == {'outcome': 'authority_error', 'code': 'owner_busy'}
            assert not ready.exists()
        assert owner.readiness()['storage_ready'] is True
    finally:
        owner.close()


@pytest.mark.parametrize('stage', ['before_commit', 'after_commit_before_ack'])
def test_killed_submit_recovers_same_request_and_exactly_one_task_receipt(tmp_path, stage):
    database = fresh_state(tmp_path)
    request_id = str(uuid4())
    goal = 'bounded synthetic independent submit'
    with independent_actor(tmp_path, database, 'submit', stage=stage, request_id=request_id, goal=goal) as (child, ready, result, run):
        reached = await_file(child, ready, run)
        assert reached['reached_stage'] == stage
        assert not result.exists(), 'no return acknowledgement should exist at fault boundary'
        kill_ready(child)
    recovered = Authority(database)
    try:
        existing = recovered.receipt(ACTOR, request_id)
        committed = stage == 'after_commit_before_ack'
        assert (existing is not None) is committed
        assert len(recovered.list_tasks(ACTOR)) == int(committed)
        assert event_count(recovered, request_id) == int(committed)
        receipt = recovered.submit(ACTOR, request_id, goal)
        assert receipt['replayed'] is committed
        if existing is not None:
            assert receipt['result'] == existing['result']
        again = recovered.submit(ACTOR, request_id, goal)
        assert again['replayed'] is True
        assert again['result'] == receipt['result']
        tasks = recovered.list_tasks(ACTOR)
        assert len(tasks) == 1
        assert tasks[0]['task_id'] == receipt['result']['task_id']
        assert (tasks[0]['status'], tasks[0]['outbox_state']) == ('pending', 'held')
        assert event_count(recovered, request_id) == 1
    finally:
        recovered.close()


@pytest.mark.parametrize('stage', ['after_claim', 'after_effect'])
def test_killed_simulation_becomes_unknown_and_reconciles_without_resubmission(tmp_path, stage):
    database = fresh_state(tmp_path)
    with independent_actor(tmp_path, database, 'simulate', stage=stage, goal='SQLite-only synthetic effect',
                           submit_id=str(uuid4()), claim_id=str(uuid4()), effect_id=str(uuid4())) as (child, ready, result, run):
        reached = await_file(child, ready, run)
        assert reached['reached_stage'] == stage
        assert not result.exists()
        kill_ready(child)
    recovered = Authority(database, allow_simulation=True)
    try:
        simulator = Simulator(recovered)
        tasks = recovered.list_tasks(ACTOR)
        assert len(tasks) == 1
        task = tasks[0]
        assert task['task_id'] == reached['task_id']
        assert (task['status'], task['outbox_state']) == ('unknown', 'unknown')
        assert recovered.readiness()['reconciliation_required'] == 1
        applied = int(stage == 'after_effect')
        assert effect_count(recovered, task['task_id']) == applied
        with pytest.raises(AuthorityError) as caught:
            simulator.claim(ACTOR, str(uuid4()), task['task_id'])
        assert caught.value.code == 'not_claimable'
        request_id = str(uuid4())
        receipt = simulator.reconcile(ACTOR, request_id, task['task_id'])
        expected = 'simulated_completed' if applied else 'cancelled'
        assert receipt['result'] == {'status': expected, 'evidence': 'synthetic_sqlite_effect_table', 'resubmitted': False}
        replay = simulator.reconcile(ACTOR, request_id, task['task_id'])
        assert replay['replayed'] is True
        assert replay['result'] == receipt['result']
        current = recovered.list_tasks(ACTOR)
        assert len(current) == 1
        assert (current[0]['status'], current[0]['outbox_state']) == (expected, expected)
        assert effect_count(recovered, task['task_id']) == applied
        assert event_count(recovered, request_id) == 1
        assert recovered.readiness()['reconciliation_required'] == 0
        with pytest.raises(AuthorityError) as caught:
            simulator.claim(ACTOR, str(uuid4()), task['task_id'])
        assert caught.value.code == 'not_claimable'
    finally:
        recovered.close()


@pytest.mark.parametrize('stage', ['before_commit', 'after_commit_before_ack'])
def test_killed_occurrence_keeps_task_last_run_and_receipt_atomic(tmp_path, stage):
    database = fresh_state(tmp_path)
    nominal, following = '2030-01-01T00:00:00+00:00', '2030-01-01T00:01:00+00:00'
    with independent_actor(tmp_path, database, 'occurrence', stage=stage,
                           schedule_request=str(uuid4()), control_request=str(uuid4()),
                           goal='synthetic scheduled enqueue', nominal=nominal, next_run_at=following) as (child, ready, result, run):
        reached = await_file(child, ready, run)
        assert reached['reached_stage'] == stage
        assert not result.exists()
        kill_ready(child)
    recovered = Authority(database)
    try:
        committed = stage == 'after_commit_before_ack'
        schedule = recovered.list_schedules(ACTOR)[0]
        assert schedule['job_id'] == reached['job_id']
        assert schedule['last_run'] == (nominal if committed else None)
        assert schedule['next_run_at'] == (following if committed else nominal)
        existing = recovered.receipt(ACTOR, reached['occurrence_id'])
        assert (existing is not None) is committed
        assert len(recovered.list_tasks(ACTOR)) == int(committed)
        assert event_count(recovered, reached['occurrence_id']) == int(committed)
        if committed:
            # Reopen disables scheduler admission, yet durable same-key receipt
            # replay must still return the original decision without another task.
            epoch = reached['epoch']
        else:
            epoch = recovered.scheduler_control(ACTOR, str(uuid4()), True)['result']['epoch']
        receipt = recovered.admit_occurrence(ACTOR, reached['job_id'], reached['revision'], nominal, epoch, following)
        assert receipt['request_id'] == reached['occurrence_id']
        assert receipt['replayed'] is committed
        repeated = recovered.admit_occurrence(ACTOR, reached['job_id'], reached['revision'], nominal, epoch, following)
        assert repeated['replayed'] is True
        assert repeated['result'] == receipt['result']
        tasks = recovered.list_tasks(ACTOR)
        assert len(tasks) == 1
        assert tasks[0]['task_id'] == reached['task_id'] == receipt['result']['task_id']
        assert tasks[0]['occurrence_id'] == reached['occurrence_id']
        schedule = recovered.list_schedules(ACTOR)[0]
        assert (schedule['last_run'], schedule['next_run_at']) == (nominal, following)
        assert event_count(recovered, reached['occurrence_id']) == 1
        assert recovered._conn.execute("SELECT COUNT(*) FROM records WHERE kind='occurrence' AND id=?",
                                       (reached['occurrence_id'],)).fetchone()[0] == 1
    finally:
        recovered.close()

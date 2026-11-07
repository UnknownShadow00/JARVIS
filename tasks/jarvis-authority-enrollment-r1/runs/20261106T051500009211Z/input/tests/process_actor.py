"""One fresh, cage-only synthetic authority actor; never launch from the host.

This helper opens only the explicit test database/config under its parent's
private temporary fixture tree. It never starts an app/backend or real executor.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import uuid

SOURCE = Path('/input/source')
DEPS = Path('/deps')
if not Path(__file__).resolve().is_relative_to(Path('/input/tests')) or not SOURCE.is_dir() or not DEPS.is_dir():
    raise SystemExit('fresh_cage_required')
# -S disables site discovery. These two explicit, parent-approved cage mounts are
# the only application/dependency lookup additions; no candidate package runs.
sys.path[:0] = [str(SOURCE), str(DEPS)]

from app.agent.authority import Actor, Authority, AuthorityError
from synthetic_authority import fixture_authority as Authority
from app.agent.simulation import Simulator


def atomic_json(path, value):
    raw = json.dumps(value, sort_keys=True).encode('utf-8')
    if len(raw) > 16384:
        raise ValueError('bounded_handoff_required')
    temporary = path.with_name('.' + path.name + '.' + str(os.getpid()) + '.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def hold(ready, value):
    atomic_json(ready, value)
    # Parent must kill/reap its own child promptly. This bound also prevents an
    # orphan helper from waiting forever if its parent exits unexpectedly.
    deadline = time.monotonic() + 4.0
    while time.monotonic() < deadline:
        time.sleep(0.01)
    raise RuntimeError('parent_did_not_terminate_ready_actor')


def run(config):
    database = Path(config['database'])
    ready = Path(config['ready'])
    result = Path(config['result'])
    actor = Actor(config['scope'])
    mode = config['mode']
    stage = config.get('stage')
    armed = False
    details = {'mode': mode, 'stage': stage, 'request_id': config.get('request_id')}

    def fault(current):
        if armed and current == stage:
            hold(ready, {**details, 'reached_stage': current})

    authority = None
    try:
        authority = Authority(database, allow_simulation=mode == 'simulate', fault_hook=fault)
        if mode == 'probe':
            atomic_json(result, {'outcome': 'opened', 'generation': authority.generation})
            return
        if mode == 'hold_owner':
            hold(ready, {'mode': mode, 'stage': 'owner_held', 'generation': authority.generation})
        elif mode == 'submit':
            armed = True
            receipt = authority.submit(actor, config['request_id'], config['goal'])
            atomic_json(result, {'outcome': 'returned', 'receipt': receipt})
        elif mode == 'simulate':
            simulator = Simulator(authority)
            task = authority.submit(actor, config['submit_id'], config['goal'])['result']
            claim = simulator.claim(actor, config['claim_id'], task['task_id'])['result']
            details.update(task_id=task['task_id'], claim_id=claim['claim_id'], generation=claim['generation'])
            if stage == 'after_claim':
                hold(ready, {**details, 'reached_stage': stage})
            simulator.apply(actor, config['effect_id'], task['task_id'], claim['claim_id'], claim['generation'])
            if stage != 'after_effect':
                raise ValueError('unsupported_simulation_stage')
            hold(ready, {**details, 'reached_stage': stage})
        elif mode == 'occurrence':
            job = authority.add_schedule(actor, config['schedule_request'], 'synthetic schedule',
                                         '* * * * *', config['goal'], config['nominal'])['result']
            control = authority.scheduler_control(actor, config['control_request'], True)['result']
            occurrence = str(uuid.uuid5(uuid.UUID(job['job_id']), f"{job['revision']}:{job['next_run_at']}"))
            details.update(job_id=job['job_id'], revision=job['revision'], nominal=job['next_run_at'],
                           next_run_at=config['next_run_at'], epoch=control['epoch'],
                           occurrence_id=occurrence,
                           task_id=occurrence)
            armed = True
            receipt = authority.admit_occurrence(actor, job['job_id'], job['revision'], job['next_run_at'],
                                                 control['epoch'], config['next_run_at'])
            atomic_json(result, {'outcome': 'returned', 'receipt': receipt})
        else:
            raise ValueError('unsupported_synthetic_mode')
    except AuthorityError as exc:
        atomic_json(result, {'outcome': 'authority_error', 'code': exc.code})
    finally:
        if authority is not None:
            authority.close()


def main():
    if len(sys.argv) != 2:
        raise SystemExit('explicit_test_config_required')
    with open(sys.argv[1], 'rb') as stream:
        raw = stream.read(16385)
    if len(raw) > 16384:
        raise SystemExit('bounded_test_config_required')
    run(json.loads(raw))


if __name__ == '__main__':
    main()

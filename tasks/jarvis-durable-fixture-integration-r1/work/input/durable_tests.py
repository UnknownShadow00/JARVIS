"""Seven distinct real-ASGI/disk-backed interoperability cases; no prior suite rerun."""
import ast
from dataclasses import asdict
from datetime import datetime
import asyncio
import errno
import itertools
import json
from pathlib import Path
import sys
import types
from typing import Any
from unittest import mock

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel
import pytest

counter = itertools.count()


class AuditRecorder:
    def __init__(self):self.events = []
    def log(self, name, fields):self.events.append((name, fields))


def definitions(relative, wiring, singleton=None, names=None):
    path = Path('/input/source') / relative
    tree = ast.parse(path.read_text(), filename=str(path))
    kept = []
    for node in tree.body:
        if names is not None:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in names:
                node.decorator_list = []
                kept.append(node)
            elif isinstance(node, ast.ImportFrom) and node.module == '__future__':kept.append(node)
        else:
            if isinstance(node, ast.ImportFrom) and node.module in {'app.agent.task_queue', 'app.logs.audit'}:continue
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == singleton for target in node.targets):continue
            kept.append(node)
    tree.body = kept
    module = types.ModuleType(f'durable_fixture_{next(counter)}')
    module.__file__ = str(path)
    module.__dict__.update(wiring)
    sys.modules[module.__name__] = module
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module


@pytest.fixture
def env(tmp_path):
    audit = AuditRecorder()
    queue_module = definitions('app/agent/task_queue.py', {'audit': audit}, 'task_queue')
    tasks, jobs = tmp_path / 'tasks.json', tmp_path / 'jobs.json'
    queue = queue_module.TaskQueue(tasks)
    wiring = {'audit': audit, 'task_queue': queue}
    wiring.update({name: getattr(queue_module, name) for name in ['TaskQueuePersistenceError', 'TaskQueueAuditError', 'TaskQueueIdentifierError']})
    scheduler_module = definitions('app/agent/scheduler.py', wiring, 'scheduler')
    owner = scheduler_module.Scheduler(jobs)
    names = {'TaskCreateRequest', 'TaskStatusRequest', 'ScheduledJobRequest', '_task_write_error', '_schedule_write_error',
             'create_task', 'list_tasks', 'get_task', 'update_task', 'delete_task',
             'create_scheduled_job', 'list_scheduled_jobs', 'delete_scheduled_job'}
    api = definitions('app/server.py', {**wiring, 'scheduler': owner, 'BaseModel': BaseModel, 'Any': Any,
                      'asdict': asdict, 'JSONResponse': JSONResponse,
                      'SchedulerOperationError': scheduler_module.SchedulerOperationError}, names=names)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    for path, name, method in [('/tasks', 'create_task', 'POST'), ('/tasks', 'list_tasks', 'GET'),
                               ('/tasks/{task_id}', 'get_task', 'GET'), ('/tasks/{task_id}', 'update_task', 'PATCH'),
                               ('/tasks/{task_id}', 'delete_task', 'DELETE'),
                               ('/schedule/jobs', 'create_scheduled_job', 'POST'), ('/schedule/jobs', 'list_scheduled_jobs', 'GET'),
                               ('/schedule/jobs/{job_id}', 'delete_scheduled_job', 'DELETE')]:
        app.add_api_route(path, getattr(api, name), methods=[method])
    return types.SimpleNamespace(app=app, api=api, queue=queue, owner=owner, audit=audit,
                                 queue_module=queue_module, scheduler_module=scheduler_module,
                                 tasks=tasks, jobs=jobs)


def client(env):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=env.app), base_url='http://durable-fixture.invalid', trust_env=False)


async def reloaded_tasks(env):
    # Readback only: reconstructed objects never start/write or compete as owners.
    return await env.queue_module.TaskQueue(env.tasks).list_tasks()


@pytest.mark.asyncio
async def test_task_asgi_create_update_delete_reconstructs_real_store(env):
    async with client(env) as http:
        created = await http.post('/tasks', json={'goal': ' synthetic durable task '})
        assert created.status_code == 200
        identifier = created.json()['task_id']
        assert [asdict(task) for task in await reloaded_tasks(env)] == [created.json()]
        assert json.loads(env.tasks.read_text())[0]['goal'] == ' synthetic durable task '
        updated = await http.patch('/tasks/' + identifier, json={'status': 'done', 'result': {'synthetic': True}})
        assert updated.status_code == 200
        assert [asdict(task) for task in await reloaded_tasks(env)] == [updated.json()]
        assert (await http.delete('/tasks/' + identifier)).json() == {'deleted': True}
        assert await reloaded_tasks(env) == [] and json.loads(env.tasks.read_text()) == []


@pytest.mark.asyncio
async def test_schedule_asgi_create_remove_reconstructs_real_store(env):
    async with client(env) as http:
        created = await http.post('/schedule/jobs', json={'name': ' fixture ', 'cron_expr': '0 0 1 1 *', 'goal': ' durable synthetic '})
        assert created.status_code == 200
        identifier = created.json()['job_id']
        loaded = env.scheduler_module.Scheduler(env.jobs).list_jobs()
        assert [asdict(job) for job in loaded] == [created.json()]
        assert (await http.delete('/schedule/jobs/' + identifier)).json() == {'deleted': True}
        assert env.scheduler_module.Scheduler(env.jobs).list_jobs() == []
        assert json.loads(env.jobs.read_text()) == []


@pytest.mark.asyncio
async def test_registered_callback_persists_task_last_run_needs_later_job_snapshot(env):
    async with client(env) as http:
        created = (await http.post('/schedule/jobs', json={'name': 'callback fixture', 'cron_expr': '0 0 1 1 *', 'goal': 'synthetic callback record'})).json()
        job = env.owner.list_jobs()[0]
        assert job.last_run is None
        await env.owner.start()
        try:
            registered = env.owner._scheduler.get_job(created['job_id'])
            assert registered.func.__self__ is env.owner
            await registered.func(*registered.args)  # Actual registered callback, explicitly invoked; no new clock test.
            loaded = await reloaded_tasks(env)
            assert len(loaded) == 1 and loaded[0].goal == 'synthetic callback record'
            assert loaded[0].status == 'pending'
            datetime.fromisoformat(job.last_run)
            assert env.scheduler_module.Scheduler(env.jobs).list_jobs()[0].last_run is None
            assert json.loads(env.jobs.read_text())[0]['last_run'] is None
            # Existing add_job publishes the entire snapshot incidentally; this
            # is not an atomic occurrence/task/outbox commit or a new policy.
            response = await http.post('/schedule/jobs', json={'name': 'snapshot fixture', 'cron_expr': '0 0 1 1 *', 'goal': 'not executed'})
            assert response.status_code == 200
            reloaded = {item.job_id: item for item in env.scheduler_module.Scheduler(env.jobs).list_jobs()}
            assert reloaded[job.job_id].last_run == job.last_run
            assert len(await reloaded_tasks(env)) == 1
        finally:
            await env.owner.stop()
            await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_task_real_pre_replace_failure_returns_503_preserves_store_and_reload(env):
    async with client(env) as http:
        seed = await http.post('/tasks', json={'goal': 'original durable record'})
        before = env.tasks.read_bytes()
        with mock.patch.object(env.queue_module.os, 'replace', side_effect=OSError(errno.EIO, 'synthetic replace interruption')) as replaced:
            response = await http.post('/tasks', json={'goal': 'must not persist'})
        assert replaced.call_count == 1
        assert response.status_code == 503 and response.json()['publication'] == 'not_published'
        assert env.tasks.read_bytes() == before
        assert [asdict(task) for task in await reloaded_tasks(env)] == [seed.json()]
        assert await env.queue.get_task(response.json()['task_id']) is None
        assert list(env.tasks.parent.glob('.tasks.json.*.tmp')) == []


@pytest.mark.asyncio
async def test_task_real_replace_sync_fault_readback_is_uncertain_not_retry_permission(env):
    async with client(env) as http:
        await http.post('/tasks', json={'goal': 'original durable record'})
        with mock.patch.object(env.queue, '_sync_directory', side_effect=OSError(errno.EIO, 'synthetic sync interruption')):
            response = await http.post('/tasks', json={'goal': 'visible but uncertain'})
        assert response.status_code == 409
        body = response.json()
        assert body['publication'] == 'published_durability_unknown'
        assert body['reconcile_required'] is True and body['automatic_retry'] is False
        loaded = {task.task_id: task for task in await reloaded_tasks(env)}
        assert loaded[body['task_id']].goal == 'visible but uncertain'
        assert env.queue._persistence_uncertain is True
        before = env.tasks.read_bytes()
        rejected = await http.post('/tasks', json={'goal': 'blocked same owner'})
        assert rejected.status_code == 503 and rejected.json()['publication'] == 'not_published'
        assert env.tasks.read_bytes() == before and len(await reloaded_tasks(env)) == 2


@pytest.mark.asyncio
async def test_schedule_real_pre_replace_failure_keeps_backend_and_disk_state(env):
    async with client(env) as http:
        seed = (await http.post('/schedule/jobs', json={'name': 'seed', 'cron_expr': '0 0 1 1 *', 'goal': 'not executed'})).json()
        await env.owner.start()
        try:
            before = env.jobs.read_bytes()
            ids = {job.id for job in env.owner._scheduler.get_jobs()}
            with mock.patch.object(env.scheduler_module.os, 'replace', side_effect=OSError(errno.EIO, 'synthetic replace interruption')):
                response = await http.post('/schedule/jobs', json={'name': 'not saved', 'cron_expr': '0 0 1 1 *', 'goal': 'not executed'})
            assert response.status_code == 503 and response.json()['state_applied'] is False
            assert env.jobs.read_bytes() == before
            assert {job.id for job in env.owner._scheduler.get_jobs()} == ids
            assert [asdict(job) for job in env.scheduler_module.Scheduler(env.jobs).list_jobs()] == [seed]
            assert not env.tasks.exists()
        finally:
            await env.owner.stop()
            await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_schedule_real_replace_sync_fault_keeps_retained_callback_nonadmitting(env):
    async with client(env) as http:
        seed = (await http.post('/schedule/jobs', json={'name': 'seed', 'cron_expr': '0 0 1 1 *', 'goal': 'must not enqueue'})).json()
        await env.owner.start()
        try:
            retained = env.owner._scheduler.get_job(seed['job_id'])
            with mock.patch.object(env.owner, '_sync_directory', side_effect=OSError(errno.EIO, 'synthetic job sync interruption')):
                response = await http.delete('/schedule/jobs/' + seed['job_id'])
            assert response.status_code == 409
            assert response.json()['publication'] == 'published_durability_unknown'
            assert response.json()['reconcile_required'] is True
            assert env.owner._persistence_uncertain is True
            assert env.scheduler_module.Scheduler(env.jobs).list_jobs() == []
            assert env.owner._scheduler.get_job(seed['job_id']) is not None
            await retained.func(*retained.args)
            assert not env.tasks.exists() and await reloaded_tasks(env) == []
            before = env.jobs.read_bytes()
            rejected = await http.post('/schedule/jobs', json={'name': 'blocked', 'cron_expr': '0 0 1 1 *', 'goal': 'blocked'})
            assert rejected.status_code == 503 and rejected.json()['phase'] == 'admission'
            assert rejected.json()['reconcile_required'] is True and env.jobs.read_bytes() == before
        finally:
            await env.owner.stop()
            await asyncio.sleep(0)

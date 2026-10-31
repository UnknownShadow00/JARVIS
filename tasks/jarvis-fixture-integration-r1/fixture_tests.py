"""Real frameworks around extracted current handlers; synthetic in-memory records only."""
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import importlib.metadata
import itertools
from pathlib import Path
import sys
import types
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel
from pydantic_core import SchemaValidator
import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

counter = itertools.count()


class AuditRecorder:
    def __init__(self):
        self.events = []

    def log(self, name, details):
        self.events.append((name, details))


def definitions(relative, wiring, singleton=None, names=None):
    path = Path('/input/source') / relative
    tree = ast.parse(path.read_text(), filename=str(path))
    nodes = []
    for node in tree.body:
        if names is not None:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in names:
                node.decorator_list = []
                nodes.append(node)
            elif isinstance(node, ast.ImportFrom) and node.module == '__future__':
                nodes.append(node)
        else:
            if isinstance(node, ast.ImportFrom) and node.module in {'app.logs.audit', 'app.agent.task_queue'}:
                continue
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == singleton for target in node.targets):
                continue
            nodes.append(node)
    tree.body = nodes
    module = types.ModuleType(f'fixture_{next(counter)}')
    module.__file__ = str(path)
    module.__dict__.update(wiring)
    sys.modules[module.__name__] = module
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module


@pytest.fixture
def environment():
    from dataclasses import asdict
    audit = AuditRecorder()
    queue_module = definitions('app/agent/task_queue.py', {'audit': audit}, singleton='task_queue')
    queue = queue_module.TaskQueue()  # No file store and no real default singleton.
    wiring = {'audit': audit, 'task_queue': queue}
    wiring.update({name: getattr(queue_module, name) for name in ['TaskQueuePersistenceError', 'TaskQueueAuditError', 'TaskQueueIdentifierError']})
    scheduler_module = definitions('app/agent/scheduler.py', wiring, singleton='scheduler')
    owner = scheduler_module.Scheduler()  # No scheduled-job store/default singleton.
    names = {'TaskCreateRequest', 'TaskStatusRequest', 'ScheduledJobRequest',
             'create_task', 'list_tasks', 'get_task', 'update_task', 'delete_task', '_task_write_error',
             'create_scheduled_job', 'list_scheduled_jobs', 'delete_scheduled_job', '_schedule_write_error'}
    api = definitions('app/server.py', {**wiring, 'scheduler': owner, 'BaseModel': BaseModel,
                      'Any': Any, 'asdict': asdict, 'JSONResponse': JSONResponse,
                      'SchedulerOperationError': scheduler_module.SchedulerOperationError}, names=names)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    for path, name, methods in [('/tasks', 'create_task', ['POST']), ('/tasks', 'list_tasks', ['GET']),
                                ('/tasks/{task_id}', 'get_task', ['GET']), ('/tasks/{task_id}', 'update_task', ['PATCH']),
                                ('/tasks/{task_id}', 'delete_task', ['DELETE']),
                                ('/schedule/jobs', 'create_scheduled_job', ['POST']),
                                ('/schedule/jobs', 'list_scheduled_jobs', ['GET']),
                                ('/schedule/jobs/{job_id}', 'delete_scheduled_job', ['DELETE'])]:
        app.add_api_route(path, getattr(api, name), methods=methods)
    return types.SimpleNamespace(app=app, api=api, audit=audit, queue=queue, queue_module=queue_module,
                                 owner=owner, scheduler_module=scheduler_module)


def client(env):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=env.app), base_url='http://fixture.invalid')


def test_native_pydantic_and_installed_origin(environment):
    import pydantic_core
    assert SchemaValidator({'type': 'int'}).validate_python('42') == 42
    assert pydantic_core.__version__ == '2.46.5'
    assert pydantic_core.__file__.startswith('/work/site-packages/')
    assert environment.api.TaskStatusRequest(status='done', result={'ok': True}).model_dump()['result'] == {'ok': True}


@pytest.mark.asyncio
async def test_task_crud_and_real_pydantic_422(environment):
    async with client(environment) as http:
        assert (await http.post('/tasks', json={})).status_code == 422
        assert (await http.post('/tasks', json={'goal': ['invalid']})).status_code == 422
        created = await http.post('/tasks', json={'goal': 'synthetic fixture only'})
        assert created.status_code == 200
        identifier = created.json()['task_id']
        assert (await http.get('/tasks')).json()['count'] == 1
        assert (await http.get('/tasks/' + identifier)).json()['goal'] == 'synthetic fixture only'
        assert (await http.patch('/tasks/' + identifier, json={'status': 'done', 'result': []})).status_code == 422
        assert (await http.patch('/tasks/' + identifier, json={'status': 'done', 'result': {'synthetic': True}})).json()['status'] == 'done'
        assert (await http.delete('/tasks/' + identifier)).json() == {'deleted': True}
        assert (await http.delete('/tasks/' + identifier)).json() == {'deleted': False}
        assert (await http.get('/tasks/' + identifier)).status_code == 404


@pytest.mark.parametrize('operation', ['create', 'update', 'delete'])
@pytest.mark.parametrize('published', [False, True])
@pytest.mark.asyncio
async def test_task_fault_injected_outcome_real_asgi(environment, monkeypatch, operation, published):
    task = await environment.queue.add_task('seed synthetic')
    def failed():
        raise environment.queue_module.TaskQueuePersistenceError('private synthetic detail', published=published)
    monkeypatch.setattr(environment.queue, '_save', failed)
    async with client(environment) as http:
        if operation == 'create':
            response = await http.post('/tasks', json={'goal': 'fault injection'})
        elif operation == 'update':
            response = await http.patch('/tasks/' + task.task_id, json={'status': 'done'})
        else:
            response = await http.delete('/tasks/' + task.task_id)
    assert response.status_code == (409 if published else 503)
    body = response.json()
    assert body['publication'] == ('published_durability_unknown' if published else 'not_published')
    assert body['operation'] == operation and len(body['task_id']) == 8
    assert body['automatic_retry'] is False
    assert 'private synthetic detail' not in response.text


@pytest.mark.parametrize('operation', ['create', 'update', 'delete'])
@pytest.mark.asyncio
async def test_applied_memory_audit_failure_real_asgi(environment, monkeypatch, operation):
    task = await environment.queue.add_task('seed synthetic')
    def failed(*args):
        raise RuntimeError('private audit fixture')
    monkeypatch.setattr(environment.audit, 'log', failed)
    async with client(environment) as http:
        if operation == 'create':response = await http.post('/tasks', json={'goal': 'new synthetic'})
        elif operation == 'update':response = await http.patch('/tasks/' + task.task_id, json={'status': 'done'})
        else:response = await http.delete('/tasks/' + task.task_id)
    assert response.status_code == 409
    assert response.json()['publication'] == 'memory_applied_audit_failed'
    assert response.json()['reconcile_required'] is True
    assert 'private audit fixture' not in response.text


@pytest.mark.asyncio
async def test_schedule_parser_schema_crud_real_asgi(environment):
    assert isinstance(CronTrigger.from_crontab('0 0 1 1 *', timezone=timezone.utc), CronTrigger)
    async with client(environment) as http:
        assert (await http.post('/schedule/jobs', json={})).status_code == 422
        response = await http.post('/schedule/jobs', json={'name': 'bad', 'cron_expr': 'bad cron', 'goal': 'synthetic'})
        assert response.status_code == 400 and response.json()['phase'] == 'validation'
        assert environment.owner.list_jobs() == []
        response = await http.post('/schedule/jobs', json={'name': 'fixture', 'cron_expr': '0 0 1 1 *', 'goal': 'synthetic'})
        assert response.status_code == 200
        identifier = response.json()['job_id']
        assert (await http.get('/schedule/jobs')).json()['count'] == 1
        assert (await http.delete('/schedule/jobs/' + identifier)).json() == {'deleted': True}
        assert (await http.delete('/schedule/jobs/' + identifier)).json() == {'deleted': False}


@pytest.mark.parametrize('published', [False, True])
@pytest.mark.asyncio
async def test_schedule_fault_injected_real_asgi(environment, monkeypatch, published):
    def failed():
        raise environment.scheduler_module.SchedulerOperationError('private schedule detail', applied=published, published=published, uncertain=published)
    monkeypatch.setattr(environment.owner, '_save', failed)
    async with client(environment) as http:
        response = await http.post('/schedule/jobs', json={'name': 'fixture', 'cron_expr': '0 0 1 1 *', 'goal': 'synthetic'})
    assert response.status_code == (409 if published else 503)
    assert response.json()['state_applied'] is published
    assert response.json()['automatic_retry'] is False
    assert 'private schedule detail' not in response.text


@pytest.mark.asyncio
async def test_actual_backend_manual_callback_and_lifecycle(environment):
    owner, queue = environment.owner, environment.queue
    job = owner.add_job('fixture', '0 0 1 1 *', 'synthetic only')
    await owner.start()
    first_backend = owner._scheduler
    assert isinstance(first_backend, AsyncIOScheduler) and first_backend.running
    registered = first_backend.get_job(job.job_id)
    assert registered.func.__self__ is owner
    await registered.func(*registered.args)
    assert len(await queue.list_tasks()) == 1 and job.last_run is not None
    job.enabled = False
    await registered.func(*registered.args)
    assert len(await queue.list_tasks()) == 1
    job.enabled = True
    await owner.stop()
    await asyncio.sleep(0)
    assert not first_backend.running
    await owner.start()
    try:
        await registered.func(*registered.args)
        assert len(await queue.list_tasks()) == 1
        current = owner._scheduler.get_job(job.job_id)
        assert owner.remove_job(job.job_id) is True
        await current.func(*current.args)
        assert len(await queue.list_tasks()) == 1
    finally:
        await owner.stop()
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_actual_one_shot_callback_synthetic_only(environment):
    owner, queue = environment.owner, environment.queue
    job = owner.add_job('fixture timer', '0 0 1 1 *', 'synthetic timed record only')
    await owner.start()
    try:
        owner._scheduler.reschedule_job(job.job_id, trigger=DateTrigger(run_date=datetime.now(timezone.utc) + timedelta(milliseconds=50)))
        deadline = asyncio.get_running_loop().time() + 2
        while not await queue.list_tasks() and asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(0.01)
        tasks = await queue.list_tasks()
        assert len(tasks) == 1 and tasks[0].goal == 'synthetic timed record only'
        assert job.last_run is not None
        await asyncio.sleep(0.05)
        assert len(await queue.list_tasks()) == 1
    finally:
        await owner.stop()
        await asyncio.sleep(0)

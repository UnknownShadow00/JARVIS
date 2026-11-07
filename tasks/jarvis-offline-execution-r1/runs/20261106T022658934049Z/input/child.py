"""Actual app.main/server/lifespan with synthetic configuration, no HTTP listener."""
import ast
import asyncio
from datetime import UTC, datetime
import errno
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import sys
import traceback
import uuid

report={'status':'NOT_STARTED','started_at':datetime.now(UTC).isoformat()}
try:
    expected=json.loads(Path('/input/expected.json').read_text())
    guard=Path('/input/guard.py').read_bytes()
    assert hashlib.sha256(guard).hexdigest()==expected['guard_sha256']
    nodes=[n for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef) and n.name=='boundaries']
    assert len(nodes)==1
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'/input/guard.py','exec'),globals())
    report['boundaries']=boundaries(expected)
    assert os.statvfs('/deps').f_flag & os.ST_RDONLY
    versions={d.metadata['Name'].lower().replace('_','-'):d.version for d in importlib.metadata.distributions(path=['/deps'])}
    assert versions==expected['versions']
    sys.path.insert(0,'/deps')
    import yaml
    import psutil
    from pydantic_core import SchemaValidator
    assert SchemaValidator({'type':'int'}).validate_python('42')==42
    assert yaml.load('synthetic: 1',Loader=yaml.CSafeLoader)=={'synthetic':1}
    assert psutil.Process().memory_info().rss>0
    report['native_execution']={}
    for name in ['pydantic_core._pydantic_core','yaml._yaml','psutil._psutil_linux']:
        module=importlib.import_module(name)
        path=Path(module.__file__)
        assert str(path).startswith('/deps/')
        report['native_execution'][name]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    project=Path('/work/project')
    shutil.copytree('/input/source/app',project/'app')
    raw=yaml.safe_load(Path('/input/source/config.yaml').read_text())
    raw['models']['ollama_base_url']='http://127.0.0.1:9'
    for name in ['main','coder','router','vision']:raw['models'][name]='synthetic-unused'
    raw['safety']['dry_run']=True
    raw['server'].update(host='127.0.0.1',api_token='',remote_access_enabled=False,enable_voice_on_startup=False,enable_hotkey_listener=False)
    raw['resource_mode'].update(enabled=False,preload_primary_model_on_wake=False,auto_light_sleep=False,auto_deep_sleep=False)
    raw['routing']['embedding_enabled']=False
    for key in ['mem0_enabled','chromadb_enabled','graphiti_enabled']:raw['memory'][key]=False
    raw['memory'].update(mem0_base_url='http://127.0.0.1:9',neo4j_uri='bolt://127.0.0.1:9',chromadb_path='/work/synthetic-memory',index_paths=[],neo4j_password_env='SYNTHETIC_UNUSED')
    raw['comms'].update(discord_enabled=False,telegram_enabled=False,discord_token='',telegram_token='',discord_channel_id='',telegram_chat_id='')
    raw['agent']['hermes_enabled']=False
    raw['tools']['obsidian_enabled']=False
    raw['tools']['obsidian_vault_path']='/work/synthetic-vault'
    raw['boot']['enabled']=False
    for name in raw['paths']:raw['paths'][name]='/work/synthetic-'+name
    raw['logging'].update(audit_log='/work/synthetic-audit.jsonl',log_file='/work/synthetic-app.log',log_to_file=False)
    raw['openjarvis'].update(trace_logging_enabled=False,optimization_enabled=False,traces_dir='/work/synthetic-traces')
    (project/'config.yaml').write_text(json.dumps(raw))
    report['synthetic_config_sha256']=hashlib.sha256((project/'config.yaml').read_bytes()).hexdigest()
    sys.path.insert(0,str(project))
    from app.main import app
    from app import server
    from app.agent import runtime
    from app.agent.scheduler import scheduler
    from app.agent.authority import Authority, AuthorityError
    import httpx
    report['entrypoint_origin']=sys.modules['app.main'].__file__
    report['server_origin']=server.__file__
    assert app is server.app
    results=[]
    async def check():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
                for path in ['/health','/resource/status','/memory/skills']:
                    response=await client.get(path)
                    assert response.status_code==200,(path,response.status_code)
                ready=await client.get('/ready')
                assert ready.status_code==200 and ready.json()['execution_enabled'] is False
                key=str(uuid.uuid4());body={'request_id':key,'goal':'synthetic inspection'}
                first=await client.post('/tasks',json=body)
                assert first.status_code==200 and first.json()['scope']=='local-service'
                replay=await client.post('/tasks',json=body)
                assert replay.json()['replayed'] and replay.json()['result']==first.json()['result']
                # Existing optional bearer enforcement, using a synthetic token.
                server.settings.server.api_token='fixture-token-only'
                assert (await client.get('/tasks')).status_code==401
                assert (await client.get('/tasks',headers={'Authorization':'Bearer fixture-token-only'})).status_code==200
                server.settings.server.api_token=''
                assert (await client.get('/tasks')).status_code==200
                assert (await client.patch('/tasks/'+first.json()['result']['task_id'],json={'status':'completed'})).status_code==405
                results.append('actual_entrypoint_full_lifespan_readiness_routes_auth_and_idempotency')
        assert runtime._authority is None and scheduler._backend is None
        results.append('actual_lifespan_shutdown_releases_authority_and_scheduler')
        # Explicit offline embedding into the actual entrypoint/lifespan.
        from app.agent.execution import SimulatedPolicy, phase_id
        from app.agent.reporter import reporter
        offline = Authority('/work/offline/state.sqlite', allow_simulation=True)
        runtime.bind_authority(offline)
        worker = runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope))
        demo = {'real_execution_enabled': False, 'transport': 'actual_app_ASGI_no_listener'}
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://synthetic') as client:
                assert (await client.get('/ready')).json()['execution_worker_ready']
                key = str(uuid.uuid4())
                from datetime import timedelta
                body = dict(request_id=key, goal='synthetic application workflow', capability='synthetic.echo', payload={'value':'JARVIS offline pipeline'}, expires_at=(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
                server.settings.server.api_token='offline-fixture-token'
                assert (await client.post('/execution/tasks',json=body)).status_code == 401
                assert (await client.post('/execution/tasks',content=b'x'*262145)).status_code == 401
                client.headers['Authorization']='Bearer offline-fixture-token'
                assert (await client.post('/execution/tasks',content=b'x'*262145)).status_code == 413
                admitted = await client.post('/execution/tasks',json=body)
                assert admitted.status_code == 200
                for _ in range(100):
                    current = (await client.get('/tasks/'+key)).json()
                    if current['status']=='simulated_completed':break
                    await asyncio.sleep(.01)
                assert current['result']['output']=='JARVIS offline pipeline'
                demo['admission']=admitted.json()
                demo['status']=current
                demo['publication_receipt']=(await client.get('/requests/'+phase_id(key,'publish'))).json()
                assert demo['publication_receipt']['operation']=='execution_publish'
                assert (await client.post('/execution/tasks',json=body)).json()['replayed']
                assert (await client.post('/execution/tasks',json={**body,'payload':{'value':'conflicting'}})).status_code==409
                denied=(await client.post('/execution/tasks',json={**body,'request_id':str(uuid.uuid4()),'capability':'proxmox.console'})).json()
                assert denied['result']['status']=='denied'
                demo['denied']=denied
                report=await reporter.build_report()
                assert 'simulated_completed=1' in report and 'denied=1' in report
                demo['operator_report']=report
                assert (await client.patch('/tasks/'+key,json={'result':'forged'})).status_code==405
                # Existing CLI consumes the actual status snapshot. Its HTTP
                # helper is intercepted so the fixture cannot call a listener.
                from app import cli
                from unittest.mock import patch
                import contextlib, io
                captured=io.StringIO()
                with patch.object(cli,'_get',return_value=current), contextlib.redirect_stdout(captured):
                    assert cli.main(['tasks','--task-id',key])==0
                assert json.loads(captured.getvalue())['status']=='simulated_completed'
                demo['cli_status']=json.loads(captured.getvalue())
                with patch.object(cli.httpx,'get') as get:
                    get.return_value.json.return_value=current
                    assert cli._get('/tasks/'+key)==current
                    assert get.call_args.kwargs['headers']=={'Authorization':'Bearer offline-fixture-token'}
                with patch.object(cli,'_get',return_value=None), contextlib.redirect_stderr(io.StringIO()):
                    assert cli.main(['tasks'])==1
                with patch.object(cli,'_get',side_effect=AssertionError('invalid UUID reached transport')), contextlib.redirect_stderr(io.StringIO()):
                    assert cli.main(['tasks','--task-id','invalid'])==2
                # Stop suspends the worker, so API cannot admit runnable work.
                assert (await client.post('/stop')).status_code==200
                stopped_ready=await client.get('/ready')
                assert stopped_ready.status_code==503 and not stopped_ready.json()['execution_worker_ready']
                assert (await client.post('/execution/tasks',json={**body,'request_id':str(uuid.uuid4())})).status_code==503
                held_id=str(uuid.uuid4())
                held=await client.post('/tasks',json={'request_id':held_id,'goal':'held cancellation demo'})
                assert held.status_code==200
                cancelled=await client.delete('/tasks/'+held_id,params={'request_id':str(uuid.uuid4())})
                assert cancelled.json()['result']['status']=='cancelled'
                demo['cancellation']=cancelled.json()
                await worker.start()
                # Exercise the real background service hooks used by sleep/wake.
                actions=[]
                await server.resource_manager._stop_background_services(actions)
                assert worker._task is None and 'synthetic_execution_worker_stopped' in actions
                await server.resource_manager._start_required_services(actions)
                assert worker.readiness()['execution_worker_ready']
                results.append('actual_app_synthetic_pipeline_auth_receipts_status_reporter_cli_stop_sleep_wake')
                server.settings.server.api_token=''
        assert runtime._authority is None and runtime.get_execution_worker() is None
        assert worker._task is None and offline._closed
        reopened=Authority('/work/offline/state.sqlite',allow_simulation=True)
        runtime.bind_authority(reopened)
        recovered_worker=runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope))
        async with app.router.lifespan_context(app):
            assert reopened.list_tasks(runtime.SERVICE_ACTOR)[0]['status']=='simulated_completed'
            assert recovered_worker.pipeline.run_once(runtime.SERVICE_ACTOR) is None
            demo['restart_status']=reopened.list_tasks(runtime.SERVICE_ACTOR)[0]
        results.append('actual_app_restart_keeps_receipt_result_without_resubmission')
        Path('/work/DEMONSTRATION.json').write_text(json.dumps(demo,indent=2)+'\n')
        # Mandatory storage failure blocks the actual lifespan and releases the
        # owned writer even though its durable stop cannot be confirmed.
        broken=Authority('/work/broken/db')
        broken._poisoned=True
        runtime.bind_authority(broken)
        try:
            async with app.router.lifespan_context(app):
                raise AssertionError('mandatory poisoned storage was accepted')
        except AuthorityError as e:
            assert e.code=='authority_unavailable'
        assert runtime._authority is None and broken._closed and scheduler._backend is None
        results.append('actual_lifespan_mandatory_storage_failure_propagates_and_cleans_up')
        # No implicit catch-up after downtime. Recovery is an explicit offline
        # disable/recreate operation, not a hidden startup repair.
        overdue=Authority('/work/overdue/db')
        overdue.add_schedule(runtime.SERVICE_ACTOR,str(uuid.uuid4()),'past','* * * * *','synthetic','2000-01-01T00:00:00+00:00')
        runtime.bind_authority(overdue)
        try:
            async with app.router.lifespan_context(app):
                raise AssertionError('overdue schedule startup was accepted')
        except AuthorityError as e:
            assert e.code=='overdue_schedule_reconcile_required'
        assert runtime._authority is None and overdue._closed
        results.append('actual_lifespan_overdue_schedule_blocks_without_catchup')
    asyncio.run(check())
    os.chdir(project)
    (project/'tasks').mkdir(exist_ok=True)
    import pytest
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    counts={}
    class Counts:
        def pytest_sessionfinish(self,session,exitstatus):
            terminal=session.config.pluginmanager.getplugin('terminalreporter')
            counts.update(collected=session.testscollected, failed=session.testsfailed, skipped=len(terminal.stats.get('skipped',[])), exitstatus=int(exitstatus))
    code=pytest.main(['-q','-p','pytest_asyncio.plugin','-p','no:cacheprovider','--basetemp=/work/regression-tmp','/input/regressions'],plugins=[Counts()])
    report['regressions']=counts
    assert code==0 and counts['skipped']==0
    runtime.close_authority()
    server.audit._shutdown()
    report['cases']=results
    report['versions']=versions
    assert not any(n=='pip' or n.startswith('pip.') for n in sys.modules)
    report['status']='FULL_EXISTING_APP_OFFLINE_LIFESPAN_PASS'
except BaseException as e:
    report.update(status='BLOCKED_OR_FAILED',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(limit=12))
finally:
    report['finished_at']=datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='FULL_EXISTING_APP_OFFLINE_LIFESPAN_PASS' else 2)

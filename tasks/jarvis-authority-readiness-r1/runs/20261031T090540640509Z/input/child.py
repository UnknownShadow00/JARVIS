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

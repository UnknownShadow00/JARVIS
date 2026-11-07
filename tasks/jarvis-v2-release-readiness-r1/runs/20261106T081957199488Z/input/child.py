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
    raw['server'].update(host='127.0.0.1',api_token='fixture-token-only',remote_access_enabled=False,enable_voice_on_startup=False,enable_hotkey_listener=False)
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
    sys.path.insert(0,'/input')
    from app.main import app
    from app import server
    from app.agent import runtime
    from app.agent.scheduler import scheduler
    from app.agent.authority import Authority, AuthorityError
    from synthetic_authority import fixture_authority as Authority
    import httpx
    report['entrypoint_origin']=sys.modules['app.main'].__file__
    report['server_origin']=server.__file__
    assert app is server.app
    from synthetic_authority import seed_legacy_fixture
    seed_legacy_fixture(project/'data/authority/queue.sqlite')
    runtime.bind_authority(Authority(project/'data/authority/queue.sqlite'))
    results=[]
    async def check():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers={'Authorization':'Bearer fixture-token-only'}) as client:
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
                client.headers.pop('Authorization',None)
                assert (await client.get('/tasks')).status_code==401
                assert (await client.get('/tasks',headers={'Authorization':'Bearer fixture-token-only'})).status_code==200
                server.settings.server.api_token=''
                assert (await client.get('/tasks')).status_code==401
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
                server.settings.server.api_token='offline-fixture-token'
                client.headers['Authorization']='Bearer offline-fixture-token'
                assert (await client.get('/ready')).json()['execution_worker_ready']
                client.headers.pop('Authorization')
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
        # Actual full-app startup reconciliation of an independently SIGKILLed
        # synthetic executor process with a committed result but no publication.
        import subprocess, time
        crashdir=Path('/work/app-crash')
        crashdir.mkdir(mode=0o700)
        crash_op=str(uuid.uuid4())
        crashdb=crashdir/'state.sqlite'
        ready=crashdir/'ready'
        with (crashdir/'stdout').open('w') as out, (crashdir/'stderr').open('w') as err:
            process=subprocess.Popen([sys.executable,'-I','-B','-S','/input/tests/execution_process_actor.py',str(crashdb),str(ready),crash_op,'after_record'],stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,env={'LANG':'C.UTF-8'})
            try:
                deadline=time.monotonic()+4
                while not ready.exists() and process.poll() is None and time.monotonic()<deadline:
                    time.sleep(.01)
                assert ready.exists(),(crashdir/'stderr').read_text()
                process.kill()
                process.wait(timeout=1)
                assert process.returncode<0
            finally:
                if process.poll() is None:process.kill()
                process.wait(timeout=1)
        recovered=Authority(crashdb,allow_simulation=True)
        assert recovered.get_task(runtime.SERVICE_ACTOR,crash_op)['status']=='unknown'
        runtime.bind_authority(recovered)
        server.settings.server.api_token='synthetic-restart-client'
        crash_worker=runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope))
        with patch.object(crash_worker.pipeline.registry._executor,'execute',side_effect=AssertionError('recovery dispatched again')) as execute:
            async with app.router.lifespan_context(app):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers={'Authorization':'Bearer synthetic-restart-client'}) as client:
                    crash_status=(await client.get('/tasks/'+crash_op)).json()
                    assert crash_status['status']=='simulated_completed'
                    assert crash_status['result']['output']=='crash marker'
                    assert (await client.get('/ready')).json()['reconciliation_required']==0
                    execute.assert_not_called()
                    demo['independent_crash_recovery']=crash_status
                    demo['independent_crash_publication_receipt']=(await client.get('/requests/'+phase_id(crash_op,'publish'))).json()
        results.append('actual_app_startup_reconciles_independent_SIGKILL_result_without_executor_dispatch')
        Path('/work/DEMONSTRATION.json').write_text(json.dumps(demo,indent=2)+'\n')
        # Sprint2: protected ledger + real read-only operator routes, bounded
        # authenticated local recovery/export/archive, and quiesced CLI.
        from app.agent.ledger import LedgerGuard
        from app.agent.execution import ExecutionPipeline
        from app.agent.recovery import OperatorRecovery, OperatorPermits, RecoveryActions
        from app.agent.operator_cli import main as offline_operator_main
        ledger_key=b'synthetic-full-app-ledger-key-only-00000000'
        operator_key=b'synthetic-full-app-operator-key-only-000000'
        store_id=str(uuid.uuid4())
        guarded_path=Path('/work/operator-store/state.sqlite')
        anchors=Path('/work/operator-protected')
        export_root=Path('/work/operator-exports');export_root.mkdir(mode=0o700)
        guarded=Authority(guarded_path,allow_simulation=True,ledger=LedgerGuard(anchors,ledger_key,store_id,initialize=True))
        pipeline=ExecutionPipeline(guarded,SimulatedPolicy(runtime.SERVICE_ACTOR.scope),enabled=True)
        task_id=str(uuid.uuid4())
        pipeline.submit(runtime.SERVICE_ACTOR,task_id,'synthetic lost publication','synthetic.echo',{'value':'operator recovery proof'},(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
        pipeline._fault=lambda phase: (_ for _ in ()).throw(RuntimeError('lost publication fixture')) if phase=='after_record' else None
        try:pipeline.run_once(runtime.SERVICE_ACTOR)
        except RuntimeError:pass
        guarded.close()
        guarded=Authority(guarded_path,allow_simulation=True,ledger=LedgerGuard(anchors,ledger_key,store_id))
        pipeline=ExecutionPipeline(guarded,SimulatedPolicy(runtime.SERVICE_ACTOR.scope),enabled=True)
        issuer=OperatorPermits(operator_key);recovery=RecoveryActions(guarded,issuer)
        def permit_for(command,payload,request_id):
            now=datetime.now(UTC)
            return issuer.issue(request_id=request_id,principal='synthetic-operator',scope=runtime.SERVICE_ACTOR.scope,command=command,payload=payload,checkpoint=guarded._ledger._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
        before=OperatorRecovery(guarded).diagnose(runtime.SERVICE_ACTOR,task_id=task_id)
        assert before['tasks'][0]['status']=='unknown' and before['tasks'][0]['recorded_evidence']
        recovery_id=str(uuid.uuid4());payload={'task_id':task_id}
        with patch.object(pipeline.registry._executor,'execute',side_effect=AssertionError('operator redispatched')) as execute:
            recovered=recovery.apply(runtime.SERVICE_ACTOR,recovery_id,'publish_synthetic_evidence',payload,permit_for('publish_synthetic_evidence',payload,recovery_id))
            assert recovered['result']['status']=='simulated_completed'
            execute.assert_not_called()
        pipeline.policy=SimulatedPolicy(runtime.SERVICE_ACTOR.scope,frozenset({'synthetic.echo','synthetic.sha256','synthetic.fail'}))
        failure_id=str(uuid.uuid4())
        pipeline.submit(runtime.SERVICE_ACTOR,failure_id,'synthetic failure','synthetic.fail',{'value':'failure'},(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
        pipeline.run_once(runtime.SERVICE_ACTOR)
        unknown_id=str(uuid.uuid4())
        pipeline.submit(runtime.SERVICE_ACTOR,unknown_id,'unestablished synthetic outcome','synthetic.echo',{'value':'uncertain'},(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
        pipeline._claim(runtime.SERVICE_ACTOR,unknown_id)
        pipeline._unknown(runtime.SERVICE_ACTOR,unknown_id,guarded.generation,'fixture_outcome_unestablished')
        guarded.cancel(runtime.SERVICE_ACTOR,str(uuid.uuid4()),unknown_id)
        runtime.bind_authority(guarded)
        operator_worker=runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope))
        operator_demo={'before_recovery':before,'authenticated_recovery_receipt':recovered,'real_execution_enabled':False}
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
                assert (await client.get('/operator/diagnostics')).status_code==401
                server.settings.server.api_token='operator-fixture-token'
                assert (await client.get('/operator/diagnostics')).status_code==401
                client.headers['Authorization']='Bearer operator-fixture-token'
                diagnostics=(await client.get('/operator/diagnostics')).json()
                assert diagnostics['consistent'] and diagnostics['ledger_integrity']['verified']
                assert diagnostics['failed']==1 and diagnostics['unknown']==1 and diagnostics['cancel_requested']==1
                assert all(not t['execution_completed'] for t in diagnostics['tasks'] if t['task_id']==unknown_id)
                assert (await client.post('/operator/diagnostics',json={'command':'complete'})).status_code==405
                assert (await client.post('/operator/recover',json={'command':'retry'})).status_code==404
                readiness=(await client.get('/ready')).json()
                assert readiness['ledger_integrity']['verified'] and readiness['operator_recovery']['unknown']==1
                captured=io.StringIO()
                with patch.object(cli,'_get',return_value=diagnostics),contextlib.redirect_stdout(captured):
                    assert cli.main(['recovery'])==0
                assert json.loads(captured.getvalue())['unknown']==1
                report_text=await reporter.build_report()
                assert 'Ledger integrity verified' in report_text and 'UNKNOWN 1' in report_text
                export_id=str(uuid.uuid4());export_payload={'export_id':export_id,'destination':str(export_root)}
                exported=recovery.export(runtime.SERVICE_ACTOR,export_id,export_root,permit_for('export_ledger',export_payload,export_id))
                cutoff=(datetime.now(UTC)+timedelta(seconds=1)).isoformat()
                preparation_id=str(uuid.uuid4())
                preparation_payload={'export_id':export_id,'manifest_sha256':exported['export']['manifest_sha256'],'older_than':cutoff}
                archived=recovery.prepare_archive(runtime.SERVICE_ACTOR,preparation_id,export_root/export_id,cutoff,permit_for('prepare_archive',preparation_payload,preparation_id))
                assert set(archived['result']['plan']['eligible_for_archive'])=={task_id,failure_id}
                assert archived['result']['plan']['protected_total']==1 and not archived['result']['history_deleted']
                assert guarded.get_task(runtime.SERVICE_ACTOR,unknown_id)['status']=='unknown'
                operator_demo.update(diagnostics=diagnostics,readiness=readiness,reporter=report_text,export=exported,archive_preparation=archived)
                server.settings.server.api_token=''
        results.append('actual_guarded_app_authenticated_operator_diagnostics_recovery_export_archive_and_reporting')
        before_bytes=guarded_path.read_bytes()
        checkpoint_bytes={p.name:p.read_bytes() for p in anchors.iterdir()}
        read_fd,write_fd=os.pipe()
        try:
            os.write(write_fd,ledger_key);os.close(write_fd)
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                assert offline_operator_main(['--database',str(guarded_path),'--checkpoints',str(anchors),'--store-id',store_id,'--key-fd',str(read_fd)])==0
            operator_demo['quiesced_cli_diagnostics']=json.loads(output.getvalue())
        finally:os.close(read_fd)
        assert guarded_path.read_bytes()==before_bytes and checkpoint_bytes=={p.name:p.read_bytes() for p in anchors.iterdir()}
        results.append('quiesced_offline_operator_cli_verifies_ledger_without_owner_takeover_or_file_changes')
        Path('/work/OPERATOR-DEMONSTRATION.json').write_text(json.dumps(operator_demo,indent=2)+'\n')
        # Sprint3 actual app + offline CLI disaster workflow. No production
        # listener, model provider, real key material or real database is used.
        from app.agent.archive_restore import ArchiveRestorer
        audit_key=b'synthetic-sprint3-full-app-ledger-key-0000000'
        audit_operator=b'synthetic-sprint3-full-app-operator-key-00000'
        audit_store=str(uuid.uuid4());audit_db=Path('/work/audit-store/state.sqlite')
        audit_anchors=Path('/work/audit-protected');audit_exports=Path('/work/audit-exports');audit_targets=Path('/work/audit-targets')
        audit_exports.mkdir(mode=0o700);audit_targets.mkdir(mode=0o700)
        audit_guard=LedgerGuard(audit_anchors,audit_key,audit_store,initialize=True,rollover=True,epoch_capacity=4,recovery=True)
        audit_authority=Authority(audit_db,allow_simulation=True,ledger=audit_guard)
        audit_pipeline=ExecutionPipeline(audit_authority,SimulatedPolicy(runtime.SERVICE_ACTOR.scope),enabled=True)
        held_id=str(uuid.uuid4());audit_authority.submit(runtime.SERVICE_ACTOR,held_id,'admitted and held')
        uncertain_id=str(uuid.uuid4())
        audit_pipeline.submit(runtime.SERVICE_ACTOR,uncertain_id,'uncertain retained operation','synthetic.echo',{'value':'never rerun'},(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
        audit_pipeline._claim(runtime.SERVICE_ACTOR,uncertain_id)
        audit_pipeline._unknown(runtime.SERVICE_ACTOR,uncertain_id,audit_authority.generation,'unestablished_effect')
        audit_authority.cancel(runtime.SERVICE_ACTOR,str(uuid.uuid4()),uncertain_id)
        old_checkpoint_bytes={p.name:p.read_bytes() for p in audit_anchors.glob('*.json')}
        audit_issuer=OperatorPermits(audit_operator);audit_actions=RecoveryActions(audit_authority,audit_issuer)
        runtime.bind_authority(audit_authority);runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope))
        disaster_demo={'real_execution_enabled':False,'source_store_id':audit_store}
        async with app.router.lifespan_context(app):
            server.settings.server.api_token='sprint3-fixture-token'
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers={'Authorization':'Bearer sprint3-fixture-token'}) as client:
                ready=(await client.get('/ready')).json()
                assert ready['ledger_integrity']['epoch']>=1
                diag=(await client.get('/operator/diagnostics')).json()
                assert diag['disaster_recovery']['rollover_enabled'] and diag['unknown']==1
                assert (await client.post('/operator/restore',json={'force':True})).status_code==404
                export_id=str(uuid.uuid4());now=datetime.now(UTC)
                export_payload={'export_id':export_id,'destination':str(audit_exports)}
                token=audit_issuer.issue(request_id=export_id,principal='synthetic-operator',scope=runtime.SERVICE_ACTOR.scope,command='export_ledger',payload=export_payload,checkpoint=audit_guard._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
                audit_export=audit_actions.export(runtime.SERVICE_ACTOR,export_id,audit_exports,token)
                assert audit_export['attestation']['verified']
                disaster_demo.update(source_diagnostics=diag,source_readiness=ready,export=audit_export)
            server.settings.server.api_token=''
        assert runtime._authority is None
        original_database=audit_db.read_bytes()
        now=datetime.now(UTC)
        reference_guard=LedgerGuard(audit_anchors,audit_key,audit_store,rollover=True,epoch_capacity=4,recovery=True)
        reference_guard.acquire(audit_targets/'unused.sqlite',readonly=True)
        reference=reference_guard.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
        current_head=reference_guard.history()[0];reference_guard.close()
        def disaster_cli(extra,permit=None):
            fds=[];arguments=['--checkpoints',str(audit_anchors),'--store-id',audit_store,'--rollover-enabled','--epoch-capacity','4']
            payloads=[('--key-fd',audit_key),('--trust-fd',json.dumps(reference).encode())]
            if permit is not None:payloads += [('--operator-key-fd',audit_operator),('--permit-fd',json.dumps(permit).encode())]
            try:
                for option,data in payloads:
                    read,write=os.pipe();os.write(write,data);os.close(write);fds.append(read);arguments.extend([option,str(read)])
                captured=io.StringIO()
                with contextlib.redirect_stdout(captured):code=offline_operator_main(arguments+extra)
                return code,json.loads(captured.getvalue())
            finally:
                for descriptor in fds:os.close(descriptor)
        archive=audit_exports/export_id;manifest_hash=audit_export['export']['manifest_sha256']
        code,verified_archive=disaster_cli(['--verify-archive',str(archive),'--expected-manifest-sha256',manifest_hash])
        assert code==0 and verified_archive['schema_compatible'] and not verified_archive['semantic_restore_verified']
        restore_id=str(uuid.uuid4());restore_payload={'export_id':export_id,'manifest_sha256':manifest_hash,'target_parent':str(audit_targets),'restore_id':restore_id};now=datetime.now(UTC)
        token=audit_issuer.issue(request_id=restore_id,principal='synthetic-operator',scope=runtime.SERVICE_ACTOR.scope,command='restore_archive',payload=restore_payload,checkpoint=current_head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
        request=['--restore-archive',str(archive),'--operation-id',restore_id,'--disposable-target-parent',str(audit_targets),'--expected-manifest-sha256',manifest_hash]
        code,refused=disaster_cli(request,token);assert code==1 and refused['error']=='explicit_recovery_commit_required'
        code,restored=disaster_cli(request+['--commit-recovery'],token)
        assert code==0 and restored['summary']['unknown']==1 and restored['summary']['cancel_requested']==1
        assert not restored['execution_enabled'] and not restored['runtime_activation_allowed']
        code,restored_verified=disaster_cli(['--verify-restored',str(audit_targets/restore_id)])
        assert code==0 and restored_verified['verified']
        code,checkpoint_status=disaster_cli(['--checkpoint-status'])
        assert code==0 and checkpoint_status['restores'][0]['status']=='committed'
        assert audit_db.read_bytes()==original_database
        assert all((audit_anchors/name).read_bytes()==raw for name,raw in old_checkpoint_bytes.items())
        disaster_demo.update(trusted_external_reference_fixture=reference,archive_verification=verified_archive,explicit_commit_refusal=refused,
                             restoration=restored,restoration_verification=restored_verified,checkpoint_status=checkpoint_status)
        results.append('actual_app_rollover_and_authenticated_offline_cli_archive_restore_preserves_UNKNOWN_without_execution')
        # The source can restart as a descendant; the restored snapshot stays an
        # isolated historical artifact and is never bound to the runtime.
        audit_guard=LedgerGuard(audit_anchors,audit_key,audit_store,rollover=True,epoch_capacity=4,recovery=True,trust_context=reference)
        audit_authority=Authority(audit_db,allow_simulation=True,ledger=audit_guard)
        runtime.bind_authority(audit_authority);runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope))
        async with app.router.lifespan_context(app):
            server.settings.server.api_token='sprint3-fixture-token'
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers={'Authorization':'Bearer sprint3-fixture-token'}) as client:
                diag=(await client.get('/operator/diagnostics')).json()
                assert diag['disaster_recovery']['restores'][0]['status']=='committed'
                assert (await client.get('/tasks/'+uncertain_id)).json()['status']=='unknown'
                assert (await client.get('/ready')).json()['ledger_integrity']['external_reference_configured']
                disaster_demo['source_restart_diagnostics']=diag
            server.settings.server.api_token=''
        results.append('actual_source_restart_reports_verified_restore_receipts_and_preserves_uncertain_work')
        Path('/work/DISASTER-DEMONSTRATION.json').write_text(json.dumps(disaster_demo,indent=2)+'\n')
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
        from enrollment_application import run as enrollment_scenarios
        results.extend(await enrollment_scenarios(app,server,runtime))
        from recovery_application import run as recovery_scenarios
        results.extend(await recovery_scenarios(app,server,runtime))
        from integration_application import run as integrated_scenarios
        results.extend(await integrated_scenarios(app,server,runtime))
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

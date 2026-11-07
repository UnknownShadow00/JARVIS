"""One actual application lifecycle across the five sprints and inert transport."""
import asyncio
from datetime import UTC,datetime,timedelta
import copy
import json
from pathlib import Path


async def run(app,server,runtime):
    import httpx
    from app.agent.scheduler import scheduler
    from app.agent.task_queue import task_queue
    from app.agent.execution import phase_id,SimulatedPolicy
    from app.agent.execution_transport import digest
    from app.agent.recovery import RecoveryActions,OperatorPermits
    from app.agent.archive_restore import ArchiveRestorer
    from app.agent.branch_verification import BranchVerifier
    from app.agent.recovery_decisions import RecoveryRegistry
    from app.agent.ledger import LedgerGuard
    from app.agent.authority import Authority,AuthorityError
    from app.brain.router import RouterResult
    from app.tools.registry import registry as tools,ToolError
    from app.voice.dictation import dictation
    from enrollment_application import cli
    from transport_fixtures import provision,opened,request,uid,times,KEY,OPKEY,EXEC_KEY,REQUEST_KEY,RESPONSE_KEY
    root=Path('/work/integrated-v2');state=provision(root);a,unused,transport=opened(state)
    runtime.bind_authority(a);worker=runtime.bind_offline_execution(SimulatedPolicy(runtime.SERVICE_ACTOR.scope),transport=transport)
    pipeline=worker.pipeline;actor=runtime.SERVICE_ACTOR
    token='synthetic-v6-api-token';server.settings.server.api_token=token;headers={'Authorization':'Bearer '+token}
    demo={'real_execution_enabled':False,'transport_mode':'synthetic_AF_UNIX_socketpair_same_Authority_writer',
          'scheduler_time_mode':'actual_APScheduler_registration_with_explicit_original_nominal_callback_no_wall_clock_qualification'}
    def recovery_grant(op,command,payload):
        start,end=times()
        return OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-v6-recovery-operator',scope=actor.scope,
            command=command,payload=payload,checkpoint=a._ledger.history()[0],issued_at=start,expires_at=end)
    async def wait_status(client,op,status):
        for _ in range(200):
            response=await client.get('/tasks/'+op)
            if response.status_code==200 and response.json()['status']==status:return response.json()
            await asyncio.sleep(.01)
        raise AssertionError(('task_status_timeout',op,status,response.json()))
    exports=root/'exports';exports.mkdir(mode=0o700);targets=root/'restores';targets.mkdir(mode=0o700)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=headers) as client:
            initial=(await client.get('/ready')).json()
            assert initial['storage_ready'] and initial['scheduler_ready'] and initial['execution_worker_ready']
            assert initial['execution_transport']['configured'] and initial['transport']['configured']
            assert initial['recovery_decisions']['verified'] and not initial['real_execution_enabled']
            held=uid();res=await client.post('/tasks',json={'request_id':held,'goal':'held queue operation'})
            assert res.status_code==200 and (await task_queue.get_task(held)).status=='pending'
            cancelled=await client.delete('/tasks/'+held,params={'request_id':uid()});assert cancelled.status_code==200
            r=request(pipeline,value='actual API to signed IPC to durable publication')
            unauthorized=await client.post('/execution/tasks',json=r,headers={'Authorization':'Bearer wrong-synthetic-token'})
            assert unauthorized.status_code==401 and a.receipt(actor,r['request_id']) is None
            bad=copy.deepcopy(r);bad['transport_permit']['hmac_sha256']='0'*64
            assert (await client.post('/execution/tasks',json=bad)).status_code in (400,403)
            admitted=await client.post('/execution/tasks',json=r);assert admitted.status_code==200,admitted.text
            done=await wait_status(client,r['request_id'],'simulated_completed')
            assert transport.invocations==1 and done['result']['operation_id']==r['request_id']
            assert (await task_queue.get_task(r['request_id'])).status=='simulated_completed'
            repeated=await client.post('/execution/tasks',json=r);assert repeated.status_code==200 and repeated.json()['replayed']
            assert transport.invocations==1
            phase_receipts={}
            for phase in ('claim','dispatch','transport_reserve','transport_report','record','publish'):
                receipt=await client.get('/requests/'+phase_id(r['request_id'],phase));assert receipt.status_code==200
                phase_receipts[phase]=receipt.json()
            # Nominal scheduler identity is preserved through a real callback and
            # the SAME worker/Authority; this does not wait for a wall-clock cron.
            scheduled_id=uid();job=(await client.post('/schedule/jobs',json={'request_id':scheduled_id,'goal':'scheduled pure inspection',
                'name':'synthetic nominal occurrence','cron_expr':'* * * * *','execution':{'capability':'synthetic.sha256','payload':{'value':'nominal'},'timeout_seconds':10,'expires_after_seconds':60}}))
            assert job.status_code==200,job.text
            job=job.json()['result'];nominal=job['next_run_at'];revision=job['revision']
            await scheduler._dispatch(job['job_id'],revision,nominal,scheduler._epoch)
            await scheduler._dispatch(job['job_id'],revision,nominal,scheduler._epoch)
            import uuid
            occurrence=str(uuid.uuid5(uuid.UUID(job['job_id']),f'{revision}:{nominal}'))
            scheduled=await wait_status(client,occurrence,'simulated_completed')
            assert scheduled['occurrence_id']==occurrence
            assert a._conn.execute("SELECT COUNT(*) FROM records WHERE kind='occurrence' AND id=?",(occurrence,)).fetchone()[0]==1
            assert (await client.delete('/schedule/jobs/'+job['job_id'],params={'request_id':uid()})).status_code==200
            # Renew only an already externally retained witness, with a distinct
            # authenticated offline operator decision, never an activation grant.
            reg=a._recovery_registry;ref=reg.inspect()['reference'];reg.reference=ref;start,end=times()
            nxt=a._ledger.trust_reference(valid_from=start,expires_at=end)
            renewal={'previous_witness':ref['witness'],'next_reference':nxt};renew_id=uid()
            reg.apply(actor,renew_id,'renew',renewal,recovery_grant(renew_id,'recovery_renew',renewal))
            state['reference']=reg.inspect()['reference']
            # A durable endpoint report with a lost response remains UNKNOWN.
            lost=request(pipeline,value='durable signed report; response lost')
            fired=[False]
            def interrupted(stage):
                if stage=='transport_reported' and not fired[0]:fired[0]=True;raise OSError('synthetic response interruption')
            transport._fault=interrupted
            assert (await client.post('/execution/tasks',json=lost)).status_code==200
            unknown=await wait_status(client,lost['request_id'],'unknown')
            assert transport.invocations==2
            diag=(await client.get('/operator/diagnostics')).json();assert diag['consistent'] and diag['execution_transport']['history_verified']
            unknown_diag=next(t for t in diag['tasks'] if t['task_id']==lost['request_id'])
            assert unknown_diag['transport']['report_present'] and not unknown_diag['execution_completed']
            assert not unknown_diag['transport']['report_is_completion']
            # Legacy execution/approval paths are closed even with a forged
            # process-memory confirmation or disabled dry-run preference.
            previous=server.intent_router.classify
            try:
                server.intent_router.classify=lambda _:RouterResult('use_tool',1.0,'shell','synthetic fixture')
                chat=await client.post('/chat',json={'message':'synthetic tool intent'})
                assert chat.status_code==200 and 'disabled' in chat.json()['reply'].lower()
            finally:server.intent_router.classify=previous
            server._pending_confirmations['synthetic']={'tool':'shell','params':{'command':'never execute'}}
            assert (await client.post('/confirm/synthetic')).status_code==404
            server._pending_confirmations.clear()
            for callback in (lambda:tools.call('shell',{'command':'never execute'},confirmed=True),lambda:tools.get_tool('shell').execute({})):
                try:callback()
                except ToolError:pass
                else:raise AssertionError('legacy tool executed')
            assert dictation.handle_transcript('synthetic private transcript') is False
            canary='SYNTHETIC_AUTHORIZATION_CANARY_DO_NOT_REFLECT'
            malformed={**r,'transport_permit':[canary]}
            rejected=await client.post('/execution/tasks',json=malformed)
            assert rejected.status_code==422 and canary not in rejected.text
            duplicate=b'{"request_id":"'+uid().encode()+b'","request_id":"'+uid().encode()+b'","goal":"duplicate"}'
            assert (await client.post('/tasks',content=duplicate,headers={'content-type':'application/json'})).status_code==400
            for flag in ('/operator/approve','/operator/activate','/operator/complete'):
                assert (await client.post(flag,json={})).status_code==404
            export_id=uid();export=RecoveryActions(a,OperatorPermits(OPKEY)).export(actor,export_id,exports,
                recovery_grant(export_id,'export_ledger',{'export_id':export_id,'destination':str(exports)}))
            demo.update(initial_readiness=initial,task_request_id=r['request_id'],admission=admitted.json(),completion=done,
                receipts=phase_receipts,scheduled_occurrence_id=occurrence,scheduled_completion=scheduled,
                unknown_request_id=lost['request_id'],unknown=unknown,diagnostics=diag,witness_renewal_id=renew_id)
    assert a._closed and runtime._authority is None and worker._task is None
    # Actual offline CLI records authenticated evidence, then a separate explicit
    # publication authorization; neither command invokes the endpoint.
    base=['--database',state['database'],'--checkpoints',state['config']['checkpoints'],'--store-id',state['config']['store_id'],
        '--rollover-enabled','--epoch-capacity','64','--synthetic-endpoint-id','synthetic.local.echo-v1','--commit-recovery']
    common={'--key-fd':KEY,'--operator-key-fd':OPKEY,'--trust-fd':state['trust'],'--enrollment-witness-fd':state['enrollment']['witness'],
        '--registry-config-fd':state['config'],'--registry-reference-fd':state['reference'],'--transport-operator-key-fd':EXEC_KEY,
        '--transport-request-key-fd':REQUEST_KEY,'--transport-response-key-fd':RESPONSE_KEY}
    def offline_grant(op,command,payload):
        g=LedgerGuard(state['config']['checkpoints'],KEY,state['config']['store_id'],rollover=True,epoch_capacity=64,recovery=True,trust_context=state['trust'])
        g.acquire(state['database'],readonly=True)
        try:
            start,end=times()
            return OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-offline-recovery',scope=actor.scope,command=command,
                payload=payload,checkpoint=g.history()[0],issued_at=start,expires_at=end)
        finally:g.close()
    record_op=uid();payload={'task_id':lost['request_id']};permit=offline_grant(record_op,'reconcile_synthetic_transport_report',payload)
    code,recorded=cli(base,['--reconcile-transport-report',lost['request_id'],'--operation-id',record_op],{**common,'--permit-fd':permit})
    assert code==0,recorded
    code,replayed=cli(base,['--reconcile-transport-report',lost['request_id'],'--operation-id',record_op],{**common,'--permit-fd':permit})
    assert code==0 and replayed['replayed']
    # Restart BETWEEN the two recovery decisions cannot publish marked evidence.
    restarted,rpipeline,rt=opened(state);runtime.bind_authority(restarted)
    rworker=runtime.bind_offline_execution(SimulatedPolicy(actor.scope),transport=rt)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=headers) as client:
            assert (await client.get('/tasks/'+lost['request_id'])).json()['status']=='unknown'
            assert rt.invocations==0 and (await client.get('/ready')).status_code==200
    publish_op=uid();permit=offline_grant(publish_op,'publish_synthetic_evidence',payload)
    code,published=cli(base,['--publish-transport-evidence',lost['request_id'],'--operation-id',publish_op],{**common,'--permit-fd':permit})
    assert code==0,published
    final,fp,ft=opened(state);runtime.bind_authority(final);runtime.bind_offline_execution(SimulatedPolicy(actor.scope),transport=ft)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=headers) as client:
            result=(await client.get('/tasks/'+lost['request_id'])).json()
            assert result['status']=='simulated_completed' and ft.invocations==0
            demo['restart_recovered_task']=result;demo['restart_readiness']=(await client.get('/ready')).json()
    # The same exported history verifies/restores as inert and enters the durable
    # branch-decision registry; approval still cannot turn it into an Authority.
    g=LedgerGuard(state['config']['checkpoints'],KEY,state['config']['store_id'],rollover=True,epoch_capacity=64,recovery=True,trust_context=state['trust'])
    g.acquire(state['database'])
    try:
        restorer=ArchiveRestorer(g,OperatorPermits(OPKEY));manifest=export['export']['manifest_sha256']
        archive=restorer.verify_archive(exports/export_id,manifest);rid=uid()
        restore_payload={'export_id':export_id,'manifest_sha256':manifest,'target_parent':str(targets),'restore_id':rid}
        start,end=times();restore_permit=OperatorPermits(OPKEY).issue(request_id=rid,principal='synthetic-restore-operator',scope=actor.scope,
            command='restore_archive',payload=restore_payload,checkpoint=g.history()[0],issued_at=start,expires_at=end)
        restored=restorer.restore(actor,rid,exports/export_id,targets,manifest,restore_permit,disposable=True)
        context={'format':'jarvis-branch-verification-request-v1','branch_id':uid(),'operator_id':'synthetic-restore-reviewer',
            'expected_source_head':g.history()[0],'expected_restore_id':rid,'expected_database_sha256':restored['database_sha256'],
            'expected_source_lineage':restored['source_lineage'],'expected_key_id':g.key_id,'issued_at':start,'expires_at':end,
            'reserved_branch_ids':[],'decision':'PROPOSE_ONLY'}
        verified=BranchVerifier(g).verify(targets/rid,context)
        registry=RecoveryRegistry(g,state['config'],state['reference'],OperatorPermits(OPKEY))
        pid=uid();body={'directory':str(targets/rid),'verification_request':context,'verification_sha256':digest({'proposal':verified['proposal'],'summary':verified['summary']})}
        def registry_grant(op,command,payload):
            start,end=times()
            return OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-branch-operator',scope=actor.scope,
                command='recovery_'+command,payload=payload,checkpoint=g.history()[0],issued_at=start,expires_at=end)
        registry.apply(actor,pid,'propose',body,registry_grant(pid,'propose',body))
        did=uid();start,end=times(60);decision={'proposal_id':pid,'proposal_sha256':digest(verified['proposal']),'state':'APPROVED',
            'valid_from':start,'expires_at':end,'previous_decision_id':None}
        approved=registry.apply(actor,did,'decide',decision,registry_grant(did,'decide',decision))
        try:Authority(targets/rid/'state.sqlite')
        except AuthorityError as exc:assert exc.code=='restore_activation_prohibited'
        else:raise AssertionError('restored execution activated')
        demo.update(offline_evidence_recording=recorded,offline_replay=replayed,offline_publication=published,
            archive_verification=archive,restored_branch=restored,branch_approval=approved,final_registry=registry.inspect())
    finally:g.close()
    server.settings.server.api_token=''
    # No runtime credential/key bytes may enter application logs or responses.
    serialized=json.dumps(demo)
    for secret in (KEY,OPKEY,EXEC_KEY,REQUEST_KEY,RESPONSE_KEY):
        assert secret.decode() not in serialized
        log=Path('/work/synthetic-audit.jsonl')
        if log.exists():assert secret not in log.read_bytes()
    Path('/work/INTEGRATED-DEMONSTRATION.json').write_text(json.dumps(demo,indent=2)+'\n')
    return ['actual_API_authority_queue_signed_IPC_scheduler_receipts_cancellation_recovery_witness_and_shutdown',
            'actual_offline_FD_CLI_report_reconciliation_restart_hold_and_separate_authorized_publication_no_redispatch',
            'same_integrated_history_archive_inert_restore_durable_proposal_approval_no_activation',
            'legacy_chat_confirm_tool_getters_dictation_and_validation_secret_reflection_fail_closed']

"""Actual CLI + ASGI application integration; guarded synthetic lifespans only."""
from datetime import UTC,datetime,timedelta
import json
from pathlib import Path
from enrollment_application import cli


def interval():
    now=datetime.now(UTC)
    return (now-timedelta(seconds=1)).isoformat(),(now+timedelta(seconds=120)).isoformat()


def provision(g,root):
    from enrollment_fixtures import uid
    for name in ('decision-data','decision-custody'):(root/name).mkdir(mode=0o700)
    start,end=interval();ref=g.trust_reference(valid_from=start,expires_at=end)
    config={'format':'jarvis-recovery-registry-v1','registry_id':uid(),'store_id':g.store_id,'key_id':g.key_id,
        'database':str(root/'decision-data/registry.sqlite'),'custody':str(root/'decision-custody'),
        'checkpoints':str(g.directory),'initial_reference':ref,'capacity':128,'disposable_only':True}
    external={'registry_id':config['registry_id'],'sequence':0,'event_sha256':'0'*64,
              'witness':{'renewal_id':None,'checkpoint':ref}}
    return config,external


def permit(g,op,command,payload):
    from app.agent.recovery import OperatorPermits
    from enrollment_fixtures import OPKEY
    start,end=interval()
    return OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-sprint5-operator',scope='local-service',
        command='recovery_'+command,payload=payload,checkpoint=g.history()[0],issued_at=start,expires_at=end)


async def run(app,server,runtime):
    import httpx
    from app.agent.authority import Authority,AuthorityError
    from app.agent.ledger import LedgerGuard
    from app.agent.recovery import RecoveryActions,OperatorPermits
    from app.agent.recovery_decisions import RecoveryRegistry,verify_receipt
    from app.agent.enrollment import fingerprint
    from app.agent.archive_restore import ArchiveRestorer
    from app.agent.branch_verification import BranchVerifier
    from app.agent.execution import ExecutionPipeline,SimulatedPolicy
    from enrollment_fixtures import build,uid,KEY,OPKEY
    root=Path('/work/recovery-decisions-app');s,p=build(root)
    enrolled=s.enroll(runtime.SERVICE_ACTOR,p,disposable=True);s.guard.close()
    g=LedgerGuard(root/'anchors',KEY,s.reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    a=Authority(root/'new-store/state.sqlite',ledger=g,enrollment_context=enrolled['witness'],allow_simulation=True)
    # Preserve real offline pipeline UNKNOWN evidence, without executor dispatch.
    actor=runtime.SERVICE_ACTOR;pipeline=ExecutionPipeline(a,SimulatedPolicy(actor.scope),enabled=True)
    unknown=uid();start,end=interval()
    pipeline.submit(actor,unknown,'unknown restored work','synthetic.echo',{'value':'never dispatched'},end)
    pipeline._claim(actor,unknown);pipeline._unknown(actor,unknown,a.generation,'external effect UNKNOWN');a.cancel(actor,uid(),unknown)
    # Include an actual original schedule occurrence in the exported branch.
    schedule=a.add_schedule(actor,uid(),'held occurrence','* * * * *','held work',end)['result']
    control=a.scheduler_control(actor,uid(),True)['result']
    occurrence=a.admit_occurrence(actor,schedule['job_id'],schedule['revision'],end,control['epoch'],(datetime.fromisoformat(end)+timedelta(minutes=1)).isoformat())
    a.scheduler_control(actor,uid(),False)
    exports=root/'exports';targets=root/'targets';exports.mkdir(mode=0o700);targets.mkdir(mode=0o700)
    def old_grant(op,command,payload):
        start,end=interval()
        return OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-sprint5-operator',scope=actor.scope,command=command,payload=payload,checkpoint=g.history()[0],issued_at=start,expires_at=end)
    export_id=uid();ex=RecoveryActions(a,OperatorPermits(OPKEY)).export(actor,export_id,exports,
        old_grant(export_id,'export_ledger',{'export_id':export_id,'destination':str(exports)}))
    start,end=interval();g.trust_context=g.trust_reference(valid_from=start,expires_at=end)
    restore_id=uid();manifest=ex['export']['manifest_sha256']
    restored=ArchiveRestorer(g,OperatorPermits(OPKEY)).restore(actor,restore_id,exports/export_id,targets,manifest,
        old_grant(restore_id,'restore_archive',{'export_id':export_id,'manifest_sha256':manifest,'target_parent':str(targets),'restore_id':restore_id}),disposable=True)
    start,end=interval()
    request={'format':'jarvis-branch-verification-request-v1','branch_id':uid(),'operator_id':'synthetic-sprint5-operator',
        'expected_source_head':g.history()[0],'expected_restore_id':restore_id,'expected_database_sha256':restored['database_sha256'],
        'expected_source_lineage':restored['source_lineage'],'expected_key_id':g.key_id,'issued_at':start,'expires_at':end,
        'reserved_branch_ids':[],'decision':'PROPOSE_ONLY'}
    verified=BranchVerifier(g).verify(targets/restore_id,request)
    assert verified['proposal']['original_occurrence_ids']
    config,external=provision(g,root)
    op=uid();ip=permit(g,op,'initialize',config)
    pid=uid();body={'directory':str(targets/restore_id),'verification_request':request,
        'verification_sha256':fingerprint({'proposal':verified['proposal'],'summary':verified['summary']})}
    pp=permit(g,pid,'propose',body)
    base=['--checkpoints',str(g.directory),'--store-id',g.store_id,'--rollover-enabled','--epoch-capacity','4']
    blobs={'--key-fd':KEY,'--trust-fd':g.trust_context,'--operator-key-fd':OPKEY,
        '--registry-config-fd':config,'--registry-reference-fd':external}
    trust=g.trust_context;a.close()
    code,init=cli(base,['--initialize-recovery-registry','--commit-recovery','--operation-id',op],{**blobs,'--recovery-payload-fd':config,'--permit-fd':ip})
    assert code==0,init
    code,proposed=cli(base,['--publish-recovery-proposal',str(targets/restore_id),'--commit-recovery','--operation-id',pid],{**blobs,'--recovery-payload-fd':body,'--permit-fd':pp})
    assert code==0,proposed
    # Get current reference through a genuinely read-only authenticated CLI.
    code,status=cli(base,['--recovery-registry-status','--operation-id',pid],blobs);assert code==0,status
    did=uid();start,end=interval()
    decision={'proposal_id':pid,'proposal_sha256':fingerprint(verified['proposal']),'state':'APPROVED',
        'valid_from':start,'expires_at':end,'previous_decision_id':None}
    # A fresh guard issues synthetic permits in this fixture only.
    fresh=LedgerGuard(config['checkpoints'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=trust);fresh.acquire(config['database'],readonly=True)
    dp=permit(fresh,did,'decide',decision);fresh.close()
    code,approved=cli(base,['--record-recovery-decision','--commit-recovery','--operation-id',did],{**blobs,'--recovery-payload-fd':decision,'--permit-fd':dp})
    assert code==0,approved
    code,restarted=cli(base,['--recovery-registry-status','--operation-id',did],blobs)
    assert code==0 and restarted['proposals'][0]['state']=='APPROVED'
    external=restarted['reference']
    # Advance the enrolled source under its original ownership/witness. No app
    # scheduler or execution worker is running, and all tasks remain held/UNKNOWN.
    fresh=LedgerGuard(config['checkpoints'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=trust)
    registry=RecoveryRegistry(fresh,config,external,OperatorPermits(OPKEY))
    a=Authority(root/'new-store/state.sqlite',ledger=fresh,enrollment_context=enrolled['witness'],recovery_registry=registry)
    a.submit(actor,uid(),'held new checkpoint generation')
    while fresh._epoch==external['witness']['checkpoint']['epoch']:
        a.submit(actor,uid(),'held work advances into the next protected generation')
    start,end=interval();nxt=fresh.trust_reference(valid_from=start,expires_at=end)
    assert nxt['epoch']==external['witness']['checkpoint']['epoch']+1
    rid=uid();renewal={'previous_witness':external['witness'],'next_reference':nxt};rp=permit(fresh,rid,'renew',renewal)
    a.close()
    blobs['--registry-reference-fd']=external;blobs['--trust-fd']=nxt
    code,renewed=cli(base,['--renew-recovery-witness','--commit-recovery','--operation-id',rid],{**blobs,'--recovery-payload-fd':renewal,'--permit-fd':rp})
    assert code==0,renewed
    code,newstatus=cli(base,['--recovery-registry-status','--operation-id',rid],blobs);assert code==0,newstatus
    # The actual app consumes a configured read-only registry view at startup,
    # readiness, diagnostics, and shutdown; no recovery mutation endpoint exists.
    fresh=LedgerGuard(config['checkpoints'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=nxt)
    registry=RecoveryRegistry(fresh,config,newstatus['reference'],OperatorPermits(OPKEY))
    a=Authority(root/'new-store/state.sqlite',ledger=fresh,enrollment_context=enrolled['witness'],recovery_registry=registry)
    runtime.bind_authority(a);server.settings.server.api_token='sprint5-synthetic-token'
    headers={'Authorization':'Bearer sprint5-synthetic-token'}
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=headers) as client:
            ready=(await client.get('/ready')).json();diag=(await client.get('/operator/diagnostics')).json()
            assert ready['recovery_decisions']['proposal_counts']['APPROVED']==1
            assert 'proposals' not in ready['recovery_decisions'] and 'reference' not in ready['recovery_decisions']
            assert diag['recovery_decisions']['proposals'][0]['state']=='APPROVED'
            assert (await client.get('/tasks/'+unknown)).json()['status']=='unknown'
            for path in ('/operator/recovery-decision','/operator/approve','/operator/renew-witness','/operator/activate'):
                assert (await client.post(path,json={})).status_code==404
            server.settings.server.api_token=''
            assert (await client.get('/operator/diagnostics')).status_code==401
            anonymous=(await client.get('/ready')).json()
            assert 'source_archive' not in json.dumps(anonymous['recovery_decisions'])
            receipt=approved['receipt']
            verified_receipt=verify_receipt(fresh,receipt,registry_id=config['registry_id'],request_id=did,
                payload_sha256=fingerprint(decision),event_sha256=fingerprint(receipt['event']),permits=OperatorPermits(OPKEY))
    assert a._shutdown_recovery_status['verified']
    server.settings.server.api_token=''
    # Committed decision with a lost final receipt must block actual startup;
    # cleanup releases ownership, then only explicit same-ID CLI continuation
    # may publish its already authorized receipt.
    failure_guard=LedgerGuard(config['checkpoints'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=nxt)
    pending_registry=RecoveryRegistry(failure_guard,config,newstatus['reference'],OperatorPermits(OPKEY))
    blocked=Authority(root/'new-store/state.sqlite',ledger=failure_guard,enrollment_context=enrolled['witness'],recovery_registry=pending_registry)
    revoke_id=uid();start,end=interval()
    revoke={'proposal_id':pid,'proposal_sha256':fingerprint(verified['proposal']),'state':'REVOKED',
        'valid_from':start,'expires_at':end,'previous_decision_id':did}
    revoke_permit=permit(failure_guard,revoke_id,'decide',revoke)
    def lost_receipt(stage):
        if stage=='recovery_sql_committed':raise OSError('synthetic lost receipt after durable decision')
    pending_registry._fault=lost_receipt
    try:pending_registry.apply(actor,revoke_id,'decide',revoke,revoke_permit)
    except OSError:pass
    else:raise AssertionError('synthetic receipt interruption missing')
    runtime.bind_authority(blocked)
    try:
        async with app.router.lifespan_context(app):
            raise AssertionError('incomplete recovery decision admitted app startup')
    except AuthorityError as exc:
        assert exc.code=='recovery_reconciliation_required';startup_block=exc.code
    assert runtime._authority is None and blocked._closed and not blocked._shutdown_recovery_status['verified']
    blobs['--registry-reference-fd']=newstatus['reference']
    code,reconciled=cli(base,['--reconcile-recovery-operation','--commit-recovery','--operation-id',revoke_id],
        {**blobs,'--recovery-payload-fd':{'command':'decide','payload':revoke},'--permit-fd':revoke_permit})
    assert code==0 and reconciled['replayed'],reconciled
    code,final_status=cli(base,['--recovery-registry-status','--operation-id',revoke_id],blobs)
    assert code==0 and final_status['proposals'][0]['state']=='REVOKED'
    demo={'workflow':'verified restore -> durable proposal -> authenticated decision -> receipt -> restart',
        'initialized':init,'proposal':proposed,'approved':approved,'restart':restarted,
        'renewal':renewed,'renewal_restart':newstatus,'ready':ready,'diagnostics':diag,
        'independent_receipt_verification':verified_receipt,'original_unknown_request_id':unknown,
        'original_occurrence_ids':verified['proposal']['original_occurrence_ids'],
        'shutdown_check':a._shutdown_recovery_status,'incomplete_startup_refusal':startup_block,
        'explicit_same_id_reconciliation':reconciled,'final_registry_status':final_status,'execution_enabled':False,'activation_authorized':False}
    Path('/work/RECOVERY-DECISIONS-DEMONSTRATION.json').write_text(json.dumps(demo,indent=2)+'\n')
    return ['actual_CLI_restore_proposal_authenticated_decision_receipt_restart_and_witness_renewal',
            'actual_app_configured_registry_readiness_authenticated_diagnostics_redaction_shutdown_UNKNOWN_no_activation',
            'actual_app_incomplete_decision_blocks_startup_releases_owner_and_requires_exact_CLI_reconciliation']

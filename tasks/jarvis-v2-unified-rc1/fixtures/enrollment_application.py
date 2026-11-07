"""Disposable actual-CLI/app ceremony; invoked only by guarded full-app child."""
from contextlib import redirect_stdout
from datetime import UTC,datetime,timedelta
import hashlib
import io
import json
import os
from pathlib import Path


def cli(base, flags, blobs):
    from app.agent.operator_cli import main
    fds=[];args=list(base)+list(flags)
    try:
        for flag,value in blobs.items():
            raw=value if type(value) is bytes else json.dumps(value).encode()
            fd=os.memfd_create('synthetic-ceremony',os.MFD_CLOEXEC);fds.append(fd)
            os.write(fd,raw);os.lseek(fd,0,os.SEEK_SET);args.extend([flag,str(fd)])
        output=io.StringIO()
        with redirect_stdout(output):code=main(args)
        return code,json.loads(output.getvalue())
    finally:
        for fd in fds:os.close(fd)


async def run(app,server,runtime):
    import httpx
    from app.agent.authority import Authority,AuthorityError
    from app.agent.ledger import LedgerGuard
    from app.agent.recovery import RecoveryActions,OperatorPermits
    from app.agent.execution import ExecutionPipeline,SimulatedPolicy
    from enrollment_fixtures import build,uid,KEY,OPKEY
    actor=runtime.SERVICE_ACTOR;root=Path('/scratch/work/enrollment-app')
    service,permit=build(root);reservation=service.reservation;service.guard.close()
    base=['--checkpoints',str(root/'anchors'),'--store-id',reservation['store_id'],'--rollover-enabled','--epoch-capacity','4']
    enrollment=['--custody',str(root/'custody'),'--operation-id',reservation['enrollment_id']]
    inputs={'--key-fd':KEY,'--reservation-fd':reservation}
    code,status=cli(base,enrollment+['--enrollment-status'],inputs)
    assert code==1 and status['state']=='UNENROLLED'
    code,refused=cli(base,enrollment+['--enroll-store'],inputs)
    assert code==1 and refused['error']=='explicit_recovery_commit_required'
    code,enrolled=cli(base,enrollment+['--enroll-store','--commit-recovery'],{**inputs,'--operator-key-fd':OPKEY,'--permit-fd':permit})
    assert code==0 and enrolled['state']=='VERIFIED'
    code,verified=cli(base,enrollment+['--enrollment-status'],inputs)
    assert code==0 and verified['witness']==enrolled['witness']
    g=LedgerGuard(root/'anchors',KEY,reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    a=Authority(root/'new-store/state.sqlite',ledger=g,enrollment_context=enrolled['witness'],allow_simulation=True)
    runtime.bind_authority(a)
    exports=root/'exports';exports.mkdir(mode=0o700);targets=root/'targets';targets.mkdir(mode=0o700)
    permits=OperatorPermits(OPKEY);actions=RecoveryActions(a,permits)
    def grant(request_id,command,payload,head):
        now=datetime.now(UTC)
        return permits.issue(request_id=request_id,principal='synthetic-operator',scope=actor.scope,command=command,
             payload=payload,checkpoint=head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
    demo={'real_execution_enabled':False,'initial_status':status,'enrollment':enrolled,'verify_enrollment':verified}
    server.settings.server.api_token='sprint4-synthetic-only'
    headers={'Authorization':'Bearer sprint4-synthetic-only'}
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=headers) as client:
            ready=await client.get('/ready');assert ready.status_code==200 and ready.json()['enrollment']['state']=='VERIFIED'
            held_id=uid();admitted=await client.post('/tasks',json={'request_id':held_id,'goal':'enrolled held operation'})
            assert admitted.status_code==200
            pipeline=ExecutionPipeline(a,SimulatedPolicy(actor.scope),enabled=True)
            uncertain=uid();pipeline.submit(actor,uncertain,'uncertain original operation','synthetic.echo',{'value':'no dispatch'},(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
            pipeline._claim(actor,uncertain);pipeline._unknown(actor,uncertain,a.generation,'synthetic uncertain');a.cancel(actor,uid(),uncertain)
            demo['diagnostics']=(await client.get('/operator/diagnostics')).json()
            assert demo['diagnostics']['enrollment']['state']=='VERIFIED' and demo['diagnostics']['unknown']==1
            assert (await client.post('/operator/enrollment',json={})).status_code==404
            export_id=uid();export=actions.export(actor,export_id,exports,grant(export_id,'export_ledger',{'export_id':export_id,'destination':str(exports)},g.history()[0]))
    # The actual shutdown is checkpointed before the externally held reference
    # and permit are issued, avoiding a stale authorization snapshot.
    fresh=LedgerGuard(root/'anchors',KEY,reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    fresh.acquire(root/'new-store/state.sqlite',readonly=True)
    try:
        now=datetime.now(UTC);trust=fresh.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=3)).isoformat())
        head=fresh.history()[0]
    finally:fresh.close()
    restore_id=uid();manifest=export['export']['manifest_sha256']
    blobs={'--key-fd':KEY,'--trust-fd':trust}
    code,archive=cli(base,['--verify-archive',str(exports/export_id),'--expected-manifest-sha256',manifest],blobs);assert code==0
    payload={'export_id':export_id,'manifest_sha256':manifest,'target_parent':str(targets),'restore_id':restore_id}
    code,restored=cli(base,['--restore-archive',str(exports/export_id),'--expected-manifest-sha256',manifest,'--disposable-target-parent',str(targets),'--operation-id',restore_id,'--commit-recovery'],{**blobs,'--operator-key-fd':OPKEY,'--permit-fd':grant(restore_id,'restore_archive',payload,head)})
    assert code==0 and not restored['runtime_activation_allowed']
    now=datetime.now(UTC)
    request=dict(format='jarvis-branch-verification-request-v1',branch_id=uid(),operator_id='synthetic-branch-reviewer',
                 expected_source_head=head,expected_restore_id=restore_id,expected_database_sha256=restored['database_sha256'],
                 expected_source_lineage=restored['source_lineage'],expected_key_id=reservation['key_id'],
                 issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat(),reserved_branch_ids=[],decision='PROPOSE_ONLY')
    def snapshot():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
    before=snapshot()
    code,branch=cli(base,['--verify-branch',str(targets/restore_id)],{**blobs,'--branch-context-fd':request})
    assert code==0 and branch['summary']['unknown']==1 and snapshot()==before
    assert not branch['proposal']['activation_authorized']
    try:Authority(targets/restore_id/'state.sqlite')
    except AuthorityError as exc:assert exc.code=='restore_activation_prohibited'
    else:raise AssertionError('restored branch was activated')
    g=LedgerGuard(root/'anchors',KEY,reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=trust)
    a=Authority(root/'new-store/state.sqlite',ledger=g,enrollment_context=enrolled['witness'])
    runtime.bind_authority(a)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic',headers=headers) as client:
            assert (await client.get('/tasks/'+uncertain)).json()['status']=='unknown'
            assert (await client.get('/ready')).json()['enrollment']['verified']
            demo['restart_diagnostics']=(await client.get('/operator/diagnostics')).json()
    server.settings.server.api_token=''
    demo.update(archive_verification=archive,restoration=restored,branch_verification=branch,
                branch_verification_storage_unchanged=True,operator_decision='REQUIRED_SEPARATE_AUTHORIZATION_NO_ACTIVATION')
    Path('/scratch/work/ENROLLMENT-DEMONSTRATION.json').write_text(json.dumps(demo,indent=2)+'\n')
    return ['actual_authenticated_offline_CLI_enrollment_genesis_receipt_app_startup_and_restart',
            'actual_archive_inert_restore_branch_continuity_readonly_proposal_and_UNKNOWN_preservation']

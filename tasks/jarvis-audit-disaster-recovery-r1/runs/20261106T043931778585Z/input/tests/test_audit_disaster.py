"""Rollover/restore contracts, synthetic keys, disposable SQLite state only."""
from datetime import UTC,datetime,timedelta
import json
from pathlib import Path
import uuid
import pytest
from app.agent.authority import Authority,AuthorityError
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits,RecoveryActions
from app.agent.runtime import SERVICE_ACTOR as ACTOR

KEY=b'synthetic-sprint3-ledger-only-key-00000000'
OPKEY=b'synthetic-sprint3-operator-only-key-000000'

def key():return str(uuid.uuid4())

@pytest.fixture
def env(tmp_path):
    store=key();anchors=tmp_path/'protected';db=tmp_path/'db'/'state.sqlite';exports=tmp_path/'exports';exports.mkdir(mode=0o700)
    g=LedgerGuard(anchors,KEY,store,initialize=True,rollover=True,epoch_capacity=4,recovery=True)
    a=Authority(db,allow_simulation=True,ledger=g)
    permits=OperatorPermits(OPKEY);actions=RecoveryActions(a,permits)
    yield a,g,actions,permits,{'db':db,'anchors':anchors,'exports':exports,'store_id':store,'parent':tmp_path}
    a.close()

def issue(env,command,payload,request_id):
    a,g,actions,permits,paths=env;now=datetime.now(UTC)
    return permits.issue(request_id=request_id,principal='synthetic-operator',scope=ACTOR.scope,command=command,payload=payload,checkpoint=g._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())

def exported(env):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'held synthetic task')
    export_id=key();payload={'export_id':export_id,'destination':str(paths['exports'])}
    return actions.export(ACTOR,export_id,paths['exports'],issue(env,'export_ledger',payload,export_id))

def test_rollover_retains_checkpoint_identities(env):
    a,g,actions,permits,paths=env
    old={p.name:p.read_bytes() for p in paths['anchors'].glob('*.json')}
    for _ in range(8):a.submit(ACTOR,key(),'synthetic')
    head,pending,history=g.history()
    assert g._epoch>=2 and not pending
    assert [h['sequence'] for h in history]==list(range(1,head['sequence']+1))
    assert all((paths['anchors']/name).read_bytes()==raw for name,raw in old.items())
    assert a.readiness()['ledger_integrity']['epoch']>=2

def test_export_attestation_survives_source_database_loss(env):
    a,g,actions,permits,paths=env
    result=exported(env)
    assert result['attestation']['verified']
    verified=g.verify_export(paths['exports']/result['export']['export_id'])
    assert verified['format']=='jarvis-ledger-export-v2'
    assert g.verify_export_attestation(verified)['completion_receipt_id']==result['publication']['request_id']

def test_wrong_key_and_expired_reference_refused(env):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'value')
    now=datetime.now(UTC)
    ref=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    with pytest.raises(AuthorityError,match='checkpoint_trust_key_mismatch'):
        LedgerGuard(paths['anchors'],b'wrong-synthetic-key-0000000000000000000',paths['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)
    ref['expires_at']=(now-timedelta(milliseconds=1)).isoformat()
    with pytest.raises(AuthorityError,match='checkpoint_trust_expired'):
        LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)

def test_total_generation_capacity_is_conservative(env):
    a,g,actions,permits,paths=env
    g.max_epochs=1
    a.submit(ACTOR,key(),'one');a.submit(ACTOR,key(),'two')
    with pytest.raises(AuthorityError,match='checkpoint_generation_capacity'):
        a.submit(ACTOR,key(),'refused')

@pytest.mark.parametrize('fault',['rollover_intent_durable','rollover_link_durable'])
def test_interrupted_rollover_is_not_silently_reset(env,fault):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'one');a.submit(ACTOR,key(),'two')
    def stop(stage):
        if stage==fault:raise RuntimeError('power-loss-like injected interruption')
    g._fault=stop
    with pytest.raises(RuntimeError):a.submit(ACTOR,key(),'interrupted')
    a.close()
    new=LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    if fault=='rollover_intent_durable':
        with pytest.raises(AuthorityError,match='checkpoint_rollover_incomplete'):Authority(paths['db'],ledger=new)
    else:
        recovered=Authority(paths['db'],ledger=new)
        try:assert recovered.readiness()['ledger_integrity']['epoch']==1
        finally:recovered.close()


def restore_ready(env):
    a,g,actions,permits,paths=env
    result=exported(env)
    now=datetime.now(UTC)
    g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
    from app.agent.archive_restore import ArchiveRestorer
    restorer=ArchiveRestorer(g,permits)
    target=paths['parent']/'restores';target.mkdir(mode=0o700)
    return restorer,result,paths['exports']/result['export']['export_id'],target


def restore_permit(env,result,target,restore_id):
    payload={'export_id':result['export']['export_id'],'manifest_sha256':result['export']['manifest_sha256'],'target_parent':str(target),'restore_id':restore_id}
    return issue(env,'restore_archive',payload,restore_id)


def test_restore_reconstructs_exact_disabled_artifact(env):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key();before=g._head.copy()
    receipt=restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert receipt['verified'] and receipt['state']=='committed'
    assert not receipt['execution_enabled'] and not receipt['runtime_activation_allowed']
    assert g._head==before
    artifact=parent/restore_id
    assert restorer.verify_restored(artifact)['summary']['unresolved']==1
    assert restorer.reconcile(restore_id)['replayed']
    with pytest.raises(AuthorityError,match='restore_already_exists_reconcile'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    with pytest.raises(AuthorityError,match='ledger_checkpoint_required'):
        Authority(artifact/'state.sqlite')


def test_default_restore_requires_external_reference_and_explicit_grant(env):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env
    result=exported(env);restorer=ArchiveRestorer(g,permits)
    archive=paths['exports']/result['export']['export_id']
    with pytest.raises(AuthorityError,match='restore_external_trust_reference_required'):
        restorer.verify_archive(archive,result['export']['manifest_sha256'])
    restorer,result,archive,parent=restore_ready_existing(env,result)
    restore_id=key();token=restore_permit(env,result,parent,restore_id)
    with pytest.raises(AuthorityError,match='explicit_disposable_restore_required'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],token)
    token['hmac_sha256']='0'*64
    with pytest.raises(AuthorityError,match='operator_authentication_failed'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],token,disposable=True)
    assert list(parent.iterdir())==[]


def restore_ready_existing(env,result):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env;now=datetime.now(UTC)
    g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
    parent=paths['parent']/'restores';parent.mkdir(mode=0o700)
    return ArchiveRestorer(g,permits),result,paths['exports']/result['export']['export_id'],parent


@pytest.mark.parametrize('damage',['missing','duplicate','modified','reordered'])
def test_archive_disaster_rejected_before_target_creation(env,damage):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    data=archive/'state.jsonl';lines=data.read_bytes().splitlines(keepends=True)
    if damage=='missing':lines.pop()
    elif damage=='duplicate':lines.append(lines[-1])
    elif damage=='modified':lines[-1]=lines[-1].replace(b'events',b'evEnts')
    else:lines[1],lines[2]=lines[2],lines[1]
    data.write_bytes(b''.join(lines))
    restore_id=key()
    with pytest.raises(AuthorityError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert list(parent.iterdir())==[]
    assert not list(g.directory.glob('restore-*.intent.json'))


def test_restored_unknown_and_cancellation_are_preserved(env):
    from app.agent.execution import ExecutionPipeline,SimulatedPolicy
    a,g,actions,permits,paths=env
    p=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
    op=key()
    p.submit(ACTOR,op,'uncertain','synthetic.echo',{'value':'uncertain'},(datetime.now(UTC)+timedelta(minutes=1)).isoformat())
    p._claim(ACTOR,op);p._unknown(ACTOR,op,a.generation,'uncertain');a.cancel(ACTOR,key(),op)
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key()
    restored=restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert restored['summary']['unknown']==1 and restored['summary']['cancel_requested']==1
    import sqlite3
    conn=sqlite3.connect((parent/restore_id/'state.sqlite').as_uri()+'?mode=ro',uri=True)
    try:
        row=json.loads(conn.execute("SELECT data FROM records WHERE kind='task' AND id=?",(op,)).fetchone()[0])
        assert row['status']=='unknown' and row['result'] is None and row['cancel_requested']
    finally:conn.close()


@pytest.mark.parametrize('stage',['restore_intent_durable','restore_row_inserted','restore_prepared_durable','restore_target_published'])
def test_restore_failure_is_quarantined_or_reconciled(env,stage):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key()
    restorer._fault=lambda current:(_ for _ in ()).throw(RuntimeError('simulated power interruption')) if current==stage else None
    with pytest.raises(RuntimeError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    restorer._fault=lambda _:None
    if stage in {'restore_prepared_durable','restore_target_published'}:
        assert restorer.reconcile(restore_id)['verified']
        assert restorer.verify_restored(parent/restore_id)['verified']
    else:
        with pytest.raises(AuthorityError,match='restore_incomplete_manual_quarantine'):restorer.reconcile(restore_id)
        assert not (parent/restore_id).exists()


@pytest.mark.parametrize('mode,stage',[
    ('rollover','rollover_intent_durable'),('rollover','rollover_directory_created'),('rollover','rollover_link_durable'),('rollover','rollover_committed'),
    ('restore','restore_intent_durable'),('restore','restore_stage_created'),('restore','restore_schema_created'),('restore','restore_row_inserted'),
    ('restore','restore_before_database_commit'),('restore','restore_database_committed'),('restore','restore_prepared_durable'),('restore','restore_target_published'),('restore','restore_publication_committed'),
    ('attestation','export_before_attestation'),('rollover_recovery','rollover_recovery_admitted'),
])
def test_independent_sigkill_disaster_recovery(tmp_path,mode,stage):
    import subprocess,sys,time
    from app.agent.archive_restore import ArchiveRestorer
    if not Path('/input/source').is_dir():pytest.skip('guarded runner required')
    root=tmp_path/'case';root.mkdir(mode=0o700)
    for name in ('exports','targets'):(root/name).mkdir(mode=0o700)
    config={'mode':mode,'stage':stage,'anchors':str(root/'protected'),'db':str(root/'db'/'state.sqlite'),
        'exports':str(root/'exports'),'targets':str(root/'targets'),'ready':str(root/'ready'),'context':str(root/'context.json'),
        'store_id':key(),'task_id':key(),'extra_id':key(),'request_id':key(),'failed_request_id':key(),'export_id':key()}
    path=root/'command.json';path.write_text(json.dumps(config))
    with (root/'stdout').open('w') as out,(root/'stderr').open('w') as err:
        child=subprocess.Popen([sys.executable,'-I','-B','-S',str(Path(__file__).with_name('audit_process_actor.py')),str(path)],stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,env={'LANG':'C.UTF-8'})
        try:
            deadline=time.monotonic()+4
            while not Path(config['ready']).exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(.01)
            assert Path(config['ready']).exists(),(root/'stderr').read_text()
            child.kill();child.wait(timeout=1)
            assert child.returncode<0
        finally:
            if child.poll() is None:child.kill()
            child.wait(timeout=1)
    ref=json.loads(Path(config['context']).read_text())
    def new_guard():return LedgerGuard(config['anchors'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)
    if mode=='rollover':
        if stage in {'rollover_intent_durable','rollover_directory_created'}:
            with pytest.raises(AuthorityError,match='checkpoint_rollover_incomplete'):Authority(config['db'],ledger=new_guard())
            g=new_guard();g.acquire(config['db'])
            try:
                body=json.loads((Path(config['anchors'])/'rollover-0001.intent.json').read_text())['body']
                issuer=OperatorPermits(OPKEY);now=datetime.now(UTC);request_id=key()
                permit=issuer.issue(request_id=request_id,principal='synthetic-operator',scope=ACTOR.scope,command='resume_rollover',payload={'operation_id':body['operation_id']},checkpoint=ref['head'],issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
                assert g.resume_rollover(permit,issuer,ACTOR,request_id)['epoch']==1
            finally:g.close()
        a=Authority(config['db'],ledger=new_guard())
        try:
            assert a.readiness()['ledger_integrity']['epoch']==1
            assert a.receipt(ACTOR,config['request_id']) is None
            assert len(a.list_tasks(ACTOR))==2
        finally:a.close()
    elif mode=='rollover_recovery':
        from unittest.mock import patch
        g=new_guard();g.acquire(config['db'])
        try:
            with patch.object(OperatorPermits,'verify',side_effect=AssertionError('expired grant must not be reauthenticated')):
                result=g.resume_rollover(None,None,ACTOR,config['request_id'])
                assert result['replayed'] and result['epoch']==1
                assert g.resume_rollover(None,None,ACTOR,config['request_id'])['replayed']
        finally:g.close()
        a=Authority(config['db'],ledger=new_guard())
        try:assert len(a.list_tasks(ACTOR))==2
        finally:a.close()
    elif mode=='attestation':
        a=Authority(config['db'],ledger=new_guard())
        try:
            g=a._ledger;actions=RecoveryActions(a,OperatorPermits(OPKEY));archive=root/'exports'/config['export_id']
            verified=g.verify_export(archive)
            with pytest.raises(AuthorityError):g.verify_export_attestation(verified)
            actions.reconcile_admitted_export(ACTOR,config['export_id'],root/'exports')
            assert g.verify_export_attestation(verified)['verified']
        finally:a.close()
    else:
        g=new_guard();g.acquire(root/'targets'/'unused.sqlite')
        try:
            restorer=ArchiveRestorer(g,OperatorPermits(OPKEY));target=root/'targets'/config['request_id']
            prepared=stage in {'restore_prepared_durable','restore_target_published','restore_publication_committed'}
            if prepared:
                result=restorer.reconcile(config['request_id'])
                assert result['verified'] and restorer.verify_restored(target)['verified']
                assert not result['execution_enabled']
            else:
                with pytest.raises(AuthorityError,match='restore_incomplete_manual_quarantine'):restorer.reconcile(config['request_id'])
                assert not target.exists()
            assert g.disaster_status()['restores'][0]['status']==('committed' if prepared else 'incomplete')
        finally:g.close()


@pytest.mark.parametrize('phase',['intent','prepared','final'])
def test_missing_restore_receipt_phase_is_not_reported_committed(env,phase):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    (g.directory/f'restore-{restore_id}.{phase}.json').unlink() # disposable disaster injection only
    if phase=='final':
        assert g.disaster_status()['restores'][0]['status']=='prepared'
        with pytest.raises(AuthorityError):restorer.verify_restored(parent/restore_id)
    else:
        with pytest.raises(AuthorityError,match='restore_history_incomplete'):g.disaster_status()


def test_wrong_rollover_policy_and_unexpected_generation_refused(env):
    a,g,actions,permits,paths=env
    for _ in range(4):a.submit(ACTOR,key(),'value')
    a.close()
    wrong=LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=8,recovery=True)
    with pytest.raises(AuthorityError,match='checkpoint_rollover_binding_mismatch'):Authority(paths['db'],ledger=wrong)
    extra=paths['anchors']/'epoch-0015';extra.mkdir(mode=0o700)
    normal=LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    with pytest.raises(AuthorityError,match='checkpoint_generation_gap'):Authority(paths['db'],ledger=normal)


def test_cached_checkpoint_bytes_are_still_hash_verified(env):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'value');a.readiness();hits=g.cache_hits
    a.readiness();assert g.cache_hits>hits
    final=sorted(g.directory.glob('*.final.json'))[-1]
    body=json.loads(final.read_text());body['body']['sha256']='0'*64
    final.write_text(json.dumps(body))
    with pytest.raises(AuthorityError,match='checkpoint_authentication_failed'):a.readiness()


def test_shared_guard_restore_serializes_source_mutations(env):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key();token=restore_permit(env,result,parent,restore_id)
    entered=threading.Event();release=threading.Event()
    def fault(stage):
        if stage=='restore_prepared_durable':
            entered.set();assert release.wait(2)
    restorer._fault=fault
    with ThreadPoolExecutor(max_workers=2) as pool:
        restore=pool.submit(restorer.restore,ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],token,disposable=True)
        assert entered.wait(2)
        mutation=pool.submit(a.submit,ACTOR,key(),'wait for restore')
        assert not mutation.done()
        release.set()
        assert restore.result(timeout=3)['verified']
        assert mutation.result(timeout=3)['state']=='committed'


def test_restore_does_not_require_source_database_or_archive_after_preparation(env):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    archive.rename(archive.with_name('unavailable-media'))
    assert restorer.verify_restored(parent/restore_id)['verified']


def test_guard_cannot_be_shared_by_two_authorities(env):
    a,g,actions,permits,paths=env
    with pytest.raises(AuthorityError,match='checkpoint_owner_busy'):Authority(paths['parent']/'other'/'db',ledger=g)
    assert a.readiness()['ledger_integrity']['verified']


def test_incompatible_signed_schema_is_never_executed(env):
    a,g,actions,permits,paths=env
    def extra(scope):
        a._conn.execute('CREATE INDEX synthetic_extra ON outbox(state)')
        return {'synthetic_schema_extension':True}
    a._mutate(ACTOR,key(),'synthetic_schema_fixture',{},extra)
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key()
    with pytest.raises(AuthorityError,match='restore_incompatible_schema'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert list(parent.iterdir())==[]


def test_inconsistent_restored_receipt_and_corrupt_pages_refused(env):
    import os,sqlite3
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    db=parent/restore_id/'state.sqlite';os.chmod(db,0o600)
    conn=sqlite3.connect(db)
    try:conn.execute('DELETE FROM receipts WHERE rowid=(SELECT MIN(rowid) FROM receipts)');conn.commit()
    finally:conn.close()
    os.chmod(db,0o400)
    with pytest.raises(AuthorityError,match='restore_database_modified'):restorer.verify_restored(parent/restore_id)


@pytest.mark.parametrize('failure',['disk_full','permission'])
def test_restore_publication_storage_failures_preserve_prepared_evidence(env,monkeypatch,failure):
    import app.agent.archive_restore as module
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    original=module.publish_file
    def fail(path,raw):
        if path.name.endswith('.final.json') and path.name.startswith('restore-'):
            raise OSError(28 if failure=='disk_full' else 13,'synthetic storage failure')
        return original(path,raw)
    monkeypatch.setattr(module,'publish_file',fail)
    with pytest.raises(OSError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    with pytest.raises(AuthorityError):restorer.verify_restored(parent/restore_id)
    monkeypatch.setattr(module,'publish_file',original)
    assert restorer.reconcile(restore_id)['verified']


def test_trust_reference_rejects_rolled_back_checkpoint_generation(env):
    import shutil
    a,g,actions,permits,paths=env
    prior=paths['parent']/'prior-anchors';shutil.copytree(g.directory,prior)
    for _ in range(4):a.submit(ACTOR,key(),'history')
    now=datetime.now(UTC)
    reference=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    a.close()
    # A separate copied old tree models rollback; original evidence is retained.
    rolled=LedgerGuard(prior,KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=reference)
    rolled.acquire(paths['parent']/'unused'/'db')
    try:
        with pytest.raises(AuthorityError,match='checkpoint_external_reference_mismatch'):rolled.history()
    finally:rolled.close()


def test_trust_reference_cannot_claim_a_different_epoch(env):
    a,g,actions,permits,paths=env
    for _ in range(4):a.submit(ACTOR,key(),'history')
    now=datetime.now(UTC)
    ref=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    ref.update(epoch=0,rollover_hash='0'*64)
    g.trust_context=ref
    with pytest.raises(AuthorityError,match='checkpoint_external_reference_mismatch'):a.readiness()


def test_missing_export_attestation_invalidates_restore_history(env):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    (g.directory/f"export-{result['export']['export_id']}.json").unlink()
    with pytest.raises(AuthorityError):g.disaster_status()


def test_offline_cli_verifies_and_commits_only_explicit_authorized_restore(env,capsys):
    import os
    from app.agent.operator_cli import main
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    token=restore_permit(env,result,parent,restore_id);ctx=g.trust_context
    a.close()
    def cli(extra,with_permit=False):
        fds=[];args=['--checkpoints',str(paths['anchors']),'--store-id',paths['store_id'],'--rollover-enabled','--epoch-capacity','4']
        try:
            for option,value in [('--key-fd',KEY),('--trust-fd',json.dumps(ctx).encode())]+([('--operator-key-fd',OPKEY),('--permit-fd',json.dumps(token).encode())] if with_permit else []):
                read,write=os.pipe();os.write(write,value);os.close(write);fds.append(read);args.extend([option,str(read)])
            code=main(args+extra);return code,json.loads(capsys.readouterr().out)
        finally:
            for fd in fds:os.close(fd)
    code,verified=cli(['--verify-archive',str(archive),'--expected-manifest-sha256',result['export']['manifest_sha256']])
    assert code==0 and verified['schema_compatible'] and not verified['semantic_restore_verified']
    options=['--restore-archive',str(archive),'--operation-id',restore_id,'--disposable-target-parent',str(parent),'--expected-manifest-sha256',result['export']['manifest_sha256']]
    code,refused=cli(options,True);assert code==1 and refused['error']=='explicit_recovery_commit_required'
    assert list(parent.iterdir())==[]
    code,restored=cli(options+['--commit-recovery'],True);assert code==0 and restored['state']=='committed'
    code,verified=cli(['--verify-restored',str(parent/restore_id)])
    assert code==0 and verified['verified'] and not verified['runtime_activation_allowed']


def test_actual_restored_page_bit_flip_is_detected(env):
    import os
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    db=parent/restore_id/'state.sqlite';assert db.stat().st_size>8192
    os.chmod(db,0o600)
    with db.open('r+b') as stream:
        stream.seek(4096+128);old=stream.read(1);stream.seek(4096+128);stream.write(bytes([old[0]^255]));stream.flush();os.fsync(stream.fileno())
    os.chmod(db,0o400)
    with pytest.raises(AuthorityError,match='restore_database_modified'):restorer.verify_restored(parent/restore_id)


@pytest.mark.parametrize('target_kind',['traversal','overlap','symlink','existing'])
def test_restore_paths_and_existing_targets_refused(env,target_kind):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    if target_kind=='traversal':parent=parent/'..'/'protected'
    elif target_kind=='overlap':parent=g.directory
    elif target_kind=='symlink':
        link=paths['parent']/'linked-archive';link.symlink_to(archive,target_is_directory=True);archive=link
    else:
        (parent/restore_id).mkdir(mode=0o700);(parent/restore_id/'sentinel').write_text('preserve')
    with pytest.raises(AuthorityError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert not (g.directory/f'restore-{restore_id}.intent.json').exists()
    if target_kind=='existing':assert (parent/restore_id/'sentinel').read_text()=='preserve'


def test_no_replace_publication_preserves_a_racing_target(env):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env);restore_id=key()
    def race(stage):
        if stage=='restore_before_publication':
            (parent/restore_id).mkdir(mode=0o700);(parent/restore_id/'sentinel').write_text('foreign target')
    restorer._fault=race
    with pytest.raises(OSError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert (parent/restore_id/'sentinel').read_text()=='foreign target'
    with pytest.raises(AuthorityError,match='restore_target_conflict'):restorer.reconcile(restore_id)


def test_attestation_removal_is_detected_even_before_any_restore(env):
    a,g,actions,permits,paths=env
    result=exported(env)
    assert a.receipt(ACTOR,__import__('app.agent.execution',fromlist=['phase_id']).phase_id(result['export']['export_id'],'export_attested'))
    (g.directory/f"export-{result['export']['export_id']}.json").unlink()
    with pytest.raises(AuthorityError):a.readiness()


def test_recovery_receipt_is_bound_to_committed_rollover(env):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'one');a.submit(ACTOR,key(),'two')
    def interrupted(stage):
        if stage=='rollover_intent_durable':raise RuntimeError('stop')
    g._fault=interrupted
    with pytest.raises(RuntimeError):a.submit(ACTOR,key(),'stop')
    a.close()
    g=LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    g.acquire(paths['db'])
    try:
        body=json.loads((g.directory/'rollover-0001.intent.json').read_text())['body'];now=datetime.now(UTC);request_id=key()
        token=permits.issue(request_id=request_id,principal='synthetic-operator',scope=ACTOR.scope,command='resume_rollover',payload={'operation_id':body['operation_id']},checkpoint=body['previous_head'],issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
        g.resume_rollover(token,permits,ACTOR,request_id)
        (g.directory/'rollover-0001.recovery.json').unlink()
        with pytest.raises(AuthorityError,match='checkpoint_generation_link_mismatch'):g.history()
    finally:g.close()


def test_restore_succeeds_with_source_database_unavailable(env):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    context=g.trust_context;head=g._head.copy();a.close()
    paths['db'].rename(paths['db'].with_suffix('.unavailable'))
    fresh=LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=context)
    fresh.acquire(parent/'unused.sqlite')
    try:
        restore_id=key();now=datetime.now(UTC)
        payload={'export_id':result['export']['export_id'],'manifest_sha256':result['export']['manifest_sha256'],'target_parent':str(parent),'restore_id':restore_id}
        token=permits.issue(request_id=restore_id,principal='synthetic-operator',scope=ACTOR.scope,command='restore_archive',payload=payload,checkpoint=head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
        restored=ArchiveRestorer(fresh,permits).restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],token,disposable=True)
        assert restored['verified'] and not paths['db'].exists()
        assert ArchiveRestorer(fresh).verify_restored(parent/restore_id)['verified']
    finally:fresh.close()


def test_expired_external_context_never_creates_an_anchor_directory(env):
    a,g,actions,permits,paths=env;now=datetime.now(UTC)
    ref=g.trust_reference(valid_from=(now-timedelta(seconds=3)).isoformat(),expires_at=(now-timedelta(seconds=1)).isoformat())
    target=paths['parent']/'must-not-be-created'
    with pytest.raises(AuthorityError,match='checkpoint_trust_expired'):
        LedgerGuard(target,KEY,paths['store_id'],initialize=True,rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)
    assert not target.exists()

"""Production enrollment/branch checks use real Authority; no fixture bootstrap."""
from datetime import UTC,datetime,timedelta
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import pytest
from app.agent.authority import Authority,AuthorityError
from app.agent.enrollment import OfflineEnrollment,EMPTY_HEAD
from app.agent.ledger import LedgerGuard,encode,digest_state
from app.agent.runtime import SERVICE_ACTOR as ACTOR
from enrollment_fixtures import build,reopen,uid,KEY,OPKEY


@pytest.fixture
def env(tmp_path):
    service,permit=build(tmp_path/'case')
    yield service,permit
    service.guard.close()


def opened(service, result):
    service.guard.close()
    g=LedgerGuard(service.guard.directory,KEY,service.guard.store_id,rollover=True,epoch_capacity=4,recovery=True)
    return Authority(service.destination/'state.sqlite',ledger=g,enrollment_context=result['witness'],allow_simulation=True)


def test_enroll_genesis_receipt_restart_verification(env):
    s,permit=env;result=s.enroll(ACTOR,permit,disposable=True)
    assert result['state']=='VERIFIED' and result['witness']['genesis']['sequence']==1
    assert s.verify()==result
    a=opened(s,result)
    try:
        assert a.generation==1 and a.readiness()['enrollment']['state']=='VERIFIED'
        receipt=a.receipt(ACTOR,s.reservation['enrollment_id'])
        assert receipt['operation']=='enroll_authority' and receipt['owner_generation']==0
        a.submit(ACTOR,uid(),'held offline')
    finally:a.close()
    a=opened(s,result)
    try:assert a.generation==2 and len(a.list_tasks(ACTOR))==1
    finally:a.close()


@pytest.mark.parametrize('kind',['absent','zero','schema'])
def test_plain_authority_never_creates_or_completes_store(tmp_path,kind):
    path=tmp_path/'missing'/'state.sqlite'
    if kind!='absent':
        path.parent.mkdir(mode=0o700);path.write_bytes(b'');path.chmod(0o600)
        if kind=='schema':
            from app.agent.ledger_schema import SCHEMA_SQL
            c=sqlite3.connect(path);c.executescript(SCHEMA_SQL);c.close()
    before={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises(AuthorityError):Authority(path)
    assert {str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file() and not p.name.endswith('.writer.lock')}==before
    if kind=='absent':assert not path.parent.exists()


@pytest.mark.parametrize('fault',['permit','trust','existing','history','scope','explicit'])
def test_invalid_new_store_admission_is_refused(env,fault):
    s,p=env
    if fault=='permit':p['hmac_sha256']='0'*64
    if fault=='trust':s.reservation['key_id']='0'*64
    if fault=='existing':s.destination.mkdir(mode=0o700)
    if fault=='history':
        # Checkpoint evidence cannot be mistaken for a fresh empty authority.
        (s.guard.directory/'00000001.intent.json').write_text('{}')
        (s.guard.directory/'00000001.intent.json').chmod(0o600)
    if fault=='scope':
        from app.agent.authority import Actor
        actor=Actor('untrusted')
    else:actor=ACTOR
    with pytest.raises(AuthorityError):s.enroll(actor,p,disposable=fault!='explicit')
    assert not (s.custody/'INTENT.json').exists()


def test_missing_database_final_never_recreates(env):
    s,p=env;r=s.enroll(ACTOR,p,disposable=True)
    (s.destination/'state.sqlite').rename(s.destination/'state.sqlite.unavailable')
    with pytest.raises(AuthorityError,match='enrollment_missing_database_no_recreate'):s.reconcile()
    with pytest.raises(AuthorityError,match='authority_unenrolled_or_missing'):Authority(s.destination/'state.sqlite')
    assert not (s.destination/'state.sqlite').exists()


@pytest.mark.parametrize('damage',['witness','marker','final','prepared','database','key'])
def test_enrollment_identity_and_phase_corruption_refused(env,damage):
    s,p=env;r=s.enroll(ACTOR,p,disposable=True)
    if damage=='witness':r['witness']['final_sha256']='0'*64
    elif damage in ('final','prepared'):(s.custody/(damage.upper()+'.json')).rename(s.custody/(damage.upper()+'.missing'))
    elif damage=='marker':(s.destination/'ENROLLMENT.json').write_bytes(b'{}')
    elif damage=='database':
        c=sqlite3.connect(s.destination/'state.sqlite');c.execute("UPDATE control SET epoch=123");c.commit();c.close()
    elif damage=='key':
        s.guard.close();g=LedgerGuard(s.guard.directory,b'wrong-synthetic-key-0000000000000000000',s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True)
        with pytest.raises(AuthorityError):Authority(s.destination/'state.sqlite',ledger=g,enrollment_context=r['witness'])
        return
    with pytest.raises(AuthorityError):opened(s,r)


def test_enrolled_store_requires_external_witness(env):
    s,p=env;s.enroll(ACTOR,p,disposable=True);s.guard.close()
    g=LedgerGuard(s.guard.directory,KEY,s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True)
    with pytest.raises(AuthorityError,match='enrollment_external_witness_required'):Authority(s.destination/'state.sqlite',ledger=g)


STAGES=['enrollment_intent_durable','enrollment_stage_created','enrollment_database_created',
        'enrollment_before_database_commit','enrollment_database_committed','enrollment_genesis_intent_durable',
        'enrollment_genesis_published','enrollment_prepared_durable','enrollment_before_publication',
        'enrollment_target_published','enrollment_final_durable','checkpoint_before_publication','checkpoint_published']


@pytest.mark.parametrize('stage',STAGES)
def test_independent_sigkill_enrollment(tmp_path,stage):
    root=tmp_path/'case';root.mkdir(mode=0o700)
    command={'root':str(root),'stage':stage};config=root/'command.json';config.write_text(json.dumps(command))
    with (root/'out').open('w') as out,(root/'err').open('w') as err:
        child=subprocess.Popen([sys.executable,'-I','-B','-S',str(Path(__file__).with_name('enrollment_process_actor.py')),str(config)],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env={'LANG':'C.UTF-8'},close_fds=True)
        try:
            until=time.monotonic()+4
            while not (root/'ready').exists() and child.poll() is None and time.monotonic()<until:time.sleep(.01)
            assert (root/'ready').exists(),(root/'err').read_text()
            if stage=='enrollment_intent_durable':
                reservation=json.loads((root/'reservation.json').read_text())
                contender=LedgerGuard(root/'anchors',KEY,reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True)
                with pytest.raises(AuthorityError,match='checkpoint_owner_busy'):contender.acquire(root/'new-store/state.sqlite')
            child.kill();child.wait(timeout=1);assert child.returncode<0
        finally:
            if child.poll() is None:child.kill()
            child.wait(timeout=1)
    reservation=json.loads((root/'reservation.json').read_text());s=reopen(root,reservation)
    try:
        # No ordinary open may create a store during the unfinished ceremony.
        if stage!='enrollment_final_durable':
            with pytest.raises(AuthorityError):Authority(s.destination/'state.sqlite')
        if stage in ('enrollment_database_created','enrollment_before_database_commit'):
            with pytest.raises(AuthorityError):s.reconcile()
            assert not s.destination.exists() and s.stage.exists()
        else:
            result=s.reconcile();assert result['state']=='VERIFIED'
            a=opened(s,result)
            try:assert a.readiness()['enrollment']['verified'] and a.generation==1
            finally:a.close()
    finally:s.guard.close()


@pytest.mark.parametrize('errno_value',[28,13])
def test_enrollment_publication_storage_errors_preserve_recovery(env,errno_value,monkeypatch):
    s,p=env
    import app.agent.enrollment as module
    original=module._rename_directory
    monkeypatch.setattr(module,'_rename_directory',lambda *args:(_ for _ in ()).throw(OSError(errno_value,'synthetic storage failure')))
    with pytest.raises(OSError):s.enroll(ACTOR,p,disposable=True)
    assert (s.custody/'PREPARED.json').exists() and not s.destination.exists()
    monkeypatch.setattr(module,'_rename_directory',original)
    assert s.reconcile()['state']=='VERIFIED'


def test_enrollment_durable_admission_expiry_and_duplicate(env,monkeypatch):
    s,p=env;s._fault=lambda stage:(_ for _ in ()).throw(RuntimeError('stop')) if stage=='enrollment_intent_durable' else None
    with pytest.raises(RuntimeError):s.enroll(ACTOR,p,disposable=True)
    s._fault=lambda _:None
    monkeypatch.setattr(s.permits,'verify',lambda *a:(_ for _ in ()).throw(AssertionError('must use durable admission')))
    assert s.reconcile()['state']=='VERIFIED'
    with pytest.raises(AuthorityError,match='enrollment_exists_reconcile'):s.enroll(ACTOR,p,disposable=True)


@pytest.fixture
def branch(env):
    from app.agent.recovery import RecoveryActions,OperatorPermits
    from app.agent.execution import ExecutionPipeline,SimulatedPolicy
    from app.agent.archive_restore import ArchiveRestorer
    s,p=env;result=s.enroll(ACTOR,p,disposable=True);a=opened(s,result)
    g=a._ledger;s.guard=g
    permits=OperatorPermits(OPKEY);actions=RecoveryActions(a,permits)
    root=s.destination.parent;exports=root/'exports';exports.mkdir(mode=0o700)
    targets=root/'targets';targets.mkdir(mode=0o700)
    pipeline=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
    op=uid();now=datetime.now(UTC)
    pipeline.submit(ACTOR,op,'uncertain restored work','synthetic.echo',{'value':'not dispatched'},(now+timedelta(minutes=2)).isoformat())
    pipeline._claim(ACTOR,op);pipeline._unknown(ACTOR,op,a.generation,'unknown');a.cancel(ACTOR,uid(),op)
    def grant(request,command,payload):
        now=datetime.now(UTC)
        return permits.issue(request_id=request,principal='synthetic-operator',scope=ACTOR.scope,command=command,payload=payload,checkpoint=g.history()[0],issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    export_id=uid();export=actions.export(ACTOR,export_id,exports,grant(export_id,'export_ledger',{'export_id':export_id,'destination':str(exports)}))
    now=datetime.now(UTC);g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=3)).isoformat())
    restore_id=uid();manifest=export['export']['manifest_sha256']
    restored=ArchiveRestorer(g,permits).restore(ACTOR,restore_id,exports/export_id,targets,manifest,grant(restore_id,'restore_archive',{'export_id':export_id,'manifest_sha256':manifest,'target_parent':str(targets),'restore_id':restore_id}),disposable=True)
    request=dict(format='jarvis-branch-verification-request-v1',branch_id=uid(),operator_id='synthetic-offline-operator',
                 expected_source_head=g.history()[0],expected_restore_id=restore_id,expected_database_sha256=restored['database_sha256'],
                 expected_source_lineage=restored['source_lineage'],expected_key_id=g.key_id,
                 issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat(),reserved_branch_ids=[],decision='PROPOSE_ONLY')
    yield a,targets/restore_id,request,op,result
    a.close()


def tree_bytes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


def test_branch_continuity_proposal_is_readonly_and_preserves_unknown(branch):
    from app.agent.branch_verification import BranchVerifier
    a,target,request,op,enrollment=branch
    before=tree_bytes(target.parent.parent)
    result=BranchVerifier(a._ledger).verify(target,request)
    assert tree_bytes(target.parent.parent)==before
    assert result['state']=='VERIFIED' and result['summary']['unknown']==1 and result['summary']['cancel_requested']==1
    assert result['proposal']['original_store_id']==a._ledger.store_id
    assert not result['proposal']['activation_authorized'] and not result['proposal']['execution_enabled']
    assert BranchVerifier(a._ledger).verify(target,request)['proposal_sha256']==result['proposal_sha256']
    assert a.get_task(ACTOR,op)['status']=='unknown'


@pytest.mark.parametrize('damage',['head','restore','digest','generation','key','expired','duplicate','activate','registry','marker','database','phase','copy'])
def test_branch_invalid_or_stale_state_is_refused(branch,damage):
    from app.agent.branch_verification import BranchVerifier
    import shutil
    a,target,r,op,enrollment=branch
    if damage=='head':a.submit(ACTOR,uid(),'descendant makes old verification context stale')
    elif damage=='restore':r['expected_restore_id']=uid()
    elif damage=='digest':r['expected_database_sha256']='0'*64
    elif damage=='generation':r['expected_source_lineage']['epoch']+=1
    elif damage=='key':r['expected_key_id']='0'*64
    elif damage=='expired':r['expires_at']=(datetime.now(UTC)-timedelta(seconds=1)).isoformat()
    elif damage=='duplicate':r['reserved_branch_ids']=[r['branch_id']]
    elif damage=='activate':r['decision']='ACTIVATE'
    elif damage=='registry':r['reserved_branch_ids']=[uid()]*65
    elif damage=='marker':(target/'DISPOSABLE.json').write_text('{}')
    elif damage=='database':
        db=target/'state.sqlite';db.chmod(0o600)
        c=sqlite3.connect(db);c.execute('UPDATE control SET epoch=456');c.commit();c.close();db.chmod(0o400)
    elif damage=='phase':(a._ledger.directory/f"restore-{r['expected_restore_id']}.prepared.json").unlink()
    elif damage=='copy':
        copy=target.parent.parent/'duplicate';copy.mkdir(mode=0o700);shutil.copytree(target,copy/target.name);target=copy/target.name
    before=tree_bytes(target.parent.parent)
    with pytest.raises(AuthorityError):BranchVerifier(a._ledger).verify(target,r)
    assert tree_bytes(target.parent.parent)==before


def test_deleted_final_after_owner_open_blocks_dispatch(env):
    s,p=env;r=s.enroll(ACTOR,p,disposable=True);a=opened(s,r)
    try:
        (s.custody/'FINAL.json').rename(s.custody/'FINAL.missing')
        with pytest.raises(AuthorityError):a.submit(ACTOR,uid(),'must remain unadmitted')
        assert a._poisoned
    finally:a.close()


def test_unmarked_schema_requires_explicit_legacy_capability(tmp_path):
    from synthetic_authority import seed_legacy_fixture,fixture_authority
    path=tmp_path/'legacy/state.sqlite';seed_legacy_fixture(path)
    with pytest.raises(AuthorityError,match='enrollment_or_explicit_legacy_approval_required'):Authority(path)
    a=fixture_authority(path)
    try:
        assert a.readiness()['enrollment']['state']=='LEGACY_APPROVED'
        assert a.readiness()['enrollment']['new_store_enrollment_proven'] is False
    finally:a.close()


@pytest.mark.parametrize('kind',['symlink','physical_rewrite'])
def test_finalized_genesis_physical_binding_is_verified(env,kind):
    s,p=env;s.enroll(ACTOR,p,disposable=True);db=s.destination/'state.sqlite'
    if kind=='symlink':
        saved=s.destination.parent/'copied.sqlite';db.rename(saved);db.symlink_to(saved)
    else:
        # A legal SQLite VACUUM changes file layout/header while retaining rows.
        c=sqlite3.connect(db);c.execute('VACUUM');c.close()
    with pytest.raises(AuthorityError):s.verify()


def test_branch_replacement_between_verification_and_id_read_is_refused(branch,monkeypatch):
    import app.agent.branch_verification as module
    a,target,r,op,enrollment=branch
    original=module.sqlite3.connect;count=0
    def race(path,*args,**kwargs):
        nonlocal count
        if str(path).startswith((target/'state.sqlite').as_uri()):
            count+=1
            if count==2:
                replacement=target/'race.sqlite';replacement.write_bytes((target/'state.sqlite').read_bytes());replacement.chmod(0o400)
                os.replace(replacement,target/'state.sqlite')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(module.sqlite3,'connect',race)
    with pytest.raises(AuthorityError,match='branch_artifact_changed'):module.BranchVerifier(a._ledger).verify(target,r)


def test_branch_cannot_reuse_an_original_operation_uuid(branch):
    from app.agent.branch_verification import BranchVerifier
    a,target,r,op,enrollment=branch;r['branch_id']=op
    with pytest.raises(AuthorityError,match='branch_identity_collision'):BranchVerifier(a._ledger).verify(target,r)


@pytest.mark.parametrize('change',['domain_collision','policy','target','anchor'])
def test_external_reservation_replacement_refused(env,change):
    s,p=env;r=dict(s.reservation)
    if change=='domain_collision':r['trust_id']=r['store_id']
    elif change=='policy':r['policy']={**r['policy'],'epoch_capacity':5}
    elif change=='target':r['destination']='../outside'
    elif change=='anchor':r['initial_checkpoint']={**EMPTY_HEAD,'sequence':1}
    with pytest.raises(AuthorityError):OfflineEnrollment(s.guard,s.custody,r,s.permits)


def test_invalid_actor_does_not_create_an_intent(env):
    s,p=env
    with pytest.raises(AuthorityError,match='invalid_actor'):s.enroll(object(),p,disposable=True)
    assert not (s.custody/'INTENT.json').exists()

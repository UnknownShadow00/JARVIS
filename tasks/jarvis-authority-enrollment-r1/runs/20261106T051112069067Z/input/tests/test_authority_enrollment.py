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
        'enrollment_target_published','enrollment_final_durable']


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

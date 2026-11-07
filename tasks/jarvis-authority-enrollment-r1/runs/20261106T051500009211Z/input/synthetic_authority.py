"""Explicit legacy fixture setup for pre-enrollment queue regression contracts.

Not an enrollment API. New enrollment/security tests import the real Authority
directly. This creates known synthetic legacy SQL fixtures, never real stores or
production bootstrap capabilities. The product constructor never creates a DB.
"""
from pathlib import Path
import os
import sqlite3
from datetime import UTC,datetime,timedelta
import uuid
from app.agent.authority import Authority as RealAuthority, canonical
from app.agent.ledger_schema import SCHEMA_SQL


def seed_legacy_fixture(path, ledger=None):
    path=Path(path).absolute()
    if path.exists() or path.is_symlink(): return
    if ledger is not None and (not ledger.initialize or ledger._fd is not None): return
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
    conn=sqlite3.connect(path,isolation_level=None)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.execute('INSERT INTO meta VALUES(1)')
        conn.execute("INSERT INTO ownership VALUES(1,0,'synthetic-legacy-fixture')")
        conn.execute('INSERT INTO control VALUES(1,0,0)')
        if ledger is not None:
            conn.execute('INSERT INTO records VALUES(?,?,?,?)',('ledger_config',ledger.store_id,'__authority__',canonical({'store_id':ledger.store_id,'checkpoint_required':True,'format':1})))
            ledger.acquire(path)
            try:
                head,pending,_=ledger.history()
                assert head['sequence']==0 and pending is None
                ledger._head=head
                ledger.finish(ledger.prepare(conn))
            finally:ledger.close()
    finally:conn.close()


def fixture_authority(path, **kwargs):
    if not any(Path(p).exists() or Path(p).is_symlink() for p in kwargs.get('legacy_paths',())):
        seed_legacy_fixture(path,kwargs.get('ledger'))
    if 'enrollment_context' not in kwargs:
        from app.agent.recovery import OperatorPermits
        from app.agent.ledger import digest_state
        from app.agent.enrollment import EMPTY_HEAD
        from app.agent.authority import AuthorityError
        try:
            conn=sqlite3.connect(Path(path).absolute().as_uri()+'?mode=ro',uri=True)
            try:payload={'database':str(Path(path).absolute()),'logical_state':digest_state(conn),'execution_enabled':False}
            finally:conn.close()
            now=datetime.now(UTC);verifier=OperatorPermits(b'synthetic-legacy-fixture-approval-key-0000')
            checkpoint=EMPTY_HEAD;ledger=kwargs.get('ledger')
            if ledger is not None:
                owned=ledger._fd is not None
                try:
                    if not owned:ledger.acquire(path,readonly=True)
                    checkpoint=ledger.history()[0]
                finally:
                    if not owned:ledger.close()
            permit=verifier.issue(request_id=str(uuid.uuid4()),principal='synthetic-legacy-fixture',scope='local-service',
                command='open_legacy_authority',payload=payload,checkpoint=checkpoint,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
            kwargs['legacy_approval']=(verifier,permit)
        except (OSError,sqlite3.Error,AuthorityError):pass
    return RealAuthority(path,**kwargs)

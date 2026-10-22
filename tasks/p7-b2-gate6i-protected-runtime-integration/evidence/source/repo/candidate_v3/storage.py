from __future__ import annotations
import fcntl, hashlib, json, os, sqlite3, stat, threading, uuid
from contextlib import contextmanager
from pathlib import Path
from .contracts import Refused, Resource, canonical, digest, strict_json

SCHEMA = (
 'CREATE TABLE lineage(parent TEXT PRIMARY KEY, child TEXT UNIQUE NOT NULL, archive TEXT NOT NULL, ancestor_count INTEGER NOT NULL CHECK(ancestor_count>=0))',
 'CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)',
 'CREATE TABLE control(nonce TEXT PRIMARY KEY, verb TEXT NOT NULL, body_digest TEXT NOT NULL, operator TEXT NOT NULL)',
 'CREATE TABLE permits(nonce TEXT PRIMARY KEY REFERENCES control(nonce), ordinal INTEGER UNIQUE NOT NULL, transport TEXT NOT NULL, session TEXT NOT NULL, commitment TEXT NOT NULL, expires REAL NOT NULL, spent INTEGER NOT NULL CHECK(spent IN(0,1)))',
 "CREATE TABLE attempts(id TEXT PRIMARY KEY, ordinal INTEGER UNIQUE NOT NULL CHECK(ordinal BETWEEN 1 AND 4), transport TEXT NOT NULL CHECK(transport IN ('REST','WS')), session TEXT NOT NULL, permit TEXT UNIQUE NOT NULL REFERENCES permits(nonce), origin TEXT NOT NULL CHECK(origin='OFFLINE_FIXTURE'), eligible INTEGER NOT NULL CHECK(eligible=0), delivery TEXT NOT NULL, terminal TEXT)",
 'CREATE TABLE steps(id TEXT PRIMARY KEY, attempt TEXT NOT NULL REFERENCES attempts(id), kind TEXT NOT NULL, endpoint TEXT NOT NULL, model TEXT NOT NULL, profile TEXT NOT NULL, request_digest TEXT NOT NULL, state TEXT NOT NULL, UNIQUE(attempt,kind))',
 'CREATE TABLE leases(step TEXT PRIMARY KEY REFERENCES steps(id), endpoint TEXT NOT NULL, state TEXT NOT NULL)',
 'CREATE UNIQUE INDEX endpoint_exclusion ON leases(endpoint) WHERE state IN (\'ACTIVE\',\'REMOTE_UNKNOWN\')',
 'CREATE TABLE receipts(attempt TEXT PRIMARY KEY REFERENCES attempts(id), step TEXT UNIQUE NOT NULL REFERENCES steps(id), sequence INTEGER UNIQUE NOT NULL, digest TEXT NOT NULL)',
 'CREATE TABLE checkpoints(id TEXT PRIMARY KEY, accepted INTEGER NOT NULL, event_highwater INTEGER NOT NULL, manifest_digest TEXT NOT NULL)',
 'CREATE TABLE events(sequence INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL, attempt TEXT, step TEXT)',
 "CREATE TRIGGER accepted_immutable BEFORE UPDATE OF id,ordinal,transport,session,permit,origin,eligible ON attempts BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ACCEPTANCE'); END",
 "CREATE TRIGGER accepted_no_delete BEFORE DELETE ON attempts BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ACCEPTANCE'); END",
)

def no_symlink_ancestors(path: Path):
    # Static defense; protected ancestors/dirfd publication remain a release requirement.
    if not path.is_absolute() or ".." in path.parts: raise Refused('UNSAFE_STORAGE_PATH')
    for parent in reversed((path, *path.parents)):
        if parent.is_symlink(): raise Refused('SYMLINK_ANCESTOR')

def private(path: Path, directory=False, *, owner_uid=None):
    no_symlink_ancestors(path)
    s=path.lstat()
    if (s.st_uid != (os.geteuid() if owner_uid is None else owner_uid) or stat.S_IMODE(s.st_mode) != (0o700 if directory else 0o600)
            or not (stat.S_ISDIR(s.st_mode) if directory else stat.S_ISREG(s.st_mode)) or not directory and s.st_nlink != 1):
        raise Refused('UNSAFE_STORAGE')

def sync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)

def validate_accounting(db):
    """Reject coherent SQLite files whose pilot associations are not coherent."""
    terminal=db.execute("SELECT value FROM meta WHERE key='terminal'").fetchone()
    if terminal is None or terminal[0] not in ('','CLOSED_COMPLETE','CLOSED_INCOMPLETE'):raise Refused('TERMINAL_INTEGRITY')
    attempts=db.execute('SELECT id,ordinal,transport,session,permit,delivery,terminal FROM attempts ORDER BY ordinal').fetchall()
    if len(attempts)>4:raise Refused('GLOBAL_CAP')
    for ordinal,(aid,n,transport,session,permit,delivery,settled) in enumerate(attempts,1):
        if n!=ordinal or transport!=('REST','REST','WS','WS')[ordinal-1]:raise Refused('ORDINAL_INTEGRITY')
        row=db.execute('SELECT ordinal,transport,session,spent FROM permits WHERE nonce=?',(permit,)).fetchone()
        if row!=(n,transport,session,1):raise Refused('PERMIT_ACCEPTANCE_INTEGRITY')
        if delivery not in ('NOT_ATTEMPTED','INTERRUPTED_UNKNOWN','LOCAL_SEND_COMPLETED') or settled not in (None,'SETTLED'):raise Refused('ATTEMPT_INTEGRITY')
    if db.execute('SELECT 1 FROM permits p LEFT JOIN attempts a ON a.permit=p.nonce WHERE p.spent=1 AND a.id IS NULL').fetchone():raise Refused('SPENT_WITHOUT_ACCEPTANCE')
    if db.execute("SELECT 1 FROM steps WHERE kind NOT IN ('LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE') OR state NOT IN ('POSSIBLE_SEND','KNOWN_TERMINAL','REMOTE_UNKNOWN')").fetchone():raise Refused('SUBSTEP_INTEGRITY')
    for state,lease,endpoint,lease_endpoint in db.execute('SELECT s.state,l.state,s.endpoint,l.endpoint FROM steps s LEFT JOIN leases l ON l.step=s.id'):
        expected='ACTIVE' if state=='POSSIBLE_SEND' else state
        if lease!=expected or endpoint!=lease_endpoint:raise Refused('LEASE_INTEGRITY')

class Store:
    """Disposable candidate schema5. One lifetime writer; no migration/restore entry point."""
    def __init__(self, root: Path, *, predecessor=None, child=None, bindings=None, fault=lambda _:None):
        self.root=Path(root);self.fault=fault;self.lock=threading.RLock();self.db=None;self.lockfd=None
        if not self.root.is_absolute():raise Refused('ABSOLUTE_PRIVATE_ROOT_REQUIRED')
        # Refuse production namespaces even before the independent kernel sandbox.
        if str(self.root).startswith(('/home/jarvis/JARVIS','/home/jarvis/.hermes-poc','/home/jarvis/.config')):raise Refused('PRODUCTION_PATH_FORBIDDEN')
        private(self.root.parent,True)
        fresh=predecessor is not None
        if fresh:
            if (type(predecessor) is not dict or set(predecessor) != {'epoch','status','accepted','complete','unknown','retirement','archive'}
                    or predecessor['status']!='CLOSED_COMPLETE' or type(predecessor['accepted']) is not int or predecessor['accepted']!=0
                    or predecessor['complete'] is not True or predecessor['unknown'] is not False
                    or predecessor['retirement']!='EXPLICIT_ZERO_USE_RETIREMENT'
                    or not predecessor['archive'] or not predecessor['epoch'] or child==predecessor['epoch'] or not child):raise Refused('PREDECESSOR_REFUSED')
            # One authority file per deployment root, before any child DB exists.
            # A second directory cannot mint a second successor for this lineage.
            reservation=canonical({'parent':predecessor['epoch'],'child':child,'archive':predecessor['archive'],
                                   'namespace':self.root.name,'bindings':bindings})
            try:fd=os.open(self.root.parent/'lineage-reservation.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            except FileExistsError:raise Refused('SUCCESSOR_ALREADY_RESERVED') from None
            try:
                if os.write(fd,reservation)!=len(reservation):raise Refused('RESERVATION_PARTIAL_WRITE')
                os.fsync(fd)
            finally:os.close(fd)
            sync_dir(self.root.parent);self.fault('successor_reserved')
            self.root.mkdir(mode=0o700)  # Existing partial roots never reinitialize.
            sync_dir(self.root.parent)
        private(self.root,True)
        try:
            self.lockfd=os.open(self.root/'writer.lock',os.O_RDWR|os.O_NOFOLLOW|(os.O_CREAT|os.O_EXCL if fresh else 0),0o600)
            fcntl.flock(self.lockfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            private(self.root/'writer.lock')
            p=self.root/'controller.sqlite3'
            if fresh:
                fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_RDWR|os.O_NOFOLLOW,0o600);os.close(fd)
            private(p);self.inode=p.stat().st_ino
            self.db=sqlite3.connect(p,timeout=0,isolation_level=None,check_same_thread=False)
            self.db.execute('PRAGMA foreign_keys=ON');self.db.execute('PRAGMA synchronous=FULL');self.db.execute('PRAGMA journal_mode=DELETE')
            if fresh:
                with self.tx():
                    for sql in SCHEMA:self.db.execute(sql)
                    self.db.execute('PRAGMA user_version=5')
                    self.db.execute('INSERT INTO lineage VALUES(?,?,?,0)',(predecessor['epoch'],child,predecessor['archive']))
                    self.db.executemany('INSERT INTO meta VALUES(?,?)',[('bindings',json.dumps(bindings,sort_keys=True)),('terminal',''),('lineage_hash',digest(reservation))])
                    self.fault('initialize_before_commit')
                sync_dir(self.root)
                self.fault('initialize_after_commit')
            self.validate()
        except BaseException:
            self.close();raise

    def validate(self):
        private(self.root,True);private(self.root/'controller.sqlite3')
        private(self.root.parent/'lineage-reservation.json')
        if (self.root/'controller.sqlite3').stat().st_ino != self.inode:raise Refused('DATABASE_REPLACED')
        if self.db.execute('PRAGMA user_version').fetchone()[0]!=5 or self.db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise Refused('SCHEMA_INTEGRITY')
        expected=set(SCHEMA);actual={r[0] for r in self.db.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name!='sqlite_sequence'")}
        if actual!=expected or self.db.execute('PRAGMA foreign_key_check').fetchall():raise Refused('SCHEMA_INTEGRITY')
        if self.db.execute('SELECT count(*) FROM lineage').fetchone()[0]!=1:raise Refused('LINEAGE_INTEGRITY')
        validate_accounting(self.db)
        raw=(self.root.parent/'lineage-reservation.json').read_bytes()
        try:r=strict_json(raw)
        except ValueError:raise Refused('LINEAGE_MANIFEST') from None
        if (set(r)!={'parent','child','archive','namespace','bindings'} or r['namespace']!=self.root.name
                or (r['parent'],r['child'],r['archive'],0)!=self.db.execute('SELECT * FROM lineage').fetchone()
                or r['bindings']!=strict_json(self.db.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()[0])
                or self.db.execute("SELECT value FROM meta WHERE key='lineage_hash'").fetchone()!=(digest(raw),)):raise Refused('LINEAGE_MANIFEST')

    @contextmanager
    def tx(self):
        with self.lock:
            if self.db.in_transaction:raise Refused('NESTED_TRANSACTION')
            self.db.execute('BEGIN IMMEDIATE')
            try:yield;self.db.execute('COMMIT')
            except BaseException:
                if self.db.in_transaction:self.db.execute('ROLLBACK')
                raise

    def event(self,code,attempt=None,step=None):
        self.db.execute('INSERT INTO events(code,attempt,step) VALUES(?,?,?)',(code,attempt,step))
    def count(self):return self.db.execute('SELECT count(*) FROM attempts').fetchone()[0]+self.db.execute('SELECT ancestor_count FROM lineage').fetchone()[0]
    def terminal(self):return self.db.execute("SELECT value FROM meta WHERE key='terminal'").fetchone()[0]
    def clean(self):return not self.db.execute("SELECT 1 FROM leases WHERE state IN ('ACTIVE','REMOTE_UNKNOWN')").fetchone()
    def ready(self):
        return self.db.execute('SELECT 1 FROM checkpoints WHERE accepted=? ORDER BY rowid DESC LIMIT 1',(self.count(),)).fetchone() is not None and not self.db.execute('SELECT 1 FROM attempts WHERE terminal IS NULL').fetchone()
    def control(self,a):
        try:self.db.execute('INSERT INTO control VALUES(?,?,?,?)',(a['nonce'],a['verb'],a['_signed_digest'],a['_verified_operator']))
        except sqlite3.IntegrityError:raise Refused('CONTROL_REPLAY') from None
        self.event(a['verb'])
    def opening(self,a):
        with self.tx():
            self.validate()
            if self.count() or self.terminal() or not self.clean() or not self.ready() or self.db.execute("SELECT 1 FROM control WHERE verb='OPEN_HOLD'").fetchone():raise Refused('OPEN_PREREQUISITE')
            self.control(a);self.fault('open_before_commit')
        self.fault('open_after_commit')
    def arm(self,a):
        with self.tx():
            n=self.count();p=a['payload']
            if self.terminal() or not self.clean() or not self.ready() or n>=4 or p['transport']!=('REST','REST','WS','WS')[n]:raise Refused('PERMIT_PREREQUISITE')
            if self.db.execute('SELECT 1 FROM permits WHERE spent=0').fetchone():raise Refused('OUTSTANDING_PERMIT')
            self.control(a)
            self.db.execute('INSERT INTO permits VALUES(?,?,?,?,?,?,0)',(a['nonce'],n+1,p['transport'],p['session'],p['request_commitment'],a['expires']))
    def accept(self,transport,session,commitment,*,now):
        with self.tx():
            self.validate()
            p=self.db.execute('SELECT nonce,ordinal,transport,session,commitment,expires FROM permits WHERE spent=0').fetchone()
            if self.terminal() or not self.clean() or self.count()>=4 or p is None or p[1:5]!=(self.count()+1,transport,session,commitment) or not now<p[5]:raise Refused('ADMISSION_REFUSED')
            aid=uuid.uuid4().hex
            self.db.execute('UPDATE permits SET spent=1 WHERE nonce=?',(p[0],));self.fault('permit_spent_before_insert')
            self.db.execute("INSERT INTO attempts VALUES(?,?,?,?,?,'OFFLINE_FIXTURE',0,'NOT_ATTEMPTED',NULL)",(aid,p[1],transport,session,p[0]))
            self.event('ACCEPTED',aid);self.fault('accept_before_commit')
        self.fault('accept_after_commit');return aid
    def begin(self,attempt,kind,resource,request_digest):
        with self.tx():
            if self.terminal() or not self.clean():raise Refused('OWNERSHIP_UNAVAILABLE')
            row=self.db.execute('SELECT terminal,delivery FROM attempts WHERE id=?',(attempt,)).fetchone()
            if kind not in ('LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE') or row is None or row[0] is not None:raise Refused('SUBSTEP_SCOPE')
            kinds={v[0] for v in self.db.execute('SELECT kind FROM steps WHERE attempt=?',(attempt,))}
            if (kind=='LEGACY_ROUTER' and kinds or kind=='LEGACY_RESPONDER' and not kinds<= {'LEGACY_ROUTER'}
                    or kind=='GRANITE' and ('LEGACY_RESPONDER' not in kinds or row[1]!='LOCAL_SEND_COMPLETED')):raise Refused('SUBSTEP_ORDER')
            sid=uuid.uuid4().hex
            self.db.execute('INSERT INTO steps VALUES(?,?,?,?,?,?,?,?)',(sid,attempt,kind,resource.endpoint,resource.model,resource.profile,request_digest,'POSSIBLE_SEND'))
            self.db.execute("INSERT INTO leases VALUES(?,?,'ACTIVE')",(sid,resource.endpoint));self.event('POSSIBLE_SEND',attempt,sid)
        self.fault('possible_send_committed');return sid
    def known_terminal(self,sid):
        with self.tx():
            if self.db.execute('SELECT state FROM steps WHERE id=?',(sid,)).fetchone()!=('POSSIBLE_SEND',):raise Refused('TERMINAL_ASSOCIATION')
            self.db.execute("UPDATE steps SET state='KNOWN_TERMINAL' WHERE id=?",(sid,));self.db.execute("UPDATE leases SET state='KNOWN_TERMINAL' WHERE step=?",(sid,));self.event('KNOWN_TERMINAL',step=sid)
            self.event('KNOWN_TRANSMITTED',step=sid)
        self.fault('provider_terminal_committed')
    def unknown(self,sid):
        with self.tx():
            if self.db.execute('SELECT state FROM steps WHERE id=?',(sid,)).fetchone()!=('POSSIBLE_SEND',):return
            self.db.execute("UPDATE steps SET state='REMOTE_UNKNOWN' WHERE id=? AND state='POSSIBLE_SEND'",(sid,));self.db.execute("UPDATE leases SET state='REMOTE_UNKNOWN' WHERE step=? AND state='ACTIVE'",(sid,));self.event('REMOTE_UNKNOWN',step=sid)
    def delivery(self,aid,status):
        with self.tx():
            if status not in ('LOCAL_SEND_COMPLETED','INTERRUPTED_UNKNOWN'):raise Refused('DELIVERY_STATUS')
            prior=self.db.execute('SELECT delivery FROM attempts WHERE id=?',(aid,)).fetchone()
            if prior is None:raise Refused('DELIVERY_ASSOCIATION')
            if prior[0]=='LOCAL_SEND_COMPLETED' or prior[0]==status:return
            self.db.execute('UPDATE attempts SET delivery=? WHERE id=?',(status,aid));self.event(status,aid)
    def receipt(self,aid,sid,native_digest,observation):
        with self.lock:
            return self._receipt(aid,sid,native_digest,observation)

    def _receipt(self,aid,sid,native_digest,observation):
        """Candidate minimized D04 sink; exact join, no raw output. Not production D04 adapter."""
        if self.db.execute('SELECT attempt,kind,state FROM steps WHERE id=?',(sid,)).fetchone()!=(aid,'GRANITE','KNOWN_TERMINAL'):raise Refused('RECEIPT_ASSOCIATION')
        path=self.root/'receipts.jsonl'
        seq=self.db.execute('SELECT count(*) FROM receipts').fetchone()[0]+1
        from .observation import Observation
        if type(observation) is not Observation or observation.projection.get('proposal_count')!=0:raise Refused('OBSERVATION_REQUIRED')
        from dataclasses import asdict
        record=canonical({'attempt':aid,'step':sid,'sequence':seq,'native_digest':native_digest,'proposal_count':0,'origin':'OFFLINE_FIXTURE','eligible':False,'observation':asdict(observation)})+b'\n'
        flags=os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW
        if not path.exists():flags|=os.O_CREAT|os.O_EXCL
        fd=os.open(path,flags,0o600)
        try:
            private(path)
            # No retry after an uncertain/partial append.
            if os.write(fd,record)!=len(record):raise Refused('D04_PARTIAL_APPEND')
            os.fsync(fd)
        finally:os.close(fd)
        sync_dir(self.root);self.fault('receipt_append_before_join')
        with self.tx():
            self.db.execute('INSERT INTO receipts VALUES(?,?,?,?)',(aid,sid,seq,digest(record)));self.event('D04_JOINED',aid,sid)
        self.fault('receipt_joined')
    def settle(self,aid):
        with self.tx():
            if not self.clean() or self.terminal() or not self.db.execute('SELECT 1 FROM receipts WHERE attempt=?',(aid,)).fetchone():raise Refused('SETTLEMENT_REFUSED')
            self.db.execute("UPDATE attempts SET terminal='SETTLED' WHERE id=? AND delivery='LOCAL_SEND_COMPLETED'",(aid,))
            if self.db.execute('SELECT terminal FROM attempts WHERE id=?',(aid,)).fetchone()!=('SETTLED',):raise Refused('DELIVERY_UNPROVEN')
            self.event('SETTLED',aid)
    def stop(self,reason='STOP',approval=None):
        if reason=='SIGNED_TERMINAL_STOP' and (approval is None or approval.get('verb')!='TERMINAL_STOP'):raise Refused('SIGNED_STOP_AUTHORITY')
        if reason=='OPERATOR_STOP':reason='UNATTRIBUTED_STOP'
        with self.tx():
            if approval is not None:self.control(approval)
            if reason=='FINAL_CHECKPOINT_FAILED' and self.terminal()=='CLOSED_COMPLETE':
                self.db.execute("UPDATE meta SET value='CLOSED_INCOMPLETE' WHERE key='terminal'");self.event(reason)
            if not self.terminal():
                complete=reason in ('UNATTRIBUTED_STOP','SIGNED_TERMINAL_STOP','LIFESPAN_SHUTDOWN','SIGUSR1_CONTROL','CAP_COMPLETE') and self.clean() and self.ready()
                self.db.execute("UPDATE meta SET value=? WHERE key='terminal'",('CLOSED_COMPLETE' if complete else 'CLOSED_INCOMPLETE',));self.event(reason)
            self.fault('stop_before_commit')
        self.fault('stop_after_commit')
    def close(self):
        if self.db is not None:self.db.close();self.db=None
        if self.lockfd is not None:os.close(self.lockfd);self.lockfd=None

def checkpoint(store: Store, parent: Path, *, forensic=False):
    """Exclusive manifest-last snapshot; never replace/prune/restore an existing bundle."""
    private(parent,True)
    with store.lock:
        if not forensic and (not store.clean() or store.db.execute('SELECT 1 FROM attempts WHERE terminal IS NULL').fetchone()):raise Refused('CHECKPOINT_NOT_QUIESCENT')
        store.validate();bid=uuid.uuid4().hex;root=parent/bid;root.mkdir(mode=0o700);sync_dir(parent)
        dbpath=root/'controller.sqlite3';copy=sqlite3.connect(dbpath)
        try:store.db.backup(copy)
        finally:copy.close()
        dbpath.chmod(0o600)
        fd=os.open(dbpath,os.O_RDONLY|os.O_NOFOLLOW)
        try:os.fsync(fd)
        finally:os.close(fd)
        store.fault('backup_database_synced')
        receipt_path=store.root/'receipts.jsonl'
        if receipt_path.exists() or receipt_path.is_symlink():private(receipt_path)
        raw=receipt_path.read_bytes() if receipt_path.exists() else b''
        fd=os.open(root/'receipts.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            if os.write(fd,raw)!=len(raw):raise Refused('BACKUP_SHORT_WRITE')
            os.fsync(fd)
        finally:os.close(fd)
        lineage=(store.root.parent/'lineage-reservation.json').read_bytes()
        fd=os.open(root/'lineage-reservation.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            if os.write(fd,lineage)!=len(lineage):raise Refused('BACKUP_SHORT_WRITE')
            os.fsync(fd)
        finally:os.close(fd)
        manifest={'version':3,'purpose':'FORENSIC_INCOMPLETE' if forensic else 'READY','id':bid,'accepted':store.count(),'event_highwater':store.db.execute('SELECT coalesce(max(sequence),0) FROM events').fetchone()[0],'lineage':store.db.execute('SELECT * FROM lineage').fetchall(),'bindings':strict_json(store.db.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()[0]),'files':{n:digest((root/n).read_bytes()) for n in ('controller.sqlite3','receipts.jsonl','lineage-reservation.json')}}
        store.fault('backup_before_manifest')
        body=canonical(manifest);fd=os.open(root/'manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            if os.write(fd,body)!=len(body):raise Refused('BACKUP_SHORT_WRITE')
            os.fsync(fd)
        finally:os.close(fd)
        sync_dir(root);verify_checkpoint(root)
        if not forensic:
            with store.tx():store.db.execute('INSERT INTO checkpoints VALUES(?,?,?,?)',(bid,manifest['accepted'],manifest['event_highwater'],digest(body)))
        return root

def verify_checkpoint(root: Path, *, current_highwater=None):
    private(root,True)
    for n in ('manifest.json','controller.sqlite3','receipts.jsonl','lineage-reservation.json'):private(root/n)
    if set(p.name for p in root.iterdir())!={'manifest.json','controller.sqlite3','receipts.jsonl','lineage-reservation.json'}:raise Refused('BACKUP_MEMBERS')
    try:m=strict_json((root/'manifest.json').read_bytes())
    except (ValueError,UnicodeError):raise Refused('BACKUP_MANIFEST') from None
    if set(m)!={'version','purpose','id','accepted','event_highwater','lineage','bindings','files'} or m['version']!=3 or m['purpose'] not in ('READY','FORENSIC_INCOMPLETE') or m['id']!=root.name or set(m['files'])!={'controller.sqlite3','receipts.jsonl','lineage-reservation.json'}:raise Refused('BACKUP_MANIFEST')
    if any(digest((root/n).read_bytes())!=h for n,h in m['files'].items()):raise Refused('BACKUP_CHECKSUM')
    if current_highwater is not None and current_highwater>m['event_highwater']:raise Refused('NEWER_EVIDENCE_RESTORE_REFUSED')
    db=sqlite3.connect((root/'controller.sqlite3').as_uri()+'?mode=ro',uri=True)
    try:
        db.execute('PRAGMA query_only=ON')
        if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)] or db.execute('PRAGMA foreign_key_check').fetchall():raise Refused('BACKUP_DATABASE')
        if db.execute('PRAGMA user_version').fetchone()[0]!=5:raise Refused('BACKUP_SCHEMA')
        validate_accounting(db)
        if {x[0] for x in db.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name!='sqlite_sequence'")}!=set(SCHEMA):raise Refused('BACKUP_SCHEMA')
        if [list(x) for x in db.execute('SELECT * FROM lineage')]!=m['lineage']:raise Refused('BACKUP_LINEAGE')
        if strict_json(db.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()[0])!=m['bindings']:raise Refused('BACKUP_BINDINGS')
        lr=(root/'lineage-reservation.json').read_bytes();reservation=strict_json(lr)
        if db.execute("SELECT value FROM meta WHERE key='lineage_hash'").fetchone()!=(digest(lr),) or [reservation['parent'],reservation['child'],reservation['archive'],0]!=m['lineage'][0] or reservation['bindings']!=m['bindings']:raise Refused('BACKUP_LINEAGE_HASH')
        if db.execute('SELECT count(*) FROM attempts').fetchone()[0]+db.execute('SELECT ancestor_count FROM lineage').fetchone()[0]!=m['accepted']:raise Refused('BACKUP_ACCEPTED_SET')
        if db.execute('SELECT coalesce(max(sequence),0) FROM events').fetchone()[0]!=m['event_highwater']:raise Refused('BACKUP_EVENT_HIGHWATER')
        if m['purpose']=='READY':
            if db.execute("SELECT 1 FROM leases WHERE state IN ('ACTIVE','REMOTE_UNKNOWN')").fetchone():raise Refused('BACKUP_UNKNOWN')
            if db.execute("SELECT 1 FROM attempts WHERE terminal IS NULL OR terminal!='SETTLED' OR delivery!='LOCAL_SEND_COMPLETED'").fetchone():raise Refused('BACKUP_UNSETTLED')
            if db.execute("SELECT 1 FROM steps WHERE state!='KNOWN_TERMINAL'").fetchone():raise Refused('BACKUP_SUBSTEP_UNSETTLED')
            if db.execute('SELECT count(*) FROM receipts').fetchone()[0]!=m['accepted']:raise Refused('BACKUP_MISSING_RECEIPT')
        lines=(root/'receipts.jsonl').read_bytes().splitlines(keepends=True);joins=db.execute('SELECT attempt,step,sequence,digest FROM receipts ORDER BY sequence').fetchall()
        if len(lines)<len(joins) or len(lines)!=len(joins) and m['purpose']=='READY':raise Refused('BACKUP_RECEIPT_COUNT')
        for i,(line,join) in enumerate(zip(lines,joins),1):
            v=strict_json(line)
            if join!=(v['attempt'],v['step'],i,digest(line)) or v['sequence']!=i or v['proposal_count']!=0 or v['eligible'] is not False or v['origin']!='OFFLINE_FIXTURE':raise Refused('BACKUP_RECEIPT_JOIN')
            if db.execute('SELECT attempt,kind,state FROM steps WHERE id=?',(v['step'],)).fetchone()!=(v['attempt'],'GRANITE','KNOWN_TERMINAL'):raise Refused('BACKUP_STEP_JOIN')
    finally:db.close()
    return m


def read_snapshot_db(path,*,owner_uid,expected_digest=None):
    """Bounded O_NOFOLLOW read into query-only memory; helper never follows SQLite
    paths or journal names in a service-writable directory. Torn snapshots refuse.
    """
    path=Path(path);no_symlink_ancestors(path)
    fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=owner_uid or stat.S_IMODE(st.st_mode)!=0o600 or st.st_nlink!=1 or not 0<st.st_size<=8*1024*1024:raise Refused('SNAPSHOT_FILE_BOUNDARY')
        raw=b''
        while len(raw)<st.st_size:
            block=os.read(fd,min(65536,st.st_size-len(raw)))
            if not block:raise Refused('SNAPSHOT_TRUNCATED')
            raw+=block
        end=os.fstat(fd)
        fields=('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns','st_mode','st_uid','st_nlink')
        if os.read(fd,1) or any(getattr(end,k)!=getattr(st,k) for k in fields):raise Refused('SNAPSHOT_CHANGED')
    finally:os.close(fd)
    if expected_digest is not None and digest(raw)!=expected_digest:raise Refused('SNAPSHOT_DIGEST')
    db=sqlite3.connect(':memory:')
    try:
        db.deserialize(raw);db.execute('PRAGMA query_only=ON')
        db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH,2*1024*1024)
        if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise Refused('SNAPSHOT_INTEGRITY')
        return db
    except BaseException:db.close();raise

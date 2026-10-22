"""Versioned coordinated local checkpoint, atomic directory publication.
No automatic restore; occupied destinations and stale protected high-water refuse.
"""
import os,sqlite3,uuid,shutil
from pathlib import Path
from .contracts import Refused,canonical,digest,strict_json
from .storage import private,sync_dir,checkpoint,verify_checkpoint,no_symlink_ancestors

class CheckpointWriter:
    def __init__(self,root,*,evidence,domains,highwater,ownership,fault=lambda _:None):
        self.root=Path(root);private(self.root,True)
        self.evidence,self.domains,self.highwater,self.ownership=evidence,domains,highwater,tuple(ownership)
        self.fault=fault;self.last=None
    def __call__(self,store,backups,*,final=False):
        forensic=False
        try:
            self.evidence.validate()
            if self.domains.db.execute('SELECT 1 FROM holds').fetchone():raise Refused('CHECKPOINT_D06_UNKNOWN')
            self.highwater.check(store,allow_terminal=final)
            if not store.clean() or store.db.execute('SELECT 1 FROM attempts WHERE terminal IS NULL').fetchone():raise Refused('CHECKPOINT_UNSETTLED')
        except Refused:
            if not final:raise
            forensic=True
        # Store lock coordinates the sole writer and all consumer callbacks.
        with store.lock:
            local=checkpoint(store,backups,forensic=forensic)
            tag=uuid.uuid4().hex;staging=self.root/('.pending-'+tag);staging.mkdir(mode=0o700);sync_dir(self.root)
            protected=hasattr(self.highwater,'export_db')
            exported,anchor=self.highwater.export_db() if protected else (self.highwater.db,None)
            dbs={'d04-d09.sqlite3':self.evidence.db,'domains.sqlite3':self.domains.db,'highwater.sqlite3':exported,'controller.sqlite3':store.db}
            for name,db in dbs.items():
                path=staging/name;fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_RDWR,0o600);os.close(fd)
                target=sqlite3.connect(path)
                try:db.backup(target)
                finally:target.close()
                fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
                try:os.fsync(fd)
                finally:os.close(fd)
                self.fault('checkpoint_component_synced')
            if protected:exported.close()
            raw={}
            if protected:raw['authority-token.json']=canonical(anchor)
            for i,b in enumerate(self.ownership):
                if not forensic and b.coordinator.snapshot().state is not None:raise Refused('CHECKPOINT_OWNER_UNKNOWN')
                for n in ('scope.json','state.json','ownership.managed'):
                    p=b.coordinator.marker if n=='ownership.managed' else b.coordinator.root/n;private(p);raw[f'd06-{i}-{n}']=p.read_bytes()
            for prefix,p in [('d04',self.evidence.root/'observations.jsonl'),('receipts',store.root/'receipts.jsonl')]:
                if p.exists():private(p);raw[prefix+'.jsonl']=p.read_bytes()
            raw['lineage.json']=(store.root.parent/'lineage-reservation.json').read_bytes()
            for name,body in raw.items():
                fd=os.open(staging/name,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o600)
                try:
                    if os.write(fd,body)!=len(body):raise Refused('CHECKPOINT_SHORT_WRITE')
                    os.fsync(fd)
                finally:os.close(fd)
            manifest={'version':2,'id':tag,'purpose':'FORENSIC_INCOMPLETE' if forensic else 'READY','terminal':store.terminal(),'controller_checkpoint':digest((local/'manifest.json').read_bytes()),'accepted':store.count(),
                'bindings':store.db.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()[0],
                'files':{p.name:digest(p.read_bytes()) for p in staging.iterdir()}}
            body=canonical(manifest);fd=os.open(staging/'manifest.json',os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o600)
            try:
                if os.write(fd,body)!=len(body):raise Refused('CHECKPOINT_SHORT_WRITE')
                os.fsync(fd)
            finally:os.close(fd)
            sync_dir(staging);self.fault('checkpoint_before_publish')
            destination=self.root/tag
            if destination.exists() or destination.is_symlink():raise Refused('CHECKPOINT_OCCUPIED')
            os.rename(staging,destination);sync_dir(self.root);self.fault('checkpoint_after_publish')
            validate_coordinated(destination,minimum_accepted=store.count());self.last=destination
            if protected and not final:self.highwater.checkpoint_committed(destination)
            return local

def validate_coordinated(root,*,minimum_accepted,owner_uid=None):
    if owner_uid is not None:
        from .storage import private as check_private
        def private(p,directory=False):return check_private(p,directory,owner_uid=owner_uid)
    else:
        from .storage import private
    root=Path(root);private(root,True);private(root/'manifest.json');m=strict_json((root/'manifest.json').read_bytes())
    if (type(m) is not dict or set(m)!={'version','id','purpose','terminal','controller_checkpoint','accepted','bindings','files'} or m['version']!=2
        or m['purpose'] not in ('READY','FORENSIC_INCOMPLETE') or m['terminal'] not in ('','CLOSED_COMPLETE','CLOSED_INCOMPLETE')
        or m['id']!=root.name or type(m['accepted']) is not int or not minimum_accepted<=m['accepted']<=4
        or type(m['files']) is not dict or set(m['files'])!={p.name for p in root.iterdir() if p.name!='manifest.json'}):raise Refused('COORDINATED_MANIFEST')
    for n,h in m['files'].items():
        if Path(n).name!=n:raise Refused('COORDINATED_PATH')
        private(root/n)
        if digest((root/n).read_bytes())!=h:raise Refused('COORDINATED_CHECKSUM')
    required={'controller.sqlite3','highwater.sqlite3','domains.sqlite3','d04-d09.sqlite3','lineage.json'}
    if not required<=set(m['files']):raise Refused('COORDINATED_COMPONENTS')
    dbs={}
    try:
        for n in required-{'lineage.json'}:
            from .storage import read_snapshot_db
            dbs[n]=read_snapshot_db(root/n,owner_uid=os.geteuid() if owner_uid is None else owner_uid,expected_digest=m['files'][n])
            dbs[n].execute('PRAGMA query_only=ON')
            if dbs[n].execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise Refused('COORDINATED_DATABASE')
        c=dbs['controller.sqlite3'];h=dbs['highwater.sqlite3']
        from .lineage import HIGHWATER_SCHEMA, validate_succession
        if (h.execute('PRAGMA user_version').fetchone()!=(2,)
            or {r[0] for r in h.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL")}!=set(HIGHWATER_SCHEMA)):
            raise Refused('COORDINATED_HIGHWATER_SCHEMA')
        payload=validate_succession(h,strict_json(m['bindings']))
        from .storage import validate_accounting,SCHEMA
        validate_accounting(c)
        if {x[0] for x in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name!='sqlite_sequence'")}!=set(SCHEMA):raise Refused('COORDINATED_CONTROLLER_SCHEMA')
        lineage=strict_json((root/'lineage.json').read_bytes())
        if c.execute("SELECT value FROM meta WHERE key='lineage_hash'").fetchone()!=(digest((root/'lineage.json').read_bytes()),):raise Refused('COORDINATED_LINEAGE_HASH')
        if h.execute('SELECT predecessor,successor,archive FROM root').fetchall()!=[(lineage['parent'],lineage['child'],lineage['archive'])]:raise Refused('COORDINATED_LINEAGE_ROOT')
        if (payload['predecessor'],payload['archive'])!=(lineage['parent'],lineage['archive']):raise Refused('COORDINATED_SUCCESSION')
        if c.execute('SELECT parent,child,archive FROM lineage').fetchall()!=[(lineage['parent'],lineage['child'],lineage['archive'])]:raise Refused('COORDINATED_LINEAGE_CONTROLLER')
        from app.brain.model_ownership import ModelOwnershipCoordinatorV1,qualify_endpoint
        scope_names=sorted(n for n in m['files'] if n.startswith('d06-') and n.endswith('-scope.json'))
        if not scope_names:raise Refused('COORDINATED_MISSING_OWNERSHIP')
        for name in scope_names:
            prefix=name[:-len('scope.json')]
            scope=strict_json((root/name).read_bytes());state=strict_json((root/(prefix+'state.json')).read_bytes());marker=strict_json((root/(prefix+'ownership.managed')).read_bytes())
            if type(scope) is not dict or set(scope)!={'version','resource','legacy_endpoints'} or type(scope['version']) is not int or scope['version']!=1:raise Refused('COORDINATED_D06_SCOPE')
            key=ModelOwnershipCoordinatorV1._decode_key(scope['resource'])
            if (type(scope['legacy_endpoints']) is not list or not scope['legacy_endpoints'] or key.endpoint in scope['legacy_endpoints']
                or any(qualify_endpoint(x)!=x for x in scope['legacy_endpoints'])):raise Refused('COORDINATED_D06_SCOPE')
            if marker!={'version':1,'resource':scope['resource'],'scope_digest':digest(canonical(scope))}:raise Refused('COORDINATED_D06_MARKER')
            reader=ModelOwnershipCoordinatorV1(root)
            reader._read=lambda directory,name,state=state:state
            reader._scope=lambda directory,key=key:key
            try:reader._state(None)
            except Exception:raise Refused('COORDINATED_D06_STATE') from None
            if m['purpose']=='READY' and state['current'] is not None:raise Refused('COORDINATED_D06_UNKNOWN')
        if m['purpose']=='READY':
            steps=c.execute('SELECT id,state FROM steps ORDER BY id').fetchall()
            operations=dbs['domains.sqlite3'].execute('SELECT operation,state FROM operations ORDER BY operation').fetchall()
            if steps!=operations or any(state!='KNOWN_TERMINAL' for _,state in steps):raise Refused('COORDINATED_OPERATION_JOIN')
        actual=c.execute('SELECT ordinal,transport,session,permit,id FROM attempts ORDER BY ordinal').fetchall()
        protected=h.execute('SELECT ordinal,transport,session,permit,attempt FROM accepted ORDER BY ordinal').fetchall()
        if actual!=protected and (m['purpose']=='READY' or protected[:len(actual)]!=actual or any(row[4] is not None for row in protected[len(actual):])):raise Refused('COORDINATED_ACCEPTED_SET')
        for ordinal,transport,session,permit,aid in actual:
            commitment=h.execute('SELECT commitment FROM accepted WHERE ordinal=?',(ordinal,)).fetchone()[0]
            if c.execute('SELECT ordinal,transport,session,commitment,spent FROM permits WHERE nonce=?',(permit,)).fetchone()!=(ordinal,transport,session,commitment,1):raise Refused('COORDINATED_COMMITMENT')
        if c.execute('SELECT count(*) FROM attempts').fetchone()[0]!=m['accepted']:raise Refused('COORDINATED_COUNT')
        if m['purpose']=='READY' and dbs['domains.sqlite3'].execute('SELECT 1 FROM holds').fetchone():raise Refused('COORDINATED_UNKNOWN')
        if c.execute("SELECT value FROM meta WHERE key='terminal'").fetchone()!=(m['terminal'],):raise Refused('COORDINATED_TERMINAL')
        if h.execute('SELECT bindings,terminal FROM root').fetchall()!=[(canonical(strict_json(m['bindings'])).decode(),m['terminal'])]:raise Refused('COORDINATED_ROOT')
        from app.execution.shadow_observation_sink import _decode_entry
        evidence=dbs['d04-d09.sqlite3'];entries={};previous=0
        if 'd04.jsonl' in m['files']:
            for line in (root/'d04.jsonl').read_bytes().splitlines(keepends=True):
                if not line.endswith(b'\n'):raise Refused('COORDINATED_D04_PARTIAL')
                previous=_decode_entry(line[:-1],previous);entries[previous]=strict_json(line)
        joined=set()
        for aid,step,session,turn,state,seq,sha in evidence.execute('SELECT * FROM submissions'):
            if state!='JOINED':
                if m['purpose']=='READY':raise Refused('COORDINATED_D04_UNKNOWN')
                continue
            v=entries.get(seq)
            if v is None or v['entry_sha256']!=sha or v['observation']['correlation']!={'session_id':session,'turn_id':turn}:raise Refused('COORDINATED_D04_JOIN')
            if c.execute('SELECT attempt,kind,state FROM steps WHERE id=?',(step,)).fetchone()!=(aid,'GRANITE','KNOWN_TERMINAL'):raise Refused('COORDINATED_D04_OWNER')
            joined.add(seq)
        if m['purpose']=='READY' and (joined!=set(entries) or len(joined)!=m['accepted']):raise Refused('COORDINATED_D04_COUNT')
        if c.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()!=(m['bindings'],):raise Refused('COORDINATED_BINDINGS')
    finally:
        for db in dbs.values():db.close()
    return m

def restore_for_review(bundle,destination,*,minimum_accepted):
    """Offline export only, never a runtime startup or protected-root rollback."""
    validate_coordinated(bundle,minimum_accepted=minimum_accepted);destination=Path(destination)
    private(destination.parent,True);no_symlink_ancestors(destination)
    destination.mkdir(mode=0o700) # exclusive, existing newer evidence never overwritten
    for p in Path(bundle).iterdir():
        fd=os.open(destination/p.name,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        try:
            body=p.read_bytes()
            if os.write(fd,body)!=len(body):raise Refused('RESTORE_SHORT_WRITE')
            os.fsync(fd)
        finally:os.close(fd)
    sync_dir(destination);sync_dir(destination.parent)

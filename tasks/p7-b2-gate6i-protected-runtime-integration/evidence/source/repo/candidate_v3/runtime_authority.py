"""Protected runtime transactions and fixed-path readers. No signer or transport.

Only RuntimeJournal owns the protected database. Exports are disposable projections,
never an independent counter or a restore/authorization source.
"""
import os
import sqlite3
from pathlib import Path
from .contracts import Refused, canonical, digest, strict_json
from .authority import SUCCESSOR_VERB
from .protected_authority import ProtectedJournal
from .lineage import successor_payload, HIGHWATER_SCHEMA


def token(state):
    return {'seq': state['seq'], 'seal': state['seal']}


def accepted_rows(db):
    return [dict(ordinal=n, transport=t, session=s, commitment=c, permit=p)
            for n,t,s,c,p in db.execute('SELECT a.ordinal,a.transport,a.session,p.commitment,a.permit FROM attempts a JOIN permits p ON p.nonce=a.permit ORDER BY a.ordinal')]


def projection(state):
    """Read-only derived compatibility snapshot; never used for authorization."""
    db = sqlite3.connect(':memory:')
    for sql in HIGHWATER_SCHEMA: db.execute(sql)
    db.execute('PRAGMA user_version=2')
    p=state['root']; a=state['succession']
    db.execute('INSERT INTO root VALUES(1,?,?,?,?,?)', (p['predecessor'],p['archive'],p['bindings']['epoch'],canonical(p['bindings']).decode(),state['terminal_status']))
    db.execute('INSERT INTO succession VALUES(?,?,?,?)',(a['nonce'],a['_signed_digest'],a['_verified_operator'],canonical(p).decode()))
    for r in state['accepted']:
        db.execute('INSERT INTO accepted VALUES(?,?,?,?,?,?)',(r['ordinal'],r['transport'],r['session'],r['commitment'],r['permit'],state['links'].get(str(r['ordinal']))))
    db.commit(); db.execute('PRAGMA query_only=ON')
    return db


class RuntimeJournal(ProtectedJournal):
    """Gate6I protocol: signed approval and durable service consumption are separate."""
    def _state(self):
        events,seal=self._validate()
        s=dict(seq=len(events),seal=seal,root=None,succession=None,accepted=[],checkpoint=None,
               terminal=False,terminal_status='',sends=[],pending=None,commands={},claims=[],links={},opened=False,stop_requested=False)
        for kind,d in events:
            if kind=='RUNTIME_SUCCESSOR':
                if s['root'] is not None: raise Refused('AUTHORITY_HISTORY')
                s['root']=d['payload']; s['succession']=d
            elif kind=='APPROVE':
                if s['root'] is None or s['terminal'] or d['nonce'] in s['commands']: raise Refused('AUTHORITY_HISTORY')
                s['commands'][d['nonce']]=d
                if d['verb']=='OPEN_HOLD': s['opened']=True
                if d['verb']=='TERMINAL_STOP': s['stop_requested']=True
            elif kind=='CLAIM':
                if d not in s['commands'] or d in s['claims']:raise Refused('AUTHORITY_HISTORY')
                s['claims'].append(d)
            elif kind=='ACCEPT':
                n=len(s['accepted'])+1; a=s['commands'].get(d['permit'])
                if (s['terminal'] or not a or a['verb']!='AUTHORIZE_ONE' or n>4 or d['ordinal']!=n
                    or d['transport']!=('REST','REST','WS','WS')[n-1]
                    or any(r['permit']==d['permit'] for r in s['accepted'])): raise Refused('AUTHORITY_HISTORY')
                s['accepted'].append(d); s['checkpoint']=None
            elif kind=='BIND':
                if str(d['ordinal']) in s['links'] or d['ordinal']!=len(s['accepted']): raise Refused('AUTHORITY_HISTORY')
                s['links'][str(d['ordinal'])]=d['attempt']
            elif kind=='SEND':
                if s['terminal'] or s['pending'] or d['ordinal']!=len(s['accepted']) or s['checkpoint']: raise Refused('AUTHORITY_HISTORY')
                s['pending']=d; s['sends'].append(d)
            elif kind=='SETTLE':
                if d!=s['pending'] or d is None: raise Refused('AUTHORITY_HISTORY')
                s['pending']=None
            elif kind=='CHECKPOINT':
                if s['terminal'] or s['pending'] or d['accepted']!=len(s['accepted']): raise Refused('AUTHORITY_HISTORY')
                s['checkpoint']=d
            elif kind=='RUNTIME_TERMINAL':
                if d['status'] not in ('CLOSED_COMPLETE','CLOSED_INCOMPLETE'): raise Refused('AUTHORITY_HISTORY')
                if s['terminal_status']=='CLOSED_INCOMPLETE' and d['status']!='CLOSED_INCOMPLETE': raise Refused('AUTHORITY_HISTORY')
                s['terminal']=True; s['terminal_status']=d['status']; s['stop_requested']=True
            else: raise Refused('AUTHORITY_HISTORY')
        return s

    def signed(self,raw,signature,peer,verb):
        if verb not in (SUCCESSOR_VERB,'OPEN_HOLD','AUTHORIZE_ONE','TERMINAL_STOP'): raise Refused('AUTHORITY_VERB')
        def op(s):
            proof=self.predecessor_reader() if verb==SUCCESSOR_VERB else None
            a=self.authority.check(raw,signature,peer,verb)
            if self.db.execute('SELECT 1 FROM events WHERE nonce=?',(a['nonce'],)).fetchone(): raise Refused('AUTHORITY_REPLAY')
            if verb==SUCCESSOR_VERB:
                if s['root'] is not None: raise Refused('SUCCESSOR_ALREADY_RESERVED')
                p=successor_payload(proof,self.authority.bindings.as_dict())
                if a['payload']!=p or a['checkpoint']!=digest(canonical(p)) or self.authority.bindings.epoch==proof.epoch: raise Refused('SUCCESSOR_SIGNED_BINDING')
                if self.predecessor_reader()!=proof: raise Refused('PREDECESSOR_CHANGED')
                kind='RUNTIME_SUCCESSOR'
            else:
                if s['root'] is None or s['terminal'] or s['stop_requested']: raise Refused('AUTHORITY_CLOSED')
                cp=s['checkpoint']
                # Signed stop is allowed while uncertain; it never settles a SEND.
                if verb!='TERMINAL_STOP' and (cp is None or a['checkpoint']!=cp['digest']): raise Refused('AUTHORITY_CHECKPOINT')
                if verb=='OPEN_HOLD' and (s['opened'] or s['accepted']): raise Refused('OPEN_STATE')
                if verb=='AUTHORIZE_ONE':
                    n=len(s['accepted'])+1; p=a['payload']
                    outstanding=[v for v in s['commands'].values() if v['verb']=='AUTHORIZE_ONE' and v['nonce'] not in {r['permit'] for r in s['accepted']}]
                    if not s['opened'] or outstanding or n>4 or p['transport']!=('REST','REST','WS','WS')[n-1]: raise Refused('AUTHORITY_PERMIT')
                    if (type(p['session']) is not str or not 1<=len(p['session'])<=128 or type(p['request_commitment']) is not str or len(p['request_commitment'])!=64
                        or any(c not in '0123456789abcdef' for c in p['request_commitment'])): raise Refused('AUTHORITY_PERMIT')
                    if any(r['transport']==p['transport'] and r['session']!=p['session'] for r in s['accepted']): raise Refused('AUTHORITY_SESSION')
                kind='APPROVE'
            self._identity()
            if not self.authority.clock()<a['expires']: raise Refused('CONTROL_EXPIRED')
            return self._append(s,a['nonce'],kind,a)
        return self._transaction(op)

    def claim(self,*,peer,expected,nonce):
        self._service_peer(peer)
        def op(s):
            a=s['commands'].get(nonce)
            if token(s)!=expected or not a or nonce in s['claims'] or s['terminal']:raise Refused('AUTHORITY_COMMAND_REPLAY')
            if s['stop_requested'] and a['verb']!='TERMINAL_STOP':raise Refused('AUTHORITY_CLOSED')
            if not self.authority.clock()<a['expires']:raise Refused('CONTROL_EXPIRED')
            return self._append(s,'claim-'+nonce,'CLAIM',nonce)
        return self._transaction(op)

    def consume(self,*,peer,expected,permit,snapshot_reader):
        self._service_peer(peer)
        def op(s):
            if token(s)!=expected or s['terminal'] or s['stop_requested'] or s['pending'] or s['checkpoint'] is None: raise Refused('AUTHORITY_CONSUME_STATE')
            snapshot_reader(s)  # fixed authority-side controller reader, no wire callback
            a=s['commands'].get(permit)
            if permit not in s['claims']:raise Refused('AUTHORITY_UNCLAIMED_PERMIT')
            if not a or a['verb']!='AUTHORIZE_ONE' or any(r['permit']==permit for r in s['accepted']) or len(s['accepted'])>=4: raise Refused('AUTHORITY_PERMIT')
            if not self.authority.clock()<a['expires']: raise Refused('CONTROL_EXPIRED')
            p=a['payload']; d=dict(ordinal=len(s['accepted'])+1,transport=p['transport'],session=p['session'],commitment=p['request_commitment'],permit=permit)
            return self._append(s,'consume-'+permit,'ACCEPT',d)
        return self._transaction(op)

    def bind(self,*,peer,expected,snapshot_reader):
        self._service_peer(peer)
        def op(s):
            if token(s)!=expected or s['terminal'] or s['stop_requested'] or not s['accepted']: raise Refused('AUTHORITY_BIND_STATE')
            n=len(s['accepted'])
            if str(n) in s['links']: raise Refused('AUTHORITY_ALREADY_BOUND')
            aid=snapshot_reader(s,unbound=True)
            return self._append(s,'bind-'+str(n),'BIND',dict(ordinal=n,attempt=aid))
        return self._transaction(op)

    def terminate(self,*,peer,snapshot_reader):
        self._service_peer(peer)
        def op(s):
            status=snapshot_reader()
            if status not in ('CLOSED_COMPLETE','CLOSED_INCOMPLETE') or s['root'] is None: raise Refused('AUTHORITY_TERMINAL')
            if s['pending'] or len(s['links'])!=len(s['accepted']): status='CLOSED_INCOMPLETE'
            if s['terminal_status']=='CLOSED_INCOMPLETE': status='CLOSED_INCOMPLETE'
            if s['terminal_status']==status:
                self.db.execute('COMMIT'); return token(s)
            return self._append(s,'terminal-'+str(s['seq']+1),'RUNTIME_TERMINAL',{'status':status})
        return self._transaction(op)


class ControllerReader:
    """Installer-pinned read-only controller and coordinated snapshot paths.

    Files remain service-owned: their claims are compared with protected history.
    This reader does NOT manufacture independent provider terminal attestation.
    """
    def __init__(self,root,coordinated,*,service_uid):
        self.root=Path(root);self.coordinated=Path(coordinated);self.uid=service_uid

    def database(self):
        from .storage import no_symlink_ancestors,validate_accounting,SCHEMA
        p=self.root/'controller.sqlite3'; no_symlink_ancestors(p)
        st=p.lstat()
        import stat
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=self.uid or st.st_nlink!=1 or stat.S_IMODE(st.st_mode)!=0o600: raise Refused('CONTROLLER_READER_PATH')
        from .storage import read_snapshot_db
        db=read_snapshot_db(p,owner_uid=self.uid)
        try:
            if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)] or {r[0] for r in db.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name!='sqlite_sequence'")}!=set(SCHEMA): raise Refused('CONTROLLER_READER_INTEGRITY')
            validate_accounting(db)
        except BaseException:db.close();raise
        return db

    def check(self,state,unbound=False):
        db=self.database()
        try:
            p=state['root']
            if p is None or strict_json(db.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()[0])!=p['bindings']: raise Refused('AUTHORITY_CONTROLLER_BINDING')
            if db.execute('SELECT parent,child,archive,ancestor_count FROM lineage').fetchall()!=[(p['predecessor'],p['bindings']['epoch'],p['archive'],0)]: raise Refused('AUTHORITY_CONTROLLER_LINEAGE')
            if accepted_rows(db)!=state['accepted']: raise Refused('AUTHORITY_CONTROLLER_ROLLBACK')
            rows=db.execute('SELECT ordinal,id FROM attempts ORDER BY ordinal').fetchall()
            for n,aid in rows:
                if unbound and n==len(rows):continue
                if state['links'].get(str(n))!=aid: raise Refused('AUTHORITY_CONTROLLER_ASSOCIATION')
            local_commands=db.execute('SELECT * FROM control').fetchall()
            if {r[0] for r in local_commands}!=set(state['claims']):raise Refused('AUTHORITY_CONTROL_ROLLBACK')
            for nonce,verb,sha,operator in local_commands:
                a=state['commands'].get(nonce)
                if not a or (verb,sha,operator)!=(a['verb'],a['_signed_digest'],a['_verified_operator']): raise Refused('AUTHORITY_CONTROL_ASSOCIATION')
            for nonce,n,t,se,c,expires,spent in db.execute('SELECT * FROM permits'):
                a=state['commands'].get(nonce)
                if not a or a['verb']!='AUTHORIZE_ONE' or a['payload']!=dict(transport=t,session=se,request_commitment=c) or a['expires']!=expires:raise Refused('AUTHORITY_PERMIT_ASSOCIATION')
            # Every protected send must still exist locally. Lost intent => hold.
            for send in state['sends']:
                kind='GRANITE' if send['role']=='granite' else 'LEGACY_ROUTER' if send['role']=='legacy_router' else 'LEGACY_RESPONDER'
                aid=state['links'].get(str(send['ordinal']))
                if db.execute('SELECT request_digest FROM steps WHERE attempt=? AND kind=?',(aid,kind)).fetchone()!=(send['request'],): raise Refused('AUTHORITY_SEND_ROLLBACK')
            return rows[-1][1] if unbound and rows else None
        finally:db.close()

    def send(self,state,arguments,resource):
        self.check(state)
        n=arguments['ordinal'];role=arguments['role']
        aid=state['links'].get(str(n))
        kind='GRANITE' if role=='granite' else 'LEGACY_ROUTER' if role=='legacy_router' else 'LEGACY_RESPONDER'
        db=self.database()
        try:
            expected=(resource.endpoint,resource.model,resource.profile,arguments['request_digest'],'POSSIBLE_SEND')
            if db.execute('SELECT endpoint,model,profile,request_digest,state FROM steps WHERE attempt=? AND kind=?',(aid,kind)).fetchone()!=expected:raise Refused('AUTHORITY_SEND_ASSOCIATION')
        finally:db.close()

    def terminal(self):
        db=self.database()
        try:return db.execute("SELECT value FROM meta WHERE key='terminal'").fetchone()[0]
        finally:db.close()

    def checkpoint(self,state,bundle):
        if type(bundle) is not str or len(bundle)!=32 or any(c not in '0123456789abcdef' for c in bundle): raise Refused('CHECKPOINT_IDENTIFIER')
        from .checkpoints import validate_coordinated
        root=self.coordinated/bundle
        m=validate_coordinated(root,minimum_accepted=len(state['accepted']),owner_uid=self.uid)
        if m['purpose']!='READY' or strict_json((root/'authority-token.json').read_bytes())!=token(state): raise Refused('AUTHORITY_CHECKPOINT_STALE')
        self.check(state)
        from .storage import read_snapshot_db
        db=read_snapshot_db(root/'controller.sqlite3',owner_uid=self.uid,expected_digest=m['files']['controller.sqlite3'])
        try:
            if accepted_rows(db)!=state['accepted']:raise Refused('AUTHORITY_SNAPSHOT')
            controls=db.execute('SELECT * FROM control').fetchall()
            if {r[0] for r in controls}!=set(state['claims']):raise Refused('AUTHORITY_SNAPSHOT_CONTROL')
            for nonce,verb,sha,operator in controls:
                a=state['commands'][nonce]
                if (verb,sha,operator)!=(a['verb'],a['_signed_digest'],a['_verified_operator']):raise Refused('AUTHORITY_SNAPSHOT_CONTROL')
            actual=[(n,kind,sha) for n,kind,sha in db.execute('SELECT a.ordinal,s.kind,s.request_digest FROM steps s JOIN attempts a ON s.attempt=a.id ORDER BY a.ordinal,s.rowid')]
            expected=[(s['ordinal'],'GRANITE' if s['role']=='granite' else 'LEGACY_ROUTER' if s['role']=='legacy_router' else 'LEGACY_RESPONDER',s['request']) for s in state['sends']]
            if actual!=expected:raise Refused('AUTHORITY_UNPROTECTED_SEND')
        finally:db.close()
        return dict(accepted=state['accepted'],digest=m['controller_checkpoint'],clean=True)


class AuthorityService:
    """Fixed schemas only. Readers and resources are provisioned, never wire inputs."""
    def __init__(self,journal,reader,*,terminal_reader,contracts):
        from dataclasses import asdict
        self.journal=journal; self.reader=reader; self.terminal_reader=terminal_reader;self.contracts=dict(contracts)
        if {r:digest(canonical(asdict(c))) for r,c in self.contracts.items()}!=journal.provider_resources:raise Refused('AUTHORITY_CONFIGURATION_RESOURCE')

    def dispatch(self,channel,p,peer):
        if type(p) is not dict or set(p)!={'version','operation','arguments'} or type(p['version']) is not int or p['version']!=1 or type(p['arguments']) is not dict: raise Refused('AUTHORITY_PROTOCOL')
        verb=p['operation']; a=p['arguments']; j=self.journal
        if channel=='operator':
            if verb!='SIGNED' or set(a)!={'body','signature'} or type(a['body']) is not dict or type(a['signature']) is not str or len(a['signature'])!=128:raise Refused('OPERATOR_SCHEMA')
            return j.signed(canonical(a['body']),bytes.fromhex(a['signature']),peer,a['body'].get('verb'))
        j._service_peer(peer)
        schemas={'READ':set(),'CHECK':{'expected','allow_terminal'},'CLAIM':{'expected','nonce'},'CONSUME':{'expected','permit'},'BIND':{'expected'},'CHECKPOINT':{'expected','bundle'},'SEND':{'expected','ordinal','role','request_digest'},'SETTLE':{'expected'},'TERMINATE':set()}
        if verb not in schemas or set(a)!=schemas[verb]:raise Refused('SERVICE_SCHEMA')
        with j.lock:
            if verb=='READ':return j.read()
            s=j.read()
            if verb=='TERMINATE':
                def terminal():
                    status=self.reader.terminal()
                    try:self.reader.check(s)
                    except Refused:return 'CLOSED_INCOMPLETE'
                    if s['checkpoint'] is None or s['checkpoint']['accepted']!=len(s['accepted']):return 'CLOSED_INCOMPLETE'
                    return status
                return j.terminate(peer=peer,snapshot_reader=terminal)
            if a['expected']!=token(s):raise Refused('AUTHORITY_STALE_STATE')
            if verb=='CLAIM':return j.claim(peer=peer,**a)
            if verb=='CHECK':
                if type(a['allow_terminal']) is not bool or (s['terminal'] or s['stop_requested']) and not a['allow_terminal']:raise Refused('AUTHORITY_CLOSED')
                self.reader.check(s)
                if a['allow_terminal'] and s['terminal_status']!=self.reader.terminal():raise Refused('AUTHORITY_TERMINAL_MISMATCH')
                return token(s)
            if s['terminal'] or s['stop_requested']:raise Refused('AUTHORITY_CLOSED')
            if verb=='CONSUME':return j.consume(peer=peer,expected=a['expected'],permit=a['permit'],snapshot_reader=self.reader.check)
            if verb=='BIND':return j.bind(peer=peer,expected=a['expected'],snapshot_reader=self.reader.check)
            if verb=='CHECKPOINT':return j.checkpoint(peer=peer,expected=a['expected'],snapshot_reader=lambda:self.reader.checkpoint(s,a['bundle']))
            if verb=='SEND':
                if a['role'] not in self.contracts:raise Refused('AUTHORITY_RESOURCE_UNQUALIFIED')
                self.reader.send(s,a,self.contracts[a['role']].resource)
                return j.possible_send(peer=peer,**a)
            if verb=='SETTLE':return j.settle(peer=peer,expected=a['expected'],terminal_reader=lambda:self.terminal_reader(s['pending']))


class ReleaseIdentityReader:
    """Fixed root-owned file inventory, exact config and approved live process pin.

    Installation supplies the inventory and Bindings, never the service socket.
    No credentials or environment inspection. No rebind/recovery operation.
    """
    def __init__(self,release,inventory,config,config_digest,bindings,process_pin,*,owner_uid=0):
        self.release=Path(release);self.inventory=dict(inventory);self.config=Path(config)
        self.config_digest=config_digest;self.bindings=bindings;self.pin=process_pin;self.owner=owner_uid
        if not self.inventory:raise Refused('RELEASE_INVENTORY_REQUIRED')

    def _file(self,p,expected):
        import stat
        from .storage import no_symlink_ancestors
        no_symlink_ancestors(p)
        for parent in p.parents:
            st=parent.lstat();sticky=st.st_uid==0 and bool(st.st_mode&stat.S_ISVTX)
            if st.st_uid not in (0,self.owner) or st.st_mode&0o022 and not sticky:raise Refused('RELEASE_ANCESTOR')
        st=p.lstat()
        if st.st_uid!=self.owner or not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or st.st_mode&0o022:raise Refused('RELEASE_OWNERSHIP')
        if digest(p.read_bytes())!=expected:raise Refused('RELEASE_IDENTITY')

    def __call__(self):
        for name,sha in self.inventory.items():
            if type(name) is not str or Path(name).is_absolute() or '..' in Path(name).parts:raise Refused('RELEASE_MANIFEST_PATH')
            self._file(self.release/name,sha)
        self._file(self.config,self.config_digest)
        self.pin.verify(self.pin.uid,self.pin.pid)
        b=self.bindings.as_dict()
        if (b['source']!=digest(canonical(self.inventory)) or b['config']!=self.config_digest
            or b['pid']!=str(self.pin.pid) or b['start']!=self.pin.start or b['boot']!=self.pin.boot):raise Refused('RELEASE_PROCESS_BINDING')
        return b

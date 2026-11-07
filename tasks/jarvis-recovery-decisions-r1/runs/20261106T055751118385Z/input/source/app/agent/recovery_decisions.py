"""Disposable offline recovery journal. Approval never grants execution capability.

SQLite is an index of protected append-only admissions, not the trust root. External
custody of configuration, latest reference, keys and time is required. Same-UID or
coordinated rollback of all custody is outside this contract. No production keys,
activation, task updates or executor imports occur here.
"""
from contextlib import contextmanager
from datetime import UTC, datetime
import fcntl
from functools import wraps
import hashlib
import os
from pathlib import Path
import sqlite3
import uuid

from app.agent.authority import Authority, AuthorityError, canonical, identifier, instant
from app.agent.enrollment import fingerprint
from app.agent.ledger import encode, private_directory, read_file, publish_file, sync_directory, strict_json

ZERO = '0' * 64
SCHEMA = 'CREATE TABLE events(sequence INTEGER PRIMARY KEY, request_id TEXT NOT NULL UNIQUE, envelope TEXT NOT NULL)'


def evidence_errors(method):
    @wraps(method)
    def checked(*args, **kwargs):
        try:return method(*args, **kwargs)
        except (KeyError, TypeError, ValueError, IndexError, OverflowError, RecursionError) as exc:
            raise AuthorityError('recovery_evidence_invalid') from exc
    return checked


def interval(start, end, *, fresh=True, bound=300):
    a, b = datetime.fromisoformat(instant(start)), datetime.fromisoformat(instant(end))
    if not 0 < (b-a).total_seconds() <= bound or fresh and not a <= datetime.now(UTC) < b:
        raise AuthorityError('recovery_decision_expired')
    return a, b


@evidence_errors
def verify_receipt(guard, receipt, *, registry_id, request_id, payload_sha256, event_sha256, permits):
    """Independent offline HMAC verification; expired evidence remains historical.

    Expected identities/digest come from external custody, never from this receipt.
    HMAC verification requires trusted shared keys, not a public-key signature.
    """
    if type(receipt) is not dict or set(receipt) != {'event','commit'}:
        raise AuthorityError('recovery_receipt_invalid')
    event = guard.authenticate(receipt['event']); commit = guard.authenticate(receipt['commit'])
    if (fingerprint(receipt['event']) != event_sha256 or event.get('registry_id') != registry_id
        or event.get('request_id') != request_id or fingerprint(event.get('payload')) != payload_sha256
        or commit != RecoveryRegistry.commit_body(event, event_sha256)):
        raise AuthorityError('recovery_receipt_binding_mismatch')
    auth = permits.authenticate(event['permit'])
    if (auth['request_id'], auth['command'], auth['payload_hash'], auth['checkpoint'], auth['scope']) != (
        request_id, 'recovery_'+event['command'], payload_sha256, event['checkpoint'], 'local-service'):
        raise AuthorityError('recovery_receipt_authorization_mismatch')
    interval(auth['issued_at'], auth['expires_at'], fresh=False)
    return {'verified': True, 'principal': auth['principal'], 'historical_evidence_only': True,
            'execution_enabled': False, 'activation_authorized': False}


class RecoveryRegistry:
    @evidence_errors
    def __init__(self, guard, config, external_reference, permits=None, *, fault_hook=None):
        self.guard, self.permits = guard, permits
        if permits is None:
            raise AuthorityError('recovery_operator_verifier_required')
        self._fault = fault_hook or (lambda _: None)
        fields = {'format','registry_id','store_id','key_id','database','custody','checkpoints',
                  'initial_reference','capacity','disposable_only'}
        if type(config) is not dict or set(config) != fields:
            raise AuthorityError('recovery_registry_configuration_required')
        self.config = strict_json(encode(config))
        c = self.config
        identifier(c['registry_id'])
        if (uuid.UUID(c['registry_id']).version != 4 or c['registry_id'] == guard.store_id
            or c['format'] != 'jarvis-recovery-registry-v1' or c['store_id'] != guard.store_id
            or c['key_id'] != guard.key_id or c['checkpoints'] != str(guard.directory)
            or c['disposable_only'] is not True or type(c['capacity']) is not int or not 4 <= c['capacity'] <= 256):
            raise AuthorityError('recovery_registry_context_mismatch')
        self.database = Path(c['database'])
        if not self.database.is_absolute() or '..' in self.database.parts:
            raise AuthorityError('recovery_registry_unsafe_path')
        self.directory = private_directory(self.database.parent)
        self.stage = self.directory / ('.registry-' + c['registry_id'] + '.pending')
        self.custody = private_directory(c['custody'])
        paths = (self.directory, self.custody, guard.directory)
        if any(a == b or a.is_relative_to(b) or b.is_relative_to(a) for i,a in enumerate(paths) for b in paths[i+1:]):
            raise AuthorityError('recovery_registry_custody_not_separate')
        if guard.trust_context is None or external_reference is None:
            raise AuthorityError('recovery_external_custody_required')
        self.reference = strict_json(encode(external_reference))
        self._pid = os.getpid()
        self._active_lock_identity = None
        self._paths_identity = [(p.stat().st_dev,p.stat().st_ino) for p in paths]
        r = self.reference
        if (type(r) is not dict or set(r) != {'registry_id','sequence','event_sha256','witness'}
            or r['registry_id'] != c['registry_id'] or type(r['sequence']) is not int or r['sequence'] < 0
            or not guard._hash(r['event_sha256']) or r['sequence'] == 0 and r != self.initial_reference()):
            raise AuthorityError('recovery_external_reference_invalid')

    def initial_reference(self):
        return {'registry_id': self.config['registry_id'], 'sequence': 0, 'event_sha256': ZERO,
                'witness': {'renewal_id': None, 'checkpoint': self.config['initial_reference']}}

    def _fence(self):
        self.guard._fence()
        paths = (self.directory, self.custody, self.guard.directory)
        if self._active_lock_identity is not None:
            st=(self.custody/'journal.lock').stat(follow_symlinks=False)
            if (st.st_dev,st.st_ino)!=self._active_lock_identity:
                raise AuthorityError('recovery_registry_owner_stale')
        if self._pid != os.getpid() or [(private_directory(p).stat().st_dev,p.stat().st_ino) for p in paths] != self._paths_identity:
            raise AuthorityError('recovery_registry_owner_stale')

    @contextmanager
    def _locked(self, *, write=False):
        with self.guard._operation_mutex:
            self._fence()
            if write: self.guard._writable()
            # Journal lock is deliberately provisioned by authenticated initialize.
            flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
            if write: flags |= os.O_CREAT
            fd = os.open(self.custody/'journal.lock', flags, 0o600)
            try:
                Authority._check_file(fd)
                try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc: raise AuthorityError('recovery_registry_owner_busy') from exc
                identity = os.fstat(fd)
                self._active_lock_identity=(identity.st_dev,identity.st_ino)
                self._fence()
                yield
                current = (self.custody/'journal.lock').stat(follow_symlinks=False)
                if (identity.st_dev,identity.st_ino) != (current.st_dev,current.st_ino):
                    raise AuthorityError('recovery_registry_owner_stale')
            finally:
                self._active_lock_identity=None
                os.close(fd)

    def _path(self, sequence, phase):
        return self.custody / f'{sequence:04}.{phase}.json'

    @staticmethod
    def commit_body(event, digest):
        return {'format':'jarvis-recovery-commit-v1', 'registry_id':event['registry_id'],
                'sequence':event['sequence'], 'request_id':event['request_id'],
                'event_sha256':digest, 'execution_enabled':False, 'activation_authorized':False}

    def _connect(self, *, write=False):
        read_file(self.database, 32*1024*1024)
        before = self.database.stat(follow_symlinks=False)
        conn = sqlite3.connect(self.database.as_uri()+('?mode=rw' if write else '?mode=ro'), uri=True, isolation_level=None, timeout=.1)
        after = self.database.stat(follow_symlinks=False)
        if (before.st_dev,before.st_ino) != (after.st_dev,after.st_ino):
            conn.close(); raise AuthorityError('recovery_registry_replaced')
        try:
            if conn.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise AuthorityError('recovery_registry_corrupt')
            schema = conn.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name").fetchall()
            if schema != [(SCHEMA,)]: raise AuthorityError('recovery_registry_schema_invalid')
            conn.execute('PRAGMA synchronous=FULL')
            return conn
        except BaseException:
            conn.close(); raise

    def _load(self):
        self._fence(); g = self.guard
        head, pending, history = g.history()
        if pending: raise AuthorityError('recovery_checkpoint_incomplete')
        names = {p.name for p in self.custody.iterdir()}
        if len(names) > self.config['capacity']*2+1: raise AuthorityError('recovery_registry_capacity')
        events=[]; commits=[]; expected={'journal.lock'}; previous=ZERO
        proposals={}; witness=self.initial_reference()['witness']; nonce=set()
        for seq in range(1,self.config['capacity']+1):
            ip, fp = self._path(seq,'intent'), self._path(seq,'final')
            if ip.name not in names: break
            expected.add(ip.name)
            event, digest = g._read(ip)
            fields={'format','registry_id','config_sha256','sequence','previous_sha256','request_id','command','payload','permit','checkpoint','result','execution_enabled','activation_authorized','admitted_at'}
            if (type(event) is not dict or set(event)!=fields or event['format']!='jarvis-recovery-event-v1'
                or event['registry_id']!=self.config['registry_id'] or event['config_sha256']!=fingerprint(self.config)
                or event['sequence']!=seq or event['previous_sha256']!=previous or event['execution_enabled'] is not False
                or event['activation_authorized'] is not False):
                raise AuthorityError('recovery_registry_history_conflict')
            self._historical_authorization(event)
            identifier(event['request_id'])
            if event['request_id'] in nonce: raise AuthorityError('recovery_registry_duplicate_nonce')
            nonce.add(event['request_id'])
            if event['checkpoint'] not in history: raise AuthorityError('recovery_registry_checkpoint_rollback')
            if fp.name in names:
                expected.add(fp.name)
                commit,_ = g._read(fp)
                if commit != self.commit_body(event,digest): raise AuthorityError('recovery_registry_commit_invalid')
                commits.append(g.signed(commit))
            else: commits.append(None)
            events.append((event,digest)); previous=digest
        if names != expected or any(c is None for c in commits[:-1]):
            raise AuthorityError('recovery_registry_incomplete_history')
        rows=[]
        if self.database.exists():
            conn = self._connect()
            try: rows=conn.execute('SELECT sequence,request_id,envelope FROM events ORDER BY sequence').fetchall()
            finally: conn.close()
        if len(rows)>len(events): raise AuthorityError('recovery_registry_missing_anchor')
        for index,(event,digest) in enumerate(events):
            if index<len(rows):
                if rows[index] != (index+1,event['request_id'],canonical(g.signed(event))):
                    raise AuthorityError('recovery_registry_database_conflict')
            elif commits[index] is not None or index != len(events)-1:
                raise AuthorityError('recovery_registry_database_rollback')
            if index<=len(rows):
                saved_proposals=strict_json(encode(proposals));saved_witness=witness
                command=event['command']; result=event['result']
                if (command=='initialize') != (index==0):
                    raise AuthorityError('recovery_registry_initialization_invalid')
                if command=='propose':
                    self._validate_proposal(event)
                    pid=event['request_id']
                    if pid in proposals or any(p['proposal']['branch_id']==result['proposal']['branch_id'] or p['proposal']['restore_id']==result['proposal']['restore_id'] for p in proposals.values()):
                        raise AuthorityError('recovery_registry_branch_conflict')
                    proposals[pid]={'proposal_id':pid,'proposal':result['proposal'],'summary':result['summary'],
                                    'state':'PENDING','decision_id':None,'authorization_expires_at':None,
                                    'activation_authorized':False,'execution_enabled':False}
                elif command=='decide':
                    p=proposals.get(event['payload']['proposal_id'])
                    if p is None or p['decision_id']!=event['payload']['previous_decision_id']:
                        raise AuthorityError('recovery_registry_decision_conflict')
                    self._decision_result(event['payload'],proposals,event['permit']['body'],at=event['admitted_at'])
                    if result != {'proposal_id':p['proposal_id'],'state':event['payload']['state'],'activation_authorized':False}:
                        raise AuthorityError('recovery_decision_result_invalid')
                    p.update(state=event['payload']['state'],decision_id=event['request_id'],
                             authorization_expires_at=event['payload']['expires_at'],
                             principal=event['permit']['body']['principal'])
                elif command=='renew':
                    if event['payload']['previous_witness']!=witness: raise AuthorityError('recovery_witness_history_conflict')
                    if result != {'witness':{'renewal_id':event['request_id'],'checkpoint':event['payload']['next_reference']},'history_preserved':True}:
                        raise AuthorityError('recovery_witness_result_invalid')
                    self._renewal_references(event['payload'],at=event['admitted_at'],history_state=(head,pending,history))
                    witness=result['witness']
                elif command=='initialize' and index==0:
                    if event['payload']!=self.config or result!={'initialized':True}:
                        raise AuthorityError('recovery_registry_initialization_invalid')
                else:
                    raise AuthorityError('recovery_registry_history_conflict')
                if index>=len(rows):
                    proposals=saved_proposals;witness=saved_witness
        r=self.reference
        if r['sequence']>len(rows) or r['sequence'] and events[r['sequence']-1][1]!=r['event_sha256']:
            raise AuthorityError('recovery_registry_external_rollback')
        # The externally retained renewal must be present at the retained prefix.
        anchored=self.initial_reference()['witness']
        for e,_ in events[:r['sequence']]:
            if e['command']=='renew': anchored=e['result']['witness']
        if r['witness']!=anchored: raise AuthorityError('recovery_witness_external_mismatch')
        for p in proposals.values():
            if p['state'] in {'PENDING','APPROVED'} and p['authorization_expires_at'] and datetime.now(UTC)>=datetime.fromisoformat(instant(p['authorization_expires_at'])):
                p['state']='EXPIRED'
        return events,commits,rows,proposals,witness,head

    def _receipt(self, event, digest):
        commit,_=self.guard._read(self._path(event['sequence'],'final'))
        return {'event':self.guard.signed(event),'commit':self.guard.signed(commit)}

    @evidence_errors
    def inspect(self, request_id=None):
        if request_id is not None: identifier(request_id)
        with self._locked():
            events,commits,rows,proposals,witness,head=self._load()
            pending=bool(events and (commits[-1] is None or len(rows)<len(events)))
            reference={'registry_id':self.config['registry_id'],'sequence':len(rows),
                       'event_sha256':events[len(rows)-1][1] if rows else ZERO,'witness':witness}
            minimum=witness['checkpoint']
            now=datetime.now(UTC)
            witness_current=datetime.fromisoformat(instant(minimum['valid_from']))<=now<datetime.fromisoformat(instant(minimum['expires_at']))
            result={'state':'RECONCILIATION_REQUIRED' if pending else 'VERIFIED' if witness_current else 'WITNESS_EXPIRED',
                    'verified':not pending and witness_current,'history_verified':True,
                    'witness_state':'VERIFIED' if witness_current else 'EXPIRED',
                    'proposals':list(proposals.values()),'reference':reference,'event_count':len(rows),
                    'incomplete_witness_renewal':bool(pending and events[-1][0]['command']=='renew'),
                    'execution_enabled':False,'activation_authorized':False,'external_effects':'UNKNOWN_NEVER_RETRY',
                    'automatic_retry':False}
            if request_id is not None:
                found=next(((i,e,d) for i,(e,d) in enumerate(events) if e['request_id']==request_id),None)
                if found is None: result['operation_state']='PROPOSAL_NEVER_COMMITTED'
                else:
                    i,e,d=found
                    result['operation_state']='NEVER_COMMITTED' if i>=len(rows) else 'COMMITTED_ACKNOWLEDGMENT_UNKNOWN' if commits[i] is None else 'DURABLE_RECEIPT_ACKNOWLEDGMENT_UNKNOWN'
                    result['receipt']=self._receipt(e,d) if commits[i] else None
            return result

    def _validate_reference(self, reference, *, current=False, at=None, history_state=None):
        g=self.guard
        if type(reference) is not dict or set(reference)!={'store_id','key_id','epoch','rollover_hash','head','valid_from','expires_at'}:
            raise AuthorityError('recovery_witness_invalid')
        start,end=interval(reference['valid_from'],reference['expires_at'],fresh=at is None,bound=300 if current else 86400)
        if at is not None and not start<=datetime.fromisoformat(instant(at))<end:
            raise AuthorityError('recovery_witness_admission_expired')
        if (reference['store_id'],reference['key_id'])!=(g.store_id,g.key_id):
            raise AuthorityError('recovery_witness_key_mismatch')
        head,pending,history=g.history() if history_state is None else history_state
        epoch=reference['epoch']
        if type(epoch) is not int or not 0<=epoch<len(g._epoch_ranges) or reference['head'] not in history or g._epoch_ranges[epoch]['rollover_hash']!=reference['rollover_hash']:
            raise AuthorityError('recovery_witness_rollback')
        selected=g._epoch_ranges[epoch]
        sequence=reference['head']['sequence']
        # A generation link authenticates its preceding head, including after growth.
        if not (selected['start']<=sequence<=selected['end'] or epoch>0 and sequence==selected['start']-1):
            raise AuthorityError('recovery_witness_generation_mismatch')
        if current and reference!=g.trust_reference(valid_from=reference['valid_from'],expires_at=reference['expires_at']):
            raise AuthorityError('recovery_witness_not_current')

    def _renewal_references(self, payload, *, at=None, history_state=None):
        prev=payload['previous_witness']['checkpoint']; nxt=payload['next_reference']
        self._validate_reference(prev,at=at,history_state=history_state)
        self._validate_reference(nxt,current=at is None,at=at,history_state=history_state)
        interval(nxt['valid_from'],nxt['expires_at'],fresh=False)
        if not prev['epoch']<=nxt['epoch']<=prev['epoch']+1 or nxt['head']['sequence']<prev['head']['sequence']:
            raise AuthorityError('recovery_witness_generation_bound')
        if nxt['head']==prev['head'] and nxt['epoch']==prev['epoch']:
            raise AuthorityError('recovery_witness_no_progress')

    def _prepare_initial_database(self, event):
        # Dedicated staging belongs only to this authenticated initialization.
        # Empty/schema-only stages can finish; unknown content is quarantined.
        if not self.stage.exists():
            fd=os.open(self.stage,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
            self._fault('recovery_initial_stage_created')
        read_file(self.stage,32*1024*1024)
        conn=sqlite3.connect(self.stage,isolation_level=None)
        try:
            conn.execute('PRAGMA synchronous=FULL');conn.execute('PRAGMA journal_mode=DELETE')
            if conn.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:
                raise AuthorityError('recovery_registry_partial_quarantine')
            schema=conn.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name").fetchall()
            if schema not in ([],[(SCHEMA,)]): raise AuthorityError('recovery_registry_partial_quarantine')
            if schema and conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]:
                raise AuthorityError('recovery_registry_partial_quarantine')
            conn.execute('BEGIN IMMEDIATE')
            if not schema:conn.execute(SCHEMA)
            self._fault('recovery_initial_before_schema_commit')
            conn.execute('COMMIT');self._fault('recovery_initial_schema_committed')
        finally:conn.close()
        sync_directory(self.directory)

    def _historical_authorization(self, event):
        auth=self.permits.authenticate(event['permit'])
        start,end=interval(auth['issued_at'],auth['expires_at'],fresh=False)
        at=datetime.fromisoformat(instant(event['admitted_at']))
        if (not start<=at<end or (auth['request_id'],auth['scope'],auth['command'],auth['payload_hash'],auth['checkpoint']) !=
            (event['request_id'],'local-service','recovery_'+event['command'],fingerprint(event['payload']),event['checkpoint'])):
            raise AuthorityError('recovery_historical_authorization_invalid')

    def _validate_proposal(self, event):
        p=event['result']['proposal']; r=event['payload']['verification_request']
        if fingerprint(event['result'])!=event['payload']['verification_sha256']:
            raise AuthorityError('recovery_proposal_result_binding_mismatch')
        if (p['branch_id']!=r['branch_id'] or p['original_store_id']!=self.guard.store_id
            or p['restore_id']!=r['expected_restore_id'] or p['database_sha256']!=r['expected_database_sha256']
            or p['parent_lineage']!=r['expected_source_lineage'] or p['verified_source_head']!=r['expected_source_head']
            or r['expected_source_head']!=event['checkpoint'] or p['external_context_sha256']!=fingerprint(r) or p['activation_authorized'] is not False
            or p['execution_enabled'] is not False or fingerprint(p['original_request_ids'])!=p['original_request_ids_sha256']):
            raise AuthorityError('recovery_proposal_history_invalid')

    def _decision_result(self, payload, proposals, auth, *, at=None):
        if set(payload)!={'proposal_id','proposal_sha256','state','valid_from','expires_at','previous_decision_id'}:
            raise AuthorityError('recovery_decision_invalid')
        p=proposals.get(identifier(payload['proposal_id']))
        if p is None: raise AuthorityError('recovery_proposal_not_found')
        if payload['proposal_sha256']!=fingerprint(p['proposal']):
            raise AuthorityError('recovery_decision_proposal_binding_mismatch')
        effective=p['state']
        now=datetime.now(UTC) if at is None else datetime.fromisoformat(instant(at))
        if effective in {'PENDING','APPROVED'} and p['authorization_expires_at'] and now>=datetime.fromisoformat(instant(p['authorization_expires_at'])):
            effective='EXPIRED'
        allowed={'PENDING':{'APPROVED','REJECTED','REVOKED'},'APPROVED':{'REVOKED'},'EXPIRED':{'REVOKED'}}
        # An explicit pending decision records the reviewer while awaiting approval.
        states=allowed.get(effective,set()) | ({'PENDING'} if p['decision_id'] is None else set())
        if payload['previous_decision_id']!=p['decision_id'] or payload['state'] not in states:
            raise AuthorityError('recovery_decision_conflict')
        begin,end=interval(payload['valid_from'],payload['expires_at'],fresh=at is None)
        if at is not None and not begin<=datetime.fromisoformat(instant(at))<end:
            raise AuthorityError('recovery_decision_admission_expired')
        if end>datetime.fromisoformat(instant(auth['expires_at'])):
            raise AuthorityError('recovery_decision_outlives_permit')
        return {'proposal_id':p['proposal_id'],'state':payload['state'],'activation_authorized':False}

    def _result(self, command, payload, request_id, proposals, witness, auth):
        if command=='initialize':
            if payload!=self.config: raise AuthorityError('recovery_registry_context_mismatch')
            self._validate_reference(self.config['initial_reference'],current=True)
            return {'initialized':True}
        if command=='propose':
            if set(payload)!={'directory','verification_request','verification_sha256'}: raise AuthorityError('recovery_proposal_invalid')
            from app.agent.branch_verification import BranchVerifier
            verified=BranchVerifier(self.guard).verify(payload['directory'],payload['verification_request'])
            proposal=verified['proposal']
            if any(p['proposal']['branch_id']==proposal['branch_id'] or p['proposal']['restore_id']==proposal['restore_id'] for p in proposals.values()):
                raise AuthorityError('recovery_proposal_conflict')
            if request_id in proposal['original_request_ids']+proposal['original_occurrence_ids']+proposal['original_task_ids']+[proposal['branch_id'],proposal['original_store_id'],proposal['restore_id']]:
                raise AuthorityError('recovery_proposal_identity_collision')
            result={'proposal':proposal,'summary':verified['summary']}
            if fingerprint(result)!=payload['verification_sha256']:
                raise AuthorityError('recovery_proposal_result_binding_mismatch')
            return result
        if command=='decide':
            return self._decision_result(payload,proposals,auth)
        if command=='renew':
            if set(payload)!={'previous_witness','next_reference'}: raise AuthorityError('recovery_witness_invalid')
            if payload['previous_witness']!=witness or self.reference['witness']!=witness:
                raise AuthorityError('recovery_witness_stale_substitution')
            nxt=payload['next_reference']
            self._renewal_references(payload)
            return {'witness':{'renewal_id':request_id,'checkpoint':nxt},'history_preserved':True}
        raise AuthorityError('recovery_command_invalid')

    @evidence_errors
    def apply(self, actor, request_id, command, payload, permit, *, initialize=False):
        if Authority._scope(actor)!='local-service' or self.permits is None:
            raise AuthorityError('recovery_offline_authentication_required')
        payload=strict_json(encode(payload));permit=strict_json(encode(permit))
        identifier(request_id)
        if uuid.UUID(request_id).version!=4 or request_id in {self.config['registry_id'],self.guard.store_id}:
            raise AuthorityError('recovery_request_identity_invalid')
        if type(payload) is not dict or len(encode(payload))>48000:
            raise AuthorityError('recovery_payload_bound')
        with self._locked(write=True):
            events,commits,rows,proposals,witness,head=self._load()
            found=next(((e,d) for e,d in events if e['request_id']==request_id),None)
            if found:
                event,digest=found
                if event['command']!=command or event['payload']!=payload or event['permit']!=permit:
                    raise AuthorityError('recovery_request_conflict')
                if commits[event['sequence']-1] is not None:
                    return {'receipt':self._receipt(event,digest),'replayed':True,'execution_enabled':False}
            else:
                if len(rows)!=len(events) or commits and commits[-1] is None:
                    raise AuthorityError('recovery_reconciliation_required')
                if len(events)>=self.config['capacity']: raise AuthorityError('recovery_registry_capacity')
                if (not events)!=(initialize and command=='initialize'):
                    raise AuthorityError('recovery_registry_initialization_required')
                interval(witness['checkpoint']['valid_from'],witness['checkpoint']['expires_at'],bound=86400)
                auth=self.permits.verify(permit,actor,request_id,'recovery_'+command,payload)
                if auth['checkpoint']!=head: raise AuthorityError('recovery_stale_operator_permit')
                result=self._result(command,payload,request_id,proposals,witness,auth)
                event={'format':'jarvis-recovery-event-v1','registry_id':self.config['registry_id'],
                       'config_sha256':fingerprint(self.config),'sequence':len(events)+1,
                       'previous_sha256':events[-1][1] if events else ZERO,'request_id':request_id,
                       'command':command,'payload':payload,'permit':permit,'checkpoint':head,'result':result,
                       'execution_enabled':False,'activation_authorized':False,'admitted_at':datetime.now(UTC).isoformat()}
                if len(encode(self.guard.signed(event)))>65000: raise AuthorityError('recovery_payload_bound')
                self._fence();publish_file(self._path(event['sequence'],'intent'),encode(self.guard.signed(event)))
                digest=fingerprint(self.guard.signed(event)); self._fault('recovery_intent_durable')
            seq=event['sequence']
            if seq>len(rows):
                initial = not self.database.exists()
                if initial:
                    if seq!=1: raise AuthorityError('recovery_registry_missing_database')
                    self._prepare_initial_database(event)
                    from app.agent.archive_restore import _rename_directory
                    # Atomic no-replace publication for a single regular file too.
                    _rename_directory(self.stage,self.database)
                    self._fault('recovery_database_published')
                    conn=self._connect(write=True);conn.execute('BEGIN IMMEDIATE')
                else:
                    conn=self._connect(write=True);conn.execute('BEGIN IMMEDIATE')
                try:
                    self._fence()
                    conn.execute('INSERT INTO events VALUES(?,?,?)',(seq,request_id,canonical(self.guard.signed(event))))
                    self._fault('recovery_before_sql_commit')
                    conn.execute('COMMIT'); self._fault('recovery_sql_committed')
                finally: conn.close()
                sync_directory(self.directory)
            self._fence();self.guard._writable()
            publish_file(self._path(seq,'final'),encode(self.guard.signed(self.commit_body(event,digest))))
            self._fault('recovery_receipt_durable')
            return {'receipt':self._receipt(event,digest),'replayed':found is not None,
                    'execution_enabled':False,'activation_authorized':False}

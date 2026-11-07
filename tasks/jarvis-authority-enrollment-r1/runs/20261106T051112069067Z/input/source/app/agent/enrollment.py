"""Explicit offline genesis admission. No automatic trust provisioning or resets.

Custody and checkpoint directories and the external reservation are supplied by
the trusted operator. This implementation only admits disposable offline stores.
All artifacts and uncertain bootstrap states are retained, never cleaned up.
"""
from contextlib import contextmanager
from datetime import UTC, datetime
import fcntl
import hashlib
import os
from pathlib import Path
import sqlite3
import uuid

from app.agent.authority import AuthorityError, canonical, identifier, instant
from app.agent.ledger import encode, private_directory, read_file, publish_file, sync_directory, digest_state, strict_json
from app.agent.ledger_schema import SCHEMA_SQL
from app.agent.archive_restore import _rename_directory

EMPTY_HEAD = {'sequence': 0, 'sha256': None, 'checkpoint_hash': '0'*64}


def policy(guard):
    return dict(rollover=guard.rollover_enabled, epoch_capacity=guard.epoch_capacity,
                max_epochs=guard.max_epochs, recovery=guard.recovery_enabled,
                schema_sha256=hashlib.sha256(SCHEMA_SQL.encode()).hexdigest())


def fingerprint(value):
    return hashlib.sha256(encode(value)).hexdigest()


class OfflineEnrollment:
    def __init__(self, guard, custody, reservation, permits=None, *, fault_hook=None):
        self.guard, self.permits = guard, permits
        self.custody = private_directory(custody)
        self.reservation = reservation
        self._fault = fault_hook or (lambda _: None)
        required = {'format','enrollment_id','store_id','key_id','destination','custody','checkpoints',
                    'trust_id','policy','initial_checkpoint','issued_at','expires_at','disposable_only'}
        if type(reservation) is not dict or set(reservation) != required:
            raise AuthorityError('enrollment_invalid_external_reservation')
        r = reservation
        for field in ('enrollment_id','store_id','trust_id'):
            identifier(r[field])
            if uuid.UUID(r[field]).version != 4: raise AuthorityError('enrollment_invalid_identity')
        if (r['format'] != 'jarvis-empty-store-reservation-v1' or r['store_id'] != guard.store_id
            or r['key_id'] != guard.key_id or r['policy'] != policy(guard)
            or r['initial_checkpoint'] != EMPTY_HEAD or r['disposable_only'] is not True
            or r['custody'] != str(self.custody) or r['checkpoints'] != str(guard.directory)):
            raise AuthorityError('enrollment_external_context_mismatch')
        self.destination = Path(r['destination'])
        if not self.destination.is_absolute() or '..' in self.destination.parts:
            raise AuthorityError('enrollment_unsafe_destination')
        private_directory(self.destination.parent)
        paths = [self.custody, guard.directory, self.destination]
        if any(a == b or a.is_relative_to(b) or b.is_relative_to(a) for i,a in enumerate(paths) for b in paths[i+1:]):
            raise AuthorityError('enrollment_paths_overlap')
        self.stage = self.destination.parent / ('.enroll-' + r['enrollment_id'] + '.pending')
        self._validate_interval(r)

    @staticmethod
    def _validate_interval(body, *, fresh=False):
        start = datetime.fromisoformat(instant(body['issued_at']))
        end = datetime.fromisoformat(instant(body['expires_at']))
        if not 0 < (end-start).total_seconds() <= 300 or fresh and not start <= datetime.now(UTC) < end:
            raise AuthorityError('enrollment_reservation_expired')

    @property
    def payload(self):
        return {'reservation_sha256': fingerprint(self.reservation), 'reservation': self.reservation,
                'execution_enabled': False}

    @contextmanager
    def _lock(self):
        with self.guard._operation_mutex:
            self.guard._writable()
            fd = os.open(self.custody/'journal.lock', os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_NONBLOCK, 0o600)
            try:
                from app.agent.authority import Authority
                Authority._check_file(fd)
                try: fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError as exc: raise AuthorityError('enrollment_owner_busy') from exc
                yield
            finally: os.close(fd)

    def _phases(self):
        inventory = {p.name for p in self.custody.iterdir()}
        allowed = {'journal.lock','INTENT.json','PREPARED.json','FINAL.json'}
        if not inventory <= allowed: raise AuthorityError('enrollment_custody_inventory_invalid')
        phases = {name: self.guard._read(self.custody/(name+'.json'))
                  for name in ('INTENT','PREPARED','FINAL') if name+'.json' in inventory}
        if set(phases) not in (set(), {'INTENT'}, {'INTENT','PREPARED'}, {'INTENT','PREPARED','FINAL'}):
            raise AuthorityError('enrollment_phase_missing')
        if phases:
            intent, ih = phases['INTENT']
            if set(intent) != {'format','reservation','authorization','permit_sha256','execution_enabled'} or intent['format'] != 'jarvis-enrollment-intent-v1' or intent['reservation'] != self.reservation or intent['execution_enabled'] is not False:
                raise AuthorityError('enrollment_intent_mismatch')
            auth = intent['authorization']
            required = {'request_id','principal','scope','command','payload_hash','checkpoint','expires_at','issued_at'}
            if type(auth) is not dict or set(auth) != required or (auth['request_id'],auth['scope'],auth['command'],auth['payload_hash'],auth['checkpoint']) != (self.reservation['enrollment_id'],'local-service','enroll_authority',fingerprint(self.payload),EMPTY_HEAD) or not self.guard._hash(intent['permit_sha256']):
                raise AuthorityError('enrollment_authorization_mismatch')
            self._validate_interval(auth)
            if 'PREPARED' in phases:
                prepared, ph = phases['PREPARED']
                if set(prepared) != {'format','enrollment_id','store_id','intent_sha256','genesis','logical_state','database_sha256','execution_enabled'} or prepared['format'] != 'jarvis-enrollment-prepared-v1' or prepared['intent_sha256'] != ih or prepared['enrollment_id'] != self.reservation['enrollment_id'] or prepared['store_id'] != self.guard.store_id or prepared['execution_enabled'] is not False or prepared['logical_state'] != self._expected(intent) or not self.guard._hash(prepared['database_sha256']):
                    raise AuthorityError('enrollment_preparation_mismatch')
                head,pending,history = self.guard.history()
                if prepared['genesis'] not in history or prepared['genesis']['sequence'] != 1 or prepared['genesis']['sha256'] != prepared['logical_state']['sha256']:
                    raise AuthorityError('enrollment_genesis_mismatch')
                if 'FINAL' in phases:
                    final, _ = phases['FINAL']
                    if final != self._final_body(prepared, ph): raise AuthorityError('enrollment_final_mismatch')
        return phases

    def _seed(self, conn, intent):
        for statement in SCHEMA_SQL.split(';'):
            if statement.strip(): conn.execute(statement)
        r = self.reservation; op = r['enrollment_id']; store = r['store_id']
        conn.execute('INSERT INTO meta VALUES(1)')
        conn.execute('INSERT INTO ownership VALUES(1,0,?)', ('UNENROLLED:'+op,))
        conn.execute('INSERT INTO control VALUES(1,0,0)')
        conn.execute('INSERT INTO records VALUES(?,?,?,?)', ('ledger_config',store,'__authority__',canonical({'store_id':store,'checkpoint_required':True,'format':1})))
        data = {'enrollment_id':op,'custody':str(self.custody),'reservation_sha256':fingerprint(r),
                'destination':str(self.destination),'key_id':self.guard.key_id,'policy':policy(self.guard)}
        conn.execute('INSERT INTO records VALUES(?,?,?,?)', ('authority_enrollment',op,'__authority__',canonical(data)))
        receipt = {'request_id':op,'scope':'local-service','operation':'enroll_authority',
                   'payload_hash':hashlib.sha256(canonical(['local-service','enroll_authority',self.payload]).encode()).hexdigest(),
                   'state':'committed','result':data,'at':intent['authorization']['issued_at'],'owner_generation':0}
        conn.execute('INSERT INTO receipts VALUES(?,?,?,?,?)', (op,'local-service','enroll_authority',receipt['payload_hash'],canonical(receipt)))
        conn.execute('INSERT INTO events(request_id,data) VALUES(?,?)', (op,canonical(receipt)))

    def _expected(self, intent):
        conn = sqlite3.connect(':memory:')
        try:
            self._seed(conn,intent)
            return digest_state(conn)
        finally: conn.close()

    def _database(self, directory, intent):
        directory = private_directory(directory)
        db = directory/'state.sqlite'
        read_file(db, 1024*1024)
        conn = sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,isolation_level=None)
        try:
            if conn.execute('PRAGMA integrity_check').fetchall() != [('ok',)] or digest_state(conn) != self._expected(intent):
                raise AuthorityError('enrollment_partial_manual_quarantine')
            return self.guard.verify(conn,recover=True)
        except sqlite3.Error as exc: raise AuthorityError('enrollment_partial_manual_quarantine') from exc
        finally: conn.close()

    def enroll(self, actor, permit, *, disposable=False):
        if not disposable or actor.scope != 'local-service' or self.permits is None:
            raise AuthorityError('enrollment_explicit_offline_authorization_required')
        with self._lock():
            if self._phases(): raise AuthorityError('enrollment_exists_reconcile')
            self._validate_interval(self.reservation,fresh=True)
            if self.destination.exists() or self.destination.is_symlink() or self.stage.exists() or self.stage.is_symlink():
                raise AuthorityError('enrollment_destination_not_exclusive')
            head,pending,_ = self.guard.history()
            if head != EMPTY_HEAD or pending: raise AuthorityError('enrollment_prior_history_present')
            auth = self.permits.verify(permit,actor,self.reservation['enrollment_id'],'enroll_authority',self.payload)
            if auth['checkpoint'] != EMPTY_HEAD: raise AuthorityError('enrollment_initial_anchor_mismatch')
            intent = dict(format='jarvis-enrollment-intent-v1',reservation=self.reservation,authorization=auth,
                          permit_sha256=fingerprint(permit),execution_enabled=False)
            publish_file(self.custody/'INTENT.json',encode(self.guard.signed(intent)))
            self._fault('enrollment_intent_durable')
            return self._continue()

    def reconcile(self):
        with self._lock(): return self._continue()

    def _continue(self):
        g = self.guard; phases = self._phases()
        if not phases: raise AuthorityError('enrollment_unenrolled')
        if 'FINAL' in phases: return self.verify()
        intent, ih = phases['INTENT']
        if 'PREPARED' not in phases:
            if self.destination.exists() or self.destination.is_symlink(): raise AuthorityError('enrollment_target_conflict')
            if not self.stage.exists():
                self.stage.mkdir(mode=0o700); sync_directory(self.stage.parent)
                self._fault('enrollment_stage_created')
            private_directory(self.stage)
            inventory = {p.name for p in self.stage.iterdir()}
            if not inventory:
                if os.statvfs(self.stage).f_bavail*os.statvfs(self.stage).f_frsize < 1024*1024: raise AuthorityError('enrollment_storage_exhausted')
                db = self.stage/'state.sqlite'
                fd = os.open(db,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600); os.close(fd)
                self._fault('enrollment_database_created')
                conn = sqlite3.connect(db,isolation_level=None)
                try:
                    conn.execute('PRAGMA synchronous=FULL');conn.execute('PRAGMA journal_mode=DELETE')
                    conn.execute('BEGIN IMMEDIATE');self._seed(conn,intent)
                    self._fault('enrollment_before_database_commit')
                    conn.execute('COMMIT');self._fault('enrollment_database_committed')
                finally: conn.close()
                sync_directory(self.stage)
            elif inventory != {'state.sqlite'}: raise AuthorityError('enrollment_partial_manual_quarantine')
            db = self.stage/'state.sqlite'
            # Exact deterministic committed SQL can finish genesis publication.
            # Any other partial database remains evidence for manual quarantine.
            raw = read_file(db,1024*1024)
            conn = sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,isolation_level=None)
            try:
                try: exact = conn.execute('PRAGMA integrity_check').fetchall()==[('ok',)] and digest_state(conn)==self._expected(intent)
                except sqlite3.Error: exact = False
                if not exact: raise AuthorityError('enrollment_partial_manual_quarantine')
                head,pending,_ = g.history()
                if head == EMPTY_HEAD and not pending:
                    g._head = head
                    checkpoint = g.prepare(conn);self._fault('enrollment_genesis_intent_durable')
                    g.finish(checkpoint);self._fault('enrollment_genesis_published')
                integrity = g.verify(conn,recover=True)
                if integrity['sequence'] != 1: raise AuthorityError('enrollment_prior_history_present')
            finally: conn.close()
            fd=os.open(db,os.O_RDONLY|os.O_NOFOLLOW)
            try:os.fsync(fd)
            finally:os.close(fd)
            prepared = dict(format='jarvis-enrollment-prepared-v1',enrollment_id=self.reservation['enrollment_id'],
                            store_id=g.store_id,intent_sha256=ih,genesis={k:integrity[k] for k in EMPTY_HEAD},
                            logical_state=self._expected(intent),database_sha256=hashlib.sha256(raw).hexdigest(),execution_enabled=False)
            publish_file(self.custody/'PREPARED.json',encode(g.signed(prepared)))
            self._fault('enrollment_prepared_durable')
        else: prepared = phases['PREPARED'][0]
        marker = encode(g.signed(prepared))
        if self.stage.exists() and self.destination.exists(): raise AuthorityError('enrollment_target_conflict')
        if not self.destination.exists():
            inventory = {p.name for p in private_directory(self.stage).iterdir()}
            if inventory not in ({'state.sqlite'},{'state.sqlite','ENROLLMENT.json'}): raise AuthorityError('enrollment_partial_manual_quarantine')
            if hashlib.sha256(read_file(self.stage/'state.sqlite',1024*1024)).hexdigest() != prepared['database_sha256']: raise AuthorityError('enrollment_database_substituted')
            self._database(self.stage,intent)
            if (self.stage/'ENROLLMENT.json').exists():
                if read_file(self.stage/'ENROLLMENT.json') != marker: raise AuthorityError('enrollment_marker_mismatch')
            else: publish_file(self.stage/'ENROLLMENT.json',marker)
            sync_directory(self.stage);g._writable();self._fault('enrollment_before_publication')
            _rename_directory(self.stage,self.destination);self._fault('enrollment_target_published')
        if read_file(self.destination/'ENROLLMENT.json') != marker or hashlib.sha256(read_file(self.destination/'state.sqlite',1024*1024)).hexdigest() != prepared['database_sha256']:
            raise AuthorityError('enrollment_database_substituted')
        self._database(self.destination,intent)
        publish_file(self.custody/'FINAL.json',encode(g.signed(self._final_body(prepared,fingerprint(g.signed(prepared))))))
        self._fault('enrollment_final_durable')
        return self.verify()

    def _final_body(self, prepared, ph):
        return dict(format='jarvis-enrollment-final-v1',enrollment_id=self.reservation['enrollment_id'],store_id=self.guard.store_id,
                    destination=str(self.destination),prepared_sha256=ph,genesis=prepared['genesis'],
                    reservation_sha256=fingerprint(self.reservation),execution_enabled=False,state='VERIFIED')

    def verify(self):
        phases = self._phases()
        if 'FINAL' not in phases: raise AuthorityError('enrollment_reconciliation_required')
        final, fh = phases['FINAL']; prepared = phases['PREPARED'][0]
        witness = dict(format='jarvis-enrollment-witness-v1',enrollment_id=self.reservation['enrollment_id'],store_id=self.guard.store_id,
                       custody=str(self.custody),destination=str(self.destination),key_id=self.guard.key_id,final_sha256=fh,
                       genesis=prepared['genesis'],reservation_sha256=fingerprint(self.reservation),policy=policy(self.guard))
        if not (self.destination/'state.sqlite').is_file(): raise AuthorityError('enrollment_missing_database_no_recreate')
        conn = sqlite3.connect((self.destination/'state.sqlite').as_uri()+'?mode=ro',uri=True,isolation_level=None)
        try:
            self.guard.verify(conn)
            verify_authority_enrollment(conn,self.destination/'state.sqlite',self.guard,witness)
        finally: conn.close()
        return {'state':'VERIFIED','enrollment_id':self.reservation['enrollment_id'],'witness':witness,
                'receipt':final,'execution_enabled':False,'externally_custodied_witness_required':True}

    def status(self):
        phases = self._phases()
        if not phases:
            return {'state':'UNENROLLED','verified':False,'execution_enabled':False,
                    'recommendation':'external_new_store_reservation_and_authenticated_enrollment_required'}
        if 'FINAL' in phases: return self.verify()
        return {'state':'RECONCILIATION_REQUIRED' if 'PREPARED' in phases else 'INCOMPLETE',
                'verified':False,'phases':sorted(phases),'execution_enabled':False,
                'recommendation':'preserve_all_artifacts_explicit_offline_reconciliation_only'}


def verify_authority_enrollment(conn, path, guard, witness):
    """Called before ordinary owner takeover; never generates replacement trust."""
    rows = conn.execute("SELECT id,data FROM records WHERE kind='authority_enrollment'").fetchall()
    marker = Path(path).parent/'ENROLLMENT.json'
    if not rows:
        if witness is not None or marker.exists() or marker.is_symlink(): raise AuthorityError('enrollment_identity_missing')
        return {'state':'LEGACY_UNENROLLED','verified':False}
    if len(rows) != 1 or guard is None or type(witness) is not dict:
        raise AuthorityError('enrollment_external_witness_required')
    custody = private_directory(witness.get('custody',''))
    intent, _ = guard._read(custody/'INTENT.json')
    enrollment = OfflineEnrollment(guard,custody,intent.get('reservation'))
    phases = enrollment._phases()
    if 'FINAL' not in phases: raise AuthorityError('enrollment_reconciliation_required')
    final, fh = phases['FINAL']; prepared = phases['PREPARED'][0]
    expected = dict(format='jarvis-enrollment-witness-v1',enrollment_id=enrollment.reservation['enrollment_id'],store_id=guard.store_id,
                    custody=str(custody),destination=str(Path(path).parent),key_id=guard.key_id,final_sha256=fh,
                    genesis=prepared['genesis'],reservation_sha256=fingerprint(enrollment.reservation),policy=policy(guard))
    if witness != expected or enrollment.destination != Path(path).parent or rows[0][0] != witness['enrollment_id']:
        raise AuthorityError('enrollment_witness_mismatch')
    if guard.authenticate(strict_json(read_file(marker))) != prepared:
        raise AuthorityError('enrollment_marker_mismatch')
    if guard.history()[1] is not None: raise AuthorityError('enrollment_reconciliation_required')
    return {'state':'VERIFIED','verified':True,'enrollment_id':witness['enrollment_id'],'genesis':prepared['genesis']}

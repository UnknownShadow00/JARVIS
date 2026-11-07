"""Opt-in local ledger integrity, external checkpoints and bounded archive export.

The checkpoint directory/key are trusted inputs, outside export/cleanup authority.
HMAC authenticates checkpoints; it is not a public-key signature. A malicious
same-UID process, key compromise, or rollback of BOTH trusted anchors and SQLite
is outside this local contract. No history deletion or real-store enrollment.
"""
from __future__ import annotations

import fcntl
import ctypes
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import uuid
from collections import OrderedDict
from app.agent.checkpoint_epochs import CheckpointEpochs
from app.agent.audit_attestations import AuditAttestations
import copy
import threading
import math
from app.agent.checkpoint_epochs import guard_locked

from app.agent.authority import AuthorityError, canonical, identifier

TABLES = ('meta', 'ownership', 'control', 'records', 'receipts', 'events', 'outbox', 'simulation_effects', 'sqlite_sequence')
MAX_BYTES = 32 * 1024 * 1024
MAX_ROWS = 100000
MAX_EXPORTS = 16
MAX_EXPORT_BYTES = 64 * 1024 * 1024
ZERO = '0' * 64


def encode(value):
    return (canonical(value) + '\n').encode('ascii')


def strict_json(raw):
    def pairs(values):
        result = {}
        for k, v in values:
            if k in result:
                raise ValueError('duplicate key')
            result[k] = v
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise AuthorityError('ledger_invalid_json') from exc


def private_directory(path, *, create=False):
    path = Path(path).absolute()
    if '..' in path.parts:
        raise AuthorityError('unsafe_ledger_path')
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise AuthorityError('unsafe_ledger_path')
    from app.agent.storage_paths import StorageAncestry
    StorageAncestry(path, create=create)
    st = path.stat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise AuthorityError('unsafe_ledger_directory')
    return path


def read_file(path, limit=65536):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            st = os.fstat(stream.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != os.getuid() or st.st_mode & 0o077 or st.st_size > limit:
                raise AuthorityError('unsafe_ledger_file')
            raw = stream.read(limit+1)
            if len(raw) > limit:
                raise AuthorityError('ledger_bound_exceeded')
            return raw
    except OSError as exc:
        raise AuthorityError('ledger_file_unavailable') from exc


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_file(path, raw):
    """No overwrite. Partial staging is never considered a completed record."""
    temporary = path.with_name('.stage-' + str(uuid.uuid4()))
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # Linux no-replace atomic rename: a crash cannot publish a two-link file.
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, 'renameat2', None)
        if rename is None:
            raise AuthorityError('atomic_publication_unavailable')
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(temporary), -100, os.fsencode(path), 1) != 0:
            errno = ctypes.get_errno()
            raise OSError(errno, 'no-replace publication failed')
        sync_directory(path.parent)
    finally:
        # Only this invocation's temporary file, never a checkpoint/history row.
        temporary.unlink(missing_ok=True)


def state_lines(conn):
    schema = [tuple(r) for r in conn.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name")]
    yield encode({'type':'schema', 'value':schema})
    for table in TABLES:  # identifiers are fixed, never caller-supplied SQL
        for row in conn.execute(f'SELECT rowid,* FROM {table} ORDER BY rowid'):
            yield encode({'type':'row','table':table,'value':list(row)})


def digest_state(conn):
    digest, size, rows = hashlib.sha256(), 0, 0
    for line in state_lines(conn):
        size += len(line); rows += 1
        if size > MAX_BYTES or rows > MAX_ROWS:
            raise AuthorityError('ledger_bound_exceeded')
        digest.update(line)
    return {'sha256':digest.hexdigest(), 'bytes':size, 'rows':rows}


class LedgerGuard(CheckpointEpochs, AuditAttestations):
    """Append-only signed intent/final journal, protected separately from SQLite.

    Key provisioning is external. Tests supply explicit synthetic bytes only.
    The lifetime lock also prevents sharing one journal between two owners.
    """
    def __init__(self, directory, key, store_id, *, initialize=False, fault_hook=None, rollover=False, epoch_capacity=9999, max_epochs=16, recovery=False, trust_context=None, cache_verified=True):
        identifier(store_id)
        if type(key) is not bytes or len(key) < 32:
            raise AuthorityError('invalid_ledger_key')
        self.directory = Path(directory).absolute()
        self.store_id, self._key, self.initialize = store_id, key, initialize is True
        self._fault = fault_hook or (lambda stage: None)
        self._fd = None
        self._head = None
        self._pid = os.getpid()
        self._readonly = False
        self._operation_mutex = threading.RLock()
        self._verified_cache = OrderedDict()
        self.cache_verified = cache_verified is True
        self.cache_hits = self.cache_misses = 0
        self._configure_epochs(rollover=rollover, epoch_capacity=epoch_capacity, max_epochs=max_epochs, recovery=recovery, trust_context=trust_context)
        self.directory = private_directory(self.directory, create=initialize)
        from app.agent.storage_paths import StorageAncestry
        self._ancestry = StorageAncestry(self.directory)

    def acquire(self, db_path, *, readonly=False):
        if self._fd is not None:raise AuthorityError('checkpoint_owner_busy')
        db_path = Path(db_path).absolute()
        if '..' in db_path.parts:
            raise AuthorityError('unsafe_ledger_path')
        if self.directory == db_path.parent or self.directory.is_relative_to(db_path.parent) or db_path.parent.is_relative_to(self.directory):
            raise AuthorityError('checkpoint_not_separate')
        flags=(os.O_RDONLY if readonly else os.O_RDWR|(os.O_CREAT if self.initialize else 0))|os.O_NOFOLLOW|os.O_NONBLOCK
        self._readonly = readonly is True
        fd = os.open(self.directory/'journal.lock',flags,0o600)
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077 or st.st_nlink != 1:
                raise AuthorityError('unsafe_ledger_file')
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except AuthorityError:
            os.close(fd)
            raise
        except BlockingIOError as exc:
            os.close(fd)
            raise AuthorityError('checkpoint_owner_busy') from exc
        except OSError as exc:
            os.close(fd)
            raise AuthorityError('checkpoint_lock_unavailable') from exc
        self._fd = fd
        self._identity = st.st_dev, st.st_ino

    def close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None

    def _writable(self):
        self._fence()
        if self._readonly:raise AuthorityError('checkpoint_read_only')

    def _fence(self):
        self._check_trust_time()
        if self._fd is None or os.getpid() != self._pid:
            raise AuthorityError('checkpoint_owner_unavailable')
        try:
            st = (self.directory/'journal.lock').stat(follow_symlinks=False)
        except OSError as exc:
            raise AuthorityError('checkpoint_missing') from exc
        if (st.st_dev,st.st_ino) != self._identity:
            raise AuthorityError('checkpoint_replaced')
        self._ancestry.verify()
        private_directory(self.directory)

    def signed(self, body):
        return {'body':body, 'hmac_sha256':hmac.new(self._key,encode(body),hashlib.sha256).hexdigest()}

    def authenticate(self, envelope):
        if type(envelope) is not dict or set(envelope) != {'body','hmac_sha256'}:
            raise AuthorityError('checkpoint_invalid')
        signature = self.signed(envelope['body'])['hmac_sha256']
        if type(envelope['hmac_sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',envelope['hmac_sha256']) or not hmac.compare_digest(signature,envelope['hmac_sha256']):
            raise AuthorityError('checkpoint_authentication_failed')
        return envelope['body']

    def _read(self, path):
        raw=read_file(path)
        digest=hashlib.sha256(raw).hexdigest()
        if self.cache_verified and digest in self._verified_cache:
            self.cache_hits+=1
            self._verified_cache.move_to_end(digest)
            return copy.deepcopy(self._verified_cache[digest])
        self.cache_misses+=1
        envelope=strict_json(raw)
        result=self.authenticate(envelope),hashlib.sha256(encode(envelope)).hexdigest()
        if self.cache_verified:
            self._verified_cache[digest]=copy.deepcopy(result)
            if len(self._verified_cache)>2048:self._verified_cache.popitem(last=False)
        return result

    def _history_group(self, directory, head):
        staging = [p for p in directory.iterdir() if p.name.startswith('.stage-')]
        if len(staging)>32:
            raise AuthorityError('checkpoint_staging_capacity')
        for path in staging:
            read_file(path)
        self.staging_files = len(staging)
        names = sorted(p.name for p in directory.iterdir() if not p.name.startswith('.stage-') and p.name != 'journal.lock' and not (directory!=self.directory and p.name=='LINK.json') and not (directory==self.directory and self._auxiliary(p.name)))
        if len(names)>20000 or any(not re.fullmatch(r'\d{8}\.(intent|final)\.json',n) for n in names):
            raise AuthorityError('checkpoint_invalid_inventory')
        result,pending=[],None
        start=head['sequence']+1
        for seq in range(start,start+len(names)//2+1):
            intent_path=directory/f'{seq:08}.intent.json'
            final_path=directory/f'{seq:08}.final.json'
            if not intent_path.exists():
                break
            intent, intent_hash=self._read(intent_path)
            if type(intent) is not dict or set(intent)!={'format','store_id','sequence','previous','before_sha256','after','last_event'} or intent['format']!='jarvis-checkpoint-intent-v1' or intent['store_id']!=self.store_id or type(intent['sequence']) is not int or intent['sequence']!=seq or intent['previous']!=head['checkpoint_hash'] or intent['before_sha256']!=head['sha256']:
                raise AuthorityError('checkpoint_continuity_failed')
            after = intent['after']
            if type(after) is not dict or set(after)!={'sha256','bytes','rows'} or type(after['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',after['sha256']) or type(after['bytes']) is not int or not 0<after['bytes']<=MAX_BYTES or type(after['rows']) is not int or not 0<after['rows']<=MAX_ROWS:
                raise AuthorityError('checkpoint_invalid')
            event = intent['last_event']
            if event is not None:
                if type(event) is not dict or set(event)!={'sequence','request_id'} or type(event['sequence']) is not int or event['sequence']<1:
                    raise AuthorityError('checkpoint_invalid_event_binding')
                identifier(event['request_id'])
            if not final_path.exists():
                pending=intent
                break
            final, final_hash=self._read(final_path)
            if type(final) is not dict or set(final)!={'format','store_id','sequence','previous','intent_hash','outcome','sha256'} or final['format']!='jarvis-checkpoint-final-v1' or final['store_id']!=self.store_id or type(final['sequence']) is not int or final['sequence']!=seq or final['previous']!=head['checkpoint_hash'] or final['intent_hash']!=intent_hash or final['outcome'] not in {'committed','aborted'} or final['sha256']!=(intent['after']['sha256'] if final['outcome']=='committed' else head['sha256']):
                raise AuthorityError('checkpoint_continuity_failed')
            head={'sequence':seq,'sha256':final['sha256'],'checkpoint_hash':final_hash}
            result.append(head)
        if len(names)!=len(result)*2+(1 if pending else 0):
            raise AuthorityError('checkpoint_gap')
        return head,pending,result

    @guard_locked
    def verify(self, conn, *, recover=False, new=False):
        head,pending,_=self.history(recover_rollover=recover)
        actual=digest_state(conn)
        if pending:
            if not recover:
                raise AuthorityError('checkpoint_reconciliation_required')
            if actual['sha256']==pending['after']['sha256']:
                self._final(pending,'committed')
            elif head['sha256'] is not None and actual['sha256']==head['sha256']:
                self._final(pending,'aborted')
            else:
                raise AuthorityError('ledger_checkpoint_mismatch')
            head,_,_=self.history()
        if head['sha256'] is None:
            if not (new and self.initialize):
                raise AuthorityError('checkpoint_missing')
            # Anchor the empty schema before the first metadata/ownership write.
            # Even the very first failed transaction now has an authenticated
            # prior state and can be resolved after a process crash.
            self._head = head
            intent = self.prepare(conn)
            self.finish(intent)
            head,_,_=self.history()
        elif actual['sha256']!=head['sha256']:
            raise AuthorityError('ledger_checkpoint_mismatch')
        self.verify_export_markers(conn)
        self._head=head
        return {**head,'verified':head['sha256'] is not None,'algorithm':'HMAC-SHA256 external full-state checkpoints',
                'state_bytes':actual['bytes'],'state_rows':actual['rows'],'max_bytes':MAX_BYTES,'max_rows':MAX_ROWS,
                'checkpoint_capacity':self.epoch_capacity,'staging_files':self.staging_files,'epoch':self._epoch,
                'max_epochs':self.max_epochs,'rollover_hash':self._rollover_hash,'recovery_enabled':self.recovery_enabled,
                'external_reference_configured':self.trust_context is not None}

    @guard_locked
    def prepare(self, conn):
        head,pending,_=self.history()
        if pending or self._head is None or head!=self._head:
            raise AuthorityError('checkpoint_reconciliation_required')
        self._writable()
        if head['sequence']-self._epoch_start+1>=self.epoch_capacity:
            if not self.rollover_enabled:raise AuthorityError('checkpoint_capacity_exceeded')
            self.rollover()
            head,pending,_=self.history()
        event = conn.execute('SELECT seq,request_id FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        intent=dict(format='jarvis-checkpoint-intent-v1',store_id=self.store_id,sequence=head['sequence']+1,
                    previous=head['checkpoint_hash'],before_sha256=head['sha256'],after=digest_state(conn),
                    last_event={'sequence':event[0],'request_id':event[1]} if event else None)
        publish_file(self._epoch_directories[-1]/f"{intent['sequence']:08}.intent.json",encode(self.signed(intent)))
        self._fault('checkpoint_intent_durable')
        return intent

    def _final(self, intent, outcome):
        self._writable()
        envelope=self.signed(intent)
        body=dict(format='jarvis-checkpoint-final-v1',store_id=self.store_id,sequence=intent['sequence'],
                  previous=intent['previous'],intent_hash=hashlib.sha256(encode(envelope)).hexdigest(),outcome=outcome,
                  sha256=intent['after']['sha256'] if outcome=='committed' else intent['before_sha256'])
        publish_file(self._checkpoint_directory(intent['sequence'])/f"{intent['sequence']:08}.final.json",encode(self.signed(body)))

    @guard_locked
    def finish(self, intent):
        self._fault('checkpoint_before_publication')
        self._final(intent,'committed')
        self._head=self.history()[0]
        self._fault('checkpoint_published')

    def export(self, authority, actor, export_id, directory, *, fault_hook=None):
        """Immutable bounded snapshot; no prune, delete, restore or enrollment."""
        identifier(export_id)
        fault=fault_hook or (lambda stage:None)
        a=authority
        parent=private_directory(directory)
        if parent==self.directory or parent.is_relative_to(self.directory) or self.directory.is_relative_to(parent) or parent==a.path.parent or parent.is_relative_to(a.path.parent) or a.path.parent.is_relative_to(parent):
            raise AuthorityError('unsafe_export_destination')
        dest=parent/export_id
        with a._mutex:
            a._fence()
            if a._ledger is not self:
                raise AuthorityError('ledger_not_bound')
            checkpoint=self.verify(a._conn)
            if a._scope(actor)!='local-service':
                raise AuthorityError('operator_scope_required')
            # No cleanup is performed. Incomplete directories count against
            # capacity too; only an independently scoped operator may remove any.
            exports=0;used=0
            for entry in parent.iterdir():
                exports+=1
                if exports>=MAX_EXPORTS:raise AuthorityError('export_capacity_exceeded')
                identifier(entry.name)
                private_directory(entry)
                members=0
                for member in entry.iterdir():
                    members+=1
                    st=member.stat(follow_symlinks=False)
                    if members>8 or not stat.S_ISREG(st.st_mode) or member.is_symlink():raise AuthorityError('unsafe_export_inventory')
                    used+=st.st_size
            if used+checkpoint['state_bytes']+65536>MAX_EXPORT_BYTES:
                raise AuthorityError('export_capacity_exceeded')
            space=os.statvfs(parent)
            if space.f_bavail*space.f_frsize<checkpoint['state_bytes']+65536:
                raise AuthorityError('export_storage_exhausted')
            # A whole-store export is a trusted-local operator action. Public API
            # never accepts paths, keys, export targets or mutation commands.
            try:dest.mkdir(mode=0o700)
            except FileExistsError as exc:raise AuthorityError('export_already_exists') from exc
            fd=os.open(dest/'state.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            digest,size,rows=hashlib.sha256(),0,0
            with os.fdopen(fd,'wb') as stream:
                for line in state_lines(a._conn):
                    size+=len(line);rows+=1
                    if size>MAX_BYTES or rows>MAX_ROWS:raise AuthorityError('ledger_bound_exceeded')
                    stream.write(line);digest.update(line)
                    fault('export_row_written')
                stream.flush();os.fsync(stream.fileno())
            fault('export_data_durable')
            if digest.hexdigest()!=checkpoint['sha256']:
                raise AuthorityError('export_snapshot_changed')
            body=dict(format='jarvis-ledger-export-v1',store_id=self.store_id,export_id=export_id,
                      checkpoint={k:checkpoint[k] for k in ('sequence','sha256','checkpoint_hash')},
                      files={'state.jsonl':dict(sha256=digest.hexdigest(),bytes=size,rows=rows)},history_deleted=False,
                      events=dict(zip(('first','last','count'),a._conn.execute('SELECT MIN(seq),MAX(seq),COUNT(*) FROM events').fetchone())))
            if self.recovery_enabled:
                body['format']='jarvis-ledger-export-v2'
                body['lineage']=self.checkpoint_lineage(checkpoint['sequence'])
            publish_file(dest/'COMPLETE.json',encode(self.signed(body)))
            sync_directory(parent)
            fault('export_manifest_durable')
            return self.verify_export(dest)

    def verify_export(self, directory):
        directory=private_directory(directory)
        identifier(directory.name)
        if set(p.name for p in directory.iterdir())!={'state.jsonl','COMPLETE.json'}:
            raise AuthorityError('export_incomplete')
        manifest=self.authenticate(strict_json(read_file(directory/'COMPLETE.json')))
        if type(manifest) is not dict or set(manifest)!=({'format','store_id','export_id','checkpoint','files','history_deleted','events','lineage'} if manifest.get('format')=='jarvis-ledger-export-v2' else {'format','store_id','export_id','checkpoint','files','history_deleted','events'}) or manifest['format'] not in {'jarvis-ledger-export-v1','jarvis-ledger-export-v2'} or manifest['store_id']!=self.store_id or manifest['export_id']!=directory.name or manifest['history_deleted'] is not False or type(manifest['files']) is not dict or set(manifest['files'])!={'state.jsonl'} or type(manifest['checkpoint']) is not dict:
            raise AuthorityError('export_invalid_manifest')
        _,pending,history=self.history()
        if pending or manifest['checkpoint'] not in history:
            raise AuthorityError('export_checkpoint_not_trusted')
        if manifest['format']=='jarvis-ledger-export-v2' and manifest['lineage']!=self.checkpoint_lineage(manifest['checkpoint']['sequence']):
            raise AuthorityError('export_generation_mismatch')
        raw=read_file(directory/'state.jsonl',MAX_BYTES)
        info=manifest['files']['state.jsonl']
        if type(info) is not dict or info!={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'rows':len(raw.splitlines())} or info['sha256']!=manifest['checkpoint']['sha256'] or info['rows']>MAX_ROWS:
            raise AuthorityError('export_integrity_failed')
        # Parse every record; signed manifests do not make malformed data valid.
        lines=raw.splitlines()
        task_bindings={};event_sequences=[];last_table=-1;last_rowid=0
        columns={'meta':2,'ownership':4,'control':4,'records':5,'receipts':6,'events':4,'outbox':5,'simulation_effects':3,'sqlite_sequence':3}
        for index,line in enumerate(lines):
            value=strict_json(line)
            if type(value) is not dict:raise AuthorityError('export_invalid_data')
            if index==0:
                if set(value)!={'type','value'} or value['type']!='schema':raise AuthorityError('export_invalid_data')
            elif set(value)!={'type','table','value'} or value['type']!='row' or value['table'] not in TABLES or type(value['value']) is not list:
                raise AuthorityError('export_invalid_data')
            else:
                table=value['table'];row=value['value'];order=TABLES.index(table)
                if order<last_table or len(row)!=columns[table] or type(row[0]) is not int or row[0]<1 or order==last_table and row[0]<=last_rowid:raise AuthorityError('export_row_order_invalid')
                for field in row:
                    if type(field) not in (str,int,float,type(None)) or type(field) is int and not -(2**63)<=field<2**63 or type(field) is float and not math.isfinite(field):
                        raise AuthorityError('export_invalid_data')
                    if type(field) is str:
                        try:field.encode('utf-8')
                        except UnicodeError as exc:raise AuthorityError('export_invalid_data') from exc
                if order!=last_table:last_rowid=0
                last_table,last_rowid=order,row[0]
                if table=='records' and row[1]=='task':
                    task_bindings[row[2]]=hashlib.sha256(encode(strict_json(row[4]))).hexdigest()
                if table=='events':event_sequences.append(row[1])
        actual_events={'first':event_sequences[0] if event_sequences else None,'last':event_sequences[-1] if event_sequences else None,'count':len(event_sequences)}
        if manifest['events']!=actual_events or event_sequences!=list(range(1,len(event_sequences)+1)):raise AuthorityError('export_event_order_invalid')
        return {**manifest,'verified':True,'task_bindings':task_bindings,'manifest_sha256':hashlib.sha256(read_file(directory/'COMPLETE.json')).hexdigest()}

"""Verified offline reconstruction into exclusive, disabled disposable artifacts.

No archive SQL is executed. The source DB, original request IDs and protected
checkpoint history are never modified. Restored snapshots are not live Authority
branches; they require separate explicit anchoring before any runtime use.
"""
from __future__ import annotations
from datetime import UTC,datetime
import ctypes
import hashlib
import os
from pathlib import Path
import sqlite3
import uuid
from functools import wraps

from app.agent.authority import AuthorityError,canonical,identifier
from app.agent.ledger import (MAX_BYTES,MAX_ROWS,TABLES,encode,private_directory,read_file,
                             publish_file,strict_json,sync_directory,digest_state)
from app.agent.ledger_schema import SCHEMA_SQL
from app.agent.recovery import analyze

MAX_RESTORES=4
MAX_RESTORE_BYTES=64*1024*1024


def serialized(method):
    @wraps(method)
    def run(self,*args,**kwargs):
        with self.guard._operation_mutex:return method(self,*args,**kwargs)
    return run


def _file_sha(path):
    raw=read_file(path,MAX_RESTORE_BYTES)
    return hashlib.sha256(raw).hexdigest()


def _rename_directory(source,target):
    libc=ctypes.CDLL(None,use_errno=True)
    rename=getattr(libc,'renameat2',None)
    if rename is None:raise AuthorityError('atomic_publication_unavailable')
    rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    rename.restype=ctypes.c_int
    if rename(-100,os.fsencode(source),-100,os.fsencode(target),1)!=0:
        raise OSError(ctypes.get_errno(),'restore no-replace publication failed')
    sync_directory(target.parent)


def _schema():
    conn=sqlite3.connect(':memory:')
    try:
        conn.executescript(SCHEMA_SQL)
        return [list(row) for row in conn.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name")]
    finally:conn.close()


def _inspect_snapshot(conn,expected,store_id):
    if conn.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise AuthorityError('restore_sqlite_corrupt')
    actual=digest_state(conn)
    if actual['sha256']!=expected['checkpoint']['sha256'] or actual!=expected['files']['state.jsonl']:
        raise AuthorityError('restore_logical_digest_mismatch')
    markers=conn.execute("SELECT id,scope,data FROM records WHERE kind='ledger_config'").fetchall()
    if len(markers)!=1 or tuple(markers[0])!=(store_id,'__authority__',canonical({'store_id':store_id,'checkpoint_required':True,'format':1})):
        raise AuthorityError('restore_store_identity_mismatch')
    conn.row_factory=sqlite3.Row
    values={table:[dict(row) for row in conn.execute(f'SELECT * FROM {table} ORDER BY rowid')] for table in ('meta','ownership','control','records','receipts','events','outbox','simulation_effects')}
    report=analyze(values,'local-service')
    if not report['consistent']:raise AuthorityError('restore_semantic_inconsistency')
    conn.row_factory=None
    return {'consistent':True,'logical_state':actual,'unknown':report['unknown'],'unresolved':report['unresolved'],
            'cancel_requested':report['cancel_requested'],'failed':report['failed'],'task_count':len(report['tasks']),
            'execution_enabled':False,'runtime_activation_allowed':False}


class ArchiveRestorer:
    def __init__(self,guard,permits=None,*,fault_hook=None):
        if not guard.recovery_enabled:raise AuthorityError('archive_restore_disabled')
        self.guard,self.permits=guard,permits
        self._fault=fault_hook or (lambda stage:None)

    @serialized
    def verify_archive(self,directory,expected_manifest_sha256):
        g=self.guard
        if g.trust_context is None:raise AuthorityError('restore_external_trust_reference_required')
        if not g._hash(expected_manifest_sha256):raise AuthorityError('invalid_expected_manifest_hash')
        verified=g.verify_export(directory)
        if verified['manifest_sha256']!=expected_manifest_sha256:raise AuthorityError('archive_expected_manifest_mismatch')
        proof=g.verify_export_attestation(verified)
        raw=read_file(Path(directory)/'state.jsonl',MAX_BYTES)
        lines=raw.splitlines()
        if not lines or strict_json(lines[0])!={'type':'schema','value':_schema()}:
            raise AuthorityError('restore_incompatible_schema')
        return {**verified,'completion_attestation':proof,'schema_compatible':True,'semantic_restore_verified':False,'execution_enabled':False}

    def _paths(self,restore_id):
        g=self.guard;identifier(restore_id)
        return tuple(g.directory/f'restore-{restore_id}.{phase}.json' for phase in ('intent','prepared','final'))

    def _target(self,parent,restore_id,archive,*,require_archive=True):
        parent=private_directory(parent);archive=private_directory(archive) if require_archive else Path(archive).absolute()
        if '..' in archive.parts:raise AuthorityError('unsafe_restore_destination')
        g=self.guard
        if any(parent==p or parent.is_relative_to(p) or p.is_relative_to(parent) for p in (g.directory,archive.parent)):
            raise AuthorityError('unsafe_restore_destination')
        return parent,parent/restore_id,parent/f'.restore-{restore_id}.pending'

    def _capacity(self,parent,expected_bytes):
        count=size=0
        for entry in parent.iterdir():
            count+=1
            if count>=MAX_RESTORES:raise AuthorityError('restore_capacity_exceeded')
            private_directory(entry)
            members=0
            for member in entry.iterdir():
                members+=1
                if members>8 or member.is_symlink() or not member.is_file():raise AuthorityError('unsafe_restore_inventory')
                size+=member.stat().st_size
        if size+expected_bytes*2+65536>MAX_RESTORE_BYTES:raise AuthorityError('restore_capacity_exceeded')
        space=os.statvfs(parent)
        if space.f_bavail*space.f_frsize<expected_bytes*2+65536:raise AuthorityError('restore_storage_exhausted')

    @serialized
    def restore(self,actor,restore_id,archive,parent,expected_manifest_sha256,permit,*,disposable=False):
        g=self.guard
        g._writable()
        if not disposable:raise AuthorityError('explicit_disposable_restore_required')
        identifier(restore_id)
        if uuid.UUID(restore_id).version!=4 or actor.scope!='local-service':raise AuthorityError('invalid_restore_identity')
        verified=self.verify_archive(archive,expected_manifest_sha256)
        parent,target,stage=self._target(parent,restore_id,archive)
        payload={'export_id':verified['export_id'],'manifest_sha256':expected_manifest_sha256,'target_parent':str(parent),'restore_id':restore_id}
        if self.permits is None:raise AuthorityError('operator_authentication_required')
        auth=self.permits.verify(permit,actor,restore_id,'restore_archive',payload)
        head,pending,_=g.history()
        if pending or auth['checkpoint']!=head:raise AuthorityError('stale_operator_permit')
        intent_path,prepared_path,final_path=self._paths(restore_id)
        if intent_path.exists() or target.exists() or stage.exists():raise AuthorityError('restore_already_exists_reconcile')
        if len(list(g.directory.glob('restore-*.intent.json')))>=64:raise AuthorityError('restore_capacity_exceeded')
        self._capacity(parent,verified['files']['state.jsonl']['bytes'])
        intent=dict(format='jarvis-restore-intent-v1',store_id=g.store_id,key_id=g.key_id,restore_id=restore_id,
                    archive=str(private_directory(archive)),target_parent=str(parent),manifest_sha256=expected_manifest_sha256,
                    source_checkpoint=verified['checkpoint'],source_lineage=g.checkpoint_lineage(verified['checkpoint']['sequence']),
                    source_attestation_sha256=verified['completion_attestation']['attestation_sha256'],
                    trusted_admission_head=head,authorization=auth,permit_sha256=hashlib.sha256(encode(permit)).hexdigest(),
                    admitted_at=datetime.now(UTC).isoformat(),execution_enabled=False)
        publish_file(intent_path,encode(g.signed(intent)))
        self._fault('restore_intent_durable')
        stage.mkdir(mode=0o700);sync_directory(parent)
        self._fault('restore_stage_created')
        db=stage/'state.sqlite'
        fd=os.open(db,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
        conn=sqlite3.connect(db,isolation_level=None)
        try:
            conn.execute('PRAGMA synchronous=FULL');conn.execute('PRAGMA journal_mode=DELETE')
            conn.execute('BEGIN IMMEDIATE')
            for statement in SCHEMA_SQL.split(';'):
                if statement.strip():conn.execute(statement)
            self._fault('restore_schema_created')
            # Verification reads captured bytes; no path extraction, SQL, pickle,
            # callbacks or table/column names are taken from the archive.
            raw=read_file(Path(archive)/'state.jsonl',MAX_BYTES)
            if hashlib.sha256(raw).hexdigest()!=verified['checkpoint']['sha256']:raise AuthorityError('archive_changed_during_restore')
            for line in raw.splitlines()[1:]:
                item=strict_json(line);table=item['table'];values=item['value']
                if table=='sqlite_sequence':
                    if len(values)!=3 or values[1]!='events' or type(values[2]) is not int or values[2]<0:raise AuthorityError('restore_invalid_sequence')
                    # SQLite creates this system row while inserting events.
                    # Reproduce its archived rowid/high-water mark exactly.
                    changed=conn.execute('UPDATE sqlite_sequence SET rowid=?,seq=? WHERE name=?',(values[0],values[2],values[1])).rowcount
                    if changed!=1:raise AuthorityError('restore_invalid_sequence')
                else:
                    if table not in TABLES:raise AuthorityError('restore_invalid_table')
                    conn.execute(f"INSERT INTO {table} (rowid,{','.join(r[1] for r in conn.execute('PRAGMA table_info('+table+')'))}) VALUES ({','.join('?' for _ in values)})",values)
                self._fault('restore_row_inserted')
            self._fault('restore_before_database_commit')
            conn.execute('COMMIT')
            self._fault('restore_database_committed')
            summary=_inspect_snapshot(conn,verified,g.store_id)
        except BaseException:
            if conn.in_transaction:conn.execute('ROLLBACK')
            raise
        finally:conn.close()
        fd=os.open(db,os.O_RDONLY|os.O_NOFOLLOW)
        try:os.fsync(fd)
        finally:os.close(fd)
        os.chmod(db,0o400)
        marker=dict(format='jarvis-disposable-restore-v1',restore_id=restore_id,source_store_id=g.store_id,execution_enabled=False,runtime_activation_allowed=False)
        publish_file(stage/'DISPOSABLE.json',encode(g.signed(marker)))
        receipt=dict(format='jarvis-restore-prepared-v1',store_id=g.store_id,key_id=g.key_id,restore_id=restore_id,
                     intent_sha256=hashlib.sha256(encode(g.signed(intent))).hexdigest(),manifest_sha256=expected_manifest_sha256,
                     source_checkpoint=verified['checkpoint'],source_lineage=intent['source_lineage'],source_attestation_sha256=intent['source_attestation_sha256'],
                     database_sha256=_file_sha(db),summary=summary,execution_enabled=False)
        publish_file(stage/'RESTORE.json',encode(g.signed(receipt)));sync_directory(stage)
        g._writable()
        publish_file(prepared_path,encode(g.signed(receipt)))
        self._fault('restore_prepared_durable')
        return self.reconcile(restore_id)

    def _validate_artifact(self,directory,receipt,verified):
        g=self.guard;directory=private_directory(directory)
        if set(p.name for p in directory.iterdir())!={'state.sqlite','RESTORE.json','DISPOSABLE.json'}:raise AuthorityError('restore_incomplete_artifact')
        body=g.authenticate(strict_json(read_file(directory/'RESTORE.json')))
        marker=g.authenticate(strict_json(read_file(directory/'DISPOSABLE.json')))
        if body!=receipt or marker!=dict(format='jarvis-disposable-restore-v1',restore_id=receipt['restore_id'],source_store_id=g.store_id,execution_enabled=False,runtime_activation_allowed=False):raise AuthorityError('restore_artifact_binding_mismatch')
        db=directory/'state.sqlite'
        if db.stat().st_mode&0o222 or _file_sha(db)!=receipt['database_sha256']:raise AuthorityError('restore_database_modified')
        conn=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
        try:summary=_inspect_snapshot(conn,verified,g.store_id)
        finally:conn.close()
        if summary!=receipt['summary']:raise AuthorityError('restore_summary_mismatch')
        return summary

    @serialized
    def reconcile(self,restore_id):
        """Complete only an authenticated, already prepared target. Never rebuild."""
        g=self.guard;g._writable();identifier(restore_id)
        intent_path,prepared_path,final_path=self._paths(restore_id)
        intent,intent_hash=g._read(intent_path)
        if intent.get('restore_id')!=restore_id or intent.get('store_id')!=g.store_id or intent.get('execution_enabled') is not False:raise AuthorityError('restore_intent_invalid')
        parent,target,stage=self._target(intent['target_parent'],restore_id,intent['archive'],require_archive=False)
        if not prepared_path.exists():raise AuthorityError('restore_incomplete_manual_quarantine')
        receipt,receipt_hash=g._read(prepared_path)
        verified=self._prepared_source(intent,receipt)
        if receipt.get('intent_sha256')!=intent_hash or receipt.get('restore_id')!=restore_id or receipt.get('source_checkpoint')!=verified['checkpoint'] or receipt.get('source_attestation_sha256')!=verified['completion_attestation']['attestation_sha256']:
            raise AuthorityError('restore_preparation_binding_mismatch')
        if stage.exists() and target.exists():raise AuthorityError('restore_target_conflict')
        if not target.exists():
            self._validate_artifact(stage,receipt,verified)
            g._writable();self._fault('restore_before_publication')
            _rename_directory(stage,target)
            self._fault('restore_target_published')
        summary=self._validate_artifact(target,receipt,verified)
        final=dict(format='jarvis-restore-final-v1',store_id=g.store_id,key_id=g.key_id,restore_id=restore_id,
                   prepared_sha256=receipt_hash,target_parent=str(parent),target_name=restore_id,
                   manifest_sha256=verified['manifest_sha256'],database_sha256=receipt['database_sha256'],
                   source_checkpoint=verified['checkpoint'],source_lineage=receipt['source_lineage'],execution_enabled=False,state='committed')
        if final_path.exists():
            old,_=g._read(final_path)
            if old!=final:raise AuthorityError('restore_receipt_conflict')
            replayed=True
        else:
            g._writable();publish_file(final_path,encode(g.signed(final)))
            replayed=False
        self._fault('restore_publication_committed')
        return {**final,'verified':True,'replayed':replayed,'summary':summary,'runtime_activation_allowed':False}

    @serialized
    def verify_restored(self,directory):
        g=self.guard;directory=private_directory(directory);restore_id=identifier(directory.name)
        intent_path,prepared_path,final_path=self._paths(restore_id)
        intent,intent_hash=g._read(intent_path);prepared,prepared_hash=g._read(prepared_path);final,_=g._read(final_path)
        if intent.get('restore_id')!=restore_id or intent.get('target_parent')!=str(directory.parent) or prepared.get('intent_sha256')!=intent_hash or final.get('prepared_sha256')!=prepared_hash or final.get('state')!='committed' or final.get('database_sha256')!=prepared.get('database_sha256') or final.get('execution_enabled') is not False:
            raise AuthorityError('restore_receipt_binding_mismatch')
        verified=self._prepared_source(intent,prepared)
        if prepared['source_checkpoint']!=verified['checkpoint']:raise AuthorityError('restore_source_checkpoint_mismatch')
        summary=self._validate_artifact(directory,prepared,verified)
        return {**final,'verified':True,'summary':summary,'runtime_activation_allowed':False}

    def _prepared_source(self,intent,prepared):
        """Prepared copies can be checked even after archive media is unavailable."""
        g=self.guard
        if g.trust_context is None:raise AuthorityError('restore_external_trust_reference_required')
        g.history()  # validates all protected phase links and authorization
        if type(prepared.get('summary')) is not dict or type(prepared['summary'].get('logical_state')) is not dict:raise AuthorityError('restore_history_invalid')
        verified={'export_id':Path(intent['archive']).name,'manifest_sha256':intent['manifest_sha256'],
                  'checkpoint':prepared['source_checkpoint'],'files':{'state.jsonl':prepared['summary']['logical_state']}}
        proof=g.verify_export_attestation(verified)
        if proof['attestation_sha256']!=prepared['source_attestation_sha256']:raise AuthorityError('restore_attestation_mismatch')
        return {**verified,'completion_attestation':proof}

"""Retained, same-key checkpoint generations; no pruning or key rotation.

External references are caller-custodied minimum ancestors, never discovered
from an archive. Local HMAC files alone cannot defeat a privileged rollback.
"""
from datetime import UTC, datetime
import hashlib
import re
import uuid
from functools import wraps

from app.agent.authority import AuthorityError, identifier, instant

ZERO='0'*64


def guard_locked(method):
    @wraps(method)
    def locked(self,*args,**kwargs):
        with self._operation_mutex:return method(self,*args,**kwargs)
    return locked


class CheckpointEpochs:
    def _configure_epochs(self, *, rollover, epoch_capacity, max_epochs, recovery, trust_context):
        if type(rollover) is not bool or type(recovery) is not bool or type(epoch_capacity) is not int or not 4<=epoch_capacity<=9999 or type(max_epochs) is not int or not 1<=max_epochs<=16:
            raise AuthorityError('invalid_checkpoint_epoch_policy')
        self.rollover_enabled=rollover
        self.recovery_enabled=recovery
        self.epoch_capacity=epoch_capacity if rollover else 9999
        self.max_epochs=max_epochs if rollover else 1
        self._epoch=0;self._epoch_start=1;self._rollover_hash=ZERO
        self._epoch_directories=[self.directory]
        self._epoch_ranges=[]
        self.trust_context=trust_context
        self._check_trust_time()

    @property
    def key_id(self):
        import hmac
        return hmac.new(self._key,b'jarvis-checkpoint-key-identity-v1',hashlib.sha256).hexdigest()

    def _check_trust_time(self):
        ctx=self.trust_context
        if ctx is None:return
        if type(ctx) is not dict or set(ctx)!={'store_id','key_id','epoch','rollover_hash','head','valid_from','expires_at'}:
            raise AuthorityError('invalid_external_trust_context')
        if ctx['store_id']!=self.store_id or ctx['key_id']!=self.key_id:
            raise AuthorityError('checkpoint_trust_key_mismatch')
        if type(ctx['epoch']) is not int or not 0<=ctx['epoch']<16 or type(ctx['head']) is not dict or set(ctx['head'])!={'sequence','sha256','checkpoint_hash'}:
            raise AuthorityError('invalid_external_trust_context')
        if type(ctx['head']['sequence']) is not int or ctx['head']['sequence']<0 or not self._hash(ctx['rollover_hash']) or not self._hash(ctx['head']['checkpoint_hash']):
            raise AuthorityError('invalid_external_trust_context')
        if ctx['head']['sequence']==0:
            if ctx['head']!={'sequence':0,'sha256':None,'checkpoint_hash':ZERO} or ctx['epoch']!=0 or ctx['rollover_hash']!=ZERO:
                raise AuthorityError('invalid_external_trust_context')
        elif not self._hash(ctx['head']['sha256']):raise AuthorityError('invalid_external_trust_context')
        start=datetime.fromisoformat(instant(ctx['valid_from']));end=datetime.fromisoformat(instant(ctx['expires_at']))
        if not 0<(end-start).total_seconds()<=86400 or not start<=datetime.now(UTC)<end:
            raise AuthorityError('checkpoint_trust_expired')

    @staticmethod
    def _hash(value):return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None

    @staticmethod
    def _auxiliary(name):
        return re.fullmatch(r'(rollover-\d{4}\.(intent|final|recovery)|export-[0-9a-f-]{36}|restore-[0-9a-f-]{36}\.(intent|prepared|final))\.json',name) is not None or re.fullmatch(r'epoch-\d{4}',name) is not None

    def _transition_body(self, epoch, head, previous):
        return dict(format='jarvis-checkpoint-rollover-v1',store_id=self.store_id,epoch=epoch,
                    previous_epoch=epoch-1,previous_transition=previous,previous_head=head,
                    operation_id=str(uuid.uuid5(uuid.UUID(self.store_id),f"rollover:{epoch}:{head['checkpoint_hash']}")),
                    key_id=self.key_id,epoch_capacity=self.epoch_capacity,max_epochs=self.max_epochs)

    def _validate_transition(self, body, epoch, head, previous):
        if body!=self._transition_body(epoch,head,previous):raise AuthorityError('checkpoint_rollover_binding_mismatch')

    def _transition_paths(self, epoch):
        return (self.directory/f'rollover-{epoch:04}.intent.json',self.directory/f'epoch-{epoch:04}',self.directory/f'rollover-{epoch:04}.final.json')

    def _finish_transition(self, body, intent_hash, directory, *, create_link=False):
        from app.agent.ledger import encode, private_directory, publish_file, sync_directory
        self._writable()
        epoch=body['epoch'];_,expected,final=self._transition_paths(epoch)
        if directory!=expected:raise AuthorityError('checkpoint_rollover_binding_mismatch')
        if create_link:
            if not directory.exists():
                directory.mkdir(mode=0o700);sync_directory(self.directory)
                self._fault('rollover_directory_created')
            private_directory(directory)
            if not (directory/'LINK.json').exists():
                if list(directory.iterdir()):raise AuthorityError('checkpoint_rollover_incomplete')
                link=dict(format='jarvis-checkpoint-generation-v1',store_id=self.store_id,epoch=epoch,intent_hash=intent_hash,
                          previous_head=body['previous_head'],key_id=self.key_id)
                publish_file(directory/'LINK.json',encode(self.signed(link)))
                self._fault('rollover_link_durable')
        private_directory(directory)
        link,link_hash=self._read(directory/'LINK.json')
        if link!=dict(format='jarvis-checkpoint-generation-v1',store_id=self.store_id,epoch=epoch,intent_hash=intent_hash,previous_head=body['previous_head'],key_id=self.key_id):
            raise AuthorityError('checkpoint_generation_link_mismatch')
        if set(p.name for p in directory.iterdir())!={'LINK.json'}:
            raise AuthorityError('checkpoint_rollover_incomplete')
        result=dict(format='jarvis-checkpoint-rollover-commit-v1',store_id=self.store_id,epoch=epoch,intent_hash=intent_hash,
                    link_hash=link_hash,previous_head=body['previous_head'],key_id=self.key_id)
        self._writable()
        publish_file(final,encode(self.signed(result)))
        self._fault('rollover_committed')

    @guard_locked
    def history(self, *, recover_rollover=False):
        from app.agent.ledger import private_directory
        self._fence()
        entries=list(self.directory.iterdir())
        if len(entries)>21000:raise AuthorityError('checkpoint_invalid_inventory')
        auxiliary=[p for p in entries if self._auxiliary(p.name)]
        if auxiliary and not (self.rollover_enabled or self.recovery_enabled):
            raise AuthorityError('checkpoint_features_required')
        if len([p for p in auxiliary if p.name.startswith('export-')])>256 or len([p for p in auxiliary if p.name.startswith('restore-')])>192:
            raise AuthorityError('checkpoint_auxiliary_capacity')
        for path in auxiliary:
            if path.name.startswith(('export-','restore-')) or path.name.endswith('.recovery.json'):
                body,_=self._read(path)
                if type(body) is not dict or body.get('store_id')!=self.store_id or body.get('key_id')!=self.key_id:
                    raise AuthorityError('checkpoint_auxiliary_invalid')
                if path.name.startswith('export-'):
                    if path.name!=f"export-{identifier(body.get('export_id'))}.json" or body.get('format')!='jarvis-export-attestation-v1':raise AuthorityError('checkpoint_auxiliary_invalid')
                elif path.name.startswith('restore-'):
                    if not path.name.startswith('restore-'+identifier(body.get('restore_id'))+'.') or body.get('format') not in {'jarvis-restore-intent-v1','jarvis-restore-prepared-v1','jarvis-restore-final-v1'}:raise AuthorityError('checkpoint_auxiliary_invalid')
                elif body.get('format')!='jarvis-rollover-recovery-v1':raise AuthorityError('checkpoint_auxiliary_invalid')
        head,pending,result=self._history_group(self.directory,{'sequence':0,'sha256':None,'checkpoint_hash':ZERO})
        epoch=0;previous=ZERO;directories=[self.directory];ranges=[{'epoch':0,'start':1,'end':head['sequence'],'rollover_hash':ZERO}]
        expected_aux={p.name for p in auxiliary if p.name.startswith(('export-','restore-'))}
        for next_epoch in range(1,self.max_epochs):
            intent,directory,final=self._transition_paths(next_epoch)
            if not intent.exists():break
            if not self.rollover_enabled or pending:raise AuthorityError('checkpoint_rollover_incomplete')
            body,intent_hash=self._read(intent)
            self._validate_transition(body,next_epoch,head,previous)
            expected_aux.add(intent.name)
            recovery=self.directory/f'rollover-{next_epoch:04}.recovery.json'
            if recovery.exists():expected_aux.add(recovery.name)
            if not final.exists():
                if not recover_rollover or not (directory/'LINK.json').exists():raise AuthorityError('checkpoint_rollover_incomplete')
                if {p.name for p in auxiliary}!=expected_aux|{directory.name}:raise AuthorityError('checkpoint_generation_gap')
                self._finish_transition(body,intent_hash,directory)
                return self.history(recover_rollover=True)
            private_directory(directory)
            link,link_hash=self._read(directory/'LINK.json')
            expected_link=dict(format='jarvis-checkpoint-generation-v1',store_id=self.store_id,epoch=next_epoch,intent_hash=intent_hash,previous_head=head,key_id=self.key_id)
            commit,commit_hash=self._read(final)
            if link!=expected_link or commit!=dict(format='jarvis-checkpoint-rollover-commit-v1',store_id=self.store_id,epoch=next_epoch,intent_hash=intent_hash,link_hash=link_hash,previous_head=head,key_id=self.key_id):
                raise AuthorityError('checkpoint_generation_link_mismatch')
            expected_aux.update((directory.name,final.name))
            recovery=self.directory/f'rollover-{next_epoch:04}.recovery.json'
            if recovery.exists():expected_aux.add(recovery.name)
            start=head['sequence']+1
            head,pending,tail=self._history_group(directory,head)
            if len(tail)>self.epoch_capacity:raise AuthorityError('checkpoint_epoch_capacity_exceeded')
            result.extend(tail);epoch=next_epoch;previous=commit_hash;directories.append(directory)
            ranges.append({'epoch':epoch,'start':start,'end':head['sequence'],'rollover_hash':previous})
        if {p.name for p in auxiliary}!=expected_aux:raise AuthorityError('checkpoint_generation_gap')
        self._epoch,self._rollover_hash=epoch,previous
        self._epoch_start=ranges[-1]['start'];self._epoch_directories=directories;self._epoch_ranges=ranges
        self._validate_auxiliary(result)
        ctx=self.trust_context
        if ctx is not None:
            if ctx['epoch']>epoch or ranges[ctx['epoch']]['rollover_hash']!=ctx['rollover_hash'] or ctx['head']['sequence'] and ctx['head'] not in result:
                raise AuthorityError('checkpoint_external_reference_mismatch')
            selected=ranges[ctx['epoch']]
            if ctx['head']['sequence'] and not (selected['start']<=ctx['head']['sequence']<=selected['end'] or selected['start']>selected['end'] and ctx['head']['sequence']==selected['start']-1):
                raise AuthorityError('checkpoint_external_reference_mismatch')
        return head,pending,result

    def _checkpoint_directory(self, sequence):
        for generation in self._epoch_ranges:
            if generation['start']<=sequence<=generation['end'] or generation['epoch']==self._epoch and sequence==generation['end']+1:
                return self._epoch_directories[generation['epoch']]
        raise AuthorityError('checkpoint_generation_gap')

    def checkpoint_lineage(self, sequence):
        for generation in self._epoch_ranges:
            if generation['start']<=sequence<=generation['end']:
                return {'epoch':generation['epoch'],'rollover_hash':generation['rollover_hash'],'key_id':self.key_id}
        raise AuthorityError('checkpoint_not_found')

    def trust_reference(self, *, valid_from, expires_at):
        head,pending,_=self.history()
        if pending:raise AuthorityError('checkpoint_reconciliation_required')
        return dict(store_id=self.store_id,key_id=self.key_id,epoch=self._epoch,rollover_hash=self._rollover_hash,head=head,
                    valid_from=instant(valid_from),expires_at=instant(expires_at))

    @guard_locked
    def rollover(self):
        from app.agent.ledger import encode, publish_file
        self._writable()
        if not self.rollover_enabled:raise AuthorityError('checkpoint_rollover_disabled')
        head,pending,_=self.history()
        if pending or self._head!=head:raise AuthorityError('checkpoint_reconciliation_required')
        epoch=self._epoch+1
        if epoch>=self.max_epochs:raise AuthorityError('checkpoint_generation_capacity')
        intent,directory,_=self._transition_paths(epoch)
        body=self._transition_body(epoch,head,self._rollover_hash)
        raw=encode(self.signed(body));intent_hash=hashlib.sha256(raw).hexdigest()
        publish_file(intent,raw)
        self._fault('rollover_intent_durable')
        self._finish_transition(body,intent_hash,directory,create_link=True)
        self._head=self.history()[0]
        return {'epoch':self._epoch,'head':self._head,'rollover_hash':self._rollover_hash,'history_deleted':False}

    @guard_locked
    def resume_rollover(self, permit, permits, actor, request_id):
        """Explicit authenticated completion when a new link was never published."""
        from app.agent.ledger import read_file, strict_json
        self._writable()
        if not self.recovery_enabled:raise AuthorityError('checkpoint_recovery_disabled')
        # Validate the prior chain without trusting a directory's numeric maximum.
        epoch=1
        while epoch<self.max_epochs and self._transition_paths(epoch)[2].exists():epoch+=1
        intent,directory,final=self._transition_paths(epoch)
        body,intent_hash=self._read(intent)
        auth=permits.verify(permit,actor,request_id,'resume_rollover',{'operation_id':body['operation_id']})
        if auth['checkpoint']!=body['previous_head'] or actor.scope!='local-service':raise AuthorityError('stale_operator_permit')
        # Reuse the normal verifier to authenticate the complete old prefix.
        # It must fail only for this unique missing terminal link/commit.
        try:self.history()
        except AuthorityError as exc:
            if exc.code!='checkpoint_rollover_incomplete':raise
        else:raise AuthorityError('checkpoint_rollover_not_pending')
        if final.exists():raise AuthorityError('checkpoint_rollover_not_pending')
        from app.agent.ledger import encode, publish_file
        recovery=self.directory/f'rollover-{epoch:04}.recovery.json'
        decision=dict(format='jarvis-rollover-recovery-v1',store_id=self.store_id,key_id=self.key_id,
                      request_id=request_id,operation_id=body['operation_id'],epoch=epoch,
                      authorization=auth,permit_sha256=hashlib.sha256(encode(permit)).hexdigest(),state='authorized')
        if recovery.exists():
            existing,_=self._read(recovery)
            if existing!=decision:raise AuthorityError('request_conflict')
        else:publish_file(recovery,encode(self.signed(decision)))
        self._finish_transition(body,intent_hash,directory,create_link=True)
        self._head=self.history()[0]
        return {'operation_id':body['operation_id'],'epoch':self._epoch,'history_deleted':False}

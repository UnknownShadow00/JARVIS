"""Protected export-completion attestations independent of a surviving source DB."""
import hashlib
from app.agent.authority import AuthorityError, identifier


class AuditAttestations:
    def verify_export_markers(self,conn):
        """A later SQL checkpoint binds each published external proof identity."""
        from app.agent.ledger import strict_json
        for row in conn.execute("SELECT data FROM receipts WHERE operation='operator_export_attested'"):
            if not self.recovery_enabled:raise AuthorityError('checkpoint_features_required')
            receipt=strict_json(row[0])
            if type(receipt) is not dict or type(receipt.get('result')) is not dict:raise AuthorityError('archive_attestation_marker_mismatch')
            result=receipt['result']
            export_id=identifier(result.get('export_id'))
            body,digest=self._read(self.directory/f'export-{export_id}.json')
            if result.get('attestation_sha256')!=digest or result.get('manifest_sha256')!=body.get('manifest_sha256'):
                raise AuthorityError('archive_attestation_marker_mismatch')

    def attest_export(self, authority, actor, verified):
        from app.agent.execution import phase_id
        from app.agent.ledger import encode, publish_file
        self._writable()
        if not self.recovery_enabled:raise AuthorityError('archive_restore_disabled')
        a=authority
        with a._mutex:
            a._fence()
            if a._ledger is not self or a._scope(actor)!='local-service':raise AuthorityError('operator_scope_required')
            export_id=identifier(verified['export_id'])
            admission=a.receipt(actor,export_id)
            completion=a.receipt(actor,phase_id(export_id,'export_complete'))
            if admission is None or admission['operation']!='operator_export_admit' or completion is None or completion['operation']!='operator_export_complete' or completion['result'].get('manifest_sha256')!=verified['manifest_sha256']:
                raise AuthorityError('export_audit_publication_missing')
            _,pending,history=self.history()
            if pending:raise AuthorityError('checkpoint_reconciliation_required')
            checkpoint=None
            for head in reversed(history):
                intent,_=self._read(self._checkpoint_directory(head['sequence'])/f"{head['sequence']:08}.intent.json")
                if intent['last_event'] and intent['last_event']['request_id']==completion['request_id']:
                    final,_=self._read(self._checkpoint_directory(head['sequence'])/f"{head['sequence']:08}.final.json")
                    if final['outcome']=='committed':checkpoint=head;break
            if checkpoint is None:raise AuthorityError('export_publication_checkpoint_missing')
            body=dict(format='jarvis-export-attestation-v1',store_id=self.store_id,key_id=self.key_id,export_id=export_id,
                manifest_sha256=verified['manifest_sha256'],snapshot_checkpoint=verified['checkpoint'],
                publication_checkpoint=checkpoint,publication_lineage=self.checkpoint_lineage(checkpoint['sequence']),
                admission_receipt=admission,completion_receipt=completion,
                completion_receipt_sha256=hashlib.sha256(encode(completion)).hexdigest())
            path=self.directory/f'export-{export_id}.json'
            if path.exists():
                old,_=self._read(path)
                if old!=body:raise AuthorityError('export_attestation_conflict')
            else:
                if len(list(self.directory.glob('export-*.json')))>=256:raise AuthorityError('checkpoint_auxiliary_capacity')
                self._fault('export_before_attestation')
                publish_file(path,encode(self.signed(body)))
                self._fault('export_attested')
            return self.verify_export_attestation(verified)

    def verify_export_attestation(self, verified, *, _history=None):
        from app.agent.execution import phase_id
        from app.agent.ledger import encode
        self._fence()
        if not self.recovery_enabled:raise AuthorityError('archive_restore_disabled')
        body,attestation_hash=self._read(self.directory/f"export-{identifier(verified['export_id'])}.json")
        keys={'format','store_id','key_id','export_id','manifest_sha256','snapshot_checkpoint','publication_checkpoint','publication_lineage','admission_receipt','completion_receipt','completion_receipt_sha256'}
        if type(body) is not dict or set(body)!=keys or body['format']!='jarvis-export-attestation-v1' or body['store_id']!=self.store_id or body['key_id']!=self.key_id or body['export_id']!=verified['export_id'] or body['manifest_sha256']!=verified['manifest_sha256'] or body['snapshot_checkpoint']!=verified['checkpoint']:
            raise AuthorityError('archive_attestation_mismatch')
        if _history is None:
            _,pending,history=self.history()
        else:
            pending=None;history=_history
        if pending or body['publication_checkpoint'] not in history or body['publication_lineage']!=self.checkpoint_lineage(body['publication_checkpoint']['sequence']):
            raise AuthorityError('archive_attestation_checkpoint_mismatch')
        if body['snapshot_checkpoint'] not in history or body['publication_checkpoint']['sequence']<=body['snapshot_checkpoint']['sequence'] or not self._hash(body['manifest_sha256']):
            raise AuthorityError('archive_attestation_checkpoint_mismatch')
        admission=body['admission_receipt'];completion=body['completion_receipt']
        if type(admission) is not dict or type(completion) is not dict or admission.get('request_id')!=body['export_id'] or admission.get('scope')!='local-service' or admission.get('operation')!='operator_export_admit' or admission.get('state')!='committed' or completion.get('request_id')!=phase_id(body['export_id'],'export_complete') or completion.get('scope')!='local-service' or completion.get('operation')!='operator_export_complete' or completion.get('state')!='committed' or type(completion.get('result')) is not dict or completion['result'].get('manifest_sha256')!=body['manifest_sha256'] or body['completion_receipt_sha256']!=hashlib.sha256(encode(completion)).hexdigest():
            raise AuthorityError('archive_attestation_invalid_receipts')
        return {'verified':True,'attestation_sha256':attestation_hash,'publication_checkpoint':body['publication_checkpoint'],
                'publication_lineage':body['publication_lineage'],'completion_receipt_id':completion['request_id']}

    def _validate_auxiliary(self,history):
        """Authenticate receipt groups; phase existence is never completion proof."""
        from pathlib import Path
        from app.agent.ledger import encode
        for path in self.directory.glob('export-*.json'):
            body,_=self._read(path)
            if not {'export_id','manifest_sha256','snapshot_checkpoint'}<=set(body):raise AuthorityError('archive_attestation_mismatch')
            self.verify_export_attestation({'export_id':body['export_id'],'manifest_sha256':body['manifest_sha256'],'checkpoint':body['snapshot_checkpoint']},_history=history)
        groups={}
        for path in self.directory.glob('restore-*.json'):
            ident,phase=path.name[len('restore-'):].removesuffix('.json').split('.')
            groups.setdefault(ident,{})[phase]=self._read(path)
        if len(groups)>64:raise AuthorityError('restore_capacity_exceeded')
        required_intent={'format','store_id','key_id','restore_id','archive','target_parent','manifest_sha256','source_checkpoint','source_lineage','source_attestation_sha256','trusted_admission_head','authorization','permit_sha256','admitted_at','execution_enabled'}
        required_prepared={'format','store_id','key_id','restore_id','intent_sha256','manifest_sha256','source_checkpoint','source_lineage','source_attestation_sha256','database_sha256','summary','execution_enabled'}
        required_final={'format','store_id','key_id','restore_id','prepared_sha256','target_parent','target_name','manifest_sha256','database_sha256','source_checkpoint','source_lineage','execution_enabled','state'}
        for restore_id,phases in groups.items():
            if set(phases) not in ({'intent'},{'intent','prepared'},{'intent','prepared','final'}):raise AuthorityError('restore_history_incomplete')
            intent,intent_hash=phases['intent']
            if any(body.get('restore_id')!=restore_id for body,_ in phases.values()):raise AuthorityError('restore_history_invalid')
            if set(intent)!=required_intent or intent['format']!='jarvis-restore-intent-v1' or intent['trusted_admission_head'] not in history or intent['source_checkpoint'] not in history or intent['execution_enabled'] is not False or not self._hash(intent['manifest_sha256']) or not self._hash(intent['permit_sha256']):raise AuthorityError('restore_history_invalid')
            for value in ('archive','target_parent'):
                if type(intent[value]) is not str or not Path(intent[value]).is_absolute() or '..' in Path(intent[value]).parts:raise AuthorityError('restore_history_invalid')
            identifier(Path(intent['archive']).name)
            expected_payload={'export_id':Path(intent['archive']).name,'manifest_sha256':intent['manifest_sha256'],'target_parent':intent['target_parent'],'restore_id':restore_id}
            auth=intent['authorization']
            if type(auth) is not dict or auth.get('request_id')!=restore_id or auth.get('command')!='restore_archive' or auth.get('scope')!='local-service' or auth.get('checkpoint')!=intent['trusted_admission_head'] or auth.get('payload_hash')!=hashlib.sha256(encode(expected_payload)).hexdigest():raise AuthorityError('restore_authorization_binding_mismatch')
            if intent['source_lineage']!=self.checkpoint_lineage(intent['source_checkpoint']['sequence']):raise AuthorityError('restore_history_invalid')
            proof=self.verify_export_attestation({'export_id':Path(intent['archive']).name,'manifest_sha256':intent['manifest_sha256'],'checkpoint':intent['source_checkpoint']},_history=history)
            if intent['source_attestation_sha256']!=proof['attestation_sha256']:raise AuthorityError('restore_attestation_mismatch')
            if 'prepared' in phases:
                prepared,prepared_hash=phases['prepared']
                if set(prepared)!=required_prepared or prepared['format']!='jarvis-restore-prepared-v1' or prepared['intent_sha256']!=intent_hash or prepared['execution_enabled'] is not False or not self._hash(prepared['database_sha256']) or type(prepared['summary']) is not dict:raise AuthorityError('restore_history_invalid')
                if any(prepared[k]!=intent[k] for k in ('manifest_sha256','source_checkpoint','source_lineage','source_attestation_sha256')):raise AuthorityError('restore_history_invalid')
                if 'final' in phases:
                    final,_=phases['final']
                    if set(final)!=required_final or final['format']!='jarvis-restore-final-v1' or final['prepared_sha256']!=prepared_hash or final['target_parent']!=intent['target_parent'] or final['target_name']!=restore_id or final['state']!='committed' or final['execution_enabled'] is not False or any(final[k]!=prepared[k] for k in ('database_sha256','manifest_sha256','source_checkpoint','source_lineage')):raise AuthorityError('restore_history_invalid')
        self._restore_groups=groups

    def disaster_status(self):
        from app.agent.ledger import strict_json, read_file
        head,pending,_=self.history()
        results=[]
        ids=sorted(self._restore_groups)
        if len(ids)>64:raise AuthorityError('restore_capacity_exceeded')
        for restore_id in ids:
            identifier(restore_id)
            phases=self._restore_groups[restore_id]
            state='committed' if 'final' in phases else 'prepared' if 'prepared' in phases else 'incomplete'
            results.append({'restore_id':restore_id,'status':state,'artifact_currently_verified':False,'execution_enabled':False,'automatic_retry':False})
        return {'epoch':self._epoch,'max_epochs':self.max_epochs,'epoch_capacity':self.epoch_capacity,
                'rollover_enabled':self.rollover_enabled,'rollover_hash':self._rollover_hash,
                'trust_reference_configured':self.trust_context is not None,'restore_enabled':self.recovery_enabled,
                'restores':results,'history_deleted':False}

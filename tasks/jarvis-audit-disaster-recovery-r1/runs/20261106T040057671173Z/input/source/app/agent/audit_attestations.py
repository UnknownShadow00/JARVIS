"""Protected export-completion attestations independent of a surviving source DB."""
import hashlib
from app.agent.authority import AuthorityError, identifier


class AuditAttestations:
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

    def verify_export_attestation(self, verified):
        from app.agent.execution import phase_id
        from app.agent.ledger import encode
        self._fence()
        if not self.recovery_enabled:raise AuthorityError('archive_restore_disabled')
        body,attestation_hash=self._read(self.directory/f"export-{identifier(verified['export_id'])}.json")
        keys={'format','store_id','key_id','export_id','manifest_sha256','snapshot_checkpoint','publication_checkpoint','publication_lineage','admission_receipt','completion_receipt','completion_receipt_sha256'}
        if type(body) is not dict or set(body)!=keys or body['format']!='jarvis-export-attestation-v1' or body['store_id']!=self.store_id or body['key_id']!=self.key_id or body['export_id']!=verified['export_id'] or body['manifest_sha256']!=verified['manifest_sha256'] or body['snapshot_checkpoint']!=verified['checkpoint']:
            raise AuthorityError('archive_attestation_mismatch')
        _,pending,history=self.history()
        if pending or body['publication_checkpoint'] not in history or body['publication_lineage']!=self.checkpoint_lineage(body['publication_checkpoint']['sequence']):
            raise AuthorityError('archive_attestation_checkpoint_mismatch')
        admission=body['admission_receipt'];completion=body['completion_receipt']
        if type(admission) is not dict or type(completion) is not dict or admission.get('request_id')!=body['export_id'] or admission.get('scope')!='local-service' or admission.get('operation')!='operator_export_admit' or admission.get('state')!='committed' or completion.get('request_id')!=phase_id(body['export_id'],'export_complete') or completion.get('scope')!='local-service' or completion.get('operation')!='operator_export_complete' or completion.get('state')!='committed' or type(completion.get('result')) is not dict or completion['result'].get('manifest_sha256')!=body['manifest_sha256'] or body['completion_receipt_sha256']!=hashlib.sha256(encode(completion)).hexdigest():
            raise AuthorityError('archive_attestation_invalid_receipts')
        return {'verified':True,'attestation_sha256':attestation_hash,'publication_checkpoint':body['publication_checkpoint'],
                'publication_lineage':body['publication_lineage'],'completion_receipt_id':completion['request_id']}

    def disaster_status(self):
        from app.agent.ledger import strict_json, read_file
        head,pending,_=self.history()
        results=[]
        ids=sorted(p.name.removeprefix('restore-').removesuffix('.intent.json') for p in self.directory.glob('restore-*.intent.json'))
        if len(ids)>64:raise AuthorityError('restore_capacity_exceeded')
        for restore_id in ids:
            identifier(restore_id)
            intent,_=self._read(self.directory/f'restore-{restore_id}.intent.json')
            state='committed' if (self.directory/f'restore-{restore_id}.final.json').exists() else 'prepared' if (self.directory/f'restore-{restore_id}.prepared.json').exists() else 'incomplete'
            results.append({'restore_id':restore_id,'status':state,'execution_enabled':False,'automatic_retry':False})
        return {'epoch':self._epoch,'max_epochs':self.max_epochs,'epoch_capacity':self.epoch_capacity,
                'rollover_enabled':self.rollover_enabled,'rollover_hash':self._rollover_hash,
                'trust_reference_configured':self.trust_context is not None,'restore_enabled':self.recovery_enabled,
                'restores':results,'history_deleted':False}

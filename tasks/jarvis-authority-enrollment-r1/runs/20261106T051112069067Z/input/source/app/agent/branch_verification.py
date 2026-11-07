"""Read-only historical branch continuity and re-anchoring proposals.

There is deliberately no branch activation, re-key, SQL import or registry writer.
Registry freshness and external parent-reference custody belong to the operator.
"""
from datetime import UTC, datetime
import hashlib
from pathlib import Path
import sqlite3
import uuid

from app.agent.authority import AuthorityError, identifier, instant, text
from app.agent.archive_restore import ArchiveRestorer, serialized
from app.agent.enrollment import fingerprint, policy


class BranchVerifier:
    def __init__(self, guard):
        self.guard = guard

    @serialized
    def verify(self, directory, request):
        g = self.guard; g._fence()
        fields = {'format','branch_id','operator_id','expected_source_head','expected_restore_id',
                  'expected_database_sha256','expected_source_lineage','expected_key_id',
                  'issued_at','expires_at','reserved_branch_ids','decision'}
        if type(request) is not dict or set(request) != fields:
            raise AuthorityError('branch_invalid_verification_context')
        if request['format'] != 'jarvis-branch-verification-request-v1' or request['decision'] != 'PROPOSE_ONLY':
            raise AuthorityError('branch_proposal_only')
        branch_id = identifier(request['branch_id']); identifier(request['expected_restore_id'])
        if uuid.UUID(branch_id).version != 4 or branch_id in (g.store_id,request['expected_restore_id']):
            raise AuthorityError('branch_invalid_identity')
        text(request['operator_id'],128)
        start = datetime.fromisoformat(instant(request['issued_at'])); end = datetime.fromisoformat(instant(request['expires_at']))
        if not 0 < (end-start).total_seconds() <= 300 or not start <= datetime.now(UTC) < end:
            raise AuthorityError('branch_context_expired')
        registry = request['reserved_branch_ids']
        if type(registry) is not list or len(registry)>64 or any(type(x) is not str for x in registry) or len(set(registry)) != len(registry):
            raise AuthorityError('branch_invalid_registry')
        for item in registry: identifier(item)
        if branch_id in registry: raise AuthorityError('branch_identity_already_reserved')
        head,pending,_ = g.history()
        if pending or head != request['expected_source_head']:
            raise AuthorityError('branch_stale_source_reference')
        if request['expected_key_id'] != g.key_id: raise AuthorityError('branch_key_mismatch')
        restored = ArchiveRestorer(g).verify_restored(directory)
        if restored['restore_id'] != request['expected_restore_id'] or restored['database_sha256'] != request['expected_database_sha256']:
            raise AuthorityError('branch_restored_identity_mismatch')
        if restored['source_lineage'] != request['expected_source_lineage']:
            raise AuthorityError('branch_generation_mismatch')
        conn = sqlite3.connect((Path(directory)/'state.sqlite').absolute().as_uri()+'?mode=ro',uri=True)
        try:
            # Read original identities; never assign replacement request UUIDs.
            ids = [row[0] for row in conn.execute('SELECT request_id FROM receipts ORDER BY request_id')]
        finally: conn.close()
        _, final_hash = g._read(g.directory/f"restore-{restored['restore_id']}.final.json")
        proposal = dict(format='jarvis-inert-reanchoring-proposal-v1',branch_id=branch_id,
                        original_store_id=g.store_id,restore_id=restored['restore_id'],
                        parent_checkpoint=restored['source_checkpoint'],parent_lineage=restored['source_lineage'],
                        verified_source_head=head,restore_final_sha256=final_hash,
                        database_sha256=restored['database_sha256'],original_request_ids_sha256=fingerprint(ids),
                        external_context_sha256=fingerprint(request),external_trust_sha256=fingerprint(g.trust_context),
                        operator_id=request['operator_id'],key_id=g.key_id,policy=policy(g),
                        execution_enabled=False,activation_authorized=False,decision_required=True,
                        required_decision='separate_authorized_offline_branch_ceremony',
                        history_semantics='historical_parent_snapshot_not_source_head_continuation')
        return {'state':'VERIFIED','verified':True,'proposal':proposal,'proposal_sha256':fingerprint(proposal),
                'summary':restored['summary'],'original_request_count':len(ids),
                'registry_written':False,'registry_freshness_externally_required':True,
                'execution_enabled':False,'operator_decision':'REQUIRED_NO_ACTIVATION_AUTHORIZED'}

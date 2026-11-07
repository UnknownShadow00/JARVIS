"""Offline diagnostics and explicitly authorized disposable disaster recovery.

Default modes verify only. Keys and permits arrive through inherited descriptors;
no credential paths/environment lookup, runtime startup or executor activation.
"""
import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from app.agent.authority import AuthorityError,identifier
from app.agent.ledger import LedgerGuard,strict_json,private_directory,encode
from app.agent.recovery import inspect_offline,OperatorPermits
from app.agent.runtime import SERVICE_ACTOR


def _read_fd(number,limit):
    if number is None or number<3:raise AuthorityError('invalid_key_descriptor')
    raw=os.read(number,limit+1)
    if len(raw)>limit:raise AuthorityError('operator_descriptor_too_large')
    return raw


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database')
    parser.add_argument('--checkpoints')
    parser.add_argument('--store-id')
    parser.add_argument('--key-fd',type=int)
    parser.add_argument('--trust-fd',type=int)
    parser.add_argument('--task-id')
    parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--offset',type=int,default=0)
    parser.add_argument('--rollover-enabled',action='store_true')
    parser.add_argument('--disaster-recovery-enabled',action='store_true')
    parser.add_argument('--epoch-capacity',type=int,default=9999)
    parser.add_argument('--max-epochs',type=int,default=16)
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--checkpoint-status',action='store_true')
    modes.add_argument('--verify-archive')
    modes.add_argument('--verify-restored')
    modes.add_argument('--restore-archive')
    modes.add_argument('--reconcile-restore')
    modes.add_argument('--resume-rollover',action='store_true')
    modes.add_argument('--enrollment-status',action='store_true')
    modes.add_argument('--enroll-store',action='store_true')
    modes.add_argument('--reconcile-enrollment',action='store_true')
    modes.add_argument('--verify-branch')
    modes.add_argument('--recovery-registry-status',action='store_true')
    modes.add_argument('--initialize-recovery-registry',action='store_true')
    modes.add_argument('--publish-recovery-proposal')
    modes.add_argument('--record-recovery-decision',action='store_true')
    modes.add_argument('--renew-recovery-witness',action='store_true')
    modes.add_argument('--reconcile-recovery-operation',action='store_true')
    modes.add_argument('--reconcile-transport-report')
    modes.add_argument('--publish-transport-evidence')
    parser.add_argument('--synthetic-endpoint-id')
    parser.add_argument('--transport-operator-key-fd',type=int)
    parser.add_argument('--transport-request-key-fd',type=int)
    parser.add_argument('--transport-response-key-fd',type=int)
    parser.add_argument('--registry-config-fd',type=int)
    parser.add_argument('--registry-reference-fd',type=int)
    parser.add_argument('--recovery-payload-fd',type=int)
    parser.add_argument('--custody')
    parser.add_argument('--reservation-fd',type=int)
    parser.add_argument('--branch-context-fd',type=int)
    parser.add_argument('--enrollment-witness-fd',type=int)
    parser.add_argument('--expected-manifest-sha256')
    parser.add_argument('--disposable-target-parent')
    parser.add_argument('--operation-id')
    parser.add_argument('--operator-key-fd',type=int)
    parser.add_argument('--permit-fd',type=int)
    parser.add_argument('--commit-recovery',action='store_true')
    args=parser.parse_args(argv)
    registry=bool(args.recovery_registry_status or args.initialize_recovery_registry or args.publish_recovery_proposal or args.record_recovery_decision or args.renew_recovery_witness or args.reconcile_recovery_operation)
    registry_mutation=registry and not args.recovery_registry_status
    transport_recovery=bool(args.reconcile_transport_report or args.publish_transport_evidence)
    mutation=bool(transport_recovery or registry_mutation or args.restore_archive or args.reconcile_restore or args.resume_rollover or args.enroll_store or args.reconcile_enrollment)
    enrollment=bool(args.enrollment_status or args.enroll_store or args.reconcile_enrollment)
    disaster=bool(registry or args.checkpoint_status or args.verify_archive or args.verify_restored or args.verify_branch or enrollment or mutation)
    ledger=None;authority=None
    try:
        configured=(args.checkpoints is not None,args.store_id is not None,args.key_fd is not None)
        if any(configured) and not all(configured):raise AuthorityError('complete_checkpoint_configuration_required')
        if disaster and not all(configured):raise AuthorityError('complete_checkpoint_configuration_required')
        if mutation and not args.commit_recovery:raise AuthorityError('explicit_recovery_commit_required')
        if all(configured):
            if enrollment:private_directory(args.checkpoints)  # Never provision new trust directories.
            raw=_read_fd(args.key_fd,128)
            if len(raw)<32:raise AuthorityError('invalid_ledger_key')
            trust=strict_json(_read_fd(args.trust_fd,16384)) if args.trust_fd is not None else None
            ledger=LedgerGuard(args.checkpoints,raw,args.store_id,initialize=args.enroll_store or args.reconcile_enrollment,rollover=args.rollover_enabled,
                               epoch_capacity=args.epoch_capacity,max_epochs=args.max_epochs,recovery=disaster or args.disaster_recovery_enabled or args.rollover_enabled,trust_context=trust)
        if transport_recovery:
            from app.agent.authority import Authority
            from app.agent.enrollment import verify_authority_enrollment
            from app.agent.recovery import RecoveryActions
            from app.agent.recovery_decisions import RecoveryRegistry
            from app.agent.execution_transport import SyntheticTransport,verify_history_readonly
            from app.agent.ledger import read_file
            if not args.database:raise AuthorityError('database_path_required')
            operation=identifier(args.operation_id)
            task=identifier(args.reconcile_transport_report or args.publish_transport_evidence)
            command='reconcile_synthetic_transport_report' if args.reconcile_transport_report else 'publish_synthetic_evidence'
            payload={'task_id':task}
            permits=OperatorPermits(_read_fd(args.operator_key_fd,128))
            permit=strict_json(_read_fd(args.permit_fd,65536))
            auth=permits.authenticate(permit)
            witness=strict_json(_read_fd(args.enrollment_witness_fd,16384))
            config=strict_json(_read_fd(args.registry_config_fd,16384))
            reference=strict_json(_read_fd(args.registry_reference_fd,16384))
            transport=SyntheticTransport(args.synthetic_endpoint_id,OperatorPermits(_read_fd(args.transport_operator_key_fd,128)),
                _read_fd(args.transport_request_key_fd,128),_read_fd(args.transport_response_key_fd,128),enabled=True)
            database=Path(args.database).absolute();read_file(database,32*1024*1024)
            ledger.acquire(database,readonly=True)
            registry_service=RecoveryRegistry(ledger,config,reference,permits)
            if not registry_service.inspect()['verified']:raise AuthorityError('recovery_reconciliation_required')
            conn=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True,isolation_level=None)
            try:
                ledger.verify(conn);verify_authority_enrollment(conn,database,ledger,witness)
                verify_history_readonly(conn,ledger,registry_service,transport)
                row=conn.execute('SELECT data FROM receipts WHERE request_id=?',(operation,)).fetchone()
                if row:
                    previous=strict_json(row[0]);expected=previous['result'].get('operator_authorization')
                    if (previous['operation']!='operator_recovery' or expected!=auth
                        or auth['request_id']!=operation or auth['scope']!=SERVICE_ACTOR.scope or auth['command']!=command
                        or auth['payload_hash']!=hashlib.sha256(encode(payload)).hexdigest()):
                        raise AuthorityError('request_conflict')
                    print(json.dumps({'receipt':previous,'replayed':True,'executor_invoked':False,'execution_enabled':False}));return 0
            finally:conn.close()
            permits.verify(permit,SERVICE_ACTOR,operation,command,payload)
            opening=ledger.history()[0]
            if auth['checkpoint']!=opening:raise AuthorityError('stale_operator_permit')
            ledger.close()
            registry_service=RecoveryRegistry(ledger,config,reference,permits)
            authority=Authority(database,ledger=ledger,enrollment_context=witness,recovery_registry=registry_service,
                                allow_simulation=True,expected_open_checkpoint=opening)
            transport.configure(authority)
            result=RecoveryActions(authority,permits).apply(SERVICE_ACTOR,operation,command,payload,permit,offline_open=True)
            authority.close();authority=None;success=True
        elif not disaster:
            if not args.database:raise AuthorityError('database_path_required')
            witness=strict_json(_read_fd(args.enrollment_witness_fd,16384)) if args.enrollment_witness_fd is not None else None
            result=inspect_offline(args.database,SERVICE_ACTOR,ledger=ledger,enrollment_context=witness,task_id=args.task_id,limit=args.limit,offset=args.offset)
            success=result['consistent']
        else:
            # This opens only the existing protected journal lock. No source DB
            # is opened or created. An active application owner excludes this CLI.
            coordinate=Path(args.disposable_target_parent) if args.disposable_target_parent else ledger.directory.parent/'.operator-coordination'
            if args.enrollment_status and not (ledger.directory/'journal.lock').exists():
                if any(ledger.directory.iterdir()) or args.custody is None or any(private_directory(args.custody).iterdir()):
                    raise AuthorityError('enrollment_missing_initial_anchor_lock')
                from app.agent.enrollment import OfflineEnrollment
                result=OfflineEnrollment(ledger,args.custody,strict_json(_read_fd(args.reservation_fd,16384))).status()
                print(json.dumps(result,indent=2));return 1
            ledger.acquire(coordinate/'unused.sqlite',readonly=not mutation)
            if registry:
                from app.agent.recovery_decisions import RecoveryRegistry
                config=strict_json(_read_fd(args.registry_config_fd,16384))
                reference=strict_json(_read_fd(args.registry_reference_fd,16384))
                permits=OperatorPermits(_read_fd(args.operator_key_fd,128))
                service=RecoveryRegistry(ledger,config,reference,permits)
                if args.recovery_registry_status:
                    result=service.inspect(args.operation_id);success=result['verified']
                else:
                    permit=strict_json(_read_fd(args.permit_fd,65536))
                    payload=strict_json(_read_fd(args.recovery_payload_fd,65536))
                    if args.initialize_recovery_registry:command='initialize'
                    elif args.publish_recovery_proposal:command='propose'
                    elif args.record_recovery_decision:command='decide'
                    elif args.renew_recovery_witness:command='renew'
                    else:
                        if set(payload)!={'command','payload'}:raise AuthorityError('recovery_reconciliation_payload_required')
                        command=payload['command'];payload=payload['payload']
                    if args.publish_recovery_proposal and payload.get('directory')!=str(Path(args.publish_recovery_proposal).absolute()):
                        raise AuthorityError('recovery_proposal_path_mismatch')
                    result=service.apply(SERVICE_ACTOR,identifier(args.operation_id),command,payload,permit,initialize=command=='initialize')
                    success=True
            elif enrollment:
                from app.agent.enrollment import OfflineEnrollment
                if not args.custody:raise AuthorityError('enrollment_custody_required')
                reservation=strict_json(_read_fd(args.reservation_fd,16384))
                service=OfflineEnrollment(ledger,args.custody,reservation)
                if args.operation_id is not None and args.operation_id!=reservation['enrollment_id']:
                    raise AuthorityError('enrollment_invalid_identity')
                if args.enrollment_status:
                    result=service.status();success=result['state']=='VERIFIED'
                elif args.reconcile_enrollment:
                    result=service.reconcile();success=True
                else:
                    permits=OperatorPermits(_read_fd(args.operator_key_fd,128))
                    permit=strict_json(_read_fd(args.permit_fd,65536))
                    result=OfflineEnrollment(ledger,args.custody,reservation,permits).enroll(SERVICE_ACTOR,permit,disposable=True);success=True
            elif args.verify_branch:
                from app.agent.branch_verification import BranchVerifier
                result=BranchVerifier(ledger).verify(args.verify_branch,strict_json(_read_fd(args.branch_context_fd,16384)));success=True
            elif args.checkpoint_status:
                result=ledger.disaster_status();success=True
            else:
                from app.agent.archive_restore import ArchiveRestorer
                restorer=ArchiveRestorer(ledger)
                if args.verify_archive:
                    result=restorer.verify_archive(args.verify_archive,args.expected_manifest_sha256);success=True
                elif args.verify_restored:
                    result=restorer.verify_restored(args.verify_restored);success=True
                elif args.reconcile_restore:
                    # Audit-only continuation of an existing protected admission;
                    # no new SQL reconstruction or effects, even after grant expiry.
                    result=restorer.reconcile(identifier(args.reconcile_restore));success=True
                else:
                    if args.resume_rollover and args.operator_key_fd is None and args.permit_fd is None:
                        permits=permit=None
                    else:
                        key=_read_fd(args.operator_key_fd,128)
                        permits=OperatorPermits(key);permit=strict_json(_read_fd(args.permit_fd,65536))
                    if args.resume_rollover:
                        result=ledger.resume_rollover(permit,permits,SERVICE_ACTOR,identifier(args.operation_id));success=True
                    else:
                        if not args.disposable_target_parent:raise AuthorityError('disposable_target_parent_required')
                        result=ArchiveRestorer(ledger,permits).restore(SERVICE_ACTOR,identifier(args.operation_id),args.restore_archive,
                            args.disposable_target_parent,args.expected_manifest_sha256,permit,disposable=True)
                        success=True
        print(json.dumps(result,indent=2));return 0 if success else 1
    except (AuthorityError,OSError,sqlite3.Error) as exc:
        print(json.dumps({'verified':False,'error':exc.code if isinstance(exc,AuthorityError) else 'operator_io_unavailable',
            'state':'RECONCILIATION_REQUIRED' if mutation else 'BLOCKED',
            'recommendation':'preserve_artifacts_and_protected_anchors_no_automatic_retry',
            'mutation_outcome':'reconciliation_required' if mutation else 'none','operation_id':args.operation_id or args.reconcile_restore,
            'execution_enabled':False}))
        return 1
    finally:
        if authority is not None:
            try:authority.close()
            except (AuthorityError,OSError,sqlite3.Error):pass
        if ledger is not None:ledger.close()


if __name__=='__main__':raise SystemExit(main())

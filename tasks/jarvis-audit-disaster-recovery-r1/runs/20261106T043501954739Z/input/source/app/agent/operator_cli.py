"""Offline diagnostics and explicitly authorized disposable disaster recovery.

Default modes verify only. Keys and permits arrive through inherited descriptors;
no credential paths/environment lookup, runtime startup or executor activation.
"""
import argparse
import json
import os
from pathlib import Path
from app.agent.authority import AuthorityError,identifier
from app.agent.ledger import LedgerGuard,strict_json
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
    parser.add_argument('--expected-manifest-sha256')
    parser.add_argument('--disposable-target-parent')
    parser.add_argument('--operation-id')
    parser.add_argument('--operator-key-fd',type=int)
    parser.add_argument('--permit-fd',type=int)
    parser.add_argument('--commit-recovery',action='store_true')
    args=parser.parse_args(argv)
    mutation=bool(args.restore_archive or args.reconcile_restore or args.resume_rollover)
    disaster=bool(args.checkpoint_status or args.verify_archive or args.verify_restored or mutation)
    ledger=None
    try:
        configured=(args.checkpoints is not None,args.store_id is not None,args.key_fd is not None)
        if any(configured) and not all(configured):raise AuthorityError('complete_checkpoint_configuration_required')
        if disaster and not all(configured):raise AuthorityError('complete_checkpoint_configuration_required')
        if mutation and not args.commit_recovery:raise AuthorityError('explicit_recovery_commit_required')
        if all(configured):
            raw=_read_fd(args.key_fd,128)
            if len(raw)<32:raise AuthorityError('invalid_ledger_key')
            trust=strict_json(_read_fd(args.trust_fd,16384)) if args.trust_fd is not None else None
            ledger=LedgerGuard(args.checkpoints,raw,args.store_id,rollover=args.rollover_enabled,
                               epoch_capacity=args.epoch_capacity,max_epochs=args.max_epochs,recovery=disaster or args.disaster_recovery_enabled or args.rollover_enabled,trust_context=trust)
        if not disaster:
            if not args.database:raise AuthorityError('database_path_required')
            result=inspect_offline(args.database,SERVICE_ACTOR,ledger=ledger,task_id=args.task_id,limit=args.limit,offset=args.offset)
            success=result['consistent']
        else:
            # This opens only the existing protected journal lock. No source DB
            # is opened or created. An active application owner excludes this CLI.
            coordinate=Path(args.disposable_target_parent) if args.disposable_target_parent else ledger.directory.parent/'.operator-coordination'
            ledger.acquire(coordinate/'unused.sqlite',readonly=not mutation)
            if args.checkpoint_status:
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
    except (AuthorityError,OSError) as exc:
        print(json.dumps({'verified':False,'error':exc.code if isinstance(exc,AuthorityError) else 'operator_io_unavailable',
            'recommendation':'preserve_artifacts_and_protected_anchors_no_automatic_retry',
            'mutation_outcome':'reconciliation_required' if mutation else 'none','operation_id':args.operation_id or args.reconcile_restore,
            'execution_enabled':False}))
        return 1
    finally:
        if ledger is not None:ledger.close()


if __name__=='__main__':raise SystemExit(main())

"""Quiesced offline diagnostics, without application/provider startup.

Checkpoint key bytes arrive only through an explicitly inherited descriptor.
No secret path, environment lookup, enrollment, recovery mutation or retry.
"""
import argparse
import json
import os
import sys
from app.agent.authority import AuthorityError
from app.agent.ledger import LedgerGuard
from app.agent.recovery import inspect_offline
from app.agent.runtime import SERVICE_ACTOR


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',required=True)
    parser.add_argument('--checkpoints')
    parser.add_argument('--store-id')
    parser.add_argument('--key-fd',type=int)
    parser.add_argument('--task-id')
    parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--offset',type=int,default=0)
    args=parser.parse_args(argv)
    try:
        configured=(args.checkpoints is not None,args.store_id is not None,args.key_fd is not None)
        if any(configured) and not all(configured):raise AuthorityError('complete_checkpoint_configuration_required')
        ledger=None
        if all(configured):
            if args.key_fd<3:raise AuthorityError('invalid_key_descriptor')
            raw=os.read(args.key_fd,129)
            if not 32<=len(raw)<=128:raise AuthorityError('invalid_ledger_key')
            ledger=LedgerGuard(args.checkpoints,raw,args.store_id)
        result=inspect_offline(args.database,SERVICE_ACTOR,ledger=ledger,task_id=args.task_id,limit=args.limit,offset=args.offset)
        print(json.dumps(result,indent=2))
        return 0 if result['consistent'] else 1
    except (AuthorityError,OSError) as exc:
        print(json.dumps({'consistent':False,'error':exc.code if isinstance(exc,AuthorityError) else 'operator_io_unavailable',
                          'recommendation':'preserve_store_and_checkpoints_investigate_no_retry','mutated':False}))
        return 1


if __name__=='__main__':raise SystemExit(main())

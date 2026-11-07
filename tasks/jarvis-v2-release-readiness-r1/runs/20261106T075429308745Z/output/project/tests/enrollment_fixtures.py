"""Synthetic external provisioning fixtures; not application trust generation."""
from datetime import UTC,datetime,timedelta
from pathlib import Path
import uuid
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits
from app.agent.enrollment import OfflineEnrollment, EMPTY_HEAD, policy
from app.agent.runtime import SERVICE_ACTOR

KEY=b'synthetic-sprint4-ledger-key-000000000000'
OPKEY=b'synthetic-sprint4-operator-key-000000000'
def uid(): return str(uuid.uuid4())

def build(root, *, fault_hook=None):
    root=Path(root);root.mkdir(mode=0o700,parents=True,exist_ok=True)
    for name in ('custody','anchors'):(root/name).mkdir(mode=0o700)
    g=LedgerGuard(root/'anchors',KEY,uid(),initialize=True,rollover=True,epoch_capacity=4,recovery=True)
    now=datetime.now(UTC)
    r=dict(format='jarvis-empty-store-reservation-v1',enrollment_id=uid(),store_id=g.store_id,key_id=g.key_id,
           destination=str(root/'new-store'),custody=str(root/'custody'),checkpoints=str(g.directory),trust_id=uid(),
           policy=policy(g),initial_checkpoint=EMPTY_HEAD,issued_at=(now-timedelta(seconds=1)).isoformat(),
           expires_at=(now+timedelta(minutes=4)).isoformat(),disposable_only=True)
    permits=OperatorPermits(OPKEY);service=OfflineEnrollment(g,root/'custody',r,permits,fault_hook=fault_hook)
    permit=permits.issue(request_id=r['enrollment_id'],principal='synthetic-operator',scope=SERVICE_ACTOR.scope,
                         command='enroll_authority',payload=service.payload,checkpoint=EMPTY_HEAD,
                         issued_at=r['issued_at'],expires_at=r['expires_at'])
    g.acquire(root/'new-store/state.sqlite')
    return service,permit

def reopen(root,reservation,*,fault_hook=None):
    g=LedgerGuard(Path(root)/'anchors',KEY,reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    g.acquire(Path(root)/'new-store/state.sqlite')
    return OfflineEnrollment(g,Path(root)/'custody',reservation,fault_hook=fault_hook)

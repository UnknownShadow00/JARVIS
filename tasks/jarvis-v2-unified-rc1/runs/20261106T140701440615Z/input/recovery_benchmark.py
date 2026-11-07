"""Bounded real SQLite/HMAC/checkpoint costs; no executors or model calls."""
import json
from pathlib import Path
import statistics
import time


def run():
    from app.agent.authority import Authority
    from app.agent.ledger import LedgerGuard
    from app.agent.recovery import OperatorPermits
    from app.agent.recovery_decisions import RecoveryRegistry,verify_receipt
    from app.agent.enrollment import fingerprint
    from app.agent.runtime import SERVICE_ACTOR as actor
    from enrollment_fixtures import build,uid,KEY,OPKEY
    from recovery_application import provision,permit,interval
    results=[]
    for count in (0,8,32):
        root=Path('/work/recovery-benchmark-'+str(count));s,p=build(root)
        enrolled=s.enroll(actor,p,disposable=True);s.guard.close()
        g=LedgerGuard(root/'anchors',KEY,s.reservation['store_id'],rollover=True,epoch_capacity=4,recovery=True)
        a=Authority(root/'new-store/state.sqlite',ledger=g,enrollment_context=enrolled['witness'])
        start,end=interval();g.trust_context=g.trust_reference(valid_from=start,expires_at=end)
        config,external=provision(g,root);registry=RecoveryRegistry(g,config,external,OperatorPermits(OPKEY))
        op=uid();registry.apply(actor,op,'initialize',config,permit(g,op,'initialize',config),initialize=True)
        costs=[];latest=None
        for i in range(count):
            a.submit(actor,uid(),'held benchmark work')
            external=registry.inspect()['reference'];registry.reference=external
            start,end=interval();body={'previous_witness':external['witness'],
                'next_reference':g.trust_reference(valid_from=start,expires_at=end)}
            op=uid();grant=permit(g,op,'renew',body);beg=time.perf_counter()
            latest=registry.apply(actor,op,'renew',body,grant);costs.append(time.perf_counter()-beg)
        samples=[]
        for _ in range(12):
            beg=time.perf_counter();status=registry.inspect();samples.append(time.perf_counter()-beg)
        reopened=RecoveryRegistry(g,config,status['reference'],OperatorPermits(OPKEY));beg=time.perf_counter()
        assert reopened.inspect()['reference']==status['reference'];restart=time.perf_counter()-beg
        if latest:
            receipt=latest['receipt'];verify_receipt(g,receipt,registry_id=config['registry_id'],request_id=op,
                payload_sha256=fingerprint(body),event_sha256=fingerprint(receipt['event']),permits=OperatorPermits(OPKEY))
        results.append({'renewals':count,'events':status['event_count'],'epoch':g._epoch,
            'inspection_samples':len(samples),'inspection_median_seconds':statistics.median(samples),
            'inspection_max_seconds':max(samples),'renewal_median_seconds':statistics.median(costs) if costs else None,
            'renewal_max_seconds':max(costs) if costs else None,'restart_seconds':restart,
            'sqlite_bytes':registry.database.stat().st_size,'custody_bytes':sum(p.stat().st_size for p in registry.custody.iterdir()),
            'held_source_tasks':len(a.list_tasks(actor)),'execution_enabled':False,'activation_authorized':False})
        assert len(a.list_tasks(actor))==count
        a.close()
    return results

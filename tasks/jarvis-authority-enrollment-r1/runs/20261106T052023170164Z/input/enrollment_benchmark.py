"""Bounded actual enrollment/restoration costs in the existing offline cage."""
from datetime import UTC,datetime,timedelta
from pathlib import Path
import resource
import time

def run():
    from enrollment_fixtures import build,uid,KEY,OPKEY
    from app.agent.authority import Authority
    from app.agent.ledger import LedgerGuard
    from app.agent.recovery import OperatorPermits,RecoveryActions
    from app.agent.execution import ExecutionPipeline,SimulatedPolicy
    from app.agent.archive_restore import ArchiveRestorer
    from app.agent.branch_verification import BranchVerifier
    from app.agent.runtime import SERVICE_ACTOR as actor
    rows=[]
    def timed(fn):
        start=time.perf_counter();result=fn();return time.perf_counter()-start,result
    for count in (0,16,64):
        root=Path('/work/enrollment-benchmark')/str(count)
        s,p=build(root)
        enrollment,enrolled=timed(lambda:s.enroll(actor,p,disposable=True))
        verification,_=timed(s.verify);checkpoint,_=timed(s.guard.history)
        s.guard.close()
        def owner():
            g=LedgerGuard(s.guard.directory,KEY,s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True)
            return Authority(s.destination/'state.sqlite',ledger=g,enrollment_context=enrolled['witness'],allow_simulation=True)
        first_open,a=timed(owner);g=a._ledger
        pipeline=ExecutionPipeline(a,SimulatedPolicy(actor.scope),enabled=True);op=uid()
        pipeline.submit(actor,op,'uncertain benchmark','synthetic.echo',{'value':'undispatched'},(datetime.now(UTC)+timedelta(minutes=3)).isoformat())
        pipeline._claim(actor,op);pipeline._unknown(actor,op,a.generation,'uncertain');a.cancel(actor,uid(),op)
        populate,_=timed(lambda:[a.submit(actor,uid(),'held') for _ in range(count)])
        exports=root/'exports';targets=root/'targets';exports.mkdir(mode=0o700);targets.mkdir(mode=0o700)
        permits=OperatorPermits(OPKEY);actions=RecoveryActions(a,permits)
        def grant(request_id,command,payload):
            now=datetime.now(UTC)
            return permits.issue(request_id=request_id,principal='synthetic-benchmark',scope=actor.scope,command=command,payload=payload,checkpoint=g.history()[0],issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
        export_id=uid();export_time,export=timed(lambda:actions.export(actor,export_id,exports,grant(export_id,'export_ledger',{'export_id':export_id,'destination':str(exports)})))
        now=datetime.now(UTC);g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=3)).isoformat())
        restore_id=uid();manifest=export['export']['manifest_sha256']
        restore_time,restored=timed(lambda:ArchiveRestorer(g,permits).restore(actor,restore_id,exports/export_id,targets,manifest,grant(restore_id,'restore_archive',{'export_id':export_id,'manifest_sha256':manifest,'target_parent':str(targets),'restore_id':restore_id}),disposable=True))
        request=dict(format='jarvis-branch-verification-request-v1',branch_id=uid(),operator_id='synthetic-benchmark',expected_source_head=g.history()[0],
                     expected_restore_id=restore_id,expected_database_sha256=restored['database_sha256'],expected_source_lineage=restored['source_lineage'],
                     expected_key_id=g.key_id,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat(),reserved_branch_ids=[],decision='PROPOSE_ONLY')
        branch_time,branch=timed(lambda:BranchVerifier(g).verify(targets/restore_id,request))
        assert branch['summary']['unknown']==1 and branch['summary']['cancel_requested']==1 and not branch['proposal']['activation_authorized']
        generations=g._epoch+1;a.close()
        restart,a=timed(owner)
        try:assert a.get_task(actor,op)['status']=='unknown' and a.readiness()['enrollment']['verified']
        finally:a.close()
        files=[f for f in root.rglob('*') if f.is_file()]
        rows.append(dict(held_tasks=count,unknown_tasks=1,enrollment_seconds=enrollment,enrollment_verify_seconds=verification,
            checkpoint_verify_seconds=checkpoint,first_owner_seconds=first_open,populate_seconds=populate,export_seconds=export_time,
            restore_seconds=restore_time,branch_verify_seconds=branch_time,restart_seconds=restart,generations=generations,
            files=len(files),apparent_bytes=sum(f.stat().st_size for f in files),allocated_bytes=sum(f.stat().st_blocks*512 for f in files),
            process_cumulative_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,uncertain_reexecution_count=0))
    return rows

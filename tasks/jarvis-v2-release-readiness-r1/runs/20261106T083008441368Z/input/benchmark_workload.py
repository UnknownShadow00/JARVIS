"""Bounded synthetic state/history benchmark; never imports providers or runtime."""
from datetime import UTC,datetime,timedelta
import json
from pathlib import Path
import resource
import statistics
import time
import uuid

from app.agent.authority import Authority
from synthetic_authority import fixture_authority as Authority
from app.agent.ledger import LedgerGuard
from app.agent.execution import ExecutionPipeline,SimulatedPolicy
from app.agent.recovery import OperatorPermits,RecoveryActions
from app.agent.archive_restore import ArchiveRestorer
from app.agent.runtime import SERVICE_ACTOR as ACTOR

KEY=b'synthetic-benchmark-checkpoint-key-only-000000'
OPKEY=b'synthetic-benchmark-operator-key-only-00000000'


def key():return str(uuid.uuid4())


def sample(fn,repeats=3):
    values=[];value=None
    for _ in range(repeats):
        start=time.perf_counter();value=fn();values.append(time.perf_counter()-start)
    return {'seconds':values,'median_seconds':statistics.median(values)},value


def usage(root):
    files=[p for p in root.rglob('*') if p.is_file() and not p.is_symlink()]
    return {'files':len(files),'apparent_bytes':sum(p.stat().st_size for p in files),'allocated_bytes':sum(p.stat().st_blocks*512 for p in files)}


def run():
    rows=[]
    for case,count,transactions,capacity in [('state16',16,8,16),('state128',128,32,16),('state512',512,64,16),('history256',16,256,32)]:
        root=Path('/work/benchmarks')/case;root.mkdir(mode=0o700,parents=True)
        exports=root/'exports';targets=root/'targets';exports.mkdir(mode=0o700);targets.mkdir(mode=0o700)
        store=key();anchors=root/'protected';db=root/'db'/'state.sqlite'
        g=LedgerGuard(anchors,KEY,store,initialize=True,rollover=True,epoch_capacity=capacity,recovery=True)
        start=time.perf_counter();a=Authority(db,allow_simulation=True,ledger=g);creation=time.perf_counter()-start
        p=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True);unknown_id=key()
        p.submit(ACTOR,unknown_id,'uncertain benchmark','synthetic.echo',{'value':'never dispatched'},(datetime.now(UTC)+timedelta(minutes=5)).isoformat())
        p._claim(ACTOR,unknown_id);p._unknown(ACTOR,unknown_id,a.generation,'synthetic_uncertain')
        start=time.perf_counter()
        seed_tasks=[{'task_id':f'synthetic-legacy-{i:06}','goal':'bounded synthetic benchmark payload','status':'pending'} for i in range(count)]
        # Explicit test-only historical fixture, preserving the protected marker.
        # The product migration gate is unchanged and no source file is imported.
        def seed_history(scope):
            mapping={}
            for old in seed_tasks:
                task_id=str(uuid.uuid5(uuid.UUID(store),old['task_id']))
                mapping[old['task_id']]=task_id
                a._new_task(scope,task_id,old['goal'],metadata={'legacy':old,'synthetic_benchmark':True})
            return {'task_ids':mapping,'schedule_ids':{},'tasks_imported':len(mapping),'schedules_imported':0,'evidence':{'synthetic_benchmark':True}}
        imported=a._mutate(ACTOR,key(),'import_legacy_snapshot',{'tasks':seed_tasks,'schedules':[],'evidence':{'synthetic_benchmark':True}},seed_history)
        seed=time.perf_counter()-start
        generation_times=[];rollover_times=[]
        for _ in range(transactions):
            epoch=g._epoch;start=time.perf_counter();a.scheduler_control(ACTOR,key(),False);elapsed=time.perf_counter()-start
            (rollover_times if g._epoch!=epoch else generation_times).append(elapsed)
        # Both measurements use warmed filesystem pages and identical state;
        # cache hits still read/hash every file and hash the complete SQLite state.
        g.cache_verified=False;g.verify(a._conn)
        uncached,_=sample(lambda:g.verify(a._conn))
        g.cache_verified=True;g._verified_cache.clear();g.verify(a._conn)
        hits=g.cache_hits;cached,_=sample(lambda:g.verify(a._conn));cache_hits=g.cache_hits-hits
        query,_=sample(lambda:a.task_page(ACTOR,limit=20))
        raw_sql,_=sample(lambda:a._conn.execute("SELECT r.data FROM records r JOIN outbox o ON r.id=o.task_id WHERE r.kind='task' AND r.scope=? ORDER BY r.rowid LIMIT 20",(ACTOR.scope,)).fetchall())
        issuer=OperatorPermits(OPKEY);actions=RecoveryActions(a,issuer)
        def permit(command,payload,op,head):
            now=datetime.now(UTC)
            return issuer.issue(request_id=op,principal='synthetic-benchmark-operator',scope=ACTOR.scope,command=command,payload=payload,checkpoint=head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
        export_id=key();payload={'export_id':export_id,'destination':str(exports)}
        start=time.perf_counter();exported=actions.export(ACTOR,export_id,exports,permit('export_ledger',payload,export_id,g._head));export_seconds=time.perf_counter()-start
        now=datetime.now(UTC);reference=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat());g.trust_context=reference
        restore_id=key();payload={'export_id':export_id,'manifest_sha256':exported['export']['manifest_sha256'],'target_parent':str(targets),'restore_id':restore_id}
        start=time.perf_counter();restored=ArchiveRestorer(g,issuer).restore(ACTOR,restore_id,exports/export_id,targets,exported['export']['manifest_sha256'],permit('restore_archive',payload,restore_id,g._head),disposable=True);restore_seconds=time.perf_counter()-start
        assert restored['summary']['unknown']==1 and not restored['execution_enabled']
        byte_count=exported['export']['files']['state.jsonl']['bytes'];head=g._head.copy();epochs=g._epoch+1
        a.close()
        restarted_guard=LedgerGuard(anchors,KEY,store,rollover=True,epoch_capacity=capacity,recovery=True,trust_context=reference)
        start=time.perf_counter();a=Authority(db,allow_simulation=True,ledger=restarted_guard);startup=time.perf_counter()-start
        pipeline=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
        start=time.perf_counter();reconciled=pipeline.reconcile(ACTOR);reconciliation=time.perf_counter()-start
        assert reconciled==[] and a.get_task(ACTOR,unknown_id)['status']=='unknown'
        a.close()
        rows.append({'case':case,'epoch_capacity':capacity,'tasks':count+1,'history_mutations':transactions,'checkpoint_head_before_restart':head,'generations':epochs,
            'creation_seconds':creation,'seed_seconds':seed,'checkpoint_commit_seconds':generation_times,'rollover_commit_seconds':rollover_times,
            'checkpoint_commit_median_seconds':statistics.median(generation_times),
            'rollover_commit_median_seconds':statistics.median(rollover_times) if rollover_times else None,
            'verification_uncached':uncached,'verification_cached':cached,'cache_hash_validated_hits':cache_hits,
            'verification_speedup':uncached['median_seconds']/cached['median_seconds'],
            'protected_query':query,'raw_sql_component':raw_sql,'export_seconds':export_seconds,'restore_seconds':restore_seconds,
            'logical_export_bytes':byte_count,'export_bytes_per_second':byte_count/export_seconds,'restore_bytes_per_second':byte_count/restore_seconds,
            'startup_seconds':startup,'uncertain_reconciliation_seconds':reconciliation,'uncertain_reexecution_count':0,
            'storage':usage(root),'process_cumulative_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024})
        Path('/work/BENCHMARK-PROGRESS.json').write_text(json.dumps({'completed_cases':rows},indent=2)+'\n')
    result={'format':'jarvis-offline-audit-benchmark-v1','synthetic_only':True,'sizes':[17,129,513,17],'samples':rows,
        'notes':['Warmed filesystem, three verification/query samples; no physical cold-cache or production throughput claim.',
                 'Cache keys are SHA256 of every freshly read file, never mtime-only. Full SQLite state is still hashed.',
                 'RSS is cumulative process peak, not a per-case allocation delta. Limits are inherited unchanged from the guarded runner.',
                 'Rollover overhead is measured inside real checkpoint commits, including transaction/intent/final fsync.']}
    Path('/work/BENCHMARKS.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

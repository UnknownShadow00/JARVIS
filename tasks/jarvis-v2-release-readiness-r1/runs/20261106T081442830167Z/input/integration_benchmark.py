"""Bounded actual synthetic IPC, Authority and authenticated history costs."""
from pathlib import Path
import statistics
import time


def run():
    from transport_fixtures import provision,opened,request,ACTOR
    results=[]
    for count in (1,4,8):
        state=provision(Path('/work/transport-benchmark-'+str(count)));a,p,t=opened(state)
        try:
            admissions=[];dispatches=[]
            for i in range(count):
                body=request(p,value='bounded-'+str(i));start=time.perf_counter();p.submit(ACTOR,**body);admissions.append(time.perf_counter()-start)
                start=time.perf_counter();receipt=p.run_once(ACTOR);dispatches.append(time.perf_counter()-start)
                assert receipt['result']['status']=='simulated_completed'
            samples=[]
            for _ in range(5):
                start=time.perf_counter();assert a.readiness()['execution_transport']['history_verified'];samples.append(time.perf_counter()-start)
            results.append({'tasks':count,'endpoint_invocations':t.invocations,'admission_median_seconds':statistics.median(admissions),
                'dispatch_and_durable_publication_median_seconds':statistics.median(dispatches),'authenticated_readiness_median_seconds':statistics.median(samples),
                'authenticated_readiness_max_seconds':max(samples),'source_sqlite_bytes':a.path.stat().st_size,
                'checkpoint_sequence':a._ledger.history()[0]['sequence'],'generation':a.generation,'real_execution_enabled':False})
            assert t.invocations==count and len(a.list_tasks(ACTOR))==count
        finally:a.close()
    return results

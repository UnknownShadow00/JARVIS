from pathlib import Path
from datetime import UTC,datetime,timedelta
import uuid,json
from synthetic_authority import fixture_authority
from app.agent.authority import Actor,AuthorityError
from app.agent.execution import ExecutionPipeline,SimulatedPolicy,ExecutorRegistry,SyntheticExecutor

def uid():return str(uuid.uuid4())
def err(fn,code):
 try:fn()
 except AuthorityError as e:
  assert e.code==code,(e.code,code)
  return e.code
 raise AssertionError('expected '+code)
root=Path('/scratch/state');root.mkdir(mode=0o700)
a=fixture_authority(root/'queue.sqlite',allow_simulation=True)
actor=Actor('local-service');other=Actor('different-scope');results={}
try:
 op=uid();first=a.submit(actor,op,'fixture goal');replay=a.submit(actor,op,'fixture goal')
 assert replay['replayed'] and replay['result']==first['result']
 results['same_request_replay_once']=a._conn.execute('SELECT count(*) FROM records WHERE kind=\'task\'').fetchone()[0]
 results['payload_conflict']=err(lambda:a.submit(actor,op,'changed goal'),'request_conflict')
 results['scope_conflict']=err(lambda:a.submit(other,op,'fixture goal'),'request_conflict')
 results['scope_read_denied']=err(lambda:a.get_task(other,op),'not_found')
 a.cancel(actor,uid(),op)
 p=ExecutionPipeline(a,SimulatedPolicy(actor.scope),enabled=True,max_pending=1)
 def submit(cap='synthetic.echo'):
  op=uid();p.submit(actor,op,'offline fixture',cap,{'value':'harmless'},(datetime.now(UTC)+timedelta(minutes=1)).isoformat());return op
 op=submit();results['capacity_denied']=err(submit,'queue_capacity_exceeded')
 p._fault=lambda stage:a.cancel(actor,uid(),op) if stage=='after_claim' else None
 result=p.run_once(actor);assert result['result']['status']=='cancelled'
 results['cancel_after_claim']=result['result']['status']
 p._fault=lambda _:None;op=submit();p.policy=SimulatedPolicy(actor.scope,frozenset(),revision='revoked')
 result=p.run_once(actor);assert result['result']['status']=='denied';results['revocation_at_dispatch']=result['result']['status']
 class Pretend(SyntheticExecutor):pass
 results['real_or_subclass_registration']=err(lambda:ExecutorRegistry(enabled=True).register(Pretend()),'real_execution_disabled')
 results['second_writer']=err(lambda:fixture_authority(root/'queue.sqlite',allow_simulation=True),'owner_busy')
 print(json.dumps(results,sort_keys=True))
finally:a.close()

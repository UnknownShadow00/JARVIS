"""External synthetic provisioning only; never generates production trust."""
from datetime import UTC,datetime,timedelta
from pathlib import Path
from enrollment_fixtures import build,uid,KEY,OPKEY
from app.agent.authority import Authority
from app.agent.enrollment import policy
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits
from app.agent.recovery_decisions import RecoveryRegistry
from app.agent.execution import ExecutionPipeline,SimulatedPolicy,validate_spec
from app.agent.execution_transport import SyntheticTransport
from app.agent.runtime import SERVICE_ACTOR as ACTOR

EXEC_KEY=b'synthetic-v6-independent-operator-000000000000'
REQUEST_KEY=b'synthetic-v6-request-signing-key-00000000000'
RESPONSE_KEY=b'synthetic-v6-response-signing-key-0000000000'


def times(seconds=120):
    now=datetime.now(UTC)
    return (now-timedelta(seconds=1)).isoformat(),(now+timedelta(seconds=seconds)).isoformat()


def provision(root):
    root=Path(root);s,p=build(root)
    s.guard.epoch_capacity=64;s.reservation['policy']=policy(s.guard)
    r=s.reservation
    p=s.permits.issue(request_id=r['enrollment_id'],principal='synthetic-v6-enroller',scope=ACTOR.scope,
        command='enroll_authority',payload=s.payload,checkpoint=r['initial_checkpoint'],issued_at=r['issued_at'],expires_at=r['expires_at'])
    enrolled=s.enroll(ACTOR,p,disposable=True);s.guard.close()
    g=LedgerGuard(root/'anchors',KEY,r['store_id'],rollover=True,epoch_capacity=64,recovery=True)
    a=Authority(root/'new-store/state.sqlite',ledger=g,enrollment_context=enrolled['witness'],allow_simulation=True)
    start,end=times();trust=g.trust_reference(valid_from=start,expires_at=end);g.trust_context=trust
    for name in ('registry-data','registry-custody'):(root/name).mkdir(mode=0o700)
    config={'format':'jarvis-recovery-registry-v1','registry_id':uid(),'store_id':g.store_id,'key_id':g.key_id,
        'database':str(root/'registry-data/registry.sqlite'),'custody':str(root/'registry-custody'),
        'checkpoints':str(g.directory),'initial_reference':trust,'capacity':128,'disposable_only':True}
    ref={'registry_id':config['registry_id'],'sequence':0,'event_sha256':'0'*64,
         'witness':{'renewal_id':None,'checkpoint':trust}}
    registry=RecoveryRegistry(g,config,ref,OperatorPermits(OPKEY));op=uid()
    registry.apply(ACTOR,op,'initialize',config,OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-v6-registry-operator',
        scope=ACTOR.scope,command='recovery_initialize',payload=config,checkpoint=g.history()[0],issued_at=start,expires_at=end),initialize=True)
    state={'root':str(root),'database':str(a.path),'enrollment':enrolled,'config':config,'reference':registry.inspect()['reference'],'trust':trust}
    a.close()
    return state


def opened(state,*,fault_hook=None,endpoint_id="synthetic.local.echo-v1"):
    g=LedgerGuard(state['config']['checkpoints'],KEY,state['config']['store_id'],rollover=True,epoch_capacity=64,recovery=True,trust_context=state['trust'])
    registry=RecoveryRegistry(g,state['config'],state['reference'],OperatorPermits(OPKEY))
    a=Authority(state['database'],ledger=g,enrollment_context=state['enrollment']['witness'],allow_simulation=True,recovery_registry=registry)
    transport=SyntheticTransport(endpoint_id,OperatorPermits(EXEC_KEY),REQUEST_KEY,RESPONSE_KEY,enabled=True,fault_hook=fault_hook)
    pipeline=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True,transport=transport)
    return a,pipeline,transport


def request(pipeline,*,operation_id=None,value='synthetic-safe',seconds=120,timeout_seconds=10,capability='synthetic.echo'):
    op=operation_id or uid();start,end=times(seconds)
    spec=validate_spec(capability,{'value':value},end,timeout_seconds)
    body={'request_id':op,'goal':'synthetic authenticated transport','capability':spec['capability'],
          'payload':spec['payload'],'expires_at':spec['expires_at'],'timeout_seconds':timeout_seconds}
    binding=pipeline.transport.binding(pipeline.authority,ACTOR,op,body['goal'],spec)
    permit=OperatorPermits(EXEC_KEY).issue(request_id=op,principal='synthetic-v6-independent-execution-operator',scope=ACTOR.scope,
        command='dispatch_synthetic_transport',payload=binding,checkpoint=pipeline.authority._ledger.history()[0],issued_at=start,expires_at=end)
    return {**body,'transport_permit':permit}

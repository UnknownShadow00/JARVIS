"""Parent sandbox only: synthetic registry/runtime lifecycle and CLI refusals."""
import contextlib,io,json,sqlite3,uuid
from pathlib import Path
from datetime import UTC,datetime,timedelta
from app.agent.authority import Actor,AuthorityError
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits,OperatorRecovery
from app.agent.recovery_decisions import RecoveryRegistry
from app.agent import recovery_decisions as decisions, runtime, operator_cli
from synthetic_authority import fixture_authority

def uid():return str(uuid.uuid4())
def refused(fn,code):
    try:fn()
    except AuthorityError as exc:
        assert exc.code==code,(exc.code,code)
        return exc.code
    raise AssertionError('expected '+code)
root=Path('/scratch/runtime-integration');root.mkdir(mode=0o700)
for name in ('registry-data','registry-custody'):(root/name).mkdir(mode=0o700)
g=LedgerGuard(root/'anchors',b'synthetic-audit-checkpoint-key-000000000000',uid(),initialize=True,rollover=True,epoch_capacity=4,recovery=True)
a=fixture_authority(root/'source/state.sqlite',ledger=g)
now=datetime.now(UTC);start=(now-timedelta(seconds=1)).isoformat();end=(now+timedelta(seconds=120)).isoformat()
reference=g.trust_reference(valid_from=start,expires_at=end);g.trust_context=reference
config=dict(format='jarvis-recovery-registry-v1',registry_id=uid(),store_id=g.store_id,key_id=g.key_id,database=str(root/'registry-data/registry.sqlite'),custody=str(root/'registry-custody'),checkpoints=str(g.directory),initial_reference=reference,capacity=16,disposable_only=True)
external=dict(registry_id=config['registry_id'],sequence=0,event_sha256='0'*64,witness=dict(renewal_id=None,checkpoint=reference))
permits=OperatorPermits(b'synthetic-audit-operator-key-00000000000000')
s=RecoveryRegistry(g,config,external,permits)
op=uid();permit=permits.issue(request_id=op,principal='synthetic-audit-operator',scope=runtime.SERVICE_ACTOR.scope,command='recovery_initialize',payload=config,checkpoint=g.history()[0],issued_at=start,expires_at=end)
s.apply(runtime.SERVICE_ACTOR,op,'initialize',config,permit,initialize=True)
# Trusted embedding supplies the registry; no runtime/API input can assign it.
a._recovery_registry=s
runtime.bind_authority(a)
out={}
try:
    ready=a.readiness();summary=ready['recovery_decisions']
    assert summary['verified'] and summary['execution_enabled'] is False and summary['activation_authorized'] is False
    assert 'proposals' not in summary and 'reference' not in summary
    out['readiness_aggregate_only']=True
    report=OperatorRecovery(a).diagnose(runtime.SERVICE_ACTOR,limit=1)
    assert report['recovery_decisions']['history_verified'] and report['recovery_mutations_publicly_enabled'] is False
    out['operator_diagnostic_nonactivating']=True
    out['different_scope_diagnostics']=refused(lambda:OperatorRecovery(a).diagnose(Actor('remote-client')),'operator_scope_required')
    original_datetime=decisions.datetime
    class Future(datetime):
        @classmethod
        def now(cls,tz=None):return datetime.now(tz)+timedelta(seconds=130)
    decisions.datetime=Future
    try:
        assert s.inspect()['state']=='WITNESS_EXPIRED'
        out['expired_witness_readiness']=refused(a.readiness,'recovery_reconciliation_required')
    finally:decisions.datetime=original_datetime
    output=io.StringIO()
    with contextlib.redirect_stdout(output):
        status=operator_cli.main(['--record-recovery-decision','--checkpoints','/scratch/never-opened','--store-id',uid(),'--key-fd','3'])
    assert status==1 and json.loads(output.getvalue())['error']=='explicit_recovery_commit_required'
    assert not Path('/scratch/never-opened').exists()
    out['cli_missing_commit_refused_before_paths_or_descriptors']=True
    original_inspect=s.inspect
    def failed_inspection():raise AuthorityError('synthetic_close_inspection_failure')
    s.inspect=failed_inspection
    out['close_preserves_failure']=refused(runtime.close_authority,'synthetic_close_inspection_failure')
    assert runtime._authority is None and g._fd is None
    try:a._conn.execute('SELECT 1')
    except sqlite3.ProgrammingError:out['close_releases_sqlite_and_ledger_even_on_inspection_failure']=True
    else:raise AssertionError('SQLite left open')
    print(json.dumps(out,sort_keys=True))
finally:
    s.inspect=original_inspect if 'original_inspect' in globals() else s.inspect
    if runtime._authority is not None:runtime.close_authority()

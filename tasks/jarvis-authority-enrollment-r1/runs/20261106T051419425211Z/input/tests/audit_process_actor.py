"""Independent cage-only rollover/restore/attestation crash actor."""
from datetime import UTC,datetime,timedelta
import json
from pathlib import Path
import sys,time
if not Path('/input/source').is_dir():raise SystemExit('isolated runner required')
sys.path[:0]=['/input/source','/input','/deps']
from app.agent.authority import Authority
from synthetic_authority import fixture_authority as Authority
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits,RecoveryActions
from app.agent.archive_restore import ArchiveRestorer
from app.agent.runtime import SERVICE_ACTOR as ACTOR

KEY=b'synthetic-sprint3-ledger-only-key-00000000';OPKEY=b'synthetic-sprint3-operator-only-key-000000'
config=json.loads(Path(sys.argv[1]).read_text());armed=False

def fault(stage):
    if armed and stage==config['stage']:
        Path(config['ready']).write_text(stage)
        deadline=time.monotonic()+4
        while time.monotonic()<deadline:time.sleep(.01)
        raise RuntimeError('parent did not terminate owned actor')

g=LedgerGuard(config['anchors'],KEY,config['store_id'],initialize=True,rollover=True,epoch_capacity=4,recovery=True,fault_hook=fault)
a=Authority(config['db'],allow_simulation=True,ledger=g)
issuer=OperatorPermits(OPKEY);actions=RecoveryActions(a,issuer)

def context():
    now=datetime.now(UTC)
    value=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
    Path(config['context']).write_text(json.dumps(value));return value

def issue(command,payload,request_id,head):
    now=datetime.now(UTC)
    return issuer.issue(request_id=request_id,principal='synthetic-operator',scope=ACTOR.scope,command=command,payload=payload,checkpoint=head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())

if config['mode']=='rollover_recovery':
    a.submit(ACTOR,config['task_id'],'one');a.submit(ACTOR,config['extra_id'],'two')
    ref=context()
    def interrupt(stage):
        if stage=='rollover_intent_durable':raise RuntimeError('stop before link')
    g._fault=interrupt
    try:a.submit(ACTOR,config['failed_request_id'],'interrupted')
    except RuntimeError:pass
    a.close()
    g=LedgerGuard(config['anchors'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref,fault_hook=fault)
    g.acquire(config['db'])
    body=json.loads((Path(config['anchors'])/'rollover-0001.intent.json').read_text())['body']
    permit=issue('resume_rollover',{'operation_id':body['operation_id']},config['request_id'],ref['head'])
    armed=True
    g.resume_rollover(permit,issuer,ACTOR,config['request_id'])
elif config['mode']=='rollover':
    a.submit(ACTOR,config['task_id'],'one');a.submit(ACTOR,config['extra_id'],'two')
    context();armed=True
    a.submit(ACTOR,config['request_id'],'interrupted rollover')
else:
    a.submit(ACTOR,config['task_id'],'held and never executed')
    export_id=config['export_id'];payload={'export_id':export_id,'destination':config['exports']}
    if config['mode']=='attestation':context();armed=True
    result=actions.export(ACTOR,export_id,config['exports'],issue('export_ledger',payload,export_id,g._head))
    ref=context();a.close()
    g=LedgerGuard(config['anchors'],KEY,config['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)
    g.acquire(Path(config['targets'])/'unused.sqlite')
    restore_id=config['request_id'];payload={'export_id':export_id,'manifest_sha256':result['export']['manifest_sha256'],'target_parent':config['targets'],'restore_id':restore_id}
    permit=issue('restore_archive',payload,restore_id,ref['head'])
    armed=True
    ArchiveRestorer(g,issuer,fault_hook=fault).restore(ACTOR,restore_id,Path(config['exports'])/export_id,config['targets'],result['export']['manifest_sha256'],permit,disposable=True)
raise SystemExit('requested crash stage not reached')

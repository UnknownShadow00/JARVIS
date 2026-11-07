"""Cage-only independent crash actor. Keys and state are synthetic fixtures."""
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import sys
import time

if not Path('/input/source').is_dir():raise SystemExit('isolated runner required')
sys.path[:0]=['/input/source','/deps']
from app.agent.authority import Authority
from app.agent.execution import ExecutionPipeline, SimulatedPolicy, phase_id
from app.agent.ledger import LedgerGuard
from app.agent.recovery import RecoveryActions, OperatorPermits
from app.agent.runtime import SERVICE_ACTOR as ACTOR

KEY=b'synthetic-ledger-test-key-only-000000000000'
PERMIT=b'synthetic-operator-test-key-only-000000000'
config=json.loads(Path(sys.argv[1]).read_text())
mode,stage=config['mode'],config['stage']
armed=mode=='bootstrap'
a=None

def hold():
    Path(config['ready']).write_text(stage)
    end=time.monotonic()+4
    while time.monotonic()<end:time.sleep(.01)
    raise RuntimeError('parent did not kill owned actor')

def guard_fault(current):
    if armed and stage==current:hold()

def sql_fault(current):
    if not armed:return
    if mode in {'retention','reconcile'}:
        expected=config['request_id'] if mode=='retention' else phase_id(config['task_id'],'publish')
        if not a._conn.execute('SELECT 1 FROM receipts WHERE request_id=?',(expected,)).fetchone():return
    if current==stage:hold()

def open_authority(initialize):
    g=LedgerGuard(config['anchors'],KEY,config['store_id'],initialize=initialize,fault_hook=guard_fault)
    a=Authority(config['db'],allow_simulation=True,ledger=g,fault_hook=sql_fault)
    p=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
    return a,p,g

def issue(command,payload,request_id):
    now=datetime.now(UTC)
    return issuer.issue(request_id=request_id,principal='synthetic-operator',scope=ACTOR.scope,command=command,payload=payload,
                        checkpoint=g._head,issued_at=now.isoformat(),expires_at=(now+timedelta(seconds=1)).isoformat())

a,p,g=open_authority(True)
issuer=OperatorPermits(PERMIT);actions=RecoveryActions(a,issuer)
if mode=='bootstrap':raise SystemExit('bootstrap crash stage not reached')
if mode=='mutation':
    armed=True
    a.submit(ACTOR,config['request_id'],'crash admission')
else:
    p.submit(ACTOR,config['task_id'],'crash ledger fixture','synthetic.echo',{'value':'protected outcome'},(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
    if mode=='reconcile':
        p._fault=lambda current: (_ for _ in ()).throw(RuntimeError('stop after record')) if current=='after_record' else None
        try:p.run_once(ACTOR)
        except RuntimeError:pass
        a.close();a,p,g=open_authority(False)
        armed=True
        p.reconcile(ACTOR)
    else:
        p.run_once(ACTOR)
        export_id=config['export_id']
        token=issue('export_ledger',{'export_id':export_id,'destination':config['exports']},export_id)
        if mode=='export':
            armed=True
            actions.export(ACTOR,export_id,config['exports'],token,fault_hook=lambda current:hold() if current==stage else None)
        elif mode=='retention':
            result=actions.export(ACTOR,export_id,config['exports'],token)
            cutoff=(datetime.now(UTC)+timedelta(seconds=1)).isoformat()
            payload={'export_id':export_id,'manifest_sha256':result['export']['manifest_sha256'],'older_than':cutoff}
            token=issue('prepare_archive',payload,config['request_id'])
            # Crash only the archive transaction, not its preceding export.
            armed=True
            actions.prepare_archive(ACTOR,config['request_id'],Path(config['exports'])/export_id,cutoff,token)
        else:raise SystemExit('unsupported fixture mode')
raise SystemExit('crash stage not reached')

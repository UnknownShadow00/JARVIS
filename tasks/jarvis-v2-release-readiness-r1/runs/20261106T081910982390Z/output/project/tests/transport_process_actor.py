"""Actual independent crash actor; guarded disposable runner only."""
import json
import os
from pathlib import Path
import sys
import time
sys.path[:0]=['/input/source','/input/tests','/input','/deps']
from transport_fixtures import opened,request,ACTOR
from app.agent.execution import phase_id
c=json.loads(Path(sys.argv[1]).read_text());root=Path(c['state']['root']);target=c['stage']
a,p,t=opened(c['state'])

def pause(stage):
    if stage=='transport_computed':
        with (root/'invocations.jsonl').open('a') as f:f.write(json.dumps({'operation_id':c['operation_id'],'event':'pure_computation_observed'})+'\n')
    if stage==target:
        (root/'ready').write_text(stage)
        while True:time.sleep(.02)
p._fault=t._fault=pause
r=request(p,operation_id=c['operation_id']);(root/'original-request.json').write_text(json.dumps(r));(root/'original-request.json').chmod(0o600)
if target.startswith(('reserve_','record_','publish_')):
    phase,boundary=target.split('_',1)
    ident=phase_id(c['operation_id'],'transport_reserve' if phase=='reserve' else phase)
    def authority_fault(stage):
        expected='before_commit' if boundary=='before_commit' else 'ledger_database_committed'
        if stage==expected and a._conn.execute('SELECT 1 FROM receipts WHERE request_id=?',(ident,)).fetchone():pause(target)
    a._fault=authority_fault
p.submit(ACTOR,**r)
p.run_once(ACTOR)
raise SystemExit('requested crash point not reached')

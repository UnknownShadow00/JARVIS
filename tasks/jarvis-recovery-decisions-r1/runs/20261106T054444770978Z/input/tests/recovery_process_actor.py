"""Run only inside the guarded cage, against explicit disposable state."""
import json
import sys
import time
from pathlib import Path
sys.path[:0]=['/input/source','/input/tests','/input','/deps']
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits
from app.agent.recovery_decisions import RecoveryRegistry
from app.agent.runtime import SERVICE_ACTOR
from enrollment_fixtures import KEY,OPKEY
c=json.loads(Path(sys.argv[1]).read_text());root=Path(c['root'])
def fault(stage):
    if stage==c['stage']:
        (root/'ready').write_text(stage)
        while True:time.sleep(.02)
g=LedgerGuard(c['config']['checkpoints'],KEY,c['config']['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=c['trust'])
g.acquire(c['config']['database'])
try:
    s=RecoveryRegistry(g,c['config'],c['reference'],OperatorPermits(OPKEY),fault_hook=fault)
    s.apply(SERVICE_ACTOR,c['operation_id'],c['command'],c['payload'],c['permit'])
finally:g.close()

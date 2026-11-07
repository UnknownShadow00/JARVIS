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
active_connection=None
def fault(stage):
    if stage==c['stage']:
        if c.get('force_hot_journal'):
            # Force real page spill before COMMIT, including overwritten prior
            # pages. Recovery must use SQLite's durable original rollback data.
            active_connection.execute("UPDATE events SET envelope=envelope || ?",('synthetic-uncommitted-pages'*5000,))
        (root/'ready').write_text(stage)
        while True:time.sleep(.02)
if c['stage'].startswith('partial_'):
    import os
    import app.agent.recovery_decisions as module
    original_publish=module.publish_file
    phase=c['stage'].split('_',1)[1]
    def partial(path,raw):
        if path.name.endswith('.'+phase+'.json'):
            fd=os.open(path.parent/'.stage-interrupted-witness',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            os.write(fd,raw[:len(raw)//2]);os.fsync(fd);os.close(fd)
            fault(c['stage'])
        return original_publish(path,raw)
    module.publish_file=partial
g=LedgerGuard(c['config']['checkpoints'],KEY,c['config']['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=c['trust'])
g.acquire(c['config']['database'])
try:
    s=RecoveryRegistry(g,c['config'],c['reference'],OperatorPermits(OPKEY),fault_hook=fault)
    if c.get('force_hot_journal'):
        original_connect=s._connect
        def spill(*,write=False):
            global active_connection
            conn=original_connect(write=write)
            if write:
                conn.execute('PRAGMA cache_size=1');conn.execute('PRAGMA cache_spill=1')
                active_connection=conn
            return conn
        s._connect=spill
    s.apply(SERVICE_ACTOR,c['operation_id'],c['command'],c['payload'],c['permit'],initialize=c['command']=='initialize')
finally:g.close()

"""Independent synthetic enrollment process, guarded runner only."""
import json
import sys
import time
from pathlib import Path
sys.path[:0]=['/input/source','/input/tests','/input','/deps']
from enrollment_fixtures import build
from app.agent.runtime import SERVICE_ACTOR
c=json.loads(Path(sys.argv[1]).read_text());root=Path(c['root'])
def fault(stage):
    if stage==c['stage']:
        (root/'ready').write_text(stage)
        while True:time.sleep(.02)
s,p=build(root,fault_hook=fault)
s.guard._fault=fault
(root/'reservation.json').write_text(json.dumps(s.reservation))
s.enroll(SERVICE_ACTOR,p,disposable=True)

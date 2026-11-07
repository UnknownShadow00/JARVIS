"""Independent crash helper. Only the disposable cage state path is opened."""
from pathlib import Path
import sys
import time
from datetime import UTC, datetime, timedelta

if not Path('/input/source').is_dir() or not Path('/deps').is_dir():
    raise SystemExit('isolated runner required')
sys.path[:0] = ['/input/source', '/deps']
from app.agent.authority import Authority
from app.agent.execution import ExecutionPipeline, SimulatedPolicy
from app.agent.runtime import SERVICE_ACTOR

database, ready, op, stage = sys.argv[1:]
a = Authority(database, allow_simulation=True)
def fault(current):
    if current == stage:
        Path(ready).write_text(current)
        deadline = time.monotonic()+4
        while time.monotonic()<deadline:
            time.sleep(.01)
        raise RuntimeError('parent failed to kill owned child')
p = ExecutionPipeline(a, SimulatedPolicy(SERVICE_ACTOR.scope), enabled=True, fault_hook=fault)
p.submit(SERVICE_ACTOR, op, 'crash probe', 'synthetic.echo', {'value':'crash marker'}, (datetime.now(UTC)+timedelta(minutes=1)).isoformat())
p.run_once(SERVICE_ACTOR)
raise SystemExit('fault boundary was not reached')

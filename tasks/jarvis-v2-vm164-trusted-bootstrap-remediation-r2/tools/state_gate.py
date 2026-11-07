"""Offline r2 state consistency. No live ejection edge or live action/authority."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
OLD=TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1/tools/state_validator.py'
ISO='local:iso/vm164-trusted-bootstrap-r2-09185f1f69108ab1.iso'
ISO_SHA='09185f1f69108ab18fbdf2b589c5eba9bb8b8e90c85dd92a797926b8972aa2ee'
expected=json.loads((TASK/'evidence/ENTRY.json').read_text())['predecessor_files'][str(OLD.relative_to(TASK.parents[1]))]
if hashlib.sha256(OLD.read_bytes()).hexdigest()!=expected:raise ValueError('pinned_validator_changed')
spec=importlib.util.spec_from_file_location('state_validator_r2_base',OLD)
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
# In-memory specialization of sealed conservative parser/schema/freshness policy.
V.ISO=ISO;V.ISO_SHA=ISO_SHA
V.STATES={'initial_empty':('stopped',False),'preflight_attached':('stopped',True),
          'debug_attached':('running',True),'closed_attached':('stopped',True),
          'closed_empty':('stopped',False),'clean_running':('running',False),
          'final_empty':('stopped',False)}
V.EDGES={('initial_empty','preflight_attached'),('preflight_attached','debug_attached'),
         ('debug_attached','closed_attached'),('closed_attached','closed_empty'),
         ('closed_empty','clean_running'),('clean_running','final_empty')}
def evaluate(bundle,now):
    r=V.evaluate(bundle,now=now)
    r.update(root_boot_go=False,installation_qualified=False,live_ejection_supported=False,
             live_ejection_attempted=False,workflow='r2_attached_media_diagnostic_only',
             runtime_fence_backend_implemented=False)
    return r
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',required=True)
    p.add_argument('--as-of',required=True,help='Explicit offline replay clock; not present freshness')
    a=p.parse_args()
    try:print(json.dumps(evaluate(V.parse(V.read_local(a.bundle)),V.timestamp(a.as_of)),indent=2))
    except (ValueError,OSError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'NO_GO','reason':str(exc) if isinstance(exc,V.Refusal)
                          else type(exc).__name__,'root_boot_go':False,'actions_executed':False}));raise SystemExit(1)

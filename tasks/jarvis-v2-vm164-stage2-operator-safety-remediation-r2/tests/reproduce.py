"""Read-only baseline replay; source packets and their evidence remain untouched."""
import contextlib,hashlib,importlib.util,io,json,os,socket,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
REPO=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS')
PREP=REPO/'tasks/jarvis-v2-vm164-stage2-operator-preparation-r1'
AUDIT=REPO/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r1'
R3=REPO/'tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3'
sys.dont_write_bytecode=True
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def deny(*a,**k):raise AssertionError('offline process/network/signaling tripwire')
def run(label,module):
 stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
 (ROOT/'evidence'/f'{label}.log').write_text(stream.getvalue())
 return {'tests':r.testsRun,'passed':r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),'failed':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),'failures':[t.id() for t,_ in r.failures]}
if __name__=='__main__':
 with contextlib.ExitStack() as s:
  for ob,n in ((subprocess,'Popen'),(os,'system'),(os,'kill'),(os,'killpg'),(socket,'socket'),(socket,'create_connection')):s.enter_context(patch.object(ob,n,deny))
  a=run('baseline-original71',load('original71',PREP/'tests/test_packet.py'))
  b=run('baseline-audit30',load('audit30',AUDIT/'tests/test_independent.py'))
  seals={'prep':load('prep_verifier',PREP/'src/verify_packet.py').verify(),'r3':load('r3_verifier',R3/'tools/verify_packet.py').verify()}
 assert (a['passed'],a['failed'],a['errors'],a['skips'])==(71,0,0,0)
 assert (b['passed'],b['failed'],b['errors'],b['skips'])==(20,10,0,0)
 record={'kind':'EXPECTED_RED_BASELINE_NOT_HOST_EVIDENCE','original71':a,'audit30':b,'integrity':seals}
 (ROOT/'evidence/BASELINE.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

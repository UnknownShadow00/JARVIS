"""Read-only loading of reviewed tests; all new outputs stay in audit folder."""
import contextlib,datetime,hashlib,importlib.util,io,json,os,socket,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
AUDIT=Path(__file__).resolve().parents[1]
TARGET=AUDIT.parent/'jarvis-v2-vm164-stage2-operator-preparation-r1'
R3=AUDIT.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3'

def deny(*args,**kwargs):raise AssertionError('OFFLINE audit forbids process/network/signal execution')
def protect(event,args):
 if event=='open':
  path=args[0]
  if isinstance(path,(str,bytes,os.PathLike)):
   value=Path(os.fsdecode(path)).absolute()
   if any(value==root or root in value.parents for root in (TARGET,R3)):
    mode=args[1] or '';flags=args[2] or 0
    if any(c in mode for c in 'wax+') or flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
     raise AssertionError('Reviewed packet write forbidden')
 if event in ('os.mkdir','os.remove','os.rmdir','os.rename','os.chmod','os.chown'):
  for path in args[:2]:
   if isinstance(path,(str,bytes,os.PathLike)):
    value=Path(os.fsdecode(path)).absolute()
    if any(value==root or root in value.parents for root in (TARGET,R3)):raise AssertionError('Reviewed packet mutation forbidden')
sys.addaudithook(protect)

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run(name,module):
 stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromModule(module)
 r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (AUDIT/'evidence'/f'{name}.log').write_text(stream.getvalue())
 return {'tests':r.testsRun,'passes':r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),
 'failures':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),
 'failed_tests':[t.id() for t,_ in r.failures],'error_tests':[t.id() for t,_ in r.errors]}
with contextlib.ExitStack() as stack:
 for obj,name in ((subprocess,'Popen'),(os,'system'),(os,'kill'),(os,'killpg'),(socket,'socket'),(socket,'create_connection')):
  stack.enter_context(patch.object(obj,name,deny))
 first=run('reviewed-71-rerun',load('reviewed_tests',TARGET/'tests/test_packet.py'))
 second=run('independent-negative-probes',load('independent_tests',AUDIT/'tests/test_independent.py'))
 prep=load('preparation_verifier',TARGET/'src/verify_packet.py').verify()
 predecessor=load('predecessor_verifier',R3/'tools/verify_packet.py').verify()
record={'kind':'INDEPENDENT_OFFLINE_AUDIT_TEST_RESULTS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'reviewed_suite':first,'independent_probes':second,'preparation_integrity':prep,'predecessor_integrity':predecessor,
 'tripwires':'subprocess/network/signals; audit hook rejects writes to both reviewed trees',
 'host_operations':False,'stage2_authorized':False,'live_qualification':False,
 'probes_sha256':hashlib.sha256((AUDIT/'tests/test_independent.py').read_bytes()).hexdigest()}
(AUDIT/'evidence/TEST-RESULTS.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
# Nonzero accurately reports discovered safeguard gaps; outputs are still retained.
raise SystemExit(1 if first['failures'] or first['errors'] or second['failures'] or second['errors'] else 0)

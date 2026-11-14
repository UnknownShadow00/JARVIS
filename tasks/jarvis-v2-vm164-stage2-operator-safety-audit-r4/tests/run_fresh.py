"""Run independent synthetic probes with no subprocess/network/NSS/host access."""
from pathlib import Path
import sys,json,os,socket,pwd,grp,subprocess,contextlib,io,unittest,hashlib
from unittest.mock import patch
A=Path(__file__).resolve().parents[1];P=Path(json.loads((A/'evidence/WORKSPACE.json').read_bytes())['candidate'])
sys.path[:0]=[str(P/'src'),str(P/'tests'),str(A/'tests')]
def deny(*a,**k):raise AssertionError('AUDIT effect forbidden')
def hook(event,args):
 if event.startswith('socket.') or event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','os.kill','os.killpg','os.fork'):deny()
 if event=='open':
  path,mode,flags=args
  if isinstance(path,int):return
  if str(path).startswith(('/proc/','/sys/','/etc/passwd','/etc/group','/etc/shadow','/etc/nsswitch','/etc/sudo','/opt/jarvis-vm164-r3-stage2')):deny()
  if flags&(os.O_CREAT|os.O_TRUNC|os.O_WRONLY|os.O_RDWR|os.O_APPEND) and not Path(path).resolve().is_relative_to(A):deny()
sys.addaudithook(hook)
with contextlib.ExitStack() as stack:
 for obj,names in [(subprocess,['Popen']),(os,['system','kill','killpg']),(socket,['socket','create_connection']),(pwd,['getpwnam','getpwuid','getpwall']),(grp,['getgrnam','getgrgid','getgrall'])]:
  for name in names:stack.enter_context(patch.object(obj,name,deny))
 import fresh_adversaries as m
 raw=(P/'evidence/SYNTHETIC-12-CASE.json').read_bytes();m.BASE=json.loads(raw)
 suite=unittest.defaultTestLoader.loadTestsFromModule(m);ids=[t.id() for group in suite for t in group];out=io.StringIO();r=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
 (A/'evidence/INDEPENDENT.log').write_text(out.getvalue());(A/'evidence/INDEPENDENT-OBSERVED.json').write_text(json.dumps({'baseline_sha256':hashlib.sha256(raw).hexdigest(),'cases':m.OBSERVED},indent=2)+'\n')
 result={'tests':r.testsRun,'passed':r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),'failed':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),'test_ids':ids,'failures':[t.id() for t,_ in r.failures],'error_ids':[t.id() for t,_ in r.errors]};(A/'evidence/INDEPENDENT-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(not r.wasSuccessful())

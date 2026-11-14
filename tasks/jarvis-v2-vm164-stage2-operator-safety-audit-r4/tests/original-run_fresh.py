import sys,json,importlib.util,pathlib,contextlib,subprocess,os,socket,pwd,grp,tempfile,unittest,io
from unittest.mock import patch
A=pathlib.Path(__file__).resolve().parents[1];W=pathlib.Path(json.loads((A/'evidence/WORKSPACE.json').read_text())['disposable_copy']);P=W/'tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r3-verified'
sys.path[:0]=[str(P/'src'),str(A/'tests')];tempfile.tempdir=str(A/'temporary');pathlib.Path(tempfile.tempdir).mkdir(exist_ok=True)
def deny(*a,**k):raise AssertionError('Offline audit denies host/network/process effect')
def hook(event,args):
 if event.startswith('socket.') or event in ('subprocess.Popen','os.system','os.kill','os.killpg','os.exec','os.posix_spawn'):deny()
 if event=='open':
  path,mode,flags=args
  if isinstance(path,int):return
  s=str(path)
  if s.startswith(('/proc/','/sys/','/etc/passwd','/etc/group','/etc/shadow','/etc/nsswitch','/etc/sudo','/opt/jarvis-vm164-r3-stage2')):deny()
  if flags & (os.O_CREAT|os.O_TRUNC|os.O_WRONLY|os.O_RDWR|os.O_APPEND):
   if not pathlib.Path(path).resolve().is_relative_to(A):deny()
sys.addaudithook(hook)
with contextlib.ExitStack() as stack:
 for obj,names in [(subprocess,['Popen']),(os,['system','kill','killpg']),(socket,['socket','create_connection']),(pwd,['getpwnam','getpwuid','getpwall']),(grp,['getgrnam','getgrgid','getgrall'])]:
  for name in names:stack.enter_context(patch.object(obj,name,deny))
 import fresh_probes as m
 m.BASE=json.loads((P/'evidence/SYNTHETIC-12-CASE.json').read_text())
 suite=unittest.defaultTestLoader.loadTestsFromModule(m);ids=[t.id() for group in suite for t in group];buf=io.StringIO();r=unittest.TextTestRunner(stream=buf,verbosity=2).run(suite)
 (A/'evidence/FRESH.log').write_text(buf.getvalue());(A/'evidence/FRESH-OBSERVED.json').write_text(json.dumps(m.OBSERVED,indent=2)+'\n')
 out=dict(tests=r.testsRun,passed=r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),failures=[t.id() for t,_ in r.failures],errors=[t.id() for t,_ in r.errors],skips=r.skipped,test_ids=ids)
 (A/'evidence/FRESH-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 raise SystemExit(not r.wasSuccessful())

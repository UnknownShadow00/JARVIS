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

 import fresh_probes as helper,inspect,difflib,textwrap
 old=W/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2/tests/test_independent.py'
 spec=importlib.util.spec_from_file_location('original_astra',old);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 helper.BASE=json.loads((P/'evidence/SYNTHETIC-12-CASE.json').read_text());m.BASE=helper.BASE;m.R2=P;m.seal=helper.seal
 # Two former inputs were encoded in the old positive fixture, not in the test's mutation.
 adapters=[]
 for name in ('test_execstart_exit_disagreement_must_fail','test_missing_raw_cgroup_capture_must_fail'):
  original=textwrap.dedent(inspect.getsource(getattr(m.RemainingGaps,name)));new=original
  if 'execstart' in name:new=new.replace(".replace('code=(null) ; status=0','code=exited ; status=7')",".replace('code=exited ; status=0','code=exited ; status=7')")
  else:new=new.replace('r=seed()','r=seed()\n for row in r[\'cases\'].values():\n  row[\'final\'][\'cgroup\'].pop(\'raw\',None);row[\'final\'][\'cgroup\'].pop(\'receipt\',None)')
  ns=dict(m.__dict__);exec(compile(new,'<independent fixture adapter>','exec'),ns);setattr(m.RemainingGaps,name,ns[name]);adapters.extend(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile=name+' original',tofile=name+' R3 input'))
 (A/'evidence/INDEPENDENT-FIXTURE-ADAPTERS.diff').write_text(''.join(adapters))
 CALLS=[];real=m.results.validate
 def tracked(*a,**k):
  try:out=real(*a,**k);CALLS.append({'result':out});return out
  except Exception as e:CALLS.append({'raised':type(e).__name__,'reason':str(e)});raise
 m.results.validate=tracked
 suite=unittest.defaultTestLoader.loadTestsFromModule(m);tests=[t for group in suite for t in group];allrows=[];log=io.StringIO()
 for test in tests:
  CALLS.clear();res=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.TestSuite([test]));allrows.append(dict(test_id=test.id(),passed=res.wasSuccessful(),failures=len(res.failures),errors=len(res.errors),skips=len(res.skipped),calls=list(CALLS)))
 out={'tests':len(allrows),'passed':sum(x['passed'] for x in allrows),'failures':sum(x['failures'] for x in allrows),'errors':sum(x['errors'] for x in allrows),'skips':sum(x['skips'] for x in allrows),'cases':allrows}
 (A/'evidence/ORIGINAL-METHODS-R3.log').write_text(log.getvalue());(A/'evidence/ORIGINAL-METHODS-R3.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='cases'});raise SystemExit(out['failures']+out['errors']>0)

"""Independent read-only replay. Writes only this audit and its temporary fixtures."""
import argparse,contextlib,hashlib,importlib.util,io,json,os,socket,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];TASKS=ROOT.parent
R2=TASKS/'jarvis-v2-vm164-stage2-operator-safety-remediation-r2'
R1=TASKS/'jarvis-v2-vm164-stage2-operator-preparation-r1'
A1=TASKS/'jarvis-v2-vm164-stage2-operator-safety-audit-r1'
R3=TASKS/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3'
sys.dont_write_bytecode=True
TMP=ROOT/'temporary';TMP.mkdir(exist_ok=True);tempfile.tempdir=str(TMP)

def inside(p,root):
 try:return Path(p).resolve().is_relative_to(root.resolve())
 except (TypeError,ValueError,OSError):return False

def audit_hook(event,args):
 if event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','os.fork','os.forkpty','os.kill','os.killpg') or event.startswith('socket.'):
  raise AssertionError('AUDIT: process/network/signaling forbidden')
 if event=='open':
  path,mode,flags=args
  if isinstance(path,int):return
  if str(path).startswith(('/etc/shadow','/etc/gshadow','/etc/nsswitch','/etc/passwd','/etc/sudo','/proc/','/opt/jarvis-vm164-r3-stage2')):
   raise AssertionError('AUDIT: live host/identity/private path forbidden')
  writing=(flags or 0)&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND) or (isinstance(mode,str) and any(c in mode for c in 'wax+'))
  if writing and not inside(path,ROOT):raise AssertionError('AUDIT: write outside new audit')
 if event in ('os.mkdir','os.remove','os.rmdir','os.rename','os.chmod','os.chown','os.utime','os.link','os.symlink','os.truncate'):
  paths=args[:2] if event in ('os.rename','os.link') else (args[1],) if event=='os.symlink' else args[:1]
  for path in paths:
   if isinstance(path,int):continue
   # dir_fd relative removals are used only by TemporaryDirectory under this audit.
   if not os.path.isabs(str(path)) and event in ('os.remove','os.rmdir') and any(isinstance(x,int) and x>=0 for x in args[1:]):continue
   if not inside(path,ROOT):raise AssertionError('AUDIT: mutation outside new audit')
sys.addaudithook(audit_hook)

def deny(*a,**kw):raise AssertionError('AUDIT: prohibited effect')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def run(label,module):
 stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromModule(module)
 ids=[]
 def enumerate_tests(s):
  for t in s:
   if isinstance(t,unittest.TestSuite):enumerate_tests(t)
   else:ids.append(t.id())
 enumerate_tests(suite)
 r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (ROOT/'evidence'/f'{label}.log').write_text(stream.getvalue())
 return dict(tests=r.testsRun,passed=r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),failed=len(r.failures),errors=len(r.errors),skips=len(r.skipped),test_ids=ids,failures=[t.id() for t,_ in r.failures],error_ids=[t.id() for t,_ in r.errors])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('baseline','r2','negative'));a=parser.parse_args();report={}
 with contextlib.ExitStack() as stack:
  for obj,name in ((subprocess,'Popen'),(os,'system'),(os,'kill'),(os,'killpg'),(socket,'socket'),(socket,'create_connection')):stack.enter_context(patch.object(obj,name,deny))
  import pwd,grp
  for obj,names in ((pwd,('getpwnam','getpwuid','getpwall')),(grp,('getgrnam','getgrgid','getgrall'))):
   for name in names:stack.enter_context(patch.object(obj,name,deny))
  if a.phase=='baseline':
   report['original71']=run('original71',load('original71',R1/'tests/test_packet.py'))
   report['audit30_original']=run('audit30-original',load('audit30_original',A1/'tests/test_independent.py'))
   report['original_integrity']={'preparation':load('v1',R1/'src/verify_packet.py').verify(),'r3':load('v3',R3/'tools/verify_packet.py').verify()}
  else:
   sys.path[:0]=[str(R2/'src'),str(R2/'tests'),str(ROOT/'tests')]
   import packet,results,fixtures,proposals,catalog
   if a.phase=='r2':
    old=load('audit30_r2',A1/'tests/test_independent.py')
    old.p=types.SimpleNamespace(**vars(packet));old.p.cleanup_argv=lambda n,c,o,current:packet.cleanup_argv(n,c,o,dict(current))
    old.results=results;old.ident=fixtures.ident;old.session=fixtures.session;old.sample=fixtures.sample;old.ownership=fixtures.ownership
    old.CAT={'install':proposals.install('/SYNTHETIC/canary.py',fixtures.session(),fixtures.sample()),'read':{'R19-policy-or-manual-read':proposals.protected_read('/SYNTHETIC/policy',1048576,'d'*64),'R20-manual-gzip-read':proposals.protected_read('/SYNTHETIC/manual.gz',1048576,'d'*64,True)}}
    report['audit30_r2']=run('audit30-r2',old)
    design=load('design',R2/'tests/test_design.py');design.CAT=json.loads((R1/'COMMAND-CATALOG.json').read_bytes());report['design_original']=run('design-original',design)
    design.CAT=catalog.build();report['design_r2']=run('design-r2',design)
    report['regression92']=run('regression92',load('regression92',R2/'tests/test_regression.py'))
    report['r2_integrity']=load('v2',R2/'src/verify_packet.py').verify()
    retained=json.loads((R2/'evidence/SYNTHETIC-12-CASE.json').read_bytes());import artifacts
    report['published_synthetic12']=results.validate(retained,artifacts.load(R2/'evidence/SYNTHETIC-ARTIFACTS',retained['evidence_manifest']),expected_manifest_sha256=retained['evidence_manifest_sha256'],expected_packet_manifest_sha256=retained['packet_manifest_sha256'])
   else:
    independent=load('independent',ROOT/'tests/test_independent.py');report['independent']=run('independent-probes',independent)
    (ROOT/'evidence/ACCEPTED-COUNTEREXAMPLES.json').write_text(json.dumps(independent.OBSERVED,indent=2)+'\n')
 (ROOT/'evidence'/f'{a.phase.upper()}-RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:{x:y for x,y in v.items() if x not in ('test_ids','failures','error_ids')} if isinstance(v,dict) else v for k,v in report.items()},indent=2))
 expected_failures={'audit30_original':10,'design_original':3}
 failed=any(v.get('errors',0) or v.get('skips',0) or v.get('failed',0)!=expected_failures.get(k,0) for k,v in report.items() if isinstance(v,dict))
 return 1 if failed else 0
if __name__=='__main__':raise SystemExit(main())

"""Installed-source synthetic smoke in a fresh capability-free networkless cage."""
import argparse,datetime,hashlib,json,os,resource,shutil,signal,subprocess,time
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def limits():
 os.umask(0o077)
 for k,p in [(resource.RLIMIT_AS,(1073741824,1073741824)),(resource.RLIMIT_CPU,(120,121)),(resource.RLIMIT_FSIZE,(67108864,67108864)),(resource.RLIMIT_NOFILE,(64,64)),(resource.RLIMIT_CORE,(0,0))]:resource.setrlimit(k,p)
def descendants(root):
 rows={}
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   s=(p/'stat').read_text().rsplit(')',1)[1].split();rows[int(p.name)]=(int(s[1]),s[19],int(s[21])*os.sysconf('SC_PAGE_SIZE'))
  except (OSError,IndexError):continue
 owned={root}
 while True:
  new={p for p,row in rows.items() if row[0] in owned}
  if new<=owned:break
  owned|=new
 return {p:rows[p] for p in owned if p in rows}
def main():
 p=argparse.ArgumentParser();p.add_argument('installed_tree',type=Path);p.add_argument('output',type=Path);p.add_argument('installed_manifest_sha256');a=p.parse_args()
 if os.geteuid()==0:raise SystemExit('REFUSED: smoke must run as an existing unprivileged lab principal')
 root=a.installed_tree.resolve();inputs=a.output/'input';work=a.output/'work'
 a.output.mkdir(mode=0o700,exist_ok=False);inputs.mkdir(mode=0o700);work.mkdir(mode=0o700);(work/'tmp').mkdir(mode=0o700)
 # Immutable public installation inventory checked before any target import.
 if sha(root/'INSTALL-MANIFEST.json')!=a.installed_manifest_sha256:raise SystemExit('REFUSED: independent installation manifest pin mismatch')
 receipt=json.loads((root/'INSTALL-MANIFEST.json').read_text())
 for n,h in receipt['files'].items():
  f=root/n
  if f.is_symlink() or sha(f)!=h:raise SystemExit('REFUSED: installed source/dependency drift')
 shutil.copytree(root/'source/app',inputs/'source/app')
 shutil.copyfile(root/'source/config.yaml.example',inputs/'source/config.yaml')
 shutil.copytree(root/'source/tests',inputs/'tests')
 for f in (root/'tools/smoke-inputs').iterdir():
  if f.is_file():shutil.copyfile(f,inputs/f.name)
 regressions=inputs/'regressions';regressions.mkdir()
 for name in ['test_reporter.py','test_resource_manager.py','test_server_auth.py','test_cancel_token.py','test_health_check.py','test_operator_app.py','test_audit_disaster_app.py','test_enrollment_app.py','test_safety_levels.py','test_approval_gates.py','test_audit_integration_fixes.py','test_ready_client.py','test_authority_http_security.py','test_ue5_security.py','test_storage_ancestry_security.py','test_release_security.py']:
  shutil.copyfile(root/'source/tests'/name,regressions/name)
 shutil.copyfile(root/'source/tests/synthetic_authority.py',regressions/'synthetic_authority.py')
 for name in ['synthetic_authority.py','enrollment_fixtures.py','transport_fixtures.py']:shutil.copyfile(root/'source/tests'/name,inputs/name)
 canary=b'synthetic readonly input\n';(inputs/'readonly-canary.txt').write_bytes(canary)
 outside=a.output/'outside-canary.txt';outside.write_text('synthetic canary only\n')
 source={str(f.relative_to(root/'source')):sha(f) for f in (root/'source/app').rglob('*.py')}
 expected={'parent_namespaces':{n:os.readlink('/proc/self/ns/'+n) for n in ['user','mnt','pid','net','ipc','uts']},'outside_canary_path':str(outside.resolve()),'readable_canary_sha256':hashlib.sha256(canary).hexdigest(),'guard_sha256':sha(inputs/'guard.py'),'source_sha256':source,'versions':receipt['versions']}
 (inputs/'expected.json').write_text(json.dumps(expected,indent=2)+'\n')
 hashes={str(f.relative_to(inputs)):sha(f) for f in inputs.rglob('*') if f.is_file()};(a.output/'INPUT-SHA256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n')
 argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--setenv','TZ','UTC','--cap-drop','ALL','--dir','/usr','--ro-bind','/usr/bin','/usr/bin','--ro-bind','/usr/lib','/usr/lib','--dir','/usr/share','--ro-bind','/usr/share/zoneinfo','/usr/share/zoneinfo','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--dir','/run','--ro-bind',str(inputs.resolve()),'/input','--ro-bind',str(root/'python'),'/deps','--bind',str(work.resolve()),'/work','--symlink','/work/tmp','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3.14','-I','-B','-S','-c',"import resource,runpy;resource.setrlimit(resource.RLIMIT_NPROC,(64,64));runpy.run_path('/input/child.py',run_name='__main__')"]
 start=time.monotonic();stop=None;peak=0
 with (a.output/'stdout.txt').open('x') as out,(a.output/'stderr.txt').open('x') as err:
  proc=subprocess.Popen(argv,env={'PATH':'/usr/bin:/bin'},stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,start_new_session=True,preexec_fn=limits)
  while proc.poll() is None:
   owned=descendants(proc.pid);rss=sum(x[2] for x in owned.values());peak=max(peak,rss)
   size=count=0
   for f in work.rglob('*'):
    try:
     if f.is_file() and not f.is_symlink():size+=f.stat().st_size;count+=1
    except FileNotFoundError:pass
   if time.monotonic()-start>120 or rss>768*1024**2 or len(owned)>4 or size>256*1024**2 or count>20000:
    stop='owned_workload_resource_bound'
    for pid,row in reversed(list(owned.items())):
     try:
      current=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
      if current[19]==row[1]:os.kill(pid,signal.SIGKILL)
     except OSError:pass
    break
   time.sleep(.05)
  proc.wait(timeout=5)
 child=json.loads((work/'RESULT.json').read_text()) if (work/'RESULT.json').exists() else None
 status='PASS' if proc.returncode==0 and not stop else 'FAIL'
 result={'status':status,'exitcode':proc.returncode,'guard_stop':stop,'wall_seconds':time.monotonic()-start,'peak_rss':peak,'source_sha256':source,'child':child,'network':'unshared no external listeners/routes/credentials; synthetic AF_UNIX only','installed_state_mutated':False}
 for n,h in receipt['files'].items():
  if sha(root/n)!=h:raise SystemExit('REFUSED: installed inputs changed during smoke')
 (a.output/'SMOKE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':status,'tests':(child or {}).get('regressions'),'application_scenario_groups':len((child or {}).get('cases',[])),'wall_seconds':result['wall_seconds'],'guard_stop':stop},indent=2));return 0 if status=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

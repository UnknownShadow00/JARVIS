"""Review candidate broker only in a disposable offline copy; never installs/starts services."""
from pathlib import Path
from datetime import datetime,UTC
import hashlib,json,os,resource,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lab_package import load_bundle
P=Path(__file__).resolve().parents[1]
def limits():
 os.umask(0o077)
 for k,p in [(resource.RLIMIT_AS,(1073741824,1073741824)),(resource.RLIMIT_CPU,(120,121)),(resource.RLIMIT_FSIZE,(67108864,67108864)),(resource.RLIMIT_NOFILE,(96,96)),(resource.RLIMIT_CORE,(0,0))]:resource.setrlimit(k,p)
def main():
 os.umask(0o077)
 b=json.loads((P/'BUNDLE.json').read_text());m,files=load_bundle(P/b['bundle'],b['bundle_sha256'])
 run=P/'runs'/('broker-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'));work=run/'work';work.mkdir(mode=0o700,parents=True)
 for n,raw in files.items():
  if n.startswith('serial-candidate/'):
   target=work/'candidate'/n[len('serial-candidate/'):];target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);target.write_bytes(raw)
 argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--setenv','OPENSSL_CONF','/dev/null','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--symlink','usr/bin','/bin','--bind',str(work),'/work','--proc','/proc','--dev','/dev','--dir','/work/tmp','--symlink','/work/tmp','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3.14','-I','-B','-S','-c',"import resource,runpy;resource.setrlimit(resource.RLIMIT_NPROC,(64,64));runpy.run_path('/work/candidate/tests/run_offline.py',run_name='__main__')"]
 with (run/'stdout.txt').open('x') as out,(run/'stderr.txt').open('x') as err:r=subprocess.run(argv,stdout=out,stderr=err,stdin=subprocess.DEVNULL,env={'PATH':'/usr/bin:/bin'},timeout=120,preexec_fn=limits)
 result={'run':str(run.relative_to(P)),'exitcode':r.returncode,'source_manifest_sha256':b['broker_source_manifest_sha256'],'namespace':'unshared network/user/mount/pid/ipc/uts; no real credentials/state/socket/device','protected_multi_uid_or_guest_qualification':False,'tests':json.loads((work/'candidate/evidence/offline-tests.json').read_text()) if (work/'candidate/evidence/offline-tests.json').exists() else None}
 (run/'RUN.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');(P/'BROKER-TEST-RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())

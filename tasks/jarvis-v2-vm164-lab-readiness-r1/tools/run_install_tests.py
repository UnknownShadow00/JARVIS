"""Resource-bounded unprivileged installer fixture tests in an empty network namespace."""
from pathlib import Path
import datetime,hashlib,json,os,resource,shutil,subprocess,sys
P=Path(__file__).resolve().parents[1]
def limits():
 os.umask(0o077)
 for k,pair in [(resource.RLIMIT_AS,(1073741824,1073741824)),(resource.RLIMIT_CPU,(120,121)),(resource.RLIMIT_FSIZE,(67108864,67108864)),(resource.RLIMIT_NOFILE,(96,96)),(resource.RLIMIT_CORE,(0,0))]:resource.setrlimit(k,pair)
def main():
 before={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for d in ['tools','tests'] for f in (P/d).glob('*.py')}
 run=P/'runs'/('install-'+datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%S%fZ'));run.mkdir(mode=0o700,parents=True);work=run/'work';work.mkdir(mode=0o700)
 fixture=P/'wheel-fixture'
 if not fixture.exists():
  fixture.mkdir();src=next(Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/artifacts/wheels').glob('idna-*.whl'));shutil.copyfile(src,fixture/src.name)
 child=run/'child.py';child.write_text('''import sys,unittest,json,os,resource
resource.setrlimit(resource.RLIMIT_NPROC,(64,64))
sys.path.insert(0,'/input/tests')
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('/input/tests'))
from pathlib import Path
Path('/work/TEST-RESULTS.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),'successful':result.wasSuccessful(),'uid':os.getuid(),'guest_or_protected_install_performed':False},indent=2)+'\\n')
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
''')
 argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--ro-bind',str(P.resolve()),'/input','--ro-bind',str(child),'/child.py','--bind',str(work),'/work','--proc','/proc','--dev','/dev','--symlink','/work','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3.14','-I','-B','-S','/child.py']
 with (run/'stdout.txt').open('x') as out,(run/'stderr.txt').open('x') as err:
  r=subprocess.run(argv,env={'PATH':'/usr/bin:/bin'},stdout=out,stderr=err,stdin=subprocess.DEVNULL,timeout=120,preexec_fn=limits)
 result={'run':str(run.relative_to(P)),'exitcode':r.returncode,'bundle':json.loads((P/'BUNDLE.json').read_text()),'tests':json.loads((work/'TEST-RESULTS.json').read_text()) if (work/'TEST-RESULTS.json').exists() else None,'input_sha256':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for d in ['tools','tests'] for f in (P/d).glob('*.py')},'namespace':'network/user/mount/pid/ipc/uts unshared; no host credentials, config, devices, or service sockets','limits':{'AS':1073741824,'CPU':120,'wall':120,'file_size':67108864,'FD':96,'processes':64}}
 assert before==result['input_sha256'],'test inputs changed during execution'
 (run/'RUN.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())

"""Trusted audit runner. Never imports target code outside the sandbox."""
import os,sys,resource,subprocess,json,stat,selectors,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
agent,script=sys.argv[1:3]
snapshot_name=sys.argv[3] if len(sys.argv)>3 else 'snapshot'
if snapshot_name not in ('before','red','green','baseline','candidate-1','candidate-2','candidate-3','final'):raise SystemExit('invalid snapshot')
SNAPSHOT=ROOT/snapshot_name
if not agent.replace('-','').replace('_','').isalnum() or not agent[0].isalnum() or agent.lower()!=agent:raise SystemExit('unsafe agent')
a=ROOT/'agents'/agent;s=a/'scratch';d=a/'artifacts'
s.mkdir(parents=True,exist_ok=True);d.mkdir(parents=True,exist_ok=True)
sfd=os.open(s,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);dfd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
os.set_inheritable(sfd,False);os.set_inheritable(dfd,False)
script=Path(script).resolve()
if script.parent!=s.resolve() or script.is_symlink():raise SystemExit('harness must be direct scratch child')
cmd=['/usr/bin/bwrap','--unshare-all','--unshare-user','--disable-userns','--die-with-parent','--new-session','--cap-drop','ALL',
 '--ro-bind','/usr','/usr','--ro-bind','/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages','/toolchain','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64',
 '--size','1048576','--tmpfs','/target',
 *[item for child in sorted(SNAPSHOT.iterdir()) for item in ('--ro-bind',str(child),'/target/'+child.name)],
 '--ro-bind',str(SNAPSHOT/'config.yaml.example'),'/target/config.yaml','--remount-ro','/target',
 '--ro-bind',str(script),'/harness.py',
 '--size','33554432','--tmpfs','/scratch','--dir','/scratch/home','--dir','/scratch/tmp','--dir','/scratch/cache',
 '--dir','/input','--ro-bind',str(ROOT/'before/app/agent/api.py'),'/input/baseline_api.py','--ro-bind',str(SNAPSHOT),'/input/source','--ro-bind',str(SNAPSHOT/'tests'),'/input/tests',
 '--ro-bind','/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages','/deps',
 '--dir','/scratch/work','--symlink','/scratch/work','/work',
 '--proc','/proc','--remount-ro','/proc','--dev','/dev','--remount-ro','/dev',
 '--clearenv','--setenv','PATH','/usr/local/bin:/usr/bin:/bin','--setenv','HOME','/scratch/home','--setenv','TMPDIR','/scratch/tmp',
 '--setenv','XDG_CACHE_HOME','/scratch/cache','--setenv','PYTHONDONTWRITEBYTECODE','1','--setenv','PYTHONPATH','/toolchain:/target:/target/tests',
 '--setenv','OPENBLAS_NUM_THREADS','1','--setenv','OMP_NUM_THREADS','1','--setenv','OPENSSL_CONF','/dev/null','--chdir','/scratch',
 '/usr/bin/python3.14','-B','-c',"import resource,runpy;resource.setrlimit(resource.RLIMIT_NPROC,(64,64));runpy.run_path('/harness.py',run_name='__main__')"]
def limits():
 for k,v in [(resource.RLIMIT_CPU,10),(resource.RLIMIT_AS,536870912),(resource.RLIMIT_NOFILE,96),(resource.RLIMIT_FSIZE,2097152),(resource.RLIMIT_CORE,0)]:resource.setrlimit(k,(v,v))
# Pipes are consumed into bounded parent-side files; target receives no host writable mount.
try:
 result=subprocess.Popen(['/usr/bin/timeout','--signal=KILL','25',*cmd],env={'PATH':'/usr/bin:/bin'},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limits)
 data=bytearray();selection=selectors.DefaultSelector();selection.register(result.stdout,selectors.EVENT_READ);deadline=time.monotonic()+30
 try:
  while selection.get_map():
   if time.monotonic()>deadline:raise RuntimeError('wall timeout')
   for key,_ in selection.select(timeout=0.5):
    chunk=os.read(key.fileobj.fileno(),min(4096,262145-len(data)))
    if not chunk:selection.unregister(key.fileobj);continue
    data.extend(chunk)
    if len(data)>262144:raise RuntimeError('output exceeds promotion allowlist')
  result.wait(timeout=max(0.1,deadline-time.monotonic()))
 finally:
  selection.close()
  if result.poll() is None:result.kill();result.wait(timeout=5)
 data=bytes(data)
 leaf=script.stem+'.txt'
 fd=os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=sfd)
 with os.fdopen(fd,'wb') as f:f.write(data)
 # Predeclared allowlist: only matching script stem .txt, max256KiB and cumulative256KiB per invocation.
 src=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=sfd);before=os.fstat(src)
 if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>262144:raise SystemExit('unsafe artifact')
 raw=os.read(src,before.st_size+1);after=os.fstat(src)
 if len(raw)!=before.st_size or (before.st_dev,before.st_ino,before.st_nlink,before.st_size)!=(after.st_dev,after.st_ino,after.st_nlink,after.st_size):raise SystemExit('changing artifact')
 dst=os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=dfd)
 info=os.fstat(dst)
 if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:raise SystemExit('unsafe destination')
 with os.fdopen(dst,'wb') as f:f.write(raw)
 os.close(src)
 print(json.dumps({'exit_code':result.returncode,'artifact':str((d/leaf).relative_to(ROOT)),'bytes':len(raw)}))
 print(raw.decode('utf-8',errors='replace'))
finally:os.close(sfd);os.close(dfd)

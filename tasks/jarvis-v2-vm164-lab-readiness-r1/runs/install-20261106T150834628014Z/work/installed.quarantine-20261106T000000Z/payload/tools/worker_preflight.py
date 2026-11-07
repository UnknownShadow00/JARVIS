"""Future guest read-only metadata inspection; never opens serial, state or credentials."""
from pathlib import Path
import argparse,hashlib,json,os,stat,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lab_package import protected_chain,regular,Refusal,require

def assess(d):
 required={'source_manifest_matches':True,'source_root_protected':True,'worker_uid_nonroot':True,'worker_gid_matches':True,'worker_login_disabled':True,'tty_owner_matches':True,'tty_mode_private':True,'kernel_serial_console_absent':True,'getty_masked':True,'serial_open_holders':0,'network_interfaces':['lo']}
 problems=[k for k,v in required.items() if d.get(k)!=v]
 return {'metadata_checks_pass':not problems,'failed_checks':problems,'activation_ready':False,'remaining_external_gates':['trusted installed OS/root/identity','locked account and escalation/capability/FD review','actual multi-UID DAC/service/seccomp/egress and buffering qualification','independent finite grant/config/CA/token custody','explicit activation authorization'],'qualification':'metadata inspection only; not privileged Gate6K qualification or authorization'}

def inspect(source,uid,gid):
 d={};require(uid>0 and gid>0,'nonroot_worker_binding_required')
 try:
  fd=protected_chain(source,directory=True);os.close(fd);d['source_root_protected']=True
  raw=regular(Path(source)/'SOURCE-SHA256SUMS',65536);require(hashlib.sha256(raw).hexdigest()=='9e5bdd0ea59fa36021f462f4388597fefd4b65f9cee32024e86ba5d33d700301','reviewed_manifest_pin');manifest=raw.decode();expected={}
  for line in manifest.splitlines():
   h,n=line.split('  ',1);n=n.removeprefix('./');require(not n.startswith('/') and '..' not in Path(n).parts,'unsafe_source_manifest');expected[n]=h
  for name in [*expected,'SOURCE-SHA256SUMS']:
   fd=protected_chain(Path(source)/name);os.close(fd)
  actual={str(f.relative_to(source)) for f in Path(source).rglob('*') if f.is_file() or f.is_symlink()}
  require(actual==set(expected)|{'SOURCE-SHA256SUMS'},'source_inventory_mismatch')
  d['source_manifest_matches']=len(expected)==13 and all(hashlib.sha256(regular(Path(source)/n)).hexdigest()==h for n,h in expected.items())
 except (OSError,Refusal,ValueError):d['source_root_protected']=d['source_manifest_matches']=False
 accounts=[x.split(':') for x in Path('/etc/passwd').read_text().splitlines() if x.split(':',1)[0]=='g6k-bridge']
 d['worker_uid_nonroot']=len(accounts)==1 and int(accounts[0][2])==uid
 d['worker_gid_matches']=len(accounts)==1 and int(accounts[0][3])==gid
 d['worker_login_disabled']=len(accounts)==1 and accounts[0][6] in ('/usr/sbin/nologin','/sbin/nologin','/bin/false')
 try:
  tty=os.lstat('/dev/ttyS0');d['tty_owner_matches']=stat.S_ISCHR(tty.st_mode) and tty.st_uid==uid and tty.st_gid==gid;d['tty_mode_private']=stat.S_IMODE(tty.st_mode)==0o600
 except OSError:d['tty_owner_matches']=d['tty_mode_private']=False
 cmdline=Path('/proc/cmdline').read_text().split();d['kernel_serial_console_absent']=not any(x.startswith(('console=ttyS0','earlycon','earlyprintk')) for x in cmdline)
 getty=Path('/etc/systemd/system/serial-getty@ttyS0.service');d['getty_masked']=getty.is_symlink() and str(getty.readlink())=='/dev/null'
 holders=0;unknown=False
 for process in Path('/proc').iterdir():
  if not process.name.isdigit():continue
  try:
   for fd in (process/'fd').iterdir():
    try:
     if str(fd.readlink())=='/dev/ttyS0':holders+=1
    except FileNotFoundError:pass
  except FileNotFoundError:pass
  except PermissionError:unknown=True
 d['serial_open_holders']=None if unknown else holders
 d['network_interfaces']=sorted(x.name for x in Path('/sys/class/net').iterdir());return d

def main():
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('worker_uid',type=int);p.add_argument('worker_gid',type=int);args=p.parse_args()
 d=inspect(args.source,args.worker_uid,args.worker_gid);result=assess(d);result['observations']=d
 print(json.dumps(result,indent=2,sort_keys=True));return 0 if result['metadata_checks_pass'] else 1
if __name__=='__main__':raise SystemExit(main())

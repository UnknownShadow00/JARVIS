"""Exercise installed generator in no-network, no-privilege, no-PID1 sandbox."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
BIN='/usr/lib/systemd/system-generators/systemd-debug-generator'
def run(out):
 out.mkdir(mode=0o700);results={}
 for name,flags in {'trusted_tty1':'systemd.debug_shell=tty1 systemd.mask=getty@tty1.service','normal_boot':'root=UUID=fixture ro','default_tty9':'systemd.debug_shell=1'}.items():
  d=out/name;d.mkdir()
  for part in ('normal','early','late'):(d/part).mkdir()
  cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--proc','/proc','--dev','/dev','--dir','/tmp','--bind',str(d),'/work','--setenv','SYSTEMD_PROC_CMDLINE',flags,BIN,'/work/normal','/work/early','/work/late']
  r=subprocess.run(cmd,timeout=20,capture_output=True,env={'PATH':'/usr/bin:/bin','LANG':'C'})
  assert r.returncode==0,r.stderr.decode()
  wants=d/'early/default.target.wants/debug-shell.service';drop=d/'early/debug-shell.service.d/50-tty.conf';mask=d/'early/getty@tty1.service'
  if name=='trusted_tty1':
   assert wants.is_symlink() and os.readlink(wants)=='/usr/lib/systemd/system/debug-shell.service'
   assert 'TTYPath=/dev/tty1' in drop.read_text() and 'ConditionPathExists=\n' in drop.read_text()
   assert mask.is_symlink() and os.readlink(mask)=='/dev/null'
  elif name=='normal_boot':assert not wants.is_symlink() and not drop.exists() and not mask.is_symlink()
  else:assert wants.is_symlink() and not drop.exists() and not mask.is_symlink()
  results[name]={'pass':True,'files':{str(p.relative_to(d)):{'symlink':os.readlink(p)} if p.is_symlink() else {'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(d.rglob('*')) if p.is_symlink() or p.is_file()}}
 unit=Path('/usr/lib/systemd/system/debug-shell.service').read_text();assert 'Restart=always' in unit and 'KillMode=process' in unit
 (out/'stock-debug-shell.service.txt').write_text(unit)
 report={'generator_sha256':hashlib.sha256(Path(BIN).read_bytes()).hexdigest(),'unit_sha256':hashlib.sha256(unit.encode()).hexdigest(),'cases':results,'actual_guest_generator_verified':False,'system_manager_started_or_called':False,'network_namespace':'isolated','result':'PASS_3_OFFLINE_GENERATOR_CASES'}
 with (out/'RESULT.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out.resolve())

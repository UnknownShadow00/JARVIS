"""Future VM164-only RAM staging, pinned read-only probe and temporary-root closure.
Nothing happens at import. No install, credential edit, network or serial-device open.
"""
import argparse,base64,hashlib,json,os,re,stat,subprocess,sys,time
from pathlib import Path
UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193';SERIAL='g6k164-12821f6b54a2'
PROBE_SHA='08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a'
RAM=Path('/run/vm164-bootstrap-r1');MEDIA=Path('/run/vm164-bootstrap-media')
FLAGS=('systemd.debug_shell=tty1','systemd.mask=getty@tty1.service')
WATCHED=('/etc/default/grub','/boot/grub/grub.cfg','/boot/grub/grubenv','/etc/passwd','/etc/group','/etc/hostname','/etc/machine-id')
class Refusal(Exception):pass
def need(ok,reason):
 if not ok:raise Refusal(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def js(d):return (json.dumps(d,indent=2,sort_keys=True)+'\n').encode()
def command(args,*,check=True):
 r=subprocess.run(args,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=20,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8'})
 if check:need(r.returncode==0,'fixed_command_failed:'+args[0])
 return r
def write_new(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data)
def read_regular(path,max_size=65536):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  st=os.fstat(fd);need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size<=max_size,'unsafe_input_file')
  data=os.read(fd,max_size+1);need(len(data)==st.st_size,'input_size_changed');return data
 finally:os.close(fd)
def mount_rows():return [x.split() for x in Path('/proc/self/mountinfo').read_text().splitlines()]
def assess(facts):
 need(facts['vm_uuid']==UUID,'wrong_vm_before_actions');need(facts['disk_serial']==SERIAL and facts['disk_bytes']==64*1024**3,'wrong_disk')
 need(facts['uid']==facts['euid']==0 and facts['pid1']=='systemd','trusted_installed_systemd_root_required')
 need(facts['root_fstype']=='ext4' and facts['run_fstype']=='tmpfs','installed_root_and_tmpfs_required')
 need(facts['network']==['lo'] and facts['disks']==['sda'],'unexpected_network_or_disk')
 tokens=facts['cmdline'].split()
 need(all(tokens.count(x)==1 for x in FLAGS),'exact_one_boot_flags_required')
 need(all(not x.startswith(('init=','rdinit=','rd.break','rd.systemd.debug','systemd.unit=','systemd.break=','autoinstall','ds=')) for x in tokens),'conflicting_boot_mode')
 need([x for x in tokens if x.startswith('systemd.debug_shell=')]==[FLAGS[0]],'conflicting_debug_tty')
 need([x for x in tokens if x.startswith('systemd.mask=')]==[FLAGS[1]],'conflicting_masks')
 need(not set(tokens)&{'single','emergency','rescue','systemd.debug_shell'},'conflicting_boot_flags')
 need(not facts['persistent_debug'] and facts['root_password_locked'],'persistent_debug_or_unlocked_root_outside_scope')
 need(facts['watchdog_active'],'watchdog_required')
 return True
def facts(*,console=False):
 vm=Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower();need(vm==UUID,'wrong_vm_before_inspection')
 serial=Path('/sys/block/sda/device/serial').read_text().strip();need(serial==SERIAL,'wrong_disk_before_inspection')
 rows=mount_rows();root=next(r for r in rows if r[4]=='/');run=next(r for r in rows if r[4]=='/run')
 status=command(['/usr/bin/passwd','-S','root']).stdout.split()
 persistent=any(p.name=='debug-shell.service' or p.name=='debug-shell.service.d' for p in Path('/etc/systemd/system').rglob('*'))
 d={'vm_uuid':vm,'disk_serial':serial,'disk_bytes':int(Path('/sys/block/sda/size').read_text().strip())*512,'uid':os.getuid(),'euid':os.geteuid(),'pid1':Path('/proc/1/comm').read_text().strip(),'root_fstype':root[root.index('-')+1],'run_fstype':run[run.index('-')+1],'network':sorted(p.name for p in Path('/sys/class/net').iterdir()),'disks':sorted(p.name for p in Path('/sys/block').iterdir() if re.fullmatch(r'(sd[a-z]+|vd[a-z]+|nvme\d+n\d+)',p.name)),'cmdline':Path('/proc/cmdline').read_text().strip(),'root_password_locked':len(status)>1 and status[0]=='root' and status[1]=='L','persistent_debug':persistent,'watchdog_active':command(['/usr/bin/systemctl','is-active','vm164-bootstrap-watchdog.timer'],check=False).stdout.strip()=='active','machine_id':Path('/etc/machine-id').read_text().strip(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
 assess(d)
 if console:need(os.ttyname(0)=='/dev/tty1','VGA_tty1_required')
 return d
def snapshot():
 out={}
 for name in WATCHED:
  p=Path(name)
  if not p.exists():out[name]=None;continue
  out[name]=sha(read_regular(p,8*1024**2))
 return out
def binding(d):return {k:d[k] for k in ('vm_uuid','disk_serial','disk_bytes','machine_id','boot_id')}
def match_session(d,s):need(binding(d)==s['identity'],'session_identity_changed')
def stage():
 d=facts(console=True)
 rows=mount_rows();media=next((r for r in rows if r[4]==str(MEDIA)),None)
 need(media is not None and media[media.index('-')+1]=='iso9660' and set(('ro','nosuid','nodev','noexec'))<=set(media[5].split(',')),'verified_readonly_data_media_required')
 need(set(p.name for p in MEDIA.iterdir())=={'BOOT.PY','LABPKG.PY','SHA256.SUM'},'media_inventory')
 raw=read_regular(MEDIA/'LABPKG.PY');need(sha(raw)==PROBE_SHA,'pinned_probe_mismatch')
 manifest={n:h for h,n in (x.split('  ',1) for x in read_regular(MEDIA/'SHA256.SUM').decode().splitlines())}
 need(set(manifest)=={'BOOT.PY','LABPKG.PY'} and manifest['LABPKG.PY']==PROBE_SHA,'media_manifest')
 for name,h in manifest.items():need(sha(read_regular(MEDIA/name))==h,'payload_hash')
 os.mkdir(RAM,0o700)
 for name in ('BOOT.PY','LABPKG.PY'):write_new(RAM/name,read_regular(MEDIA/name))
 write_new(RAM/'STATE.JSON',js({'identity':binding(d),'persistent_baseline':snapshot(),'probe_sha256':PROBE_SHA}))
 print('RAM_STAGED; unmount data media, eject it from PVE, then run probe from /run')
def probe():
 d=facts(console=True);s=json.loads(read_regular(RAM/'STATE.JSON'));match_session(d,s)
 need(not any(r[4]==str(MEDIA) for r in mount_rows()),'unmount_delivery_media_first')
 need(all(not (p/'size').exists() or int((p/'size').read_text().strip())==0 for p in Path('/sys/block').iterdir() if p.name.startswith('sr')),'eject_delivery_media_first')
 need(sha(read_regular(RAM/'LABPKG.PY'))==PROBE_SHA,'RAM_probe_pin')
 r=command(['/usr/bin/python3.14','-I','-B','-S',str(RAM/'LABPKG.PY'),'probe'])
 result=json.loads(r.stdout);need(result['vm_uuid']==UUID and result['boot_id']==d['boot_id'] and not result['optical_media_present'],'probe_identity_or_media')
 need(snapshot()==s['persistent_baseline'],'persistent_files_changed_stop_no_repair')
 write_new(RAM/'PROBE.JSON',r.stdout.encode());write_new(RAM/'PROBE.SHA', (sha(r.stdout.encode())+'\n').encode())
 print('PROBE_RETAINED_IN_RAM_SHA256='+sha(r.stdout.encode()))
 print('Capture every page before closing; this temporary-root boot is NOT Gate6K/installation qualification.')
def pages(page):
 need(0<=page<=999,'page_bound');raw=read_regular(RAM/'PROBE.JSON',256*1024)
 # 54-column rows fit VGA; capture/transcribe and independently verify locally.
 encoded=base64.b64encode(raw).decode();lines=[encoded[i:i+48] for i in range(0,len(encoded),48)]
 count=(len(lines)+7)//8;need(page<count,'page_not_present')
 print(f'PROBE_PAGE {page+1}/{count} ROWS={len(lines)}')
 print('SHA256='+sha(raw))
 for i in range(page*8,min((page+1)*8,len(lines))):print(f'R{i:04d}:'+lines[i])
def close():
 d=facts(console=True);s=json.loads(read_regular(RAM/'STATE.JSON'));match_session(d,s)
 need((RAM/'PROBE.JSON').exists(),'capture_or_explicit_abort_required')
 r=command(['/usr/bin/systemd-run','--unit=vm164-bootstrap-close','--property=Type=oneshot','--property=StandardOutput=tty','--property=StandardError=tty','--property=TTYPath=/dev/tty1','--property=TimeoutStartSec=45s','/usr/bin/python3.14','-I','-B','-S',str(RAM/'BOOT.PY'),'close-unit'])
 print('Independent close unit submitted; do not exit the debug shell as a substitute.')
def close_unit():
 # This runs in its own transient unit, so stopping debug-shell cannot kill the closer.
 s=json.loads(read_regular(RAM/'STATE.JSON'));d=facts();match_session(d,s)
 unchanged=snapshot()==s['persistent_baseline'];closed=False
 try:
  command(['/usr/bin/systemctl','mask','--runtime','debug-shell.service'])
  command(['/usr/bin/systemctl','stop','debug-shell.service'])
  command(['/usr/bin/systemctl','kill','--kill-whom=all','--signal=KILL','debug-shell.service'],check=False)
  values=command(['/usr/bin/systemctl','show','debug-shell.service','-p','ActiveState','-p','MainPID','-p','UnitFileState']).stdout
  props=dict(x.split('=',1) for x in values.splitlines() if '=' in x)
  cgroup=Path('/sys/fs/cgroup/system.slice/debug-shell.service/cgroup.procs')
  empty=not cgroup.exists() or not cgroup.read_text().strip()
  closed=props.get('ActiveState') in ('inactive','failed') and props.get('MainPID')=='0' and props.get('UnitFileState')=='masked-runtime' and empty
  print(json.dumps({'temporary_root_closed_this_boot':closed,'persistent_files_unchanged':unchanged,'boot_id':d['boot_id'],'clean_boot_still_required':True}),flush=True)
 finally:
  print('GRACEFUL_POWEROFF_REQUEST_IN_10_SECONDS; capture this screen.',flush=True);time.sleep(10)
  command(['/usr/bin/systemctl','--no-block','poweroff'])
 need(closed and unchanged,'closure_not_verified_use_supervised_failure_procedure')
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','probe','page','close','close-unit']);p.add_argument('page',nargs='?',type=int,default=0);a=p.parse_args()
 {'stage':stage,'probe':probe,'page':lambda:pages(a.page),'close':close,'close-unit':close_unit}[a.action]()
if __name__=='__main__':
 try:main()
 except (Refusal,OSError,ValueError,KeyError,StopIteration) as e:
  print(json.dumps({'status':'STOP_PRESERVE_AND_CLOSE','reason':str(e) if isinstance(e,Refusal) else type(e).__name__,'retry_or_repair_authorized':False}));raise SystemExit(1)

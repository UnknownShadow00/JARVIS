"""Offline fixtures only. Every service command is mocked; no VM/host manager calls."""
import base64,contextlib,copy,hashlib,importlib.util,importlib.machinery,io,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TASK=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path,loader=importlib.machinery.SourceFileLoader(name,str(path)));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
B=load('boot',TASK/'payload/BOOT.PY');H=load('guard',TASK/'tools/host_guard.py');D=load('decode',TASK/'tools/decode_probe.py');M=load('media',TASK/'tools/check_media.py')
def facts():return {'vm_uuid':B.UUID,'disk_serial':B.SERIAL,'disk_bytes':64*1024**3,'uid':0,'euid':0,'pid1':'systemd','root_fstype':'ext4','run_fstype':'tmpfs','network':['lo'],'disks':['sda'],'cmdline':'BOOT_IMAGE=/vmlinuz root=UUID=fixture ro '+ ' '.join(B.FLAGS),'persistent_debug':False,'root_password_locked':True,'debug_shell_active_tty1':True,'cgroup_v2':True,'watchdog_active':True,'machine_id':'a'*32,'boot_id':'11111111-2222-3333-4444-555555555555'}
def config():return {'smbios1':'uuid='+B.UUID,'scsi0':H.VOLUME+',serial='+B.SERIAL+',size=64G','ide2':'none,media=cdrom','boot':'order=scsi0','onboot':0,'agent':'0','serial0':'socket','vga':'std','hotplug':'0','protection':1,'digest':'a'*40,'cores':4,'memory':6000,'balloon':0}
ISO='local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso'
def valid_probe():return {'format':'vm164-readonly-probe-v1','vm_uuid':B.UUID,'boot_id':facts()['boot_id'],'disk_serial':B.SERIAL,'disk_bytes':64*1024**3,'optical_media_present':False}
class PureTests(unittest.TestCase):
 def test_good_boot(self):self.assertTrue(B.assess(facts()))
 def test_cgroup_host_view(self):
  props={'ControlGroup':'/system.slice/debug-shell.service','MainPID':'123'}
  for pid1 in ('0::/','0::/init.scope'):self.assertTrue(B.unified_cgroup(pid1,props,'123\n456\n',True))
  self.assertFalse(B.unified_cgroup('0::/container',props,'123',True))
  self.assertFalse(B.unified_cgroup('0::/init.scope',props,'456',True))
  self.assertFalse(B.unified_cgroup('0::/init.scope',props,'123',False))
  self.assertFalse(B.unified_cgroup('0::/init.scope',dict(props,MainPID='0'),'0',True))
 def test_uuid_refusal_before_commands(self):
  with patch.object(B,'Path') as path,patch.object(B,'command') as command:
   path.return_value.read_text.return_value='wrong'
   with self.assertRaises(B.Refusal):B.facts()
   command.assert_not_called();self.assertEqual(path.call_count,1)
 def test_serial_refusal_before_commands(self):
  with patch.object(B,'Path') as path,patch.object(B,'command') as command:
   path.return_value.read_text.side_effect=[B.UUID,'wrong']
   with self.assertRaises(B.Refusal):B.facts()
   command.assert_not_called();self.assertEqual(path.call_count,2)
 def test_all_boot_boundaries(self):
  changes={'vm_uuid':'wrong','disk_serial':'wrong','disk_bytes':128*1024**3,'uid':1000,'euid':1000,'pid1':'bash','root_fstype':'overlay','run_fstype':'ext4','network':['lo','ens18'],'disks':['sda','sdb'],'cmdline':'root=/dev/sda','persistent_debug':True,'root_password_locked':False,'debug_shell_active_tty1':False,'cgroup_v2':False,'watchdog_active':False}
  for k,v in changes.items():
   with self.subTest(field=k):
    f=facts();f[k]=v
    with self.assertRaises(B.Refusal):B.assess(f)
 def test_conflicting_cmdlines(self):
  for arg in ('init=/bin/bash','rdinit=/bin/sh','rd.break','systemd.unit=rescue.target','systemd.debug_shell=tty9','systemd.debug_shell','single','emergency','autoinstall','ds=nocloud','systemd.mask=sshd.service',B.FLAGS[0],B.FLAGS[1]):
   with self.subTest(arg=arg):
    f=facts();f['cmdline']+=' '+arg
    with self.assertRaises(B.Refusal):B.assess(f)
 def test_changed_boot_identity(self):
  s={'identity':B.binding(facts())};d=facts();d['boot_id']='different'
  with self.assertRaises(B.Refusal):B.match_session(d,s)
 def test_session_ok(self):B.match_session(facts(),{'identity':B.binding(facts())})
 def test_good_host(self):self.assertEqual(H.validate(config(),{'vmid':164,'status':'stopped'},[],phase='empty',iso_volume=ISO,expect_status='stopped')['status'],'PASS_HOST_READBACK_ONLY')
 def test_attached_host(self):
  c=config();c['ide2']=ISO+',media=cdrom';H.validate(c,{'vmid':164,'status':'running'},[],phase='attached',iso_volume=ISO,expect_status='running')
 def test_host_boundaries(self):
  changes={'smbios1':'uuid=wrong','scsi0':H.VOLUME.replace('164/','163/')+',serial='+B.SERIAL+',size=64G','ide2':'installer.iso,media=cdrom','boot':'order=ide2;scsi0','onboot':1,'agent':1,'vga':'serial0','serial0':'/dev/ttyUSB0','hotplug':'disk','protection':0,'digest':'invalid','net0':'virtio','hostpci0':'00:01','usb0':'host=1234','virtiofs0':'share','parallel0':'/dev/lp0','scsi1':'extra','serial1':'socket','args':'-net user','hookscript':'local:script','lock':'backup','cores':1,'memory':4000,'balloon':1}
  for k,v in changes.items():
   with self.subTest(field=k):
    c=config();c[k]=v
    with self.assertRaises(ValueError):H.validate(c,{'vmid':164,'status':'stopped'},[],phase='empty',iso_volume=ISO,expect_status='stopped')
 def test_other_vmid_or_state(self):
  for s in ({'vmid':163,'status':'stopped'},{'vmid':164,'status':'running'}):
   with self.assertRaises(ValueError):H.validate(config(),s,[],phase='empty',iso_volume=ISO,expect_status='stopped')
 def test_pending_refused(self):
  with self.assertRaises(ValueError):H.validate(config(),{'vmid':164,'status':'stopped'},[{'key':'net0','pending':'virtio'}],phase='empty',iso_volume=ISO,expect_status='stopped')
 def test_unknown_media_refused(self):
  with self.assertRaises(ValueError):H.validate(config(),{'vmid':164,'status':'stopped'},[],phase='empty',iso_volume='local:iso/ubuntu.iso',expect_status='stopped')
class FixtureTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.ram=self.root/'ram';self.media=self.root/'media';self.media.mkdir()
  self.patches=[patch.object(B,'RAM',self.ram),patch.object(B,'MEDIA',self.media),patch.object(B,'facts',return_value=facts()),patch.object(B,'snapshot',return_value={'fixture':'abc'})]
  for p in self.patches:p.start()
  self.probe=(TASK.parents[1]/'tasks/jarvis-v2-vm164-lab-readiness-r1/tools/lab_package.py').read_bytes();helper=(TASK/'payload/BOOT.PY').read_bytes()
  for n,b in {'BOOT.PY':helper,'LABPKG.PY':self.probe,'SHA256.SUM':(hashlib.sha256(helper).hexdigest()+'  BOOT.PY\n'+B.PROBE_SHA+'  LABPKG.PY\n').encode()}.items():(self.media/n).write_bytes(b)
  self.rows=[['1','0','0:1','/',str(self.media),'ro,nosuid,nodev,noexec','-','iso9660','/dev/sr0','ro']]
  self.stdout=io.StringIO();self.redirect=contextlib.redirect_stdout(self.stdout);self.redirect.__enter__()
 def tearDown(self):
  self.redirect.__exit__(None,None,None)
  for p in reversed(self.patches):p.stop()
  self.tmp.cleanup()
 def stage(self):
  with patch.object(B,'mount_rows',return_value=self.rows):B.stage()
 def test_full_stage(self):
  self.stage();self.assertEqual((self.ram/'LABPKG.PY').read_bytes(),self.probe);self.assertEqual(os.stat(self.ram).st_mode&0o777,0o700);self.assertEqual(os.stat(self.ram/'BOOT.PY').st_mode&0o777,0o600)
 def test_destination_exists_preserved(self):
  self.ram.mkdir();(self.ram/'keep').write_text('keep')
  with self.assertRaises(FileExistsError):self.stage()
  self.assertEqual((self.ram/'keep').read_text(),'keep')
 def test_corrupt_probe_refused_before_write(self):
  (self.media/'LABPKG.PY').write_text('corrupt')
  with self.assertRaises(B.Refusal):self.stage()
  self.assertFalse(self.ram.exists())
 def test_corrupt_helper_refused(self):
  (self.media/'BOOT.PY').write_text('corrupt')
  with self.assertRaises(B.Refusal):self.stage()
 def test_extra_media_refused(self):
  (self.media/'AUTOEXEC').write_text('x')
  with self.assertRaises(B.Refusal):self.stage()
 def test_writable_media_refused(self):
  self.rows[0][5]='rw,nosuid,nodev,noexec'
  with self.assertRaises(B.Refusal):self.stage()
 def test_media_symlink_refused(self):
  (self.media/'LABPKG.PY').unlink();(self.media/'LABPKG.PY').symlink_to(TASK.parents[1]/'tasks/jarvis-v2-vm164-lab-readiness-r1/tools/lab_package.py')
  with self.assertRaises(OSError):self.stage()
 def test_hardlink_refused(self):
  os.link(self.media/'LABPKG.PY',self.root/'second')
  with self.assertRaises(B.Refusal):self.stage()
 def test_fifo_refused_without_blocking(self):
  p=self.root/'fifo';os.mkfifo(p)
  with self.assertRaises(B.Refusal):B.read_regular(p)
 def test_oversized_input_refused(self):
  p=self.root/'oversize';p.write_bytes(b'a'*65537)
  with self.assertRaises(B.Refusal):B.read_regular(p)
 def test_write_new_no_clobber(self):
  p=self.root/'file';p.write_bytes(b'original')
  with self.assertRaises(FileExistsError):B.write_new(p,b'new')
  self.assertEqual(p.read_bytes(),b'original')
 def test_session_preserved_on_partial_failure(self):
  orig=B.write_new
  def fail(path,data):
   if path.name=='LABPKG.PY':raise OSError('injected')
   orig(path,data)
  with patch.object(B,'write_new',side_effect=fail):
   with self.assertRaises(OSError):self.stage()
  self.assertTrue((self.ram/'BOOT.PY').exists())
 def test_probe_requires_unmounted_media(self):
  self.stage()
  with patch.object(B,'mount_rows',return_value=self.rows),patch.object(B,'command') as cmd:
   with self.assertRaises(B.Refusal):B.probe()
   cmd.assert_not_called()
 def test_probe_full_and_capture_roundtrip(self):
  self.stage();raw=json.dumps(valid_probe(),indent=2)+'\n'
  # Map only sys/block inventory to an empty disposable fixture; never device IO.
  original=Path
  def path(n):return self.root/'empty-sys' if str(n)=='/sys/block' else original(n)
  (self.root/'empty-sys').mkdir()
  with patch.object(B,'Path',side_effect=path),patch.object(B,'mount_rows',return_value=[]),patch.object(B,'command',return_value=subprocess.CompletedProcess([],0,raw,'')) as cmd:B.probe()
  self.assertEqual(cmd.call_args.args[0],['/usr/bin/python3.14','-I','-B','-S',str(self.ram/'LABPKG.PY'),'probe'])
  self.stdout.seek(0);self.stdout.truncate(0)
  for i in range(2):
   try:B.pages(i)
   except B.Refusal:break
  self.assertEqual(D.decode(self.stdout.getvalue(),hashlib.sha256(raw.encode()).hexdigest()),raw.encode())
 def test_close_requires_probe(self):
  self.stage()
  with patch.object(B,'command') as cmd:
   with self.assertRaises(B.Refusal):B.close()
   cmd.assert_not_called()
 def test_close_submits_independent_unit(self):
  self.stage();(self.ram/'PROBE.JSON').write_text('{}')
  with patch.object(B,'command') as cmd:B.close()
  self.assertIn('--unit=vm164-bootstrap-close',cmd.call_args.args[0]);self.assertIn('close-unit',cmd.call_args.args[0])
 def close_fixture(self,props='ActiveState=inactive\nMainPID=0\nUnitFileState=masked-runtime\n',fail_stop=False,unchanged=True,broken_console=False):
  self.stage();calls=[]
  def fake(args,**kwargs):
   calls.append(args)
   if fail_stop and args[1]=='stop':raise B.Refusal('injected_stop_failure')
   return subprocess.CompletedProcess(args,0,props if args[1]=='show' else '', '')
  def output(line):
   if broken_console:raise OSError('injected_TTY_hangup')
   print(line)
  with patch.object(B,'command',side_effect=fake),patch.object(B.time,'sleep'),patch.object(B,'console_line',side_effect=output),patch.object(B,'snapshot',return_value={'fixture':'abc' if unchanged else 'changed'}):
   try:B.close_unit()
   except (B.Refusal,OSError):pass
  self.assertEqual(calls[-1],['/usr/bin/systemctl','--no-block','poweroff'])
  return calls
 def test_cleanup_checks_and_shutdown(self):
  calls=self.close_fixture();self.assertIn(['/usr/bin/systemctl','mask','--runtime','debug-shell.service'],calls);self.assertIn('"temporary_root_closed_this_boot": true',self.stdout.getvalue())
 def test_cleanup_failure_still_shutdown(self):
  self.close_fixture(fail_stop=True);self.assertNotIn('"temporary_root_closed_this_boot": true',self.stdout.getvalue())
 def test_console_hangup_still_shutdown(self):self.close_fixture(broken_console=True)
 def test_incomplete_cleanup_never_passes(self):
  self.close_fixture('ActiveState=active\nMainPID=99\nUnitFileState=masked-runtime\n');self.assertIn('"temporary_root_closed_this_boot": false',self.stdout.getvalue())
 def test_remaining_processes_never_pass(self):
  cgroup=self.root/'cgroup.procs';cgroup.write_text('1234\n');original=Path
  def path(n):return cgroup if str(n)=='/sys/fs/cgroup/system.slice/debug-shell.service/cgroup.procs' else original(n)
  with patch.object(B,'Path',side_effect=path):self.close_fixture()
  self.assertIn('"temporary_root_closed_this_boot": false',self.stdout.getvalue())
 def test_changed_persistent_file_not_repaired(self):
  self.close_fixture(unchanged=False);self.assertIn('"persistent_files_unchanged": false',self.stdout.getvalue())
class CaptureAndMedia(unittest.TestCase):
 def rows(self,raw):
  b=base64.b64encode(raw).decode();return '\n'.join(f'R{i//48:04d}:'+b[i:i+48] for i in range(0,len(b),48))
 def test_decode_ok(self):
  raw=json.dumps(valid_probe()).encode();self.assertEqual(D.decode(self.rows(raw),hashlib.sha256(raw).hexdigest()),raw)
 def test_decode_tamper(self):
  raw=json.dumps(valid_probe()).encode()
  with self.assertRaises(ValueError):D.decode(self.rows(raw),'a'*64)
 def test_decode_missing_duplicate_reorder(self):
  raw=json.dumps(valid_probe()).encode();lines=self.rows(raw).splitlines()
  for bad in (lines[1:],lines+lines[:1],list(reversed(lines))):
   with self.assertRaises(ValueError):D.decode('\n'.join(bad),hashlib.sha256(raw).hexdigest())
 def test_wrong_target_decode(self):
  d=valid_probe();d['vm_uuid']='wrong';raw=json.dumps(d).encode()
  with self.assertRaises(ValueError):D.decode(self.rows(raw),hashlib.sha256(raw).hexdigest())
 def test_media_independent(self):
  root=TASK/'media-build-9';self.assertEqual(M.check(root/'probe-data.iso',json.loads((root/'DELIVERY.json').read_text()))['status'],'PASS_NONBOOT_DATA_ISO')
 def test_reproducibility(self):self.assertEqual((TASK/'media-build-9/probe-data.iso').read_bytes(),(TASK/'media-build-10/probe-data.iso').read_bytes())
 def test_media_tamper(self):
  root=TASK/'media-build-9';d=json.loads((root/'DELIVERY.json').read_text());d['iso_sha256']='a'*64
  with self.assertRaises(ValueError):M.check(root/'probe-data.iso',d)
if __name__=='__main__':unittest.main(verbosity=2)

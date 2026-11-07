"""Real offline publication/validation plus adversarial synthetic inputs; no root claims."""
import copy,datetime,gzip,hashlib,io,json,os,stat,sys,tarfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,'/input/tools')
import lab_package as lab
ROOT=Path('/work');PACKET=Path('/input');PRODUCT=json.loads((PACKET/'BUNDLE.json').read_text())

def facts():return {'vm_uuid':lab.VM_UUID,'disk_serial':lab.SERIAL,'disk_bytes':64*1024**3,'architecture':'x86_64','python_version':'3.14.4','root_filesystem':'ext4','network_interfaces':['lo'],'block_disks':['sda'],'optical_media_present':False,'shared_or_slave_mounts':0,'external_filesystems':0,'os':{'ID':'ubuntu','VERSION_ID':'26.04'},'machine_id':'1'*32,'boot_id':'11111111-1111-4111-8111-111111111111','root_device':'8:2','root_filesystem_uuids':['22222222-2222-4222-8222-222222222222'],'python_sha256':'a'*64,'bwrap_sha256':'b'*64,'native_runtime_files':{'/usr/bin/python3.14':'a'*64,'/usr/lib/libc.so':'b'*64,'/usr/lib/ssl.so':'c'*64},'sqlite_version':'3.46.1','openssl_version':'OpenSSL 3.5.5 27 Jan 2026','cpu_count':4,'memory':{'MemTotal':6000*1024**2,'MemAvailable':4*1024**3},'free_bytes':25*1024**3}
def binding():return {k:v for k,v in facts().items() if k in ('machine_id','boot_id','root_device','root_filesystem_uuids','python_sha256','native_runtime_files','bwrap_sha256')}
def approval():return {'format':'vm164-lab-approval-v1','purpose':'DORMANT_OFFLINE_INSTALL_ONLY','operator_reference':'synthetic-only-not-an-approval','expires_at_utc':(datetime.datetime.now(datetime.UTC)+datetime.timedelta(minutes=10)).isoformat(),'bundle_sha256':'a'*64,'source_git_revision':lab.REVISION,'destination':str(lab.DESTINATION),'target':binding()}
def tar(entries):
 out=io.BytesIO()
 with tarfile.open(fileobj=out,mode='w:gz',format=tarfile.USTAR_FORMAT) as t:
  for name,data,kind in entries:
   m=tarfile.TarInfo(name);m.type=kind;m.size=len(data);m.mode=0o644;m.uid=m.gid=m.mtime=0;t.addfile(m,io.BytesIO(data))
 return out.getvalue()
class Target(unittest.TestCase):
 def test_wrong_vm_probe_refuses_before_other_metadata(self):
  from unittest.mock import patch
  def read(path,*a,**kw):
   if str(path)=='/sys/class/dmi/id/product_uuid':return 'wrong-vm'
   raise AssertionError('wrong target was inspected')
  with patch.object(lab.Path,'read_text',read),self.assertRaises(lab.Refusal):lab.probe()
 def test_good_bound_fixture(self):lab.check_target(facts(),binding())
 def test_valid_approval_schema(self):self.assertEqual(lab.validate_approval(approval(),'a'*64,facts())['purpose'],'DORMANT_OFFLINE_INSTALL_ONLY')
 def test_null_binding_refused(self):
  b=binding();b['machine_id']=None
  with self.assertRaises(lab.Refusal):lab.check_target(facts(),b)
 def test_blank_binding_refused(self):
  b=binding();b['root_filesystem_uuids']=[]
  with self.assertRaises(lab.Refusal):lab.check_target(facts(),b)
 def test_approval_wrong_hash(self):
  with self.assertRaises(lab.Refusal):lab.validate_approval(approval(),'b'*64,facts())
 def test_approval_expired(self):
  a=approval();a['expires_at_utc']=(datetime.datetime.now(datetime.UTC)-datetime.timedelta(seconds=1)).isoformat()
  with self.assertRaises(lab.Refusal):lab.validate_approval(a,'a'*64,facts())
 def test_approval_excessive_window(self):
  a=approval();a['expires_at_utc']=(datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=2)).isoformat()
  with self.assertRaises(lab.Refusal):lab.validate_approval(a,'a'*64,facts())
 def test_approval_wrong_purpose(self):
  a=approval();a['purpose']='ACTIVATE_REAL_EXECUTOR'
  with self.assertRaises(lab.Refusal):lab.validate_approval(a,'a'*64,facts())
 def test_approval_extra_field(self):
  a=approval();a['allow_nic']=True
  with self.assertRaises(lab.Refusal):lab.validate_approval(a,'a'*64,facts())
 def test_approval_wrong_destination(self):
  a=approval();a['destination']='/opt/g6k-serial'
  with self.assertRaises(lab.Refusal):lab.validate_approval(a,'a'*64,facts())
 def test_approval_unbound_boot(self):
  a=approval();a['target']['boot_id']='different'
  with self.assertRaises(lab.Refusal):lab.validate_approval(a,'a'*64,facts())
for key,value in {'vm_uuid':'wrong','disk_serial':'wrong','disk_bytes':32*1024**3,'architecture':'aarch64','python_version':'3.11.0','sqlite_version':'3.40.0','openssl_version':'unsupported','root_filesystem':'overlay','network_interfaces':['lo','eth0'],'block_disks':['sda','sdb'],'optical_media_present':True,'shared_or_slave_mounts':1,'external_filesystems':1,'os':{'ID':'ubuntu','VERSION_ID':'24.04'},'cpu_count':1,'memory':{'MemTotal':3*1024**3,'MemAvailable':2*1024**3},'free_bytes':1024}.items():
 def test(self,k=key,v=value):
  f=facts();f[k]=v
  with self.assertRaises(lab.Refusal):lab.check_target(f,binding())
 setattr(Target,'test_refuses_'+key,test)
class Archives(unittest.TestCase):
 def test_duplicate_json(self):
  with self.assertRaises(lab.Refusal):lab.decode(b'{"a":1,"a":2}')
 def test_tar_symlink(self):
  with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('x',b'',tarfile.SYMTYPE)]))
 def test_tar_hardlink(self):
  with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('x',b'',tarfile.LNKTYPE)]))
 def test_tar_fifo(self):
  with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('x',b'',tarfile.FIFOTYPE)]))
 def test_tar_duplicate(self):
  with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('x',b'a',tarfile.REGTYPE),('x',b'b',tarfile.REGTYPE)]))
 def test_tar_parent_escape(self):
  with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('../outside',b'bad',tarfile.REGTYPE)]))
 def test_tar_absolute(self):
  with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('/outside',b'bad',tarfile.REGTYPE)]))
 def test_tar_expansion_bound(self):
  before=lab.MAX_FILE;lab.MAX_FILE=2
  try:
   with self.assertRaises(lab.Refusal):lab.verify_tar(tar([('x',b'123',tarfile.REGTYPE)]))
  finally:lab.MAX_FILE=before
 def test_corrupt_bundle_hash_before_parse(self):
  with self.assertRaises(lab.Refusal):lab.load_bundle(PACKET/PRODUCT['bundle'],'0'*64)
 def test_missing_independent_pin(self):
  with self.assertRaises(lab.Refusal):lab.load_bundle(PACKET/PRODUCT['bundle'],'')
 def test_wheel_wrong_identity(self):
  raw=next((PACKET/'wheel-fixture').glob('*.whl')).read_bytes()
  with self.assertRaises(lab.Refusal):lab.wheel_payload(raw,'wrong-name','0')
 def test_wheel_record_tampering(self):
  raw=next((PACKET/'wheel-fixture').glob('*.whl')).read_bytes();out=io.BytesIO()
  with zipfile.ZipFile(io.BytesIO(raw)) as old,zipfile.ZipFile(out,'w') as z:
   for n in old.namelist():z.writestr(n,old.read(n)+(b'altered' if n.endswith('.py') else b''))
  with self.assertRaises(lab.Refusal):lab.wheel_payload(out.getvalue(),'idna','3.11')
class Filesystem(unittest.TestCase):
 def setUp(self):
  self.parent=ROOT/self._testMethodName;self.parent.mkdir(mode=0o700);self.files={'a/file':b'synthetic','b':b'other'};self.hashes={n:lab.digest(b) for n,b in self.files.items()}
 def test_public_code_modes_ignore_restrictive_umask(self):
  previous=os.umask(0o077)
  try:lab.publish(self.parent,'new',self.files,owner=os.getuid())
  finally:os.umask(previous)
  self.assertEqual(stat.S_IMODE((self.parent/'new').stat().st_mode),0o755)
  self.assertEqual(stat.S_IMODE((self.parent/'new/a').stat().st_mode),0o755)
  self.assertEqual(stat.S_IMODE((self.parent/'new/a/file').stat().st_mode),0o644)
 def test_publish_validate_quarantine_preserves_every_byte(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid());lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
  target=lab.quarantine(self.parent,'new',self.hashes,owner=os.getuid(),tag='20261106T000000Z');lab.validate_installed(self.parent/target,self.hashes,owner=os.getuid());self.assertFalse((self.parent/'new').exists())
 def test_exclusive_destination_no_overwrite(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid())
  with self.assertRaises(FileExistsError):lab.publish(self.parent,'new',{'b':b'overwrite'},owner=os.getuid())
  self.assertEqual((self.parent/'new/b').read_bytes(),b'other')
 def test_interruption_retains_partial_output(self):
  with self.assertRaises(lab.Refusal):lab.publish(self.parent,'new',self.files,owner=os.getuid(),fail_after=1)
  self.assertEqual((self.parent/'new/a/file').read_bytes(),b'synthetic')
  with self.assertRaises(lab.Refusal):lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
 def test_unsafe_parent_refused_before_creation(self):
  self.parent.chmod(0o777)
  with self.assertRaises(lab.Refusal):lab.publish(self.parent,'new',self.files,owner=os.getuid())
  self.assertFalse((self.parent/'new').exists());self.parent.chmod(0o700)
 def test_symlink_parent_refused(self):
  alias=ROOT/(self._testMethodName+'-alias');alias.symlink_to(self.parent)
  with self.assertRaises((OSError,lab.Refusal)):lab.publish(alias,'new',self.files,owner=os.getuid())
  self.assertFalse((self.parent/'new').exists())
 def test_wrong_owner_refuses_fixture_as_root_custody(self):
  with self.assertRaises(lab.Refusal):lab.protected_chain(self.parent,owner=0,directory=True)
 def test_modified_file_refused(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid());(self.parent/'new/b').write_bytes(b'changed')
  with self.assertRaises(lab.Refusal):lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
 def test_extra_file_refused(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid());(self.parent/'new/extra').write_bytes(b'unknown')
  with self.assertRaises(lab.Refusal):lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
 def test_hardlink_substitution_refused(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid());os.link(self.parent/'new/b',self.parent/'alias')
  with self.assertRaises(lab.Refusal):lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
 def test_symlink_file_refused(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid());(self.parent/'new/b').rename(self.parent/'original');(self.parent/'new/b').symlink_to(self.parent/'original')
  with self.assertRaises(lab.Refusal):lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
 def test_writable_file_refused(self):
  lab.publish(self.parent,'new',self.files,owner=os.getuid());(self.parent/'new/b').chmod(0o666)
  with self.assertRaises(lab.Refusal):lab.validate_installed(self.parent/'new',self.hashes,owner=os.getuid())
class ExactPackage(unittest.TestCase):
 def test_full_wheel_source_install_and_recheck(self):
  m,files=lab.load_bundle(PACKET/PRODUCT['bundle'],PRODUCT['bundle_sha256'])
  lab.publish(ROOT,'installed',files,owner=os.getuid());lab.validate_installed(ROOT/'installed',{n:lab.digest(b) for n,b in files.items()},owner=os.getuid())
  self.assertEqual(len(m['dependencies']),31);self.assertEqual(len(m['source_sha256']),315)
  self.assertFalse((ROOT/'installed/source/config.yaml').exists());self.assertFalse((ROOT/'installed/source/data').exists())
  (ROOT/'INSTALL-RESULT.json').write_text(json.dumps({'status':'SYNTHETIC_UNPRIVILEGED_INSTALL_PASS','files':len(files),'bytes':sum(map(len,files.values())),'root_ownership_or_multi_uid_proof':False,'installed_tree':'installed','installed_manifest_sha256':lab.digest(files['INSTALL-MANIFEST.json'])},indent=2)+'\n')
if __name__=='__main__':unittest.main()

"""Same-UID unprivileged fixtures. Never execute qualification or inspect host secrets."""
import json,os,stat,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import environment_probe as ep
from safety_preflight import validate_environment,validate_approval
from prequalification_tests import approval

HERE=Path(__file__).parent
ROOT='1 0 8:1 / / rw - ext4 /dev/sda1 rw'
BOOT='2 1 8:2 / /boot rw - ext4 /dev/sda2 rw'
CRED='3 1 0:3 / /run/credentials/fixture.service ro,nosuid,nodev,noexec - tmpfs tmpfs ro'
def environment(extra='',**kw):
    values=dict(hostname='jarvis-security',interfaces=['lo'],mountinfo=ROOT+('\n'+extra if extra else ''),credential_paths=[])
    values.update(kw);return validate_environment(**values)

class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.previous_umask=os.umask(0o022)
        self.tmp=tempfile.TemporaryDirectory(dir=HERE);self.root=Path(self.tmp.name)
        for name in ('home/jarvis','run/credentials','var/lib/cloud/instances/fixture'):
            self.path(name).mkdir(parents=True,mode=0o755)
        self.path('var/lib/cloud/instance').symlink_to('instances/fixture')
    def tearDown(self):self.tmp.cleanup();os.umask(self.previous_umask)
    def path(self,p):return self.root/p
    def write(self,p,data=b'synthetic',mode=0o600):
        f=self.path(p);f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);f.chmod(mode);return f
    def inspect(self):return ep.inspect_environment_paths(root=self.root,root_uid=os.getuid(),preparation_uid=os.getuid())
    def blocked(self):self.assertTrue(self.inspect()['findings'])
    def cache(self):return self.write('var/lib/cloud/instances/fixture/user-data.txt')
    def review(self,r):return {'cloud_cache_review':{'provenance':'FRESH_DISPOSABLE_IMAGE_NO_IMPORTED_CREDENTIALS','metadata_sha256':r['cloud_cache_metadata_sha256']}}
    def test_empty_os_containers_allowed(self):
        r=self.inspect();self.assertEqual(r['findings'],[]);ep.require_paths(r,{})
    def test_preparation_artifact_home_allowed(self):
        self.write('home/jarvis/gate6k-artifacts/offline.tar');self.write('home/jarvis/gate6l-bundle/manifest')
        self.assertEqual(self.inspect()['findings'],[])
    def test_unknown_preparation_uid_refused(self):
        self.assertIn('UNVERIFIED_PREPARATION_HOME',ep.inspect_environment_paths(root=self.root,root_uid=os.getuid())['findings'])
    def test_preparation_home_symlink_refused(self):
        self.path('home/jarvis').rmdir();self.path('home/jarvis').symlink_to('../elsewhere');self.blocked()
    def test_home_writable_refused(self):self.path('home/jarvis').chmod(0o777);self.blocked()
    def test_home_known_credential_markers_refused(self):
        for marker in ep.HOME_MARKERS:
            f=self.write('home/jarvis/'+marker)
            with self.subTest(marker=marker):self.blocked()
            f.unlink()
    def test_root_known_credential_paths_refused(self):
        self.write('root/.netrc');self.blocked()
    def test_production_state_refused(self):
        self.path('home/jarvis/.hermes-poc').mkdir();self.blocked()
    def test_credential_payload_even_empty_refused(self):
        self.write('run/credentials/fixture.service/value',b'');self.blocked()
    def test_credential_store_all_locations_refused(self):
        for store in ep.CREDENTIAL_STORES:
            f=self.write(store.lstrip('/')+'/value')
            with self.subTest(store=store):self.blocked()
            f.unlink()
    def test_credential_store_symlink_refused(self):
        self.path('run/credentials').rmdir();self.path('run/credentials').symlink_to('/absent');self.blocked()
    def test_private_cloud_cache_requires_explicit_review(self):
        self.cache();r=self.inspect();self.assertEqual(r['findings'],[]);self.assertEqual(r['cloud_cache_files'],1)
        with self.assertRaisesRegex(RuntimeError,'CLOUD_CACHE_REVIEW_REQUIRED'):ep.require_paths(r,{})
        ep.require_paths(r,self.review(r))
    def test_review_cannot_override_systemd_payload(self):
        self.cache();self.write('run/credentials/unit/value');r=self.inspect()
        self.assertEqual(r['cloud_cache_files'],1)
        with self.assertRaises(RuntimeError):ep.require_paths(r,self.review(r))
    def test_cache_metadata_change_invalidates_review(self):
        f=self.cache();r=self.inspect();f.write_bytes(b'new synthetic bytes')
        with self.assertRaises(RuntimeError):ep.require_paths(self.inspect(),self.review(r))
    def test_world_readable_opaque_cache_refused(self):
        for name in ('obj.pkl','user-data.txt','vendor-data.txt','unknown-data','scripts/run'):
            f=self.write('var/lib/cloud/instances/fixture/'+name,mode=0o644)
            with self.subTest(name=name):self.blocked()
            f.unlink()
    def test_previous_instance_and_seed_inventoried(self):
        self.write('var/lib/cloud/seed/nocloud/user-data');self.write('var/lib/cloud/instances/previous/obj.pkl')
        self.assertEqual(self.inspect()['cloud_cache_files'],2)
    def test_canonical_absolute_alias_allowed(self):
        p=self.path('var/lib/cloud/instance');p.unlink();p.symlink_to('/var/lib/cloud/instances/fixture')
        self.assertEqual(self.inspect()['findings'],[])
    def test_escaping_and_noncanonical_alias_refused(self):
        p=self.path('var/lib/cloud/instance')
        for target in ('../../root','/root','instances/../fixture','instances/missing','/var/lib/cloud/instances/fixture/extra'):
            p.unlink();p.symlink_to(target)
            with self.subTest(target=target):self.blocked()
    def test_cloud_nested_symlink_refused(self):
        self.path('var/lib/cloud/instances/fixture/link').symlink_to('/root');self.blocked()
    def test_cloud_fifo_refused(self):os.mkfifo(self.path('var/lib/cloud/instances/fixture/fifo'));self.blocked()
    def test_cloud_hardlink_refused(self):
        f=self.cache();os.link(f,self.path('var/lib/cloud/instances/fixture/other'));self.blocked()
    def test_cloud_key_indicator_refused(self):
        self.write('var/lib/cloud/instances/fixture/private.key');self.blocked()
    def test_cloud_unprotected_directory_refused(self):self.path('var/lib/cloud/instances').chmod(0o777);self.blocked()
    def test_wrong_owner_refused(self):
        r=ep.inspect_environment_paths(root=self.root,root_uid=os.getuid()+10000,preparation_uid=os.getuid())
        self.assertTrue(r['findings'])
    def test_unreadable_metadata_refuses(self):
        with patch.object(ep.os,'listdir',side_effect=PermissionError()):self.blocked()
    def test_only_directories_opened_never_secret_contents(self):
        self.cache();real=os.open;opened=[]
        def directory_only(path,flags,*args,**kwargs):
            self.assertTrue(flags&os.O_DIRECTORY);self.assertTrue(flags&os.O_NOFOLLOW)
            opened.append(True);return real(path,flags,*args,**kwargs)
        with patch.object(ep.os,'open',side_effect=directory_only),patch('builtins.open',side_effect=AssertionError('content open')):
            r=self.inspect()
        self.assertEqual(r['findings'],[]);self.assertTrue(opened)
    def test_output_contains_no_private_bytes_or_filenames(self):
        self.write('var/lib/cloud/instances/fixture/opaque-private-name',b'PRIVATE-FIXTURE-CONTENT')
        out=json.dumps(self.inspect());self.assertNotIn('PRIVATE-FIXTURE',out);self.assertNotIn('opaque-private-name',out)
    def test_missing_cloud_entry_during_scan_refuses(self):
        self.cache();real=ep.Metadata.info
        def changed(obj,path):
            if path=='/var/lib/cloud/instances':return None
            return real(obj,path)
        with patch.object(ep.Metadata,'info',changed):self.blocked()
    def test_inspection_root_writable_refused(self):self.root.chmod(0o777);self.blocked()
    def test_ancestor_symlink_refused(self):
        self.path('home/jarvis/.config').symlink_to('/elsewhere');self.blocked()
    def test_tree_depth_budget_refuses(self):
        self.path('var/lib/cloud/'+'/'.join(['deep']*19)).mkdir(parents=True);self.blocked()

class MountTests(unittest.TestCase):
    def test_documented_boot_and_empty_systemd_mounts_supported(self):environment(BOOT+'\n'+CRED,boot_source='/dev/sda2')
    def test_boot_requires_explicit_binding(self):
        with self.assertRaises(RuntimeError):environment(BOOT)
    def test_wrong_boot_source_refused(self):
        with self.assertRaises(RuntimeError):environment(BOOT,boot_source='/dev/sdb2')
    def test_missing_approved_boot_refused(self):
        with self.assertRaises(RuntimeError):environment(boot_source='/dev/sda2')
    def test_boot_bind_or_same_root_device_refused(self):
        for row in (BOOT.replace('8:2','8:1'),BOOT.replace('8:2 /','8:2 /subtree'),BOOT.replace('ext4','nfs')):
            with self.subTest(row=row),self.assertRaises(RuntimeError):environment(row,boot_source='/dev/sda2')
    def test_offline_iso_still_refused(self):
        with self.assertRaises(RuntimeError):environment('2 1 11:0 / /mnt/g6l-cd ro - iso9660 /dev/sr0 ro')
    def test_credential_mount_requires_all_protections(self):
        for flag in ('ro','nosuid','nodev','noexec'):
            with self.subTest(flag=flag),self.assertRaises(RuntimeError):environment(CRED.replace('ro,nosuid,nodev,noexec',','.join(x for x in ('ro','nosuid','nodev','noexec') if x!=flag)))
    def test_credential_bind_refused(self):
        with self.assertRaises(RuntimeError):environment(CRED.replace('0:3 /','0:3 /other'))
    def test_shared_filesystems_refused(self):
        for fs in ('9p','virtiofs','nfs','cifs','overlay','fuse.sshfs','autofs'):
            with self.subTest(fs=fs),self.assertRaises(RuntimeError):environment(f'2 1 0:4 / /mnt/shared rw - {fs} fixture rw')
    def test_hidden_protected_paths_refused(self):
        for path in ('/home','/home/jarvis','/root','/var/lib/cloud','/opt/g6k-preflight-r1','/etc/credstore'):
            with self.subTest(path=path),self.assertRaises(RuntimeError):environment(f'2 1 0:4 / {path} rw - tmpfs tmpfs rw')
    def test_network_and_prohibited_host_refused(self):
        for kwargs in ({'interfaces':['lo','ens18']},{'hostname':'nexus-services'},{'hostname':'jarvis-core'},{'hostname':'pve'},{'hostname':'ai-server'}):
            with self.subTest(kwargs=kwargs),self.assertRaises(RuntimeError):environment(**kwargs)
    def test_duplicate_mount_refused(self):
        with self.assertRaises(RuntimeError):environment(CRED+'\n'+CRED)
    def test_malformed_mount_refused(self):
        for row in ('invalid','2 1 x / /run rw - tmpfs tmpfs rw','2 1 0:1 / /run/../etc rw - tmpfs tmpfs rw'):
            with self.subTest(row=row),self.assertRaises(RuntimeError):environment(row)
    def test_shared_propagation_remains_refused(self):
        with self.assertRaises(RuntimeError):environment(CRED.replace(' - ',' shared:3 - '))

class LaunchAndApprovalTests(unittest.TestCase):
    def test_isolated_import_without_executing_qualification(self):
        program='import runpy; d=runpy.run_path('+repr(str(HERE/'qualify_all.py'))+',run_name="import_only"); assert callable(d["execute"])'
        r=subprocess.run([sys.executable,'-I','-B','-c',program],capture_output=True,text=True,timeout=15)
        self.assertEqual(r.returncode,0,r.stderr)
    def test_exact_new_release_and_optional_reviews(self):
        a=approval();a.update(release='/opt/g6k-preflight-r1',boot_source='/dev/sda2',cloud_cache_review={'provenance':'FRESH_DISPOSABLE_IMAGE_NO_IMPORTED_CREDENTIALS','metadata_sha256':'e'*64})
        validate_approval(a,'1'*32,release='/opt/g6k-preflight-r1')
        with self.assertRaises(RuntimeError):validate_approval(a,'1'*32)
    def test_invalid_optional_fields_refused(self):
        for field,value in [('boot_source','/dev/../etc'),('boot_source',True),('cloud_cache_review',{}),('cloud_cache_review',{'provenance':'OPERATOR_SILENCE','metadata_sha256':'e'*64}),('allow_credentials',True)]:
            a=approval();a[field]=value
            with self.subTest(field=field),self.assertRaises(RuntimeError):validate_approval(a,'1'*32)
    def test_preflight_report_has_no_qualification_import(self):
        import ast
        tree=ast.parse((HERE/'preflight_report.py').read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertNotIn('qualify_multi_uid',imports);self.assertNotIn('qualify_all',imports)

if __name__=='__main__':unittest.main(verbosity=2)

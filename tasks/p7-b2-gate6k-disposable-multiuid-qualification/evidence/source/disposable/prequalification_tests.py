"""Unprivileged Gate6K checks. No main(), setuid(), provisioning or real providers."""
import hashlib,io,json,os,stat,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import safe_extract as se
from safety_preflight import validate_approval,read_approval,validate_capacity,validate_environment
from offline_artifacts import verify_artifacts

HERE=Path(__file__).parent
H=lambda b:hashlib.sha256(b).hexdigest()

class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=HERE);self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def archive(self,extra=None,*,pax=None,manifest_change=None):
        content=b'reviewed fixture';manifest=(H(content)+'  repo/source.py\n').encode()
        if manifest_change:manifest=manifest_change(manifest)
        p=self.root/'release.tar'
        with tarfile.open(p,'w',format=tarfile.PAX_FORMAT) as t:
            for name,data in [('repo/source.py',content),('SOURCE-SHA256SUMS',manifest)]:
                m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o664
                if pax:m.pax_headers=pax
                t.addfile(m,io.BytesIO(data))
            if extra:
                m,data=extra;t.addfile(m,io.BytesIO(data) if data is not None else None)
        return p,H(p.read_bytes()),H(manifest)
    def extract(self,args):return se.extract(args[0],self.root/'dest',args[1],args[2])
    def test_valid_extraction_normalizes_metadata(self):
        args=self.archive(pax={'mtime':'100.1'});self.assertEqual(self.extract(args)['members'],2)
        self.assertEqual((self.root/'dest/repo/source.py').stat().st_mode&0o777,0o644)
        self.assertEqual((self.root/'dest').stat().st_mode&0o777,0o755)
    def test_restrictive_umask_keeps_package_traversable(self):
        args=self.archive();previous=os.umask(0o077)
        try:self.extract(args)
        finally:os.umask(previous)
        self.assertEqual((self.root/'dest/repo').stat().st_mode&0o777,0o755)
    def test_existing_destination_refused(self):
        args=self.archive();(self.root/'dest').mkdir()
        with self.assertRaises(FileExistsError):self.extract(args)
    def test_destination_symlink_refused(self):
        args=self.archive();(self.root/'dest').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(FileExistsError):self.extract(args)
    def test_parent_symlink_refused(self):
        args=self.archive();(self.root/'link').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(OSError):se.extract(args[0],self.root/'link/dest',*args[1:])
    def test_writable_parent_refused(self):
        args=self.archive();(self.root/'parent').mkdir(mode=0o777);(self.root/'parent').chmod(0o777)
        with self.assertRaises(ValueError):se.extract(args[0],self.root/'parent/dest',*args[1:])
    def test_archive_digest_refused_before_destination(self):
        args=self.archive()
        with self.assertRaises(ValueError):self.extract((args[0],'0'*64,args[2]))
        self.assertFalse((self.root/'dest').exists())
    def test_manifest_digest_refused(self):
        args=self.archive()
        with self.assertRaises(ValueError):self.extract((args[0],args[1],'0'*64))
    def test_member_digest_refused(self):
        with self.assertRaises(ValueError):self.extract(self.archive(manifest_change=lambda b:b.replace(b[:64],b'0'*64)))
    def test_manifest_duplicate_refused(self):
        with self.assertRaises(ValueError):self.extract(self.archive(manifest_change=lambda b:b+b))
    def test_pax_path_override_refused(self):
        with self.assertRaises(ValueError):self.extract(self.archive(pax={'path':'override'}))
    def test_sparse_pax_refused(self):
        with self.assertRaises((ValueError,tarfile.TarError)):self.extract(self.archive(pax={'GNU.sparse.size':'1'}))
    def test_archive_symlink_refused(self):
        args=self.archive();link=self.root/'link';link.symlink_to(args[0])
        with self.assertRaises(OSError):self.extract((link,*args[1:]))
    def test_archive_hardlink_refused(self):
        args=self.archive();os.link(args[0],self.root/'other')
        with self.assertRaises(ValueError):self.extract(args)
    def test_archive_fifo_refused_without_blocking(self):
        p=self.root/'fifo';os.mkfifo(p)
        with self.assertRaises(ValueError):self.extract((p,'0'*64,'0'*64))
    def test_archive_size_budget(self):
        args=self.archive()
        with patch.object(se,'MAX_ARCHIVE',1),self.assertRaises(ValueError):self.extract(args)
    def test_member_size_budget(self):
        args=self.archive()
        with patch.object(se,'MAX_FILE',1),self.assertRaises(ValueError):self.extract(args)
    def test_member_count_budget(self):
        args=self.archive()
        with patch.object(se,'MAX_MEMBERS',1),self.assertRaises(ValueError):self.extract(args)
    def test_total_size_budget(self):
        args=self.archive()
        with patch.object(se,'MAX_TOTAL',1),self.assertRaises(ValueError):self.extract(args)
    def test_interrupted_extraction_preserved_and_retry_refused(self):
        args=self.archive()
        with patch.object(se.os,'fsync',side_effect=OSError('fixture interruption')),self.assertRaises(OSError):self.extract(args)
        self.assertTrue((self.root/'dest').is_dir());self.assertEqual((self.root/'dest').stat().st_mode&0o777,0o700)
        with self.assertRaises(FileExistsError):self.extract(args)


def malicious_test(name,kind=tarfile.REGTYPE,mode=0o644,link=''):
    def test(self):
        m=tarfile.TarInfo(name);m.type=kind;m.mode=mode;m.linkname=link;m.size=0
        with self.assertRaises((ValueError,tarfile.TarError)):self.extract(self.archive((m,b'' if kind==tarfile.REGTYPE else None)))
        self.assertFalse((self.root/'dest').exists())
    return test
for label,options in {
 'absolute':('/tmp/escape',),'traversal':('../escape',),'nested_traversal':('repo/../../escape',),
 'dot':('./escape',),'empty_segment':('repo//escape',),'backslash':('repo\\escape',),'duplicate':('repo/source.py',),
 'file_parent_conflict':('repo/source.py/child',),'manifest_control_collision':('SOURCE-SHA256SUMS',),
 'symlink':('link',tarfile.SYMTYPE,0o644,'../escape'),'hardlink':('hard',tarfile.LNKTYPE,0o644,'repo/source.py'),
 'device':('dev',tarfile.CHRTYPE),'block':('block',tarfile.BLKTYPE),'fifo':('fifo',tarfile.FIFOTYPE),
 'directory':('dir',tarfile.DIRTYPE),'setuid':('suid',tarfile.REGTYPE,0o4755),'world_writable':('ww',tarfile.REGTYPE,0o666),
 'unknown_type':('unknown',b'Z')}.items():setattr(ExtractionTests,'test_reject_'+label,malicious_test(*options))


def approval():
    return dict(machine_id='1'*32,scope='GATE6K_DISPOSABLE_ONLY',network='NO_NIC',release='/opt/g6j-release',credentials='NONE',mounts='PRIVATE_ROOT_ONLY',test_scope='SYNTHETIC_MULTI_UID_NO_POWERCUT',source_manifest='a'*64,archive_sha256='b'*64,artifacts_sha256='c'*64,vmid=9876,vm_uuid='12345678-1234-1234-1234-123456789abc',hypervisor_node='reviewed-node',disk_identity='private-disk-serial',operator_console='console-review-record',snapshot_preservation_policy='retain failures; no reset')

class PreflightTests(unittest.TestCase):
    def test_exact_approval_shape(self):validate_approval(approval(),'1'*32)
    def test_each_missing_authorization_field_refused(self):
        for key in approval():
            a=approval();del a[key]
            with self.subTest(key=key),self.assertRaises(RuntimeError):validate_approval(a,'1'*32)
    def test_bad_authorization_values_refused(self):
        for key,value in [('vmid',200),('vmid',True),('vm_uuid','unknown'),('operator_console','PENDING'),('machine_id','other'),('archive_sha256','wrong'),('scope','GATE6J_DISPOSABLE_ONLY')]:
            a=approval();a[key]=value
            with self.subTest(key=key),self.assertRaises(RuntimeError):validate_approval(a,'1'*32)
    def test_shared_propagation_refused(self):
        for optional in ('shared:1','master:2','propagate_from:3'):
            with self.subTest(optional=optional),self.assertRaises(RuntimeError):validate_environment(hostname='fixture',interfaces=['lo'],mountinfo='1 0 8:1 / / rw '+optional+' - ext4 /dev/vda1 rw',credential_paths=[])
    def test_protected_mount_overrides_refused(self):
        for mount in ('/var','/var/lib','/var/lib/g6j-disposable','/opt','/opt/g6j-release','/opt/g6j-venv','/etc','/usr','/lib','/bin'):
            with self.subTest(mount=mount),self.assertRaises(RuntimeError):validate_environment(hostname='fixture',interfaces=['lo'],mountinfo='1 0 8:1 / / rw - ext4 /dev/vda1 rw\n2 1 0:1 / '+mount+' rw - tmpfs tmpfs rw',credential_paths=[])
    def test_automount_refused(self):
        with self.assertRaises(RuntimeError):validate_environment(hostname='fixture',interfaces=['lo'],mountinfo='1 0 8:1 / / rw - ext4 /dev/vda1 rw\n2 1 0:1 / /media rw - autofs systemd-1 rw',credential_paths=[])
    def test_normal_virtual_mounts_allowed(self):
        validate_environment(hostname='fixture',interfaces=['lo'],mountinfo='1 0 8:1 / / rw - ext4 /dev/vda1 rw\n2 1 0:1 / /run rw - tmpfs tmpfs rw\n3 1 0:2 / /proc rw - proc proc rw',credential_paths=[])
    def test_capacity_boundary(self):
        with patch('safety_preflight.shutil.disk_usage',return_value=SimpleNamespace(free=20*1024**3)):validate_capacity('/')
        with patch('safety_preflight.shutil.disk_usage',return_value=SimpleNamespace(free=20*1024**3-1)),self.assertRaises(RuntimeError):validate_capacity('/')
    def test_bounded_regular_marker(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            p=Path(d)/'approval';p.write_text(json.dumps(approval()));p.chmod(0o600)
            self.assertEqual(read_approval(p,owner_uid=os.getuid()),approval())
            p.write_text('{"scope":1,"scope":2}')
            with self.assertRaises(ValueError):read_approval(p,owner_uid=os.getuid())
            p.write_bytes(b' '*8193)
            with self.assertRaises(ValueError):read_approval(p,owner_uid=os.getuid())
    def test_marker_special_modes_links_refused(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            p=Path(d)/'approval';os.mkfifo(p,0o600)
            with self.assertRaises(RuntimeError):read_approval(p,owner_uid=os.getuid())
            p.unlink();p.write_text('{}');p.chmod(0o644)
            with self.assertRaises(RuntimeError):read_approval(p,owner_uid=os.getuid())
            p.chmod(0o600);os.link(p,Path(d)/'hard')
            with self.assertRaises(RuntimeError):read_approval(p,owner_uid=os.getuid())

class ArtifactTests(unittest.TestCase):
    def test_artifact_hashes_not_only_versions(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            root=Path(d);f=root/'package.whl';f.write_bytes(b'synthetic artifact');f.chmod(0o644)
            value={'distribution:fixture':dict(version='1',filename=f.name,sha256=H(f.read_bytes()),provenance_record='fixture independent record')}
            p=root/'ARTIFACTS.json';p.write_text(json.dumps(value));h=H(p.read_bytes())
            with patch('offline_artifacts.required_artifacts',return_value={'distribution:fixture':'1'}):
                self.assertEqual(verify_artifacts(root,root,h)['artifact_count'],1)
                f.write_bytes(b'tampered same declared version')
                with self.assertRaises(ValueError):verify_artifacts(root,root,h)
    def test_missing_artifact_or_record_refused(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            root=Path(d);p=root/'ARTIFACTS.json';p.write_text('{}')
            with patch('offline_artifacts.required_artifacts',return_value={'distribution:fixture':'1'}):
                with self.assertRaises(ValueError):verify_artifacts(root,root,H(p.read_bytes()))
                with self.assertRaises(ValueError):verify_artifacts(root,root,'0'*64)

class FailureEvidenceTests(unittest.TestCase):
    def test_preflight_refusal_is_blocked_and_writes_no_fixture(self):
        import qualify_all as q
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            base=Path(d)/'not_created'
            with patch.object(q,'BASE',base),patch.object(q,'execute',side_effect=RuntimeError('fixture')),patch('builtins.print') as output:
                self.assertEqual(q.guarded_execute(),1)
                self.assertEqual(json.loads(output.call_args.args[0])['result'],'BLOCKED');self.assertFalse(base.exists())
    def test_interrupted_preparation_seals_failure(self):
        import qualify_all as q
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            base=Path(d)/'new'
            def interrupted():base.mkdir();raise RuntimeError('fixture interrupted')
            with patch.object(q,'BASE',base),patch.object(q,'execute',side_effect=interrupted),patch('builtins.print'):
                self.assertEqual(q.guarded_execute(),1)
            self.assertEqual(json.loads((base/'qualification.json').read_text())['result'],'FAIL')
            self.assertTrue((base/'EVIDENCE-SHA256SUMS').is_file())
    def test_preexisting_failure_evidence_not_overwritten(self):
        import qualify_all as q
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            base=Path(d);(base/'report.json').write_bytes(b'preserved')
            with patch.object(q,'BASE',base),patch.object(q,'execute',side_effect=FileExistsError()),patch('builtins.print'):
                self.assertEqual(q.guarded_execute(),1)
            self.assertEqual((base/'report.json').read_bytes(),b'preserved');self.assertEqual(len(list(base.iterdir())),1)
    def test_socket_dac_denials_are_actual_permission_errors(self):
        from contextlib import ExitStack
        from qualify_multi_uid import socket_mutation_denials
        with ExitStack() as stack:
            for name in ('unlink','rename','chmod','symlink'):stack.enter_context(patch('qualify_multi_uid.os.'+name,side_effect=PermissionError()))
            self.assertEqual(socket_mutation_denials(Path('/fixture/control.sock')),[True]*4)
        with patch('qualify_multi_uid.os.unlink',side_effect=FileNotFoundError()),self.assertRaises(FileNotFoundError):socket_mutation_denials(Path('/fixture/control.sock'))

if __name__=='__main__':unittest.main(verbosity=2)

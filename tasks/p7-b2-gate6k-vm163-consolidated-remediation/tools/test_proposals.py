"""Unprivileged Nexus fixtures only. Root IDs/mount propagation are NOT exercised."""
import errno,hashlib,json,os,stat,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import metadata_only as mo
import artifact_transfer as at
sys.path.insert(0,'/home/nexus/.local/share/jarvis-gate6k-preflight-fix/candidate-r1/disposable')
from safety_preflight import validate_environment,validate_approval
from environment_probe import inspect_environment_paths,require_paths
ROOT=Path('/home/nexus/.local/share/jarvis-vm163-remediation-plan-r1')
H=lambda x:hashlib.sha256(x).hexdigest()

class Fixture(unittest.TestCase):
    def setUp(self):
        self.old_umask=os.umask(0o022);self.temp=tempfile.TemporaryDirectory(dir=ROOT);self.root=Path(self.temp.name)
    def tearDown(self):
        # Cleanup ONLY generated test fixtures, never a proposed VM target.
        for p in self.root.rglob('*'):
            if p.is_dir() and not p.is_symlink():p.chmod(0o700)
        self.temp.cleanup();os.umask(self.old_umask)

class MetadataTests(Fixture):
    def test_empty_ssh_classification(self):
        p=self.root/'.ssh';p.mkdir(mode=0o700);r=mo.inventory(p)
        self.assertTrue(r['empty_directory']);self.assertEqual(r['credential_free'],'NOT_ESTABLISHED_BY_METADATA')
    def test_public_auth_material_still_not_empty(self):
        p=self.root/'.ssh';p.mkdir();(p/'authorized_keys').write_bytes(b'')
        r=mo.inventory(p);self.assertFalse(r['empty_directory']);self.assertEqual(r['key_or_auth_name_indicators'],1)
    def test_key_candidate_not_read(self):
        p=self.root/'.ssh';p.mkdir();(p/'id_ed25519').write_bytes(b'SYNTHETIC NEVER READ')
        real=os.open
        def guarded(path,flags,*a,**kw):
            self.assertTrue(flags&os.O_DIRECTORY);self.assertTrue(flags&os.O_NOFOLLOW)
            return real(path,flags,*a,**kw)
        with patch.object(mo.os,'open',side_effect=guarded),patch('builtins.open',side_effect=AssertionError('content read')):r=mo.inventory(p)
        self.assertEqual(r['regular_files'],1);self.assertEqual(r['key_or_auth_name_indicators'],1)
    def test_38_files_23_flags_count_all(self):
        p=self.root/'cloud';p.mkdir();q=p/'instances/fixture';q.mkdir(parents=True)
        for i in range(38):
            f=q/('opaque-'+str(i));f.write_bytes(b'SYNTHETIC');f.chmod(0o644 if i<23 else 0o600)
        (p/'instance').symlink_to('instances/fixture')
        r=mo.inventory(p);self.assertTrue(r['complete']);self.assertEqual(r['regular_files'],38)
        self.assertEqual(r['potential_exposure_rule_matches'],23);self.assertEqual(r['symlinks'],1);self.assertEqual(r['canonical_instance_alias_syntax'],1)
    def test_partial_scan_not_empty(self):
        p=self.root/'tree';p.mkdir();(p/'one').write_bytes(b'');(p/'two').write_bytes(b'')
        r=mo.inventory(p,max_entries=1);self.assertFalse(r['complete']);self.assertFalse(r['empty_directory'])
    def test_unreadable_metadata_not_empty(self):
        with patch.object(mo.os,'scandir',side_effect=PermissionError()):r=mo.inventory(self.root)
        self.assertFalse(r['complete']);self.assertFalse(r['empty_directory'])
    def test_symlink_not_followed(self):
        (self.root/'link').symlink_to('/never-follow')
        r=mo.inventory(self.root);self.assertEqual(r['symlinks'],1)
        r=mo.inventory(self.root/'link');self.assertFalse(r['complete'])
    def test_fifo_never_opened(self):
        os.mkfifo(self.root/'fifo');r=mo.inventory(self.root);self.assertEqual(r['special_files'],1)
    def test_hardlink_reported(self):
        f=self.root/'file';f.write_bytes(b'SYNTHETIC');os.link(f,self.root/'link')
        self.assertEqual(mo.inventory(self.root)['hardlinked_regular_files'],2)
    def test_installed_r1_empty_ssh_still_refuses(self):
        for path in ('root/.ssh','home/jarvis/.ssh'):(self.root/path).mkdir(parents=True)
        r=inspect_environment_paths(root=self.root,root_uid=os.getuid(),preparation_uid=os.getuid())
        self.assertIn('CREDENTIAL_OR_HOST_PATH_PRESENT',r['findings'])
        self.assertIn('PREPARATION_HOME_CREDENTIAL_INDICATOR',r['findings'])
    def test_installed_r1_cloud_zero_is_incomplete(self):
        p=self.root/'var/lib/cloud/instances/fixture';p.mkdir(parents=True)
        (p/'opaque').write_bytes(b'SYNTHETIC');(p/'opaque').chmod(0o644)
        r=inspect_environment_paths(root=self.root,root_uid=os.getuid(),preparation_uid=os.getuid())
        self.assertEqual(r['cloud_cache_files'],0);self.assertIn('EXPOSED_CLOUD_INIT_PAYLOAD',r['findings'])
        with self.assertRaises(RuntimeError):require_paths(r,{})

class TransferTests(Fixture):
    def setUp(self):
        super().setUp();self.source=self.root/'export';self.source.mkdir(mode=0o700)
        self.opt=self.root/'protected';self.opt.mkdir(mode=0o700);self.dest=self.opt/'g6k-offline'
        self.required={'distribution:fixture':'1'}
        content=b'SYNTHETIC PUBLIC PACKAGE';self.file=self.source/'fixture.whl';self.file.write_bytes(content);self.file.chmod(0o600)
        self.rows={'distribution:fixture':dict(version='1',filename='fixture.whl',sha256=H(content),provenance_record='synthetic fixture only')}
        self.manifest=self.source/'ARTIFACTS.json';self.manifest.write_text(json.dumps(self.rows));self.manifest.chmod(0o600);self.expected=H(self.manifest.read_bytes())
    def inspect(self):return at.inspect_export(self.source,self.expected,self.required,owners={os.getuid()})
    def move(self):return at.promote(self.source,self.dest,self.expected,self.required,source_uid=os.getuid(),owner_uid=os.getuid(),owner_gid=os.getgid())
    def test_same_filesystem_same_inodes_no_duplicate(self):
        before=self.file.stat();r=self.move();after=(self.dest/'fixture.whl').stat()
        self.assertEqual((before.st_dev,before.st_ino,before.st_blocks),(after.st_dev,after.st_ino,after.st_blocks))
        self.assertFalse(self.source.exists());self.assertTrue(r['same_inodes']);self.assertFalse(r['file_data_copy'])
    def test_bad_manifest_no_move(self):
        self.expected='0'*64
        with self.assertRaises(ValueError):self.move()
        self.assertTrue(self.source.exists());self.assertFalse(self.dest.exists())
    def test_bad_artifact_no_move(self):
        self.file.write_bytes(b'TAMPER')
        with self.assertRaises(ValueError):self.move()
        self.assertTrue(self.source.exists())
    def test_extra_file_refused(self):
        (self.source/'extra').write_bytes(b'SYNTHETIC')
        with self.assertRaises(ValueError):self.move()
    def test_symlink_refused(self):
        self.file.unlink();self.file.symlink_to('/never-read')
        with self.assertRaises(OSError):self.move()
    def test_hardlink_refused(self):
        os.link(self.file,self.root/'external-link')
        with self.assertRaises(ValueError):self.move()
    def test_fifo_refused_without_blocking(self):
        self.file.unlink();os.mkfifo(self.file)
        with self.assertRaises(ValueError):self.move()
    def test_existing_destination_not_overwritten(self):
        self.dest.mkdir();(self.dest/'retained').write_bytes(b'fixture')
        with self.assertRaises(FileExistsError):self.move()
        self.assertEqual((self.dest/'retained').read_bytes(),b'fixture')
    def test_existing_stage_refused(self):
        (self.opt/'.g6k-offline-stage-r1').mkdir()
        with self.assertRaises(FileExistsError):self.move()
    def test_low_space_no_move(self):
        with patch.object(at,'free_bytes',return_value=at.MIN_FREE-1),self.assertRaises(ValueError):self.move()
        self.assertTrue(self.source.exists())
    def test_exdev_never_copies(self):
        with patch.object(at,'rename_no_replace',side_effect=OSError(errno.EXDEV,'fixture')),self.assertRaises(OSError):self.move()
        self.assertTrue(self.source.exists());self.assertFalse(self.dest.exists())
    def test_crash_after_first_rename_preserves_stage(self):
        with patch.object(at.os,'fchown',side_effect=OSError('interruption')),self.assertRaises(OSError):self.move()
        self.assertTrue((self.opt/'.g6k-offline-stage-r1/fixture.whl').is_file());self.assertFalse(self.dest.exists())
        with self.assertRaises(OSError):self.move()
    def test_late_free_space_failure_preserves_stage(self):
        with patch.object(at,'free_bytes',side_effect=[at.MIN_FREE+100*1024**2,at.MIN_FREE-1]),self.assertRaises(ValueError):self.move()
        self.assertTrue((self.opt/'.g6k-offline-stage-r1').is_dir());self.assertFalse(self.dest.exists())
    def test_open_writer_survives_rename_and_chmod_negative_control(self):
        fd=os.open(self.file,os.O_WRONLY)
        try:
            self.move();os.pwrite(fd,b'BAD',0)
            with self.assertRaises(ValueError):at.inspect_export(self.dest,self.expected,self.required,owners={os.getuid()})
        finally:os.close(fd)
    def test_noreplace_kernel_guarantee(self):
        src=at.open_directory(self.root);dst=at.open_directory(self.opt)
        self.dest.mkdir()
        try:
            with self.assertRaises(FileExistsError):at.rename_no_replace(src,'export',dst,'g6k-offline')
        finally:os.close(src);os.close(dst)
    def test_duplicate_manifest_key_refused(self):
        self.manifest.write_text('{"x":1,"x":2}');self.expected=H(self.manifest.read_bytes())
        with self.assertRaises(ValueError):self.inspect()
    def test_unsafe_artifact_mode_refused(self):
        self.file.chmod(0o6755)
        with self.assertRaises(ValueError):self.inspect()

class EmptyDirectoryOperationTests(Fixture):
    def test_empty_only_removal_fixture(self):
        p=self.root/'empty-auth-directory';p.mkdir(mode=0o700)
        self.assertTrue(mo.inventory(p)['empty_directory']);os.rmdir(p);self.assertFalse(p.exists())
    def test_nonempty_directory_cannot_be_removed(self):
        p=self.root/'auth-directory';p.mkdir();(p/'synthetic-key').write_bytes(b'fixture')
        with self.assertRaises(OSError):os.rmdir(p)
        self.assertTrue((p/'synthetic-key').is_file())
    def test_symlink_cannot_be_removed_by_rmdir(self):
        p=self.root/'link';p.symlink_to(self.root)
        with self.assertRaises(OSError):os.rmdir(p)
        self.assertTrue(p.is_symlink())
    def test_entry_added_after_metadata_refuses(self):
        p=self.root/'auth-directory';p.mkdir();self.assertTrue(mo.inventory(p)['empty_directory'])
        (p/'new-entry').write_bytes(b'fixture')
        with self.assertRaises(OSError):os.rmdir(p)

class MountSimulationTests(unittest.TestCase):
    def lines(self):
        rows=['1 0 8:1 / / rw shared:1 - ext4 /dev/sda1 rw','2 1 8:2 / /boot rw shared:2 - ext4 /dev/sda2 rw']
        rows += [f'{i+3} 1 0:{i+3} / /run/credentials/unit{i} ro,nosuid,nodev,noexec shared:{i+3} - tmpfs tmpfs ro' for i in range(5)]
        rows += [f'{i+8} 1 0:{i+8} / /run/fixture{i} rw shared:{i+8} - tmpfs tmpfs rw' for i in range(21)]
        return rows
    def check(self,rows):validate_environment(hostname='jarvis-security',interfaces=['lo'],mountinfo='\n'.join(rows),credential_paths=[],boot_source='/dev/sda2')
    def private(self,rows):return [' '.join(x for x in r.split() if not x.startswith(('shared:','master:','propagate_from:'))) for r in rows]
    def test_all_28_shared_refuse(self):
        with self.assertRaisesRegex(RuntimeError,'SHARED_MOUNT_PROPAGATION'):self.check(self.lines())
    def test_root_only_private_leaves_nested_refusals(self):
        rows=self.lines();rows[0]=self.private(rows[:1])[0]
        with self.assertRaises(RuntimeError):self.check(rows)
    def test_recursive_private_projection_passes_topology_only(self):self.check(self.private(self.lines()))
    def test_private_projection_does_not_hide_iso(self):
        rows=self.private(self.lines())+['99 1 11:0 / /mnt/offline ro - iso9660 /dev/sr0 ro']
        with self.assertRaises(RuntimeError):self.check(rows)
    def test_private_projection_does_not_fix_host_share(self):
        rows=self.private(self.lines())+['99 1 0:100 / /mnt/host rw - virtiofs shared rw']
        with self.assertRaises(RuntimeError):self.check(rows)
    def test_private_projection_does_not_fix_unsafe_credential_mount(self):
        rows=self.private(self.lines());rows[2]=rows[2].replace('ro,nosuid,nodev,noexec','rw')
        with self.assertRaises(RuntimeError):self.check(rows)
    def test_reboot_shared_projection_refuses_again(self):
        self.check(self.private(self.lines()))
        with self.assertRaises(RuntimeError):self.check(self.lines())

if __name__=='__main__':unittest.main(verbosity=2)

"""Offline synthetic tests. No block devices, installer services, or VM access."""
import ast
import asyncio
import copy
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import types
import unittest

import guard_proposal as candidate

PACKET = Path(__file__).resolve().parents[1]
OLD = PACKET.parent / 'p7-b2-gate6k-vm164-disk-matching-r4'
spec = importlib.util.spec_from_file_location('retained_r4', OLD / 'tools/disk_guard_r4.py')
r4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r4)


def fixture():
    disk = dict(name='/dev/sda', type='disk', serial=candidate.HARDWARE_SERIAL,
                size=candidate.DISK_BYTES, model='QEMU HARDDISK', ro=False, rm=False,
                mountpoints=[None], pkname=None, dev='8:0', fstype=None, pttype=None)
    optical = dict(name='/dev/sr0', type='rom', ro=True, rm=True,
                   mountpoints=['/cdrom'], pkname=None, dev='11:0')
    return dict(euid=0, uuid=candidate.VM_UUID, interfaces=['lo'],
                blockdevices=[disk, optical],
                udev={'/dev/sda': dict(DEVNAME='/dev/sda', DEVTYPE='disk',
                                      **candidate.IDENTITIES),
                      '/dev/sr0': dict(DEVNAME='/dev/sr0', DEVTYPE='disk',
                                      ID_SERIAL='optical', ID_PATH='optical-path')},
                sysfs={'/dev/sda': dict(dev='8:0', kind='disk', parent=None, partition=None,
                                       holders=[], slaves=[]),
                       '/dev/sr0': dict(dev='11:0', kind='rom', parent=None, partition=None,
                                       holders=[], slaves=[])},
                mounts=[], swaps=[], wipefs={'signatures': []})


def partitioned():
    snap = fixture()
    disk = snap['blockdevices'][0]
    disk['pttype'] = 'gpt'
    disk['children'] = []
    for number in (1, 2):
        path = f'/dev/sda{number}'
        dev = f'8:{number}'
        disk['children'].append(dict(name=path, type='part', pkname='/dev/sda',
                                     dev=dev, ro=False, rm=False, mountpoints=[None]))
        snap['udev'][path] = dict(snap['udev']['/dev/sda'], DEVNAME=path,
                                  DEVTYPE='partition')
        snap['sysfs'][path] = dict(dev=dev, kind='part', parent='/dev/sda', partition=number,
                                   holders=[], slaves=[])
    snap['wipefs'] = {'signatures': [{'type': 'gpt'}, {'type': 'PMBR'}]}
    return snap


class GuardProposal(unittest.TestCase):
    def test_virgin_single_disk_passes(self):
        self.assertEqual(candidate.validate(fixture())['disk'], '/dev/sda')

    def test_reproduce_r4_reported_error(self):
        with self.assertRaisesRegex(RuntimeError, '^UDEV_IDENTITY_NOT_UNIQUE_ID_SERIAL$'):
            r4.validate(partitioned())

    def test_partition_inheritance_passes_identity_but_refuses_admission(self):
        snap = partitioned()
        self.assertEqual(candidate.validate_identity(snap)['disk'], '/dev/sda')
        with self.assertRaisesRegex(RuntimeError, 'TARGET_HAS_PARTITIONS'):
            candidate.validate(snap)

    def test_partitions_without_signatures_still_refuse(self):
        snap = partitioned(); snap['wipefs'] = {'signatures': []}
        with self.assertRaisesRegex(RuntimeError, 'TARGET_HAS_PARTITIONS'):
            candidate.validate(snap)

    def test_second_physical_disk_distinct_or_cloned_or_readonly_refuses(self):
        for cloned in (False, True):
            for ro in (False, True):
                with self.subTest(cloned=cloned, ro=ro):
                    snap = fixture()
                    other = copy.deepcopy(snap['blockdevices'][0])
                    other.update(name='/dev/sdb', dev='8:16', ro=ro)
                    snap['blockdevices'].append(other)
                    snap['sysfs']['/dev/sdb'] = dict(snap['sysfs']['/dev/sda'], dev='8:16')
                    props = dict(snap['udev']['/dev/sda'], DEVNAME='/dev/sdb')
                    if not cloned:
                        props.update({k: 'distinct' for k in candidate.IDENTITIES})
                    snap['udev']['/dev/sdb'] = props
                    with self.assertRaisesRegex(RuntimeError, 'EXACTLY_ONE_EXPECTED_DISK'):
                        candidate.validate(snap)

    def test_each_identity_conflict_on_optical_media_refuses(self):
        for key, value in candidate.IDENTITIES.items():
            with self.subTest(key=key):
                snap = fixture(); snap['udev']['/dev/sr0'][key] = value
                with self.assertRaisesRegex(RuntimeError, 'IDENTITY_NOT_UNIQUE_' + key):
                    candidate.validate(snap)

    def test_wrong_or_missing_expected_identity_refuses(self):
        for key in candidate.IDENTITIES:
            for value in (None, 'wrong'):
                with self.subTest(key=key, value=value):
                    snap = fixture(); snap['udev']['/dev/sda'][key] = value
                    with self.assertRaises(RuntimeError): candidate.validate(snap)

    def test_wrong_uuid_root_or_nic_refuses(self):
        for key, value in [('uuid', 'wrong'), ('uuid', None), ('euid', 1000),
                           ('euid', False), ('interfaces', ['lo', 'ens18'])]:
            with self.subTest(key=key, value=value):
                snap = fixture(); snap[key] = value
                with self.assertRaises(RuntimeError): candidate.validate(snap)

    def test_wrong_target_properties_refuse(self):
        for key, value in [('serial', 'wrong'), ('size', 1), ('size', True),
                           ('model', 'OTHER'), ('ro', True), ('rm', True),
                           ('mountpoints', ['/target']), ('mountpoints', None),
                           ('pkname', '/dev/dm-0')]:
            with self.subTest(key=key, value=value):
                snap = fixture(); snap['blockdevices'][0][key] = value
                with self.assertRaises(RuntimeError): candidate.validate(snap)

    def test_gpt_mbr_ext4_lvm_raid_signatures_refuse(self):
        for kind in ('gpt', 'PMBR', 'dos', 'ext4', 'LVM2_member', 'linux_raid_member'):
            with self.subTest(kind=kind):
                snap = fixture(); snap['wipefs'] = {'signatures': [{'type': kind}]}
                with self.assertRaisesRegex(RuntimeError, 'SIGNATURES'): candidate.validate(snap)

    def test_unknown_signature_report_refuses(self):
        for report in (None, [], {}, {'signatures': None}, {'signatures': ''}):
            with self.subTest(report=report):
                snap = fixture(); snap['wipefs'] = report
                with self.assertRaisesRegex(RuntimeError, 'SIGNATURES'): candidate.validate(snap)

    def test_fstype_or_pttype_even_without_wipefs_results_refuses(self):
        for key, value in [('fstype', 'ext4'), ('pttype', 'gpt')]:
            snap = fixture(); snap['blockdevices'][0][key] = value
            with self.assertRaisesRegex(RuntimeError, 'INITIALIZED'): candidate.validate(snap)

    def test_holders_slaves_mounts_or_swap_refuse(self):
        for key in ('holders', 'slaves'):
            snap = fixture(); snap['sysfs']['/dev/sda'][key] = ['dm-0']
            with self.assertRaisesRegex(RuntimeError, 'UNSAFE_STORAGE_GRAPH'): candidate.validate(snap)
        for key in ('mounts', 'swaps'):
            snap = fixture(); snap[key] = ['8:0']
            with self.assertRaisesRegex(RuntimeError, 'TARGET_IN_USE'): candidate.validate(snap)
            snap = fixture(); del snap[key]
            with self.assertRaises(RuntimeError): candidate.validate(snap)

    def test_dm_raid_lvm_crypt_and_unknown_types_refuse(self):
        for kind in ('lvm', 'raid1', 'crypt', 'mpath', 'zram', 'unknown'):
            snap = fixture(); snap['blockdevices'][1]['type'] = kind
            with self.assertRaisesRegex(RuntimeError, 'UNSAFE_DEVICE_TYPE'): candidate.validate(snap)

    def test_loop_requires_readonly_trusted_backing_and_no_target_alias(self):
        snap = fixture(); snap['blockdevices'][1].update(type='loop', rm=False)
        snap['sysfs']['/dev/sr0']['kind'] = 'loop'
        with self.assertRaisesRegex(RuntimeError, 'LOOP_BACKING'): candidate.validate(snap)
        snap['sysfs']['/dev/sr0']['backing_origin'] = 'verified-install-media-or-ram'
        self.assertEqual(candidate.validate(snap)['disk'], '/dev/sda')
        snap['blockdevices'][1]['ro'] = False
        with self.assertRaisesRegex(RuntimeError, 'WRITABLE_MEDIA'): candidate.validate(snap)

    def test_mislabeled_partition_or_missing_parent_is_not_ignored(self):
        mutations = [('DEVTYPE', 'disk'), ('parent', '/dev/sdb'), ('partition', None)]
        for key, value in mutations:
            snap = partitioned()
            target = snap['udev'] if key == 'DEVTYPE' else snap['sysfs']
            target['/dev/sda1'][key] = value
            with self.assertRaises(RuntimeError): candidate.validate_identity(snap)
        snap = partitioned(); snap['blockdevices'].append(snap['blockdevices'][0]['children'].pop())
        with self.assertRaisesRegex(RuntimeError, 'PARTITION_PARENT'): candidate.validate_identity(snap)

    def test_duplicate_path_devnum_or_omitted_sysfs_device_refuses(self):
        snap = fixture(); snap['blockdevices'].append(copy.deepcopy(snap['blockdevices'][0]))
        with self.assertRaisesRegex(RuntimeError, 'DUPLICATE_PATH'): candidate.validate(snap)
        snap = fixture(); snap['sysfs']['/dev/hidden'] = {}
        with self.assertRaisesRegex(RuntimeError, 'INCOMPLETE_SYSFS'): candidate.validate(snap)
        snap = fixture(); snap['sysfs']['/dev/sr0']['dev'] = '8:0'
        snap['blockdevices'][1]['dev'] = '8:0'
        with self.assertRaisesRegex(RuntimeError, 'DUPLICATE_DEVNUM'): candidate.validate(snap)

    def test_missing_udev_or_disagreement_refuses(self):
        snap = fixture(); del snap['udev']['/dev/sr0']
        with self.assertRaisesRegex(RuntimeError, 'INCOMPLETE_UDEV'): candidate.validate(snap)
        snap = fixture(); snap['udev']['/dev/sda']['DEVNAME'] = '/dev/sdb'
        with self.assertRaisesRegex(RuntimeError, 'UDEV_DISAGREEMENT'): candidate.validate(snap)

    def test_malformed_topology_refuses(self):
        for key, value in [('blockdevices', {}), ('blockdevices', [None]), ('sysfs', None)]:
            snap = fixture(); snap[key] = value
            with self.assertRaises(RuntimeError): candidate.validate(snap)
        snap = fixture(); snap['blockdevices'][0]['children'] = [snap['blockdevices'][0]]
        with self.assertRaisesRegex(RuntimeError, 'DUPLICATE_PATH'): candidate.validate(snap)

    def test_disk_cannot_hide_as_optical_or_partition(self):
        snap = fixture(); snap['sysfs']['/dev/sr0']['kind'] = 'disk'
        with self.assertRaisesRegex(RuntimeError, 'KERNEL_KIND'): candidate.validate(snap)
        snap = fixture(); snap['blockdevices'][0]['type'] = 'part'
        with self.assertRaisesRegex(RuntimeError, 'KERNEL_KIND'): candidate.validate(snap)

    def test_bad_flags_and_missing_kernel_safety_metadata_refuse(self):
        for field in ('ro', 'rm'):
            for value in ('0', None, 2):
                snap = fixture(); snap['blockdevices'][0][field] = value
                with self.assertRaisesRegex(RuntimeError, 'UNKNOWN_BLOCK_FLAG'): candidate.validate(snap)
        for field in ('kind', 'parent', 'partition', 'holders', 'slaves', 'dev'):
            snap = fixture(); del snap['sysfs']['/dev/sda'][field]
            with self.assertRaises(RuntimeError): candidate.validate(snap)

    def test_partitioned_second_disk_is_counted(self):
        snap = fixture(); other = partitioned()
        other_disk = other['blockdevices'][0]
        other_disk['name'] = '/dev/sdb'; other_disk['dev'] = '8:16'
        for row in other_disk['children']:
            oldpath = row['name']; newpath = oldpath.replace('sda', 'sdb')
            row.update(name=newpath, pkname='/dev/sdb', dev='8:' + str(16 + int(newpath[-1])))
            snap['udev'][newpath] = dict(other['udev'][oldpath], DEVNAME=newpath)
            snap['sysfs'][newpath] = dict(other['sysfs'][oldpath], parent='/dev/sdb', dev=row['dev'])
        snap['blockdevices'].append(other_disk)
        snap['udev']['/dev/sdb'] = dict(other['udev']['/dev/sda'], DEVNAME='/dev/sdb')
        snap['sysfs']['/dev/sdb'] = dict(other['sysfs']['/dev/sda'], dev='8:16')
        with self.assertRaisesRegex(RuntimeError, 'EXACTLY_ONE_EXPECTED_DISK'):
            candidate.validate(snap)

    def test_partial_identity_conflict_on_second_disk_refuses(self):
        for key, expected in candidate.IDENTITIES.items():
            snap = fixture()
            snap['blockdevices'].append(dict(snap['blockdevices'][0], name='/dev/sdb', dev='8:16'))
            props = {k: 'other' for k in candidate.IDENTITIES}; props[key] = expected
            snap['udev']['/dev/sdb'] = dict(DEVNAME='/dev/sdb', DEVTYPE='disk', **props)
            snap['sysfs']['/dev/sdb'] = dict(snap['sysfs']['/dev/sda'], dev='8:16')
            with self.assertRaisesRegex(RuntimeError, 'EXACTLY_ONE_EXPECTED_DISK'):
                candidate.validate(snap)

    def test_omitted_udev_device_and_wrong_devnum_refuse(self):
        snap = fixture(); snap['udev']['/dev/hidden'] = {}
        with self.assertRaisesRegex(RuntimeError, 'INCOMPLETE_UDEV'): candidate.validate(snap)
        snap = fixture(); snap['sysfs']['/dev/sda']['dev'] = '8:16'
        with self.assertRaisesRegex(RuntimeError, 'DEVNUM_DISAGREEMENT'): candidate.validate(snap)


def pinned_start(early_fails=False, stamp_exists=False):
    """Execute only the exact startup method AST with inert collaborators."""
    source = PACKET / 'evidence/pinned-source/server.py'
    tree = ast.parse(source.read_text())
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == 'start')
    events = []
    class Base:
        async def start(self): events.append('controllers-started')
    class CommandError(Exception):
        def __init__(self, **kw): super().__init__(str(kw))
    async def sleep(_): await asyncio.sleep(0)
    class Stamp(io.StringIO):
        def close(self): events.append('success-stamp-written'); super().close()
    namespace = dict(Base=Base, asyncio=types.SimpleNamespace(sleep=sleep),
                     os=types.SimpleNamespace(path=types.SimpleNamespace(exists=lambda _: stamp_exists)),
                     subprocess=subprocess, AutoinstallUserSuppliedCmdError=CommandError,
                     ApplicationState=types.SimpleNamespace(**{s: s for s in
                        ('CLOUD_INIT_WAIT', 'EARLY_COMMANDS', 'WAITING')}),
                     open=lambda *a: Stamp())
    cls = ast.ClassDef(name='PinnedStart', bases=[ast.Name(id='Base', ctx=ast.Load())],
                       keywords=[], body=[copy.deepcopy(node)], decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])),
                 '<pinned 7403 startup with inert collaborators>', 'exec'), namespace)
    instance = namespace['PinnedStart']()
    async def early():
        events.append('early-run')
        if early_fails: raise subprocess.CalledProcessError(1, ['synthetic-guard'])
    instance.controllers = types.SimpleNamespace(load_all=lambda: None,
                         Early=types.SimpleNamespace(cmds=[['guard']], run=early))
    async def noop(): pass
    instance.start_api_server = noop
    instance.wait_for_cloudinit = noop
    instance.set_installer_password = lambda: None
    instance.select_autoinstall = lambda: '/autoinstall.yaml'
    instance.autoinstall_config = {'early-commands': [['guard']]}
    instance.load_autoinstall_config = lambda **kw: events.append('load-' + str(kw['only_early']))
    instance.update_state = lambda state: events.append(state)
    instance.state_path = lambda _: '/inert/early-commands'
    instance.load_serialized_state = lambda: None
    instance.apply_autoinstall_config = noop
    instance.interactive = False
    instance.opts = types.SimpleNamespace(dry_run=True)  # Avoid casper marker path; startup branch unchanged.
    return instance, events, CommandError


class PinnedControlFlow(unittest.IsolatedAsyncioTestCase):
    async def test_first_early_failure_never_starts_controllers_or_writes_stamp(self):
        instance, events, error = pinned_start(early_fails=True)
        with self.assertRaises(error): await instance.start()
        self.assertIn('early-run', events)
        self.assertNotIn('controllers-started', events)
        self.assertNotIn('success-stamp-written', events)
        self.assertNotIn('load-False', events)

    async def test_first_success_precedes_controller_start(self):
        instance, events, _ = pinned_start()
        await instance.start()
        self.assertLess(events.index('early-run'), events.index('success-stamp-written'))
        self.assertLess(events.index('success-stamp-written'), events.index('controllers-started'))

    async def test_existing_stamp_skips_early_on_restart(self):
        instance, events, _ = pinned_start(early_fails=True, stamp_exists=True)
        await instance.start()
        self.assertNotIn('early-run', events)
        self.assertIn('controllers-started', events)

    async def test_independent_writer_not_cancelled_by_guard_error(self):
        # This proves a logical boundary using only a temporary REGULAR FILE.
        # It is not a reproduction of actual partitioning or a VM164 attribution.
        with tempfile.TemporaryDirectory(prefix='g6k-synthetic-') as tmp:
            target = Path(tmp) / 'synthetic-evidence.txt'
            release = asyncio.Event()
            async def independent_writer():
                await release.wait()
                target.write_text('independent simulated storage mutation\n')
            task = asyncio.create_task(independent_writer())
            instance, events, error = pinned_start(early_fails=True)
            with self.assertRaises(error): await instance.start()
            release.set(); await task
            self.assertTrue(target.is_file())
            self.assertNotIn('controllers-started', events)


if __name__ == '__main__':
    unittest.main(verbosity=2)

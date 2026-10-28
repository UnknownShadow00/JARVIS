"""Synthetic controls plus actual pinned Subiquity method bodies; no devices accessed."""
import ast
import collections.abc
import copy
import fnmatch
import hashlib
import json
import logging
from pathlib import Path
import sys
import types
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import TASK
from disk_guard_r4 import (DISK_BYTES, DISK_PATH, HARDWARE_SERIAL, MATCH, UDEV_PATH,
                           UDEV_SERIAL, UDEV_SHORT, VM_UUID, parse_udev, validate)
from trusted_console_r4 import validate_config


def fixture():
    return {'euid': 0, 'uuid': VM_UUID, 'interfaces': ['lo'],
            'blockdevices': [
                {'name': DISK_PATH, 'type': 'disk', 'serial': HARDWARE_SERIAL, 'size': DISK_BYTES,
                 'model': 'QEMU HARDDISK', 'ro': False, 'rm': False, 'mountpoints': [None]},
                {'name': '/dev/sr0', 'type': 'rom', 'serial': 'optical', 'size': 3_042_836_480,
                 'model': 'QEMU DVD-ROM', 'ro': True, 'rm': True, 'mountpoints': ['/cdrom']},
                {'name': '/dev/loop0', 'type': 'loop', 'size': 1024, 'ro': True, 'rm': False,
                 'mountpoints': ['/rofs']}],
            'udev': {DISK_PATH: {'DEVNAME': DISK_PATH, 'DEVTYPE': 'disk', 'ID_SERIAL': UDEV_SERIAL,
                                'ID_SERIAL_SHORT': UDEV_SHORT, 'ID_PATH': UDEV_PATH},
                     '/dev/sr0': {'DEVNAME': '/dev/sr0', 'DEVTYPE': 'disk', 'ID_SERIAL': 'optical'},
                     '/dev/loop0': {'DEVNAME': '/dev/loop0', 'DEVTYPE': 'disk'}},
            'wipefs': {'signatures': []}}


class AnnotationStripper(ast.NodeTransformer):
    def visit_arg(self, node):
        node.annotation = None
        return node

    def visit_FunctionDef(self, node):
        node = self.generic_visit(node)
        node.returns = None
        node.decorator_list = []
        return node


METHOD_NAMES = ('_make_matchers', '_sorted_matches', '_filtered_matches', '_matching_disks',
                'disks_for_match', 'disk_for_match')


def pinned_matcher(udev):
    source = (TASK / 'evidence/pinned-source/filesystem-model.py').read_text()
    methods = {n.name: n for n in ast.walk(ast.parse(source))
               if isinstance(n, ast.FunctionDef) and n.name in METHOD_NAMES}
    if set(methods) != set(METHOD_NAMES):
        raise RuntimeError('PINNED_MATCHER_SOURCE_MISSING')
    namespace = {'fnmatch': fnmatch, 'Sequence': collections.abc.Sequence,
                 'log': logging.getLogger('subiquity-pinned-matcher-controls')}
    cls = type('PinnedSubiquity7403Matcher', (), {})
    for name, node in methods.items():
        module = ast.Module(body=[AnnotationStripper().visit(copy.deepcopy(node))], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), '<pinned Subiquity 7403 ' + name + '>', 'exec'), namespace)
        setattr(cls, name, namespace[name])
    instance = cls()
    instance._probe_data = {'blockdev': udev}
    return instance


def disk(path):
    return types.SimpleNamespace(path=path, size=DISK_BYTES, sort_key=path, _has_in_use_partition=False)


class DiskProtection(unittest.TestCase):
    def test_verified_observation_passes_all_independent_guards(self):
        self.assertEqual(validate(fixture())['subiquity_match'], MATCH)

    def test_wrong_uuid_or_unprivileged_context_refuses(self):
        for key, value in (('uuid', '1d279e9b-12cb-4a02-8815-a682cb9457a9'), ('euid', 1000)):
            snapshot = fixture(); snapshot[key] = value
            with self.assertRaises(RuntimeError): validate(snapshot)

    def test_wrong_hardware_serial_size_or_model_refuses(self):
        for key, value in (('serial', 'drive-scsi0'), ('size', DISK_BYTES - 512), ('model', 'OTHER DISK')):
            snapshot = fixture(); snapshot['blockdevices'][0][key] = value
            with self.assertRaises(RuntimeError): validate(snapshot)

    def test_additional_disk_refuses_even_if_it_does_not_match(self):
        for read_only in (False, True):
            snapshot = fixture()
            snapshot['blockdevices'].append({'name': '/dev/sdb', 'type': 'disk', 'ro': read_only})
            snapshot['udev']['/dev/sdb'] = {'DEVNAME': '/dev/sdb'}
            with self.assertRaisesRegex(RuntimeError, 'ONE_EXPECTED_DISK'): validate(snapshot)

    def test_existing_or_uninspectable_signatures_refuse(self):
        for report in ({'signatures': [{'type': 'gpt'}]}, {'signatures': [{'type': 'ext4'}]},
                       {}, {'signatures': None}, {'signatures': ''}, []):
            snapshot = fixture(); snapshot['wipefs'] = report
            with self.assertRaisesRegex(RuntimeError, 'SIGNATURES'): validate(snapshot)

    def test_target_partitions_mounts_read_only_or_removable_refuse(self):
        for key, value in (('children', [{'name': '/dev/sda1', 'type': 'part', 'ro': False}]),
                           ('mountpoints', ['/target']), ('mountpoints', None), ('ro', True), ('rm', True)):
            snapshot = fixture(); snapshot['blockdevices'][0][key] = value
            if key == 'children': snapshot['udev']['/dev/sda1'] = {'DEVNAME': '/dev/sda1'}
            with self.assertRaises(RuntimeError): validate(snapshot)

    def test_nic_or_another_writable_non_disk_device_refuses(self):
        snapshot = fixture(); snapshot['interfaces'].append('ens18')
        with self.assertRaises(RuntimeError): validate(snapshot)
        for kind in ('loop', 'lvm', 'crypt', 'raid1', 'rom'):
            snapshot = fixture(); snapshot['blockdevices'][2].update(type=kind, ro=False)
            with self.assertRaisesRegex(RuntimeError, 'EXTRA_INSTALLATION_DEVICE'): validate(snapshot)

    def test_missing_or_changed_udev_property_refuses(self):
        for key in ('ID_SERIAL', 'ID_SERIAL_SHORT', 'ID_PATH'):
            for remove in (False, True):
                snapshot = fixture()
                if remove: del snapshot['udev'][DISK_PATH][key]
                else: snapshot['udev'][DISK_PATH][key] = 'different'
                with self.assertRaises(RuntimeError): validate(snapshot)

    def test_ambiguous_udev_identity_refuses_even_on_read_only_media(self):
        for key, value in (('ID_SERIAL', UDEV_SERIAL), ('ID_SERIAL_SHORT', UDEV_SHORT), ('ID_PATH', UDEV_PATH)):
            snapshot = fixture(); snapshot['udev']['/dev/sr0'][key] = value
            with self.assertRaisesRegex(RuntimeError, 'IDENTITY_NOT_UNIQUE'): validate(snapshot)

    def test_incomplete_conflicting_or_duplicate_inventory_refuses(self):
        snapshot = fixture(); del snapshot['udev']['/dev/sr0']
        with self.assertRaisesRegex(RuntimeError, 'INCOMPLETE_UDEV'): validate(snapshot)
        snapshot = fixture(); snapshot['udev'][DISK_PATH]['DEVNAME'] = '/dev/sdb'
        with self.assertRaisesRegex(RuntimeError, 'DEVNAME'): validate(snapshot)
        snapshot = fixture(); snapshot['blockdevices'].append(copy.deepcopy(snapshot['blockdevices'][0]))
        with self.assertRaisesRegex(RuntimeError, 'DUPLICATE_BLOCK_PATH'): validate(snapshot)

    def test_udevadm_parser_refuses_duplicate_or_malformed_lines(self):
        self.assertEqual(parse_udev('DEVNAME=/dev/sda\nID_SERIAL=a=b\n')['ID_SERIAL'], 'a=b')
        for value in ('ID_SERIAL=a\nID_SERIAL=b\n', 'not-a-property\n', '=value\n'):
            with self.assertRaises(RuntimeError): parse_udev(value)


class ActualPinnedMatcher(unittest.TestCase):
    def setUp(self):
        self.snapshot = fixture()
        self.matcher = pinned_matcher(self.snapshot['udev'])
        self.target = disk(DISK_PATH)

    def test_reproduces_r3_zero_candidates_using_observed_identity(self):
        self.assertEqual(self.matcher.disks_for_match([self.target], {'serial': HARDWARE_SERIAL}), [])

    def test_corrected_conjunction_selects_only_the_intended_disk(self):
        self.assertEqual(self.matcher.disks_for_match([self.target], MATCH), [self.target])

    def test_each_match_dimension_is_required(self):
        for key in MATCH:
            spec = dict(MATCH); spec[key] = 'different'
            self.assertEqual(self.matcher.disks_for_match([self.target], spec), [])

    def test_no_fallback_or_glob_and_ambiguous_identity_still_refuses(self):
        self.assertIs(type(MATCH), dict)
        self.assertTrue(all(not any(c in v for c in '*?[]') for v in MATCH.values()))
        other = disk('/dev/sdb')
        self.matcher._probe_data['blockdev']['/dev/sdb'] = dict(self.snapshot['udev'][DISK_PATH], DEVNAME='/dev/sdb')
        self.assertEqual(self.matcher.disks_for_match([other, self.target], MATCH), [self.target])
        # The exact path must not be used to excuse an ambiguous identity: early guard refuses.
        snapshot = fixture(); snapshot['udev']['/dev/sr0']['ID_SERIAL'] = UDEV_SERIAL
        with self.assertRaisesRegex(RuntimeError, 'IDENTITY_NOT_UNIQUE'): validate(snapshot)


class FutureConsoleBinding(unittest.TestCase):
    def config(self):
        return {'smbios1': 'uuid=' + VM_UUID, 'cores': 4, 'sockets': 1, 'memory': 6000,
                'balloon': 0, 'onboot': 0, 'bios': 'seabios', 'scsihw': 'virtio-scsi-single',
                'machine': 'q35', 'agent': '0',
                'scsi0': 'downloads:164/vm-164-disk-0.raw,serial=' + HARDWARE_SERIAL + ',size=64G'}

    def test_recorded_vm164_binding_passes(self):
        self.assertEqual(validate_config(self.config()), 'downloads:164/vm-164-disk-0.raw')

    def test_foreign_vm_or_disk_or_serial_refuses(self):
        for key, value in (('smbios1', 'uuid=wrong'),
                           ('scsi0', 'downloads:163/vm-163-disk-0.raw,serial=' + HARDWARE_SERIAL + ',size=64G'),
                           ('scsi0', 'downloads:164/vm-164-disk-0.raw,serial=wrong,size=64G')):
            cfg = self.config(); cfg[key] = value
            with self.assertRaises(RuntimeError): validate_config(cfg)

    def test_external_inputs_and_extra_disks_refuse(self):
        for key in ('net0', 'scsi1', 'hostpci0', 'virtiofs0', 'args', 'hookscript', 'cicustom'):
            cfg = self.config(); cfg[key] = 'synthetic'
            with self.assertRaises(RuntimeError): validate_config(cfg)


if __name__ == '__main__':
    unittest.main(verbosity=2)

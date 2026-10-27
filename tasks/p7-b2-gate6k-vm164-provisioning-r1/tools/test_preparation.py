"""Unprivileged guards and command-construction tests. No hypervisor/guest calls."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_clean_source import fields, header, transform
from create_stopped_vm164 import UUID, SERIAL, check_storage, create_command, validate_hardware
from memory_probe import REQUIRED, assess


def sample(available=REQUIRED + 1):
    return {'boot_id': 'synthetic-one-boot', 'memory_bytes': {'MemAvailable': available},
            'vmstat': {'pswpin': 1, 'pswpout': 1, 'oom_kill': 0},
            'memory_psi': {'some': {'total': 10}, 'full': {'total': 0}}}


def hardware():
    return {'cores': 4, 'sockets': 1, 'memory': 6000, 'balloon': 0, 'onboot': 0,
            'smbios1': 'uuid=' + UUID, 'ide2': 'none,media=cdrom', 'bios': 'seabios',
            'scsihw': 'virtio-scsi-single', 'serial0': 'socket', 'agent': '0', 'cpu': 'host',
            'machine': 'q35', 'boot': 'order=scsi0', 'hotplug': '0', 'protection': 1,
            'scsi0': 'downloads:164/vm-164-disk-0.raw,serial=' + SERIAL + ',size=64G'}


class Preparation(unittest.TestCase):
    def check_early(self, *, identifier=UUID, interfaces=('lo',), serial=SERIAL, signatures=None):
        auto = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1/autoinstall-r3.yaml')
        code = yaml.safe_load(auto.read_text())['autoinstall']['early-commands'][0][-1]
        devices = {'blockdevices': [{'name': 'sda', 'type': 'disk', 'serial': serial, 'size': 64 * 1024 ** 3}]}
        signature_result = {'signatures': []} if signatures is None else signatures
        with patch('os.geteuid', return_value=0), patch.object(Path, 'read_text', return_value=identifier), \
             patch.object(Path, 'iterdir', return_value=[Path('/sys/class/net') / n for n in interfaces]), \
             patch('subprocess.check_output', side_effect=[json.dumps(devices).encode(), json.dumps(signature_result).encode()]):
            exec(compile(code, '<synthetic installer early guard>', 'exec'), {})

    def test_installer_binds_uuid_serial_and_no_nic(self):
        self.check_early()
        for overrides in ({'identifier': 'different'}, {'interfaces': ('lo', 'ens18')}, {'serial': 'old-disk'}):
            with self.assertRaises(AssertionError):
                self.check_early(**overrides)

    def test_installer_refuses_existing_or_uninspectable_disk_signatures(self):
        for signatures in ({'signatures': [{'type': 'gpt'}]}, {}, {'signatures': None}):
            with self.assertRaises(AssertionError):
                self.check_early(signatures=signatures)

    def test_reported_memory_refuses_start_even_with_no_swap_activity(self):
        result = assess([sample(12_640_000_000), sample(12_640_000_000)])
        self.assertEqual(result['screen'], 'NO_GO_START')

    def test_quiet_screen_never_authorizes_start(self):
        self.assertEqual(assess([sample(), sample()])['screen'], 'SCREEN_ONLY_PASSED_NOT_START_AUTHORIZATION')

    def test_swap_oom_pressure_or_boot_change_refuses(self):
        for field in ('pswpin', 'pswpout', 'oom_kill'):
            last = sample(); last['vmstat'][field] += 1
            self.assertEqual(assess([sample(), last])['screen'], 'NO_GO_START')
        last = sample(); last['memory_psi']['full']['total'] += 1
        self.assertEqual(assess([sample(), last])['screen'], 'NO_GO_START')
        last = sample(); last['boot_id'] = 'different'
        self.assertEqual(assess([sample(), last])['screen'], 'NO_GO_START')

    def test_only_empty_exact_ssh_directory_is_omitted(self):
        original = [b'/ D 1 755 0 0\n', b'root D 1 700 0 0\n', b'root/.ssh D 1 700 0 0\n']
        changed, old = transform(original)
        self.assertEqual(len(changed), len(original))
        self.assertNotIn(old, changed)
        self.assertIn(b'etc/cloud/cloud-init.disabled R 1787788900 644 0 0 0 0 0\n', changed)
        for unexpected in (b'root/.ssh/id_ed25519 R 1 600 0 0 1 0 0\n', b'root/.ssh x user.test=value\n'):
            with self.assertRaises(ValueError):
                transform(original + [unexpected])
        with self.assertRaises(ValueError):
            transform(original[:-1] + [b'root/.ssh S 1 777 0 0 outside\n'])

    def test_pseudo_parser_accepts_separator_but_never_exec_definitions(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'pseudo'
            p.write_bytes(b'/ D 1 755 0 0\n#\n# START OF DATA - DO NOT MODIFY\n#\n')
            self.assertEqual(header(p)[0], [b'/ D 1 755 0 0\n'])
            p.write_bytes(b'/ D 1 755 0 0\na F 1 755 0 0 arbitrary-command\n#\n# START OF DATA - DO NOT MODIFY\n#\n')
            with self.assertRaisesRegex(ValueError, 'COMMAND_OR_UNKNOWN_TYPE'):
                header(p)

    def test_storage_backend_and_capacity_refusals(self):
        good = {'type': 'dir', 'shared': 0, 'content': 'images'}
        status = {'active': 1, 'enabled': 1, 'avail': 872_660_000_000}
        self.assertGreater(check_storage(good, status, status['avail'], 10**12), 0)
        for bad in ({**good, 'shared': 1}, {**good, 'type': 'lvmthin'}, {**good, 'disable': 1}):
            with self.assertRaises(RuntimeError):
                check_storage(bad, status, status['avail'], 10**12)
        with self.assertRaises(RuntimeError):
            check_storage(good, status, 64 * 1024**3, 10**12)

    def test_create_argv_cannot_start_or_target_existing_vm(self):
        argv = create_command()
        self.assertEqual(argv[:3], ['qm', 'create', '164'])
        self.assertEqual(argv[argv.index('--start') + 1], '0')
        self.assertEqual(argv[argv.index('--onboot') + 1], '0')
        self.assertFalse(any(a.startswith('--net') for a in argv))
        self.assertIn('downloads:64,format=raw,serial=' + SERIAL + ',cache=none', argv)

    def test_hardware_is_bound_and_rejects_extra_inputs(self):
        self.assertEqual(validate_hardware(hardware()), 'downloads:164/vm-164-disk-0.raw')
        for key in ('net0', 'hookscript', 'args', 'hostpci0', 'usb0', 'virtiofs0', 'unused0', 'scsi1', 'cicustom'):
            config = hardware(); config[key] = 'synthetic'
            with self.assertRaises(RuntimeError):
                validate_hardware(config)
        config = hardware(); config['smbios1'] = 'uuid=wrong'
        with self.assertRaises(RuntimeError):
            validate_hardware(config)
        config = hardware(); config['memory'] = 4096
        with self.assertRaises(RuntimeError):
            validate_hardware(config)
        config = hardware(); config['scsi0'] = config['scsi0'].replace('164/vm-164-', '163/vm-163-')
        with self.assertRaisesRegex(RuntimeError, 'VOLUME_MUST_BELONG'):
            validate_hardware(config)


if __name__ == '__main__':
    unittest.main(verbosity=2)

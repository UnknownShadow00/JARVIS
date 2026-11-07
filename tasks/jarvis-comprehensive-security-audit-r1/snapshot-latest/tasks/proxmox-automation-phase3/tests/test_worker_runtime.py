import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from g6k_serial import provision, runtime
from g6k_serial.policy import WORKER_KEYS
from g6k_serial.protocol import Deadline, Refusal, TOKEN_ID, binding, decode, encode
from g6k_serial.securefs import SOURCE_FILES, read_checked, verify_release
from g6k_serial.worker import Inspector, bounded_file
from support import Lab, grant
import test_transport as tls_support


class WorkerRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)

    def test_worker_binding_cannot_change_principal_scope_or_action(self):
        advertisement = self.lab.worker.advertisement()
        request = json.loads(self.lab.request())
        base = binding(request, advertisement, self.lab.grant, self.lab.grant['caller_uid'], '3' * 32)
        changes = [('caller_uid', 0), ('caller_uid', self.lab.grant['caller_uid'] + 1),
                   ('grant_id', 'f' * 32), ('session', 'f' * 32), ('vmid', 163),
                   ('vm_uuid', 'wrong'), ('serial', 'serial1'), ('worker_uid', 0),
                   ('boot_id', '11111111-2222-3333-4444-555555555556')]
        for key, value in changes:
            with self.subTest(key=key), self.assertRaises(Refusal):
                self.lab.worker.process({'v': 1, 'type': 'inspect', 'binding': {**base, key: value}, 'action': 'kernel'})
        for extra in ({'action': 'sudo'}, {'type': 'report'}, {'v': True}, {'argv': ['sh']}):
            with self.subTest(extra=extra), self.assertRaises(Refusal):
                self.lab.worker.process({'v': 1, 'type': 'inspect', 'binding': base, 'action': 'kernel', **extra})
        self.assertEqual(self.lab.inspector.calls, [])

    def test_worker_nonce_and_request_id_cannot_be_reused_after_result(self):
        advertisement = self.lab.worker.advertisement()
        base = binding(json.loads(self.lab.request()), advertisement, self.lab.grant,
                       self.lab.grant['caller_uid'], '3' * 32)
        data = {'v': 1, 'type': 'inspect', 'binding': base, 'action': 'kernel'}
        self.lab.worker.process(data)
        with self.assertRaises(Refusal):
            self.lab.worker.process(data)
        self.assertEqual(self.lab.inspector.calls, ['kernel'])

    def test_inspector_requires_nonroot_matching_uid_loopback_and_no_kernel_console(self):
        settings = self.lab.worker_settings
        inspector = Inspector(settings)
        values = {'/etc/machine-id': (settings['machine_id'] + '\n').encode(),
                  '/proc/sys/kernel/random/boot_id': b'11111111-2222-3333-4444-555555555555\n',
                  '/proc/cmdline': b'root=UUID=public ro quiet'}
        with patch('g6k_serial.worker.bounded_file', side_effect=lambda p, n: values[p]), \
             patch('g6k_serial.worker.os.geteuid', return_value=settings['worker_uid']), \
             patch('g6k_serial.worker.os.listdir', return_value=['lo']):
            self.assertEqual(inspector.metadata()['machine_id'], settings['machine_id'])
            for cmdline in (b'root=public console=ttyS0,115200', b'earlycon=uart', b'kgdboc=ttyS0'):
                values['/proc/cmdline'] = cmdline
                with self.subTest(cmdline=cmdline), self.assertRaises(Refusal):
                    inspector.metadata()
            values['/proc/cmdline'] = b'root=public ro'
            with patch('g6k_serial.worker.os.listdir', return_value=['lo', 'eth0']), self.assertRaises(Refusal):
                inspector.metadata()
            with patch('g6k_serial.worker.os.geteuid', return_value=0), self.assertRaises(Refusal):
                inspector.metadata()

    def test_mount_summary_never_exports_paths_environment_or_options(self):
        raw = (b'1 0 8:1 / / rw shared:1 - ext4 /dev/sda2 rw\n'
               b'2 1 0:1 / /mnt/SYNTHETIC_SECRET rw - virtiofs host:SYNTHETIC_SECRET rw,password=SYNTHETIC_SECRET\n')
        with patch('g6k_serial.worker.bounded_file', return_value=raw):
            report = Inspector(self.lab.worker_settings).inspect('isolation-summary', {})
        self.assertEqual(report['external_fs_count'], 1)
        self.assertEqual(report['shared_mount_count'], 1)
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(report))

    def test_bounded_inspection_does_not_mistake_short_read_for_eof(self):
        class ShortReads:
            def __init__(self, pieces): self.pieces = iter(pieces)
            def read(self, n): return next(self.pieces)
            def __enter__(self): return self
            def __exit__(self, *args): pass
        with patch('g6k_serial.worker.open', return_value=ShortReads([b'a', b'b', b''])):
            self.assertEqual(bounded_file('/synthetic', 3), b'ab')
        with patch('g6k_serial.worker.open', return_value=ShortReads([b'ab', b'cd'])):
            with self.assertRaises(Refusal):
                bounded_file('/synthetic', 3)

    def test_pinned_source_manifest_detects_code_drift_and_untrusted_owners(self):
        source = Path(__file__).resolve().parents[1] / 'src'
        destination = self.lab.root / 'release'
        (destination / 'g6k_serial').mkdir(parents=True)
        destination.chmod(0o700)
        (destination / 'g6k_serial').chmod(0o700)
        manifest = []
        for name in SOURCE_FILES:
            content = (source / name).read_bytes()
            (destination / name).write_bytes(content)
            (destination / name).chmod(0o600)
            manifest.append(hashlib.sha256(content).hexdigest() + '  ' + name)
        raw = ('\n'.join(manifest) + '\n').encode()
        (destination / 'SOURCE-SHA256SUMS').write_bytes(raw)
        (destination / 'SOURCE-SHA256SUMS').chmod(0o600)
        expected = hashlib.sha256(raw).hexdigest()
        verify_release(destination, expected, owners=frozenset((os.getuid(),)), anchor=self.lab.root)
        (destination / 'g6k_serial/worker.py').write_text('# changed\n')
        with self.assertRaises(Refusal):
            verify_release(destination, expected, owners=frozenset((os.getuid(),)), anchor=self.lab.root)
        with self.assertRaises(Refusal):
            verify_release(destination, expected, owners=frozenset((0,)), anchor=self.lab.root)

    def test_settings_fail_closed_before_any_transport_for_disabled_templates(self):
        raw = encode({**self.lab.grant, 'enabled': False})
        with patch('g6k_serial.runtime.read_checked', return_value=raw), self.assertRaises(Refusal):
            runtime.settings()
        with patch('g6k_serial.runtime.read_checked', return_value=encode(self.lab.grant)), self.assertRaises(Refusal):
            runtime.settings()  # Nexus fixture is not the configured broker UID.

    def test_operator_actions_refuse_nonroot_before_reading_files_or_prompts(self):
        with patch('g6k_serial.runtime.os.geteuid', return_value=1000), patch('g6k_serial.runtime.read_checked') as read:
            for function in (runtime.initialize_state, runtime.revoke):
                with self.assertRaises(Refusal):
                    function()
            read.assert_not_called()
        with patch('g6k_serial.provision.os.geteuid', return_value=1000), patch('g6k_serial.provision.read_checked') as read:
            with self.assertRaises(Refusal):
                provision.issue(prompt=lambda _: self.fail('must not prompt'))
            read.assert_not_called()


class ProvisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tls_support.TransportTests.setUpClass()

    @classmethod
    def tearDownClass(cls):
        tls_support.TransportTests.tearDownClass()

    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)

    def test_private_issuance_captures_only_new_token_and_never_prints_secrets(self):
        ca = tls_support.TransportTests.cert.read_bytes()
        settings = {**self.lab.grant, 'enabled': False, 'ca_sha256': hashlib.sha256(ca).hexdigest()}
        directory = self.lab.root / 'capture'
        directory.mkdir(mode=0o700)
        class FakeWire:
            def send(self, request, deadline):
                self.request = request
            def close(self): pass
        wire = FakeWire()
        response = {'data': {'full-tokenid': TOKEN_ID, 'value': tls_support.SYNTHETIC_TOKEN,
                             'info': {'privsep': 1, 'expire': settings['expires_at']}}}
        prompts = iter(['SYNTHETIC_PRIVATE_SESSION', 'SYNTHETIC_PRIVATE_CSRF'])
        real_read = read_checked
        real_open = os.open
        def checked(path, *args, **kwargs):
            return encode(settings) if str(path).endswith('host.json') else ca
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        output = io.StringIO()
        try:
            with patch('g6k_serial.provision.os.geteuid', return_value=0), \
                 patch('g6k_serial.provision.os.isatty', return_value=True), \
                 patch('g6k_serial.provision.os.fchown'), \
                 patch('g6k_serial.provision.read_checked', side_effect=checked), \
                 patch('g6k_serial.provision.open_checked', return_value=os.dup(fd)), \
                 patch('g6k_serial.provision.verify_release'), patch('g6k_serial.provision.safe_account'), \
                 patch('g6k_serial.hardening.undumpable'), \
                 patch('g6k_serial.provision.http_head', return_value=(200, {})), \
                 patch('g6k_serial.provision.http_body', return_value=json.dumps(response).encode()), \
                 contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                result = provision.issue(prompt=lambda _: next(prompts), dial=lambda d: wire)
            self.assertEqual(result, 'CREDENTIAL_STORED_NO_VALUE_OUTPUT')
            self.assertEqual(output.getvalue(), '')
            self.assertIn(b'/access/users/g6k-bridge164@pve/token/serial ', wire.request)
            self.assertNotIn(b'root@pam', wire.request)
            stored = json.loads((directory / 'token.json').read_text())
            self.assertEqual(stored, {'id': TOKEN_ID, 'secret': tls_support.SYNTHETIC_TOKEN})
            self.assertEqual((directory / 'token.json').stat().st_mode & 0o777, 0o600)
        finally:
            os.close(fd)


if __name__ == '__main__':
    unittest.main()

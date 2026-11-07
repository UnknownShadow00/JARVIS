import copy
import json
import os
import threading
import time
import unittest
from unittest.mock import patch

from g6k_serial.policy import config, vm_state
from g6k_serial.protocol import ACTIONS, Deadline, Lines, Refusal, decode, encode, public_request
from support import Lab, grant, snapshot


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)

    def test_catalog_roundtrips_require_authenticated_receipts(self):
        for index, action in enumerate(ACTIONS):
            rid = f'{index + 1:032x}'
            answer = self.lab.call(action, rid)
            self.assertEqual(answer['result'], 'REPORTED')
            self.assertIs(answer['guest_report_untrusted'], True)
            with self.assertRaises(Refusal):
                self.lab.host_ledger.available()
            self.lab.receipt(rid)
            self.lab.host_ledger.available()
        self.assertEqual(self.lab.inspector.calls, list(ACTIONS))
        self.assertEqual(self.lab.pve.snapshots, 6)

    def test_request_injection_and_privileged_catalog_denied_before_transport(self):
        for action in ('sh', 'bash', 'sudo', 'root', 'guest-exec', 'qualify', 'qualify_all.py', 'reboot',
                       'passwd', 'file-read', 'file-write', 'kernel;id', '$(id)', '`id`', '../identity',
                       'kernel\nreboot', 'kernel\u001b', None, 1, [], {}):
            with self.subTest(action=action):
                answer = self.lab.broker.handle(self.lab.request(action=action), self.lab.grant['caller_uid'])
                self.assertEqual(answer['result'], 'REJECTED')
        self.assertEqual(self.lab.pve.openings, 0)
        self.assertEqual(self.lab.pve.snapshots, 0)

    def test_target_identity_and_serial_exactness(self):
        for key, values in {'vmid': [162, 163, '164', 164.0, True, 0],
                            'vm_uuid': ['wrong', None, '../164'],
                            'serial': ['serial1', '/dev/ttyS0', 'serial0;id', None]}.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    result = self.lab.broker.handle(self.lab.request(**{key: value}), self.lab.grant['caller_uid'])
                    self.assertEqual(result['result'], 'REJECTED')
        self.assertEqual(self.lab.pve.snapshots, 0)

    def test_no_client_supplied_authority_or_arguments(self):
        for key in ('caller_uid', 'principal', 'grant_id', 'signature', 'approval', 'argv', 'env',
                    'cwd', 'stdin', 'url', 'node', 'ticket', 'token', 'command', 'path', 'uid'):
            with self.subTest(key=key):
                result = self.lab.broker.handle(self.lab.request(**{key: 'SYNTHETIC_SECRET'}), self.lab.grant['caller_uid'])
                self.assertEqual(result['result'], 'REJECTED')
                self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))
        self.assertEqual(self.lab.pve.snapshots, 0)

    def test_peer_uid_is_not_coerced(self):
        for uid in (0, 123456, str(os.getuid()), float(os.getuid()), True, None):
            with self.subTest(uid=uid):
                self.assertEqual(self.lab.broker.handle(self.lab.request(), uid)['result'], 'REJECTED')
        self.assertEqual(self.lab.pve.snapshots, 0)

    def test_malformed_wire_and_structural_abuse(self):
        for raw in (b'', b' ' * 1025, b'[]', b'null', b'{', b'{"v":1,"v":1}',
                    b'{"x":NaN}', b'{"x":Infinity}', b'{}\n{}', b'{} trailing', b'\xff',
                    b'\x03', b'\x1b', b'\x00', b'\r', b'\n', b'[' * 1000):
            with self.subTest(raw=raw[:20]):
                self.assertEqual(self.lab.broker.handle(raw, self.lab.grant['caller_uid'])['result'], 'REJECTED')
        data = json.loads(self.lab.request())
        for key in list(data):
            broken = dict(data)
            del broken[key]
            with self.subTest(missing=key), self.assertRaises(Refusal):
                public_request(encode(broken)[:-1])
        for v in (True, '1', 1.0, 0, 2):
            with self.subTest(version=v), self.assertRaises(Refusal):
                public_request(encode({**data, 'v': v})[:-1])

    def test_disabled_expired_unbound_overbroad_grants(self):
        original = grant()
        for key, value in (('enabled', False), ('enabled', 1), ('expires_at', 0), ('expires_at', True),
                           ('expires_at', int(time.time()) - 1), ('machine_id', None), ('release', None),
                           ('caller_uid', 0), ('broker_uid', original['caller_uid']),
                           ('actions', ['kernel', 'shell']), ('actions', ['kernel', 'kernel']),
                           ('actions', []), ('ca_sha256', None), ('operator_reference', 'space or ; shell')):
            with self.subTest(key=key, value=value), self.assertRaises(Refusal):
                config({**original, key: value})

    def test_actual_pve_state_drift_refuses(self):
        original = snapshot()
        for key, value in (('smbios1', 'uuid=wrong'), ('serial0', '/dev/ttyS0'), ('agent', '1'),
                           ('boot', 'order=ide2'), ('net0', 'virtio'), ('hostpci0', '00:00'),
                           ('virtiofs0', 'share'), ('usb0', 'host=1'), ('unused0', 'old'),
                           ('sata0', 'other'), ('scsi1', 'other'), ('serial1', 'socket'),
                           ('ide2', 'media.iso,media=cdrom'), ('args', '-net user'),
                           ('hookscript', 'hook'), ('cicustom', 'seed'), ('cipassword', 'secret'),
                           ('lock', 'backup'), ('digest', None)):
            broken = copy.deepcopy(original)
            broken['config'][key] = value
            with self.subTest(key=key), self.assertRaises(Refusal):
                vm_state(broken)
        for pending in ([{'key': 'net0', 'pending': 'virtio'}], [{'key': 'serial0', 'delete': 1}], None):
            with self.subTest(pending=pending), self.assertRaises(Refusal):
                vm_state({**original, 'pending': pending})
        for perms in ({'/': {'VM.Console': 0}}, {'/vms/164': {'VM.Audit': 0}},
                      {**original['permissions'], '/vms/162': {'VM.Audit': 0}},
                      {**original['permissions'], '/vms/163': {'VM.Console': 0}},
                      {'/vms/164': {'VM.Audit': 0, 'VM.Console': 0, 'VM.GuestAgent.Unrestricted': 0}}):
            with self.subTest(perms=perms), self.assertRaises(Refusal):
                vm_state({**original, 'permissions': perms})
        self.assertEqual(vm_state(original)[0], 'e' * 40)  # Zero flags are grants.

    def test_replay_new_id_bypass_and_restart_refused(self):
        self.assertEqual(self.lab.call()['result'], 'REPORTED')
        self.assertEqual(self.lab.call(request_id='2' * 32)['result'], 'REJECTED')
        self.lab.receipt()
        openings = self.lab.pve.openings
        self.assertEqual(self.lab.call()['result'], 'REJECTED')
        self.assertEqual(self.lab.pve.openings, openings)
        self.assertEqual(len(self.lab.inspector.calls), 1)

    def test_lost_guest_response_latches_unknown_and_preserves_state(self):
        def modify(channel):
            original = channel.receive
            def receive(deadline):
                if channel.reply is not None:
                    raise TimeoutError('SYNTHETIC_SECRET_FROM_GUEST')
                return original(deadline)
            channel.receive = receive
        self.lab.pve.modify_channel = modify
        answer = self.lab.call()
        self.assertEqual(answer['result'], 'UNKNOWN')
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(answer))
        self.assertEqual(self.lab.call(request_id='2' * 32)['result'], 'REJECTED')
        self.assertEqual(len(self.lab.inspector.calls), 1)
        rows = self.lab.host_ledger.conn.execute('SELECT state FROM requests').fetchall()
        self.assertEqual(rows, [('UNKNOWN',)])
        self.lab.host_ledger.verify_audit()

    def test_malicious_worker_report_is_data_and_rejected(self):
        attacks = [lambda reply: {**reply, 'command': 'touch /outside'},
                   lambda reply: {**reply, 'binding': {**reply['binding'], 'caller_uid': 0}},
                   lambda reply: {**reply, 'binding': {**reply['binding'], 'serial': 'serial1'}},
                   lambda reply: {**reply, 'binding': {**reply['binding'], 'request_id': 'f' * 32}},
                   lambda reply: {**reply, 'report': {'kernel_release': '$(touch /outside)'}},
                   lambda reply: {**reply, 'report': {'kernel_release': '\u001b]52;secret'}},
                   lambda reply: {**reply, 'report': {'kernel_release': 'a' * 129}}]
        for attack in attacks:
            lab = Lab()
            try:
                def modify(channel):
                    channel.corrupt = lambda value: attack(value) if value.get('type') == 'report' else value
                lab.pve.modify_channel = modify
                self.assertEqual(lab.call()['result'], 'UNKNOWN')
                self.assertEqual(len(lab.inspector.calls), 1)
                with self.assertRaises(Refusal):
                    lab.host_ledger.available()
            finally:
                lab.close()

    def test_compromised_worker_can_lie_but_cannot_expand_schema(self):
        def modify(channel):
            channel.corrupt = lambda value: {**value, 'report': {'kernel_release': 'fabricated-1.0'}} if value.get('type') == 'report' else value
        self.lab.pve.modify_channel = modify
        answer = self.lab.call()
        self.assertEqual(answer['result'], 'REPORTED')
        self.assertIs(answer['guest_report_untrusted'], True)
        self.assertEqual(answer['report']['kernel_release'], 'fabricated-1.0')
        # This deliberately demonstrates the limitation: guest observations are
        # not cryptographic proof of a healthy/uncompromised guest.

    def test_wrong_ready_identity_prevents_any_action(self):
        for key, value in (('vm_uuid', 'wrong'), ('worker_uid', 0), ('machine_id', 'f' * 32),
                           ('release', 'f' * 64), ('serial', 'serial1')):
            lab = Lab()
            try:
                def modify(channel):
                    channel.advertisement['metadata'][key] = value
                lab.pve.modify_channel = modify
                self.assertEqual(lab.call()['result'], 'REJECTED')
                self.assertEqual(lab.inspector.calls, [])
                self.assertEqual(lab.pve.channel.outgoing, [])
            finally:
                lab.close()

    def test_state_drift_after_possible_execution_is_unknown(self):
        def modify(number):
            if number == 2:
                self.lab.pve.state['config']['digest'] = 'f' * 40
        self.lab.pve.after_snapshot = modify
        self.assertEqual(self.lab.call()['result'], 'UNKNOWN')
        self.assertEqual(self.lab.inspector.calls, ['kernel'])

    def test_concurrent_request_refused_before_transport(self):
        held = threading.Event()
        release = threading.Event()
        def operation():
            with self.lab.host_ledger.operation():
                held.set()
                release.wait(2)
        thread = threading.Thread(target=operation)
        thread.start()
        self.assertTrue(held.wait(1))
        try:
            self.assertEqual(self.lab.call()['result'], 'REJECTED')
            self.assertEqual(self.lab.pve.snapshots, 0)
        finally:
            release.set()
            thread.join()

    def test_worker_internal_failure_and_grant_revocation_halt(self):
        self.lab.inspector.failure = PermissionError('SYNTHETIC_PRIVATE_DATA')
        self.assertEqual(self.lab.call()['result'], 'UNKNOWN')
        self.assertEqual(self.lab.worker_ledger.conn.execute('SELECT state FROM requests').fetchall(), [('UNKNOWN',)])
        with self.assertRaises(Refusal):
            self.lab.worker.advertisement()

    def test_reservation_failure_prevents_send_and_audit_failure_preserves_halt(self):
        with patch.object(self.lab.host_ledger, 'reserve', side_effect=OSError('SYNTHETIC_DISK_FULL')):
            result = self.lab.call()
        self.assertEqual(result['result'], 'REJECTED')
        self.assertEqual(self.lab.inspector.calls, [])
        self.assertEqual(self.lab.pve.channel.outgoing, [])
        with patch.object(self.lab.host_ledger, 'finish', side_effect=OSError('SYNTHETIC_FSYNC_FAILED')):
            result = self.lab.call(request_id='2' * 32)
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(self.lab.inspector.calls, ['kernel'])
        self.assertEqual(self.lab.host_ledger.conn.execute('SELECT state FROM requests').fetchall(), [('RESERVED',)])
        self.assertEqual(self.lab.call(request_id='3' * 32)['result'], 'REJECTED')

    def test_source_or_activation_revocation_before_and_after_send(self):
        with patch.object(self.lab.broker, 'revalidate', side_effect=Refusal('REVOKED')):
            self.assertEqual(self.lab.call()['result'], 'REJECTED')
        self.assertEqual(self.lab.pve.snapshots, 0)
        calls = []
        def revalidate():
            calls.append(None)
            if len(calls) == 3:
                raise Refusal('REVOKED')
        self.lab.broker.revalidate = revalidate
        self.assertEqual(self.lab.call()['result'], 'UNKNOWN')
        self.assertEqual(self.lab.inspector.calls, ['kernel'])
        self.assertEqual(self.lab.call(request_id='2' * 32)['result'], 'REJECTED')

    def test_deadline_and_fragment_size_limits(self):
        with self.assertRaises(Refusal):
            Deadline(-1).remaining()
        chunks = iter([b'{"v":', b'1}\n'])
        self.assertEqual(Lines(lambda d: next(chunks)).line(Deadline()), {'v': 1})
        for chunks in ([b'a' * 16385], [b'a' * 16385 + b'\n'], [b'\n'], [b'{"v":1}\r\n']):
            source = iter(chunks)
            with self.subTest(size=len(chunks[0])), self.assertRaises((Refusal, StopIteration)):
                Lines(lambda d: next(source)).line(Deadline())


if __name__ == '__main__':
    unittest.main()

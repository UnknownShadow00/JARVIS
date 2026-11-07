"""Synthetic security-boundary checks; never import or invoke the observer."""
import copy
from dataclasses import replace
import json
import unittest

from policy_model import (ACTIONS, DISK, SERIAL, VM_UUID, Refusal, StandingGrant,
                          decode_request, plan)
from observe import ALLOWED, granted_names


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.request = {'v': 1, 'vmid': 164, 'action': 'identity', 'request_id': 'a' * 32}
        self.grant = StandingGrant('SYNTHETIC-NOT-AUTHORITY', 200, 'b' * 32, 'c' * 64, ACTIONS, 1000)
        self.config = {'smbios1': 'uuid=' + VM_UUID, 'serial0': 'socket',
                       'boot': 'order=scsi0', 'agent': '0', 'ide2': 'none,media=cdrom',
                       'scsi0': DISK + ',cache=none,serial=' + SERIAL + ',size=64G'}
        self.status = {'status': 'running', 'qmpstatus': 'running'}
        self.guest = {'vm_uuid': VM_UUID, 'machine_id': 'b' * 32, 'bundle_sha256': 'c' * 64,
                      'boot_id': '11111111-2222-3333-4444-555555555555', 'interfaces': ['lo'],
                      'euid': 997, 'role_separation_verified': True}

    def invoke(self, request=None, **changes):
        kwargs = dict(peer_uid=1000, now=100, config=self.config, status=self.status,
                      guest=self.guest, consumed_ids=frozenset())
        kwargs.update(changes)
        return plan(json.dumps(request or self.request).encode(), self.grant, **kwargs)

    def test_three_named_actions_are_plans_never_execution(self):
        for action in ACTIONS:
            result = self.invoke({**self.request, 'action': action})
            self.assertEqual(result['result'], 'VALID_PLAN_ONLY')
            self.assertIs(result['transport_enabled'], False)
            self.assertIs(result['executed'], False)

    def test_target_and_type_attacks(self):
        for target in (162, 163, 100, 0, -1, '164', 164.0, True, None, '../164'):
            with self.subTest(target=target), self.assertRaises(Refusal):
                self.invoke({**self.request, 'vmid': target})

    def test_shell_and_privileged_actions(self):
        for action in ('sh', 'bash', 'sudo', 'root', 'guest-exec', 'qualify', 'qualify_all.py',
                       'identity;id', 'identity\nuname', '$(id)', '`id`', '../identity',
                       'identity\u001b', 'reboot', 'passwd', 'file-read', 'file-write',
                       'snapshot', 'network-enable', 'Identity', '', None, ['identity']):
            with self.subTest(action=action), self.assertRaises(Refusal):
                self.invoke({**self.request, 'action': action})

    def test_extra_parameters_never_reach_executor(self):
        for key in ('argv', 'command', 'stdin', 'path', 'cwd', 'env', 'url', 'node', 'serial',
                    'uid', 'sudo', 'approval', 'signature', 'token', 'ticket'):
            with self.subTest(key=key), self.assertRaises(Refusal):
                self.invoke({**self.request, key: 'attacker-controlled'})

    def test_frames_and_duplicate_keys(self):
        cases = (b'', b' ' * 1025, b'[]', b'null', b'{', b'{"v":1,"v":1}',
                 b'{"x":NaN}', b'{"x":Infinity}', b'\xff', b'\x03', b'\x1b',
                 b'\x00', b'\r', b'\n', b'{}\n{}', b'{} trailing', b'"' + b'[' * 10 + b'"')
        for raw in cases:
            with self.subTest(raw=raw[:30]), self.assertRaises(Refusal):
                decode_request(raw)

    def test_missing_keys_versions_and_request_ids(self):
        for key in self.request:
            request = dict(self.request)
            del request[key]
            with self.subTest(missing=key), self.assertRaises(Refusal):
                decode_request(json.dumps(request).encode())
        for value in (True, '1', 1.0, 0, 2):
            with self.subTest(version=value), self.assertRaises(Refusal):
                self.invoke({**self.request, 'v': value})
        for value in ('', '../a', 'A' * 32, 'a' * 33, 123, None):
            with self.subTest(request_id=value), self.assertRaises(Refusal):
                self.invoke({**self.request, 'request_id': value})

    def test_missing_expired_or_overbroad_grant(self):
        for grant in (None, {}, replace(self.grant, expires_at=100),
                      replace(self.grant, operator_reference=''),
                      replace(self.grant, machine_id=None), replace(self.grant, bundle_sha256=None),
                      replace(self.grant, actions=frozenset(('identity', 'shell'))),
                      replace(self.grant, actions=frozenset(('kernel',))),
                      replace(self.grant, caller_uid=0)):
            with self.subTest(grant=grant), self.assertRaises(Refusal):
                plan(json.dumps(self.request).encode(), grant, peer_uid=1000, now=100,
                     config=self.config, status=self.status, guest=self.guest, consumed_ids=frozenset())

    def test_peer_expiry_and_replay(self):
        for kwargs in ({'peer_uid': 0}, {'peer_uid': 1001}, {'peer_uid': True},
                       {'now': 200}, {'now': True}, {'consumed_ids': frozenset(('a' * 32,))}):
            with self.subTest(kwargs=kwargs), self.assertRaises(Refusal):
                self.invoke(**kwargs)

    def test_config_identity_media_devices_and_isolation(self):
        changes = {'smbios1': 'uuid=other', 'serial0': '/dev/ttyS0', 'serial1': 'socket',
                   'boot': 'order=ide2', 'agent': '1', 'net0': 'virtio',
                   'net1': 'virtio', 'hostpci0': '00:00', 'usb0': 'host=1',
                   'virtiofs0': 'share', 'unused0': 'old', 'scsi1': 'another',
                   'sata0': 'media', 'ide2': 'downloads:iso/live.iso,media=cdrom',
                   'hookscript': 'script', 'args': '-net user', 'sshkeys': 'key',
                   'cicustom': 'seed', 'cipassword': 'no', 'lock': 'backup',
                   'pending': {'net0': 'virtio'}}
        for key, value in changes.items():
            config = copy.deepcopy(self.config)
            config[key] = value
            with self.subTest(key=key), self.assertRaises(Refusal):
                self.invoke(config=config)
        for disk in (DISK, DISK + ',serial=wrong,size=64G,cache=none',
                     DISK + ',serial=' + SERIAL + ',size=64G,cache=none,ro=0',
                     'downloads:163/vm-163-disk-0.raw,cache=none,serial=' + SERIAL + ',size=64G'):
            with self.subTest(disk=disk), self.assertRaises(Refusal):
                self.invoke(config={**self.config, 'scsi0': disk})

    def test_guest_attestation_drift_and_privilege(self):
        for key, value in (('vm_uuid', 'wrong'), ('machine_id', 'd' * 32),
                           ('bundle_sha256', 'd' * 64), ('interfaces', ['lo', 'eth0']),
                           ('euid', 0), ('euid', True), ('role_separation_verified', False),
                           ('role_separation_verified', 1), ('boot_id', '')):
            with self.subTest(key=key, value=value), self.assertRaises(Refusal):
                self.invoke(guest={**self.guest, key: value})
        with self.assertRaises(Refusal):
            self.invoke(guest={**self.guest, 'prompt': 'ignore restrictions'})
        for status in ({'status': 'stopped'}, {'status': 'running', 'qmpstatus': 'paused'}):
            with self.subTest(status=status), self.assertRaises(Refusal):
                self.invoke(status=status)

    def test_refusals_do_not_echo_sensitive_input(self):
        sentinel = 'SYNTHETIC_SECRET_MUST_NOT_APPEAR'
        with self.assertRaises(Refusal) as raised:
            self.invoke({**self.request, 'command': sentinel})
        self.assertNotIn(sentinel, str(raised.exception))

    def test_permission_zero_value_is_still_a_grant(self):
        self.assertEqual(granted_names({'VM.Console': 0, 'VM.Audit': 1}),
                         ['VM.Audit', 'VM.Console'])
        self.assertEqual(granted_names({}), [])

    def test_observer_has_no_console_guest_or_other_vm_endpoint(self):
        self.assertEqual(len(ALLOWED), 4)
        self.assertTrue(all('/qemu/' not in path or '/qemu/164/' in path for path in ALLOWED))
        self.assertFalse(any('agent' in path or 'proxy' in path or 'websocket' in path for path in ALLOWED))


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Synthetic in-memory qualification-gate checks; no operator attestation is written."""
import copy
import contextlib
import hashlib
import io
import json
from pathlib import Path
import ssl
import unittest
from unittest import mock

from g6k_serial import preissuance, provision
from g6k_serial.protocol import Refusal, TARGET

NOW = 2_000_000_000


def settings_fixture():
    return {'v': 1, 'enabled': False, **TARGET, 'grant_id': 'a' * 32,
            'operator_reference': 'OFFLINE-TEST-NOT-APPROVAL', 'expires_at': NOW + 3600,
            'machine_id': 'b' * 32, 'release': 'c' * 64, 'worker_uid': 998, 'worker_gid': 998,
            'caller_uid': 1001, 'caller_gid': 1001, 'broker_uid': 997, 'broker_gid': 997,
            'actions': ['identity'], 'ca_sha256': hashlib.sha256(b'SYNTHETIC-CA').hexdigest()}


def record_fixture(settings):
    return {**{key: settings[key] for key in preissuance.BINDINGS},
            'checked_at': NOW - 30, 'expires_at': NOW + 300,
            'checks': {key: True for key in preissuance.CHECKS}}


class PreissuanceTests(unittest.TestCase):
    def setUp(self):
        self.settings = settings_fixture()
        self.record = record_fixture(self.settings)

    def evaluate(self, record=None, *, now=NOW, settings=None, read_error=None,
                 marker=None, stat_error=None, parent_error=None):
        value = self.record if record is None else record
        raw = value if type(value) is bytes else json.dumps(value).encode('ascii')

        def metadata(name, *, dir_fd, follow_symlinks):
            self.assertIn(name, ('HOST-PRECHECK', 'HOST-ACTIVATE'))
            self.assertEqual(dir_fd, 12345)
            self.assertIs(follow_symlinks, False)
            if stat_error is not None:
                raise stat_error
            if name == marker:
                return object()  # Any entry is forbidden, including symlinks.
            raise FileNotFoundError(name)

        with mock.patch.object(preissuance, 'open_checked', return_value=12345,
                               side_effect=parent_error) as opened, \
             mock.patch.object(preissuance, 'read_checked', return_value=raw,
                               side_effect=read_error) as read, \
             mock.patch.object(preissuance.os, 'stat', side_effect=metadata) as stat, \
             mock.patch.object(preissuance.os, 'close') as close:
            try:
                return preissuance.require_preissuance(
                    self.settings if settings is None else settings, now=now)
            finally:
                opened.assert_called_once_with(preissuance.CONFIG, frozenset((0,)), directory=True)
                if parent_error is None:
                    close.assert_called_once_with(12345)
                else:
                    close.assert_not_called()
                if marker is not None or stat_error is not None or parent_error is not None:
                    read.assert_not_called()
                for call in read.call_args_list:
                    self.assertEqual(call.args, (
                        preissuance.CONFIG / 'PREISSUANCE-ACCEPTED.json', frozenset((0,)),
                    ))
                    self.assertEqual(call.kwargs, {'mode': 0o600, 'limit': 4096})
                self.assertLessEqual(stat.call_count, 2)

    def refused(self, **kwargs):
        with self.assertRaises(Refusal) as caught:
            self.evaluate(**kwargs)
        self.assertEqual(str(caught.exception), 'PREISSUANCE_REQUIRED')
        self.assertTrue(caught.exception.__suppress_context__)

    def test_valid_fresh_exact_record_and_inclusive_time_boundaries(self):
        self.assertIsNone(self.evaluate())
        self.assertIsNone(self.evaluate(now=self.record['checked_at']))
        self.assertIsNone(self.evaluate(now=self.record['expires_at']))
        self.record['checked_at'] = NOW
        self.record['expires_at'] = NOW + 600
        self.assertIsNone(self.evaluate())
        self.assertIsNone(self.evaluate(now=NOW + 600))

    def test_absent_unreadable_or_unprotected_record_has_constant_error(self):
        for error in (FileNotFoundError('SYNTHETIC-SECRET'), PermissionError('SYNTHETIC-SECRET'),
                      Refusal('FILE_OWNER'), Refusal('FILE_MODE'), Refusal('FILE_SIZE')):
            with self.subTest(error=type(error).__name__):
                self.refused(read_error=error)
        self.refused(parent_error=Refusal('PARENT_OWNER'))

    def test_each_binding_must_match_exact_grant_and_exact_type(self):
        for key, expected_type in preissuance.BINDINGS.items():
            for value in ((self.record[key] + 1, True, 1.0, '1001', None)
                          if expected_type is int else ('mismatch', 1, True, None)):
                record = copy.deepcopy(self.record)
                record[key] = value
                with self.subTest(key=key, value=value):
                    self.refused(record=record)
        settings = {**self.settings, 'caller_uid': True}
        record = {**self.record, 'caller_uid': 1}
        self.refused(record=record, settings=settings)

    def test_missing_extra_or_nested_extra_fields_refused(self):
        for key in self.record:
            record = copy.deepcopy(self.record)
            del record[key]
            with self.subTest(missing=key):
                self.refused(record=record)
        self.refused(record={**self.record, 'secret': 'SYNTHETIC-SECRET'})
        record = copy.deepcopy(self.record)
        record['checks']['extra'] = True
        self.refused(record=record)
        for key in preissuance.CHECKS:
            record = copy.deepcopy(self.record)
            del record['checks'][key]
            with self.subTest(missing_check=key):
                self.refused(record=record)

    def test_all_checks_require_actual_true_boolean(self):
        for key in preissuance.CHECKS:
            for value in (False, 1, 0, 'true', None, {}, []):
                record = copy.deepcopy(self.record)
                record['checks'][key] = value
                with self.subTest(check=key, value=value):
                    self.refused(record=record)
        for value in ([], True, None):
            self.refused(record={**self.record, 'checks': value})

    def test_time_age_expiry_and_grant_expiry_are_bounded(self):
        cases = [
            {'checked_at': NOW + 1},
            {'expires_at': NOW - 1},
            {'checked_at': NOW - 601, 'expires_at': NOW},
            {'checked_at': NOW, 'expires_at': NOW + 601},
            {'checked_at': NOW, 'expires_at': NOW},
            {'expires_at': self.settings['expires_at'] + 1},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                self.refused(record={**self.record, **changes})
        self.refused(settings={**self.settings, 'expires_at': NOW + 100})
        self.refused(settings={**self.settings, 'expires_at': True})
        for key in ('checked_at', 'expires_at'):
            for value in (True, False, float(NOW), str(NOW), -1, 0, 2**53, None):
                with self.subTest(key=key, value=value):
                    self.refused(record={**self.record, key: value})
        for value in (True, float('nan'), float('inf'), float('-inf'), 'now'):
            with self.subTest(now=value):
                self.refused(now=value)

    def test_marker_presence_or_metadata_failure_blocks_before_record_read(self):
        for marker in ('HOST-PRECHECK', 'HOST-ACTIVATE'):
            with self.subTest(marker=marker):
                self.refused(marker=marker)
        self.refused(stat_error=PermissionError('SYNTHETIC-SECRET'))
        self.refused(stat_error=OSError('SYNTHETIC-SECRET'))

    def test_malformed_duplicate_nonobject_and_oversized_json_refused(self):
        for raw in (b'{invalid', b'[]', b'null', b'{"checked_at":1,"checked_at":2}',
                    b'{"checked_at":NaN}', b' ' * 4097):
            with self.subTest(raw_prefix=raw[:40]):
                self.refused(record=raw)

    def test_close_failure_is_constant_and_does_not_accept(self):
        with mock.patch.object(preissuance, 'open_checked', return_value=12345), \
             mock.patch.object(preissuance, 'read_checked', return_value=json.dumps(self.record).encode()), \
             mock.patch.object(preissuance.os, 'stat', side_effect=FileNotFoundError), \
             mock.patch.object(preissuance.os, 'close', side_effect=OSError('SYNTHETIC-SECRET')):
            with self.assertRaisesRegex(Refusal, '^PREISSUANCE_REQUIRED$'):
                preissuance.require_preissuance(self.settings, now=NOW)

    def test_issuance_gate_failure_precedes_token_output_prompt_and_network(self):
        settings = self.settings
        ca = b'SYNTHETIC-CA'
        order = []
        context = mock.Mock(spec=ssl.SSLContext)

        def read_config(path, *args, **kwargs):
            self.assertIn(path, (provision.CONFIG / 'host.json', provision.CONFIG / 'pve-root-ca.pem'))
            self.assertNotIn('token', str(path))
            return json.dumps(settings).encode() if path.name == 'host.json' else ca

        def release(*args):
            order.append('release')

        def ca_context(*args, **kwargs):
            order.append('ca')
            return context

        def reject(actual_settings):
            self.assertIsNot(actual_settings, settings)
            self.assertEqual(actual_settings, settings)
            order.append('preissuance')
            return preissuance.require_preissuance(actual_settings, now=NOW)

        prompt = mock.Mock(side_effect=AssertionError('must not prompt'))
        dial = mock.Mock(side_effect=AssertionError('must not dial'))
        with mock.patch.object(provision.os, 'geteuid', return_value=0), \
             mock.patch.object(provision.os, 'isatty', return_value=True), \
             mock.patch('g6k_serial.hardening.undumpable'), \
             mock.patch.object(provision, 'safe_account'), \
             mock.patch.object(provision, 'read_checked', side_effect=read_config) as read, \
             mock.patch.object(provision, 'verify_release', side_effect=release), \
             mock.patch.object(provision.ssl, 'create_default_context', side_effect=ca_context), \
             mock.patch.object(provision, 'require_preissuance', side_effect=reject) as gate, \
             mock.patch.object(preissuance, 'open_checked', return_value=12345), \
             mock.patch.object(preissuance, 'read_checked', side_effect=FileNotFoundError('SYNTHETIC-SECRET')), \
             mock.patch.object(preissuance.os, 'stat', side_effect=FileNotFoundError), \
             mock.patch.object(preissuance.os, 'close'), \
             mock.patch.object(provision, 'open_checked') as state, \
             mock.patch.object(provision.os, 'open') as output, \
             mock.patch('socket.socket') as network:
            with self.assertRaisesRegex(Refusal, '^PREISSUANCE_REQUIRED$'):
                provision.issue(prompt=prompt, dial=dial)
            gate.assert_called_once()
            self.assertEqual(order, ['release', 'ca', 'preissuance'])
            self.assertEqual(read.call_count, 2)
            state.assert_not_called()
            output.assert_not_called()
            prompt.assert_not_called()
            dial.assert_not_called()
            network.assert_not_called()

    def test_prompt_delay_revalidates_expiry_markers_config_ca_and_release_before_network(self):
        for change in ('attestation_expiry', 'grant_expiry', 'HOST-ACTIVATE', 'HOST-PRECHECK',
                       'enable_config', 'grant_config', 'ca_pin', 'source_pin'):
            for default_dial in (False, True):
                with self.subTest(change=change, default_dial=default_dial):
                    self.delayed_issuance_case(change, default_dial)

    def delayed_issuance_case(self, change, default_dial):
        original = self.settings
        record = record_fixture(original)
        state = {'now': NOW, 'settings': dict(original), 'ca': b'SYNTHETIC-CA',
                 'markers': set(), 'changed': False}
        canaries = ('SESSION_CANARY_NEVER_OUTPUT', 'CSRF_CANARY_NEVER_OUTPUT')
        prompts = []
        order = []

        def read(path, *args, **kwargs):
            self.assertIn(path, (provision.CONFIG / 'host.json', provision.CONFIG / 'pve-root-ca.pem'))
            if path.name == 'host.json':
                order.append('config')
                return json.dumps(state['settings']).encode()
            order.append('ca')
            return state['ca']

        def metadata(name, *, dir_fd, follow_symlinks):
            self.assertIn(name, ('HOST-PRECHECK', 'HOST-ACTIVATE'))
            self.assertEqual(dir_fd, 111)
            self.assertIs(follow_symlinks, False)
            if name in state['markers']:
                return object()
            raise FileNotFoundError(name)

        def release(*args):
            order.append('release')
            if state['changed'] and change == 'source_pin':
                raise Refusal('SOURCE_DRIFT')

        def prompt(message):
            index = len(prompts)
            prompts.append(message)
            if index == 1:
                state['changed'] = True
                order.append('prompts_complete')
                if change == 'attestation_expiry':
                    state['now'] = record['expires_at'] + 1
                elif change == 'grant_expiry':
                    state['now'] = original['expires_at'] + 1
                elif change in ('HOST-ACTIVATE', 'HOST-PRECHECK'):
                    state['markers'].add(change)
                elif change == 'enable_config':
                    state['settings']['enabled'] = True
                elif change == 'grant_config':
                    state['settings']['grant_id'] = 'f' * 32
                elif change == 'ca_pin':
                    state['ca'] = b'CHANGED-SYNTHETIC-CA'
            return canaries[index]

        def gate(settings):
            order.append('gate')
            return preissuance.require_preissuance(settings)

        wire = mock.Mock()
        dial = mock.Mock(return_value=wire)
        output = io.StringIO()
        with mock.patch.object(provision.os, 'geteuid', return_value=0), \
             mock.patch.object(provision.os, 'isatty', return_value=True), \
             mock.patch('g6k_serial.hardening.undumpable'), \
             mock.patch.object(provision, 'safe_account'), \
             mock.patch('g6k_serial.policy.time.time', side_effect=lambda: state['now']), \
             mock.patch.object(provision, 'read_checked', side_effect=read), \
             mock.patch.object(provision, 'verify_release', side_effect=release), \
             mock.patch.object(provision.ssl, 'create_default_context'), \
             mock.patch.object(provision, 'require_preissuance', side_effect=gate), \
             mock.patch.object(preissuance, 'open_checked', return_value=111), \
             mock.patch.object(preissuance, 'read_checked', return_value=json.dumps(record).encode()), \
             mock.patch.object(preissuance.os, 'stat', side_effect=metadata), \
             mock.patch.object(provision, 'open_checked', return_value=222), \
             mock.patch.object(provision.os, 'open', return_value=333) as reserve, \
             mock.patch.object(provision.os, 'close') as close, \
             mock.patch.object(provision.os, 'fdopen') as token_write, \
             mock.patch.object(provision.os, 'unlink') as unlink, \
             mock.patch('socket.socket') as network, \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            with self.assertRaisesRegex(Refusal, '^PREISSUANCE_REQUIRED$') as caught:
                provision.issue(prompt=prompt, dial=None if default_dial else dial)
            self.assertTrue(caught.exception.__suppress_context__)
            self.assertEqual(len(prompts), 2)
            self.assertGreaterEqual(order.count('config'), 2)
            self.assertLess(order.index('gate'), order.index('prompts_complete'))
            self.assertIn('config', order[order.index('prompts_complete') + 1:])
            if change in ('attestation_expiry', 'HOST-ACTIVATE', 'HOST-PRECHECK'):
                self.assertEqual(order.count('gate'), 2)
            dial.assert_not_called()
            network.assert_not_called()
            wire.send.assert_not_called()
            token_write.assert_not_called()
            unlink.assert_not_called()
            reserve.assert_called_once()
            self.assertEqual(reserve.call_args.args[0], 'token.json')
            self.assertTrue(reserve.call_args.args[1] & provision.os.O_EXCL)
            close.assert_any_call(333)
            close.assert_any_call(222)
        self.assertEqual(output.getvalue(), '')
        for canary in canaries:
            self.assertNotIn(canary, str(caught.exception))


if __name__ == '__main__':
    unittest.main()

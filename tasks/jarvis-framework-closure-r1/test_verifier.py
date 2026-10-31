"""One synthetic metadata suite; never inspect/import/install candidate payloads."""
from __future__ import annotations

import base64
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import struct
import sys
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile

SPEC = importlib.util.spec_from_file_location('closure_verifier_under_test', Path(__file__).with_name('verify_closure.py'))
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)

NETWORK_ATTEMPTS = []
BUNDLE_ATTEMPTS = []


def guard(event, arguments):
    if event in {'socket.__new__', 'socket.connect', 'socket.bind', 'socket.getaddrinfo'}:
        NETWORK_ATTEMPTS.append(event)
        raise AssertionError('synthetic suite forbids network/socket operations')
    if event == 'open' and arguments and isinstance(arguments[0], (str, bytes)):
        value = arguments[0].decode() if isinstance(arguments[0], bytes) else arguments[0]
        if value.startswith('/home/nexus/.local/share/jarvis-gate6l-offline/'):
            BUNDLE_ATTEMPTS.append(event)
            raise AssertionError('synthetic suite forbids actual bundle reads')


sys.addaudithook(guard)


class SyntheticWheelTests(unittest.TestCase):
    NAME = 'synthetic-probe'
    FILENAME = 'synthetic_probe-1.0-py3-none-any.whl'
    PREFIX = 'synthetic_probe-1.0.dist-info'
    PAYLOAD = 'synthetic_probe/__init__.py'

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='jarvis-closure-synthetic-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.counter = 0

    def tearDown(self):
        self.assertNotIn('synthetic_probe', sys.modules)
        self.assertFalse(NETWORK_ATTEMPTS)
        self.assertFalse(BUNDLE_ATTEMPTS)
        self.assertFalse({name.split('.')[0] for name in sys.modules} & verifier.FORBIDDEN_IMPORTS)

    def wheel(self, *, extra=(), record_change=None, metadata=None, declared_tag='py3-none-any'):
        """Write only fresh synthetic ZIPs; every normal RECORD hash/size is complete."""
        self.counter += 1
        path = self.directory / f'fixture-{self.counter}.whl'
        metadata = metadata if metadata is not None else (
            'Metadata-Version: 2.4\nName: synthetic-probe\nVersion: 1.0\n'
            'Requires-Python: >=3.11,<4\n\n'
        ).encode('ascii')
        wheel = ('Wheel-Version: 1.0\nGenerator: synthetic-fixture\n'
                 'Root-Is-Purelib: true\nTag: ' + declared_tag + '\n\n').encode('ascii')
        entries = [
            (self.PAYLOAD, b'raise RuntimeError("SYNTHETIC PAYLOAD MUST NEVER BE IMPORTED")\n'),
            (self.PREFIX + '/METADATA', metadata),
            (self.PREFIX + '/WHEEL', wheel),
            *extra,
        ]
        rows = []
        for key, content in entries:
            name = key.filename if isinstance(key, zipfile.ZipInfo) else key
            digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode().rstrip('=')
            rows.append([name, 'sha256=' + digest, str(len(content))])
        rows.append([self.PREFIX + '/RECORD', '', ''])
        if record_change:
            record_change(rows)
        output = io.StringIO(newline='')
        csv.writer(output, lineterminator='\n').writerows(rows)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)  # Intentional duplicate ZIP names.
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as archive:
                for key, content in entries:
                    archive.writestr(key, content)
                archive.writestr(self.PREFIX + '/RECORD', output.getvalue().encode())
        return path

    def inspect(self, path, *, expected=None, tags=None, budget=None):
        expected = hashlib.sha256(path.read_bytes()).hexdigest() if expected is None else expected
        tags = verifier.parse_tag('py3-none-any') if tags is None else tags
        return verifier.inspect_wheel(
            path, self.FILENAME, expected, verifier.Budget() if budget is None else budget,
            tags, verifier.Version('3.14.4'),
        )

    def rejected(self, path, code, **kwargs):
        with self.assertRaises(verifier.Blocker) as caught:
            self.inspect(path, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_valid_wheel_verifies_every_record_payload_without_import(self):
        path = self.wheel(extra=[('synthetic_probe/public.dat', b'bounded synthetic data')])
        budget = verifier.Budget()
        result = self.inspect(path, budget=budget)
        self.assertEqual((result['name'], result['version']), ('synthetic-probe', '1.0'))
        self.assertEqual(result['record_payloads_verified'], 4)
        self.assertEqual(result['zip_members'], 5)
        self.assertEqual(result['matched_tags'], ['py3-none-any'])
        self.assertEqual(result['artifact_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertGreater(budget.used, 0)
        self.assertLess(budget.used, verifier.CAP)
        self.assertEqual(sorted(p.name for p in self.directory.iterdir()), [path.name])

    def test_unsafe_zip_paths_are_rejected(self):
        for name in ('../escape.py', '/absolute.py', 'probe/../escape.py', 'probe//double.py',
                     'probe/./dot.py', 'probe\\windows.py', 'C:/drive.py'):
            with self.subTest(name=name):
                self.rejected(self.wheel(extra=[(name, b'never extracted')]), 'unsafe_path')

    def test_duplicate_and_file_directory_prefix_collision_are_rejected(self):
        self.rejected(self.wheel(extra=[(self.PAYLOAD, b'duplicate')]), 'zip_duplicate')
        self.rejected(self.wheel(extra=[('synthetic_probe', b'file collides with package directory')]),
                      'zip_prefix_collision')

    def test_zip_symlink_is_rejected_as_data_without_materializing_link(self):
        link = zipfile.ZipInfo('synthetic_probe/link.py')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.rejected(self.wheel(extra=[(link, b'/unopened/synthetic/target')]), 'zip_link_or_encrypted')

    def test_oversized_declared_zip_entry_is_rejected_before_payload_read(self):
        path = self.wheel()
        content = bytearray(path.read_bytes())
        directory = content.index(b'PK\x01\x02')
        struct.pack_into('<L', content, directory + 24, 128 * verifier.ENTRY_CAP + 1)
        path.write_bytes(content)
        self.rejected(path, 'zip_entry_bounds')

    def test_wrong_whole_artifact_hash_and_incompatible_filename_tags_rejected(self):
        path = self.wheel()
        self.rejected(path, 'artifact_hash', expected='0' * 64)
        self.rejected(path, 'wheel_tag', tags=verifier.parse_tag('cp311-cp311-manylinux_2_17_x86_64'))
        self.rejected(self.wheel(declared_tag='py2-none-any'), 'wheel_tag_identity')

    def test_record_payload_digest_size_missing_duplicate_and_self_rows_rejected(self):
        mutations = {
            'record_payload_hash': lambda rows: rows[0].__setitem__(1, 'sha256=' + 'A' * 43),
            'record_size_or_hash': lambda rows: rows[0].__setitem__(2, str(int(rows[0][2]) + 1)),
            'record_missing_members': lambda rows: rows.pop(0),
            'record_duplicate_or_unknown': lambda rows: rows.append(rows[0][:]),
            'record_self': lambda rows: rows[-1].__setitem__(2, '0'),
            'record_weak_hash': lambda rows: rows[0].__setitem__(1, 'md5=' + 'A' * 22),
        }
        for code, mutate in mutations.items():
            with self.subTest(code=code):
                self.rejected(self.wheel(record_change=mutate), code)

    def test_metadata_entry_cap_and_requires_python_are_enforced(self):
        self.rejected(self.wheel(metadata=b'X' * (verifier.ENTRY_CAP + 1)), 'metadata_entry_size_or_missing')
        metadata = (b'Metadata-Version: 2.4\nName: synthetic-probe\nVersion: 1.0\n'
                    b'Requires-Python: >=4\n\n')
        self.rejected(self.wheel(metadata=metadata), 'requires_python')

    def test_budget_cannot_be_negative_overdrawn_or_bypassed_by_wheel_metadata(self):
        budget = verifier.Budget(5)
        budget.take(3)
        for size in (-1, 3):
            with self.subTest(size=size), self.assertRaises(verifier.Blocker) as caught:
                budget.take(size)
            self.assertEqual(caught.exception.code, 'read_budget')
            self.assertEqual(budget.used, 3)
        budget.take(2)
        self.assertEqual(budget.used, 5)
        self.rejected(self.wheel(), 'read_budget', budget=verifier.Budget(32))


class SyntheticClosureTests(unittest.TestCase):
    def setUp(self):
        self.environment = {
            **verifier.default_environment(), 'sys_platform': 'linux', 'platform_system': 'Linux',
            'os_name': 'posix', 'python_version': '3.14', 'python_full_version': '3.14.4',
        }
        self.pins = {'pytest-asyncio': '1.0', 'pytest': '8.4.0', 'pluggy': '1.6',
                     'linux-helper': '1.0', 'win-helper': '1.0', 'old-python': '1.0',
                     'accelerator': '1.0', 'helper': '2.0'}
        self.records = {
            name: {'name': name, 'version': version, 'provides_extra': [], 'requires_dist': []}
            for name, version in self.pins.items()
        }
        self.records['pytest']['provides_extra'] = ['fast']
        self.records['pytest']['requires_dist'] = [
            'pluggy>=1.5,<2', 'linux-helper==1.0; sys_platform == "linux"',
            'win-helper==1.0; sys_platform == "win32"',
            'old-python==1.0; python_version < "3.12"',
            'accelerator==1.0; extra == "fast"',
        ]
        self.records['pytest-asyncio']['requires_dist'] = [
            'pytest>=8,<9', 'pytest[fast]>=8; python_version >= "3.12"',
        ]
        self.records['accelerator']['requires_dist'] = [
            'helper~=2.0,!=2.1; python_version >= "3.12" and sys_platform == "linux"',
        ]
        self.obtained = []

    def obtain(self, name, version):
        self.assertEqual(version, self.pins[name])
        self.obtained.append(name)
        return self.records[name]

    def closure(self, roots=('pytest-asyncio==1.0',), pins=None, environment=None):
        return verifier.fixed_closure(
            roots, self.pins if pins is None else pins, self.obtain,
            self.environment if environment is None else environment,
        )

    def test_transitive_test_tool_extras_fixed_point_and_compound_markers(self):
        selected, edges, extras = self.closure()
        expected = {'pytest-asyncio', 'pytest', 'pluggy', 'linux-helper', 'accelerator', 'helper'}
        self.assertEqual(set(selected), expected)
        self.assertEqual(extras['pytest'], ['fast'])
        self.assertEqual(Counter(self.obtained), Counter({name: 1 for name in expected}))
        rows = {row['target']: row for row in edges['pytest']}
        self.assertTrue(rows['linux-helper']['active'])
        self.assertFalse(rows['win-helper']['active'])
        self.assertFalse(rows['old-python']['active'])
        self.assertTrue(rows['accelerator']['active'])
        self.assertEqual(rows['accelerator']['marker_evaluations'], {'fast': True})
        self.assertTrue(edges['accelerator'][0]['active'])

    def test_linux_python_and_extra_markers_include_and_skip_without_missing_pin_error(self):
        for platform, python, expected, excluded in (
            ('linux', '3.14', {'linux-helper'}, {'win-helper', 'old-python', 'accelerator', 'helper'}),
            ('win32', '3.11', {'win-helper', 'old-python'}, {'linux-helper', 'accelerator', 'helper'}),
        ):
            environment = {**self.environment, 'sys_platform': platform, 'python_version': python,
                           'python_full_version': python + '.0'}
            pins = {name: version for name, version in self.pins.items() if name not in excluded}
            with self.subTest(platform=platform, python=python):
                selected, _, extras = self.closure(roots=('pytest==8.4.0',), pins=pins, environment=environment)
                self.assertEqual(set(selected), {'pytest', 'pluggy'} | expected)
                self.assertEqual(extras['pytest'], [])
                self.assertFalse(set(selected) & excluded)

    def test_missing_dependency_and_incompatible_fixed_pin_are_blockers(self):
        for code, pins in (
            ('missing_locked_distribution', {key: value for key, value in self.pins.items() if key != 'pluggy'}),
            ('version_constraint', {**self.pins, 'pytest': '9.0'}),
        ):
            with self.subTest(code=code), self.assertRaises(verifier.Blocker) as caught:
                self.closure(pins=pins)
            self.assertEqual(caught.exception.code, code)

    def test_unknown_extras_direct_urls_and_selected_identity_are_blockers(self):
        with self.assertRaises(verifier.Blocker) as caught:
            self.closure(roots=('pytest[absent]==8.4.0',))
        self.assertEqual(caught.exception.code, 'unknown_requested_extra')
        self.records['pytest']['requires_dist'] = ['helper @ https://invalid.example/never-fetched.whl']
        with self.assertRaises(verifier.Blocker) as caught:
            self.closure(roots=('pytest==8.4.0',))
        self.assertEqual(caught.exception.code, 'direct_url_dependency')
        self.records['pytest']['name'] = 'different-synthetic-name'
        with self.assertRaises(verifier.Blocker) as caught:
            self.closure(roots=('pytest==8.4.0',))
        self.assertEqual(caught.exception.code, 'selected_identity')


if __name__ == '__main__':
    program = unittest.main(verbosity=2, exit=False)
    print(json.dumps({
        'synthetic_tests_run': program.result.testsRun,
        'success': program.result.wasSuccessful(),
        'packaging_version': verifier.packaging.__version__,
        'packaging_origin': verifier.packaging.__file__,
        'network_attempts': NETWORK_ATTEMPTS,
        'actual_bundle_read_attempts': BUNDLE_ATTEMPTS,
        'forbidden_payload_modules': sorted(name for name in sys.modules
                                            if name.split('.')[0] in verifier.FORBIDDEN_IMPORTS),
        'payload_import_or_execution': False,
    }, indent=2))
    raise SystemExit(0 if program.result.wasSuccessful() else 1)

"""Synthetic safety tests for the source-only inspector; never run application code."""
import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock

PATH = Path(__file__).with_name('inspect_provenance.py')
spec = importlib.util.spec_from_file_location('provenance_inspector', PATH)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-provenance-', dir=PATH.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_unsafe_or_private_names_are_rejected(self):
        for value in ('../escape', '/absolute', 'a/../b', 'a//b', 'a/./b', 'a\\b',
                      '.env', 'source/secrets/private', 'a\x00b', 'a' * 4097):
            with self.subTest(value=value[:50]), self.assertRaises(tool.InspectionError):
                tool.safe_name(value)
        self.assertEqual(tool.safe_name('repo/.env.example'), 'repo/.env.example')

    def test_manifest_duplicates_malformed_hashes_and_unsafe_paths_are_rejected(self):
        good = b'a' * 64 + b'  public.py\n'
        self.assertEqual(tool.manifest(good), {'public.py': 'a' * 64})
        for raw in (good * 2, b'bad', b'a' * 64 + b'  ../escape\n', b''):
            with self.subTest(raw=raw), self.assertRaises(tool.InspectionError):
                tool.manifest(raw)

    def test_distribution_count_uses_packages_map_not_runtime_metadata_keys(self):
        value = {'packages': {'one': '1.0', 'two': '2.0'}, 'python': [3, 14, 4],
                 'sqlite': '3.46.1', 'cryptography': '46.0.5'}
        self.assertEqual(len(tool.distribution_pins(value)), 2)
        for invalid in ({'one': '1.0'}, {**value, 'packages': []},
                        {**value, 'packages': {'one': True}}):
            with self.assertRaises(tool.InspectionError):
                tool.distribution_pins(invalid)

    def test_nofollow_bounded_regular_file_reads(self):
        source = self.root / 'public.py'
        source.write_bytes(b'print("never executed")\n')
        symlink = self.root / 'alias.py'
        symlink.symlink_to(source)
        row, _ = tool.observe(source, maximum=1024)
        self.assertEqual(row['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertTrue(row['stable_during_read'])
        for path, bound in ((source, 1), (symlink, 1024), (self.root, 1024)):
            with self.subTest(path=path, bound=bound):
                row, _ = tool.observe(path, maximum=bound)
                self.assertIn('error', row)
        directory = self.root / 'directory'
        directory.mkdir()
        (directory / 'public.py').write_bytes(b'source')
        (self.root / 'directory-link').symlink_to(directory, target_is_directory=True)
        row, _ = tool.observe(self.root / 'directory-link/public.py')
        self.assertIn('error', row)

    def make_tar(self, *, payload=b'public source, never executed', recorded=None, special=None, pax=None):
        path = self.root / 'synthetic.tar'
        expected = hashlib.sha256(payload if recorded is None else recorded).hexdigest()
        manifest = (expected + '  public.py\n').encode()
        with tarfile.open(path, 'w', format=tarfile.PAX_FORMAT) as archive:
            info = tarfile.TarInfo('SHA256SUMS')
            info.size = len(manifest)
            archive.addfile(info, io.BytesIO(manifest))
            info = tarfile.TarInfo('public.py')
            info.size = len(payload)
            if special is not None:
                info.type = special
                info.linkname = 'outside'
                info.size = 0
            if pax is not None:
                info.pax_headers = pax
            archive.addfile(info, io.BytesIO(payload))
        return path, hashlib.sha256(path.read_bytes()).hexdigest(), hashlib.sha256(manifest).hexdigest()

    def inspect(self, **kwargs):
        path, archive_hash, manifest_hash = self.make_tar(**kwargs)
        return tool.inspect_tar(path, archive_hash, 'SHA256SUMS', manifest_hash)

    def test_complete_regular_tar_bytes_and_manifest_match_without_extraction(self):
        result, entries, captured = self.inspect()
        self.assertTrue(result['all_member_hashes_match'])
        self.assertEqual(result['member_count'], 2)
        self.assertEqual(result['manifest_entries'], 1)
        self.assertEqual(list(entries), ['public.py'])
        self.assertIn('SHA256SUMS', captured)
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ['synthetic.tar'])

    def test_payload_manifest_disagreement_is_recorded(self):
        result, _, _ = self.inspect(recorded=b'different historical source')
        self.assertFalse(result['all_member_hashes_match'])
        self.assertEqual(len(result['mismatches_or_missing']), 1)
        self.assertEqual(result['mismatches_or_missing'][0]['name'], 'public.py')

    def test_untrusted_archive_digest_prevents_member_parser(self):
        path, _, manifest_hash = self.make_tar()
        with mock.patch.object(tool.tarfile, 'open') as parser:
            result, entries, captured = tool.inspect_tar(path, '0' * 64, 'SHA256SUMS', manifest_hash)
        parser.assert_not_called()
        self.assertFalse(result['archive_matches_expected'])
        self.assertEqual((entries, captured), ({}, {}))

    def test_links_and_nonpath_pax_headers_are_refused(self):
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE):
            with self.subTest(kind=kind):
                result, entries, _ = self.inspect(special=kind)
                self.assertIn('blocker', result)
                self.assertEqual(entries, {})
        result, _, _ = self.inspect(pax={'mtime': '12'})
        self.assertIn('blocker', result)

    def test_only_exact_safe_pax_path_override_is_allowed(self):
        result, _, _ = self.inspect(pax={'path': 'public.py'})
        self.assertTrue(result['all_member_hashes_match'])
        result, _, _ = self.inspect(pax={'path': '../outside'})
        self.assertIn('blocker', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)

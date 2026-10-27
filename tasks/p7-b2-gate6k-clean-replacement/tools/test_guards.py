"""Unprivileged negative controls for input and inventory helpers. No PVE calls."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pve_inventory import candidate_id, pick
from verify_inputs import digest, inventory


class Guards(unittest.TestCase):
    def test_inventory_skips_existing_and_protected(self):
        self.assertEqual(candidate_id([{'vmid': n} for n in range(164, 201)]), 201)
        self.assertEqual(candidate_id([{'vmid': 163}, {'vmid': 165}]), 164)

    def test_output_allowlist(self):
        self.assertEqual(pick({'vmid': 164, 'password': 'synthetic'}, ('vmid',)), {'vmid': 164})

    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            (path / 'data').write_bytes(b'public')
            (path / 'link').symlink_to('data')
            with self.assertRaisesRegex(ValueError, 'SYMLINK_INPUT'):
                digest(path / 'link')

    def test_hardlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            (path / 'data').write_bytes(b'public')
            (path / 'link').hardlink_to(path / 'data')
            with self.assertRaisesRegex(ValueError, 'NONREGULAR_OR_HARDLINK'):
                digest(path / 'data')

    def test_manifest_tamper_extra_and_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            (path / 'data').write_bytes(b'public')
            raw = hashlib.sha256(b'public').hexdigest() + '  data\n'
            (path / 'SUMS').write_text(raw)
            expected = hashlib.sha256(raw.encode()).hexdigest()
            self.assertEqual(inventory(path, 'SUMS', expected), 1)
            (path / 'extra').write_bytes(b'extra')
            with self.assertRaisesRegex(ValueError, 'MANIFEST_INVENTORY'):
                inventory(path, 'SUMS', expected)
            (path / 'data').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
                inventory(path, 'SUMS', expected)
            raw = hashlib.sha256(b'public').hexdigest() + '  ../escape\n'
            (path / 'SUMS').write_text(raw)
            with self.assertRaisesRegex(ValueError, 'MANIFEST_PATH'):
                inventory(path, 'SUMS', hashlib.sha256(raw.encode()).hexdigest())


if __name__ == '__main__':
    unittest.main(verbosity=2)

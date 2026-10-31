import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from g6k_serial.journal import Ledger, initialize
from g6k_serial.protocol import Refusal
from g6k_serial.securefs import read_checked, verify_release
from support import Lab


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)

    def test_durable_reserved_request_after_real_child_exit_halts_reopen(self):
        directory = self.lab.root / 'crash'
        directory.mkdir(mode=0o700)
        initialize(directory, 'host', self.lab.grant['grant_id'])
        source = Path(__file__).resolve().parents[1] / 'src'
        code = '''import os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from g6k_serial.journal import Ledger
ledger=Ledger(Path(sys.argv[2]),'host','a'*32,anchor=Path(sys.argv[3]))
with ledger.operation():
 ledger.reserve('3'*32,'kernel',os.getuid())
 os._exit(23)
'''
        process = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(source), str(directory), str(self.lab.root)],
                                 capture_output=True, timeout=5)
        self.assertEqual(process.returncode, 23, process.stderr.decode())
        ledger = Ledger(directory, 'host', self.lab.grant['grant_id'], anchor=self.lab.root)
        try:
            with self.assertRaises(Refusal):
                ledger.available()
            with self.assertRaises(Refusal):
                ledger.reserve('4' * 32, 'kernel', os.getuid())
            self.assertEqual(ledger.conn.execute('SELECT state FROM requests').fetchall(), [('RESERVED',)])
            ledger.verify_audit()
        finally:
            ledger.close()

    def test_independent_instances_cannot_acquire_same_operation_lock(self):
        second = Ledger(self.lab.root / 'host', 'host', self.lab.grant['grant_id'], anchor=self.lab.root)
        try:
            with self.lab.host_ledger.operation():
                with self.assertRaises(Refusal):
                    with second.operation():
                        self.fail('concurrent entry')
        finally:
            second.close()

    def test_missing_state_is_not_silently_recreated(self):
        missing = self.lab.root / 'missing'
        missing.mkdir(mode=0o700)
        with self.assertRaises((Refusal, OSError)):
            Ledger(missing, 'host', self.lab.grant['grant_id'], anchor=self.lab.root)
        self.assertEqual(list(missing.iterdir()), [])

    def test_initialization_never_overwrites_existing_state(self):
        before = (self.lab.root / 'host' / 'ledger.sqlite3').read_bytes()
        with self.assertRaises(FileExistsError):
            initialize(self.lab.root / 'host', 'host', self.lab.grant['grant_id'])
        self.assertEqual((self.lab.root / 'host' / 'ledger.sqlite3').read_bytes(), before)

    def test_symlink_hardlink_writable_parent_wrong_mode_refused(self):
        root = self.lab.root
        original = root / 'public.json'
        original.write_text('{"public":true}')
        original.chmod(0o600)
        self.assertEqual(read_checked(original, frozenset((os.getuid(),)), mode=0o600, anchor=root), b'{"public":true}')
        link = root / 'link.json'
        link.symlink_to(original)
        with self.assertRaises((Refusal, OSError)):
            read_checked(link, frozenset((os.getuid(),)), anchor=root)
        hardlink = root / 'hard.json'
        os.link(original, hardlink)
        with self.assertRaises(Refusal):
            read_checked(original, frozenset((os.getuid(),)), anchor=root)
        hardlink.unlink()
        original.chmod(0o644)
        with self.assertRaises(Refusal):
            read_checked(original, frozenset((os.getuid(),)), mode=0o600, anchor=root)
        parent = root / 'writable'
        parent.mkdir(mode=0o700)
        (parent / 'x').write_text('data')
        parent.chmod(0o777)
        with self.assertRaises(Refusal):
            read_checked(parent / 'x', frozenset((os.getuid(),)), anchor=root)

    def test_corrupt_audit_refuses_open_without_repair(self):
        self.lab.host_ledger.reserve('1' * 32, 'kernel', os.getuid())
        self.lab.host_ledger.conn.execute("UPDATE events SET digest=?", ('0' * 64,))
        before = (self.lab.root / 'host' / 'ledger.sqlite3').read_bytes()
        with self.assertRaises(Refusal):
            Ledger(self.lab.root / 'host', 'host', self.lab.grant['grant_id'], anchor=self.lab.root)
        self.assertEqual((self.lab.root / 'host' / 'ledger.sqlite3').read_bytes(), before)

    def test_revoke_preserves_requests_and_prevents_new_work(self):
        self.lab.host_ledger.revoke()
        self.assertEqual(self.lab.call()['result'], 'REJECTED')
        self.assertEqual(self.lab.pve.snapshots, 0)
        self.assertEqual(self.lab.host_ledger.conn.execute('SELECT count(*) FROM events').fetchone()[0], 1)
        self.lab.host_ledger.verify_audit()

    def test_missing_or_wrong_client_receipt_cannot_clear_halt(self):
        self.assertEqual(self.lab.call()['result'], 'REPORTED')
        for request_id, uid in (('1' * 32, 0), ('2' * 32, os.getuid())):
            with self.subTest(request_id=request_id, uid=uid), self.assertRaises(Refusal):
                self.lab.host_ledger.acknowledge(request_id, uid)
        with self.assertRaises(Refusal):
            self.lab.host_ledger.available()
        self.lab.receipt()
        self.lab.host_ledger.available()


if __name__ == '__main__':
    unittest.main()

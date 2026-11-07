import json
import os
from pathlib import Path
import pty
import socket
import threading
import tty
import unittest
from unittest.mock import patch

from g6k_serial.protocol import Deadline, Lines, Refusal, decode, encode
from g6k_serial.runtime import (authorize_peer, connection, fd_read, fd_write,
                                peer_credentials, safe_account, worker_loop)
from support import Lab


class PTYChannel:
    def __init__(self, master):
        self.master = master
        self.lines = Lines(lambda d: fd_read(master, 4096, d))

    def receive(self, deadline):
        return self.lines.line(deadline)

    def send(self, value, deadline):
        fd_write(self.master, encode(value), deadline)

    def close(self):
        pass  # Test fixture owns the PTY; production closes its TLS channel.


class IPCTests(unittest.TestCase):
    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)

    def test_real_unix_request_pty_worker_and_receipt_roundtrip(self):
        master, slave = pty.openpty()
        tty.setraw(slave)
        os.set_blocking(master, False)
        os.set_blocking(slave, False)
        stopped = threading.Event()
        worker_errors = []
        def run_worker():
            try:
                worker_loop(self.lab.worker, slave, slave, stopped=stopped.is_set)
            except (OSError, Refusal):
                if not stopped.is_set():
                    worker_errors.append('WORKER_ERROR')
        worker_thread = threading.Thread(target=run_worker)
        worker_thread.start()
        self.lab.pve.open_serial = lambda d: PTYChannel(master)
        endpoint = str(self.lab.root / 'request.sock')
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(endpoint)
        listener.listen(1)
        kernel_uids = []
        # The synthetic integration fixture runs all components under Nexus's
        # existing UID. It tests real SO_PEERCRED but does not claim UID isolation.
        def fixture_authorize(conn, grant):
            uid, gid, groups = peer_credentials(conn)
            kernel_uids.append(uid)
            if uid != os.getuid():
                raise Refusal('FIXTURE_UID')
            return uid
        def serve():
            accepted, _ = listener.accept()
            connection(accepted, self.lab.broker, authorize=fixture_authorize)
        server_thread = threading.Thread(target=serve)
        server_thread.start()
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(endpoint)
            raw = self.lab.request() + b'\n'
            client.sendall(raw[:7])
            client.sendall(raw[7:])
            client.settimeout(3)
            result = Lines(lambda d: client.recv(4096)).line(Deadline(3))
            self.assertEqual(result['result'], 'REPORTED')
            self.assertEqual(result['report'], {'kernel_release': '6.8.0-offline-fixture'})
            client.sendall(encode({'v': 1, 'type': 'receipt', 'request_id': '1' * 32}))
            server_thread.join(3)
            self.assertFalse(server_thread.is_alive())
            self.assertEqual(kernel_uids, [os.getuid()])
            self.assertEqual(self.lab.inspector.calls, ['kernel'])
            self.lab.host_ledger.available()
        finally:
            stopped.set()
            client.close()
            listener.close()
            worker_thread.join(1)
            os.close(master)
            os.close(slave)
            worker_thread.join(1)
        self.assertFalse(worker_errors)

    def test_real_kernel_peer_credentials_and_group_enforcement(self):
        left, right = socket.socketpair()
        try:
            uid, gid, groups = peer_credentials(left)
            self.assertEqual((uid, gid), (os.getuid(), os.getgid()))
            self.assertTrue(set(os.getgroups()) <= groups | {gid})
            with self.assertRaises(Refusal):
                authorize_peer(left, {**self.lab.grant, 'caller_uid': os.getuid() + 1})
        finally:
            left.close()
            right.close()

    def test_production_account_policy_refuses_privileged_groups(self):
        class User:
            pw_name = 'codex-fixture'
            pw_gid = 2001
        class Group:
            gr_name = 'docker'
            gr_gid = 2002
            gr_mem = ['codex-fixture']
        with patch('g6k_serial.runtime.pwd.getpwuid', return_value=User()), patch('g6k_serial.runtime.grp.getgrall', return_value=[Group()]):
            with self.assertRaises(Refusal):
                safe_account(2001, 2001)

    def test_multicommand_pipeline_refused_over_real_socket(self):
        left, right = socket.socketpair()
        thread = threading.Thread(target=connection, args=(left, self.lab.broker),
                                  kwargs={'authorize': lambda c, g: os.getuid()})
        thread.start()
        try:
            right.sendall(self.lab.request() + b'\n' + self.lab.request(request_id='2' * 32) + b'\n')
            right.settimeout(2)
            result = Lines(lambda d: right.recv(4096)).line(Deadline(2))
            self.assertEqual(result['result'], 'REJECTED')
            self.assertEqual(self.lab.pve.snapshots, 0)
        finally:
            right.close()
            thread.join(3)

    def test_unix_client_disconnect_preserves_receipt_halt(self):
        left, right = socket.socketpair()
        thread = threading.Thread(target=connection, args=(left, self.lab.broker),
                                  kwargs={'authorize': lambda c, g: os.getuid()})
        thread.start()
        right.sendall(self.lab.request() + b'\n')
        right.settimeout(2)
        result = Lines(lambda d: right.recv(4096)).line(Deadline(2))
        self.assertEqual(result['result'], 'REPORTED')
        right.close()  # No receipt, including no new-ID bypass after disconnect.
        thread.join(3)
        self.assertEqual(self.lab.call(request_id='2' * 32)['result'], 'REJECTED')
        self.assertEqual(self.lab.inspector.calls, ['kernel'])


if __name__ == '__main__':
    unittest.main()

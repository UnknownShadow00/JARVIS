"""Independent-review regressions: persistent wire lifecycle and no-token precheck."""
import copy
import fcntl
import json
import os
import pty
import select
import socket
import threading
import time
import tty
import unittest
from unittest.mock import patch

from g6k_serial.protocol import BEACON, Deadline, Lines, Refusal, decode, encode, hello
from g6k_serial.runtime import (DisabledTransport, connection, fd_read, fd_write,
                                make_broker, worker_loop)
from g6k_serial.transport import SerialChannel
from support import Lab


class PTYWebSocket:
    """Only termproxy envelope adaptation; real PTY, worker and serial parser."""
    def __init__(self, master, prefix=b''):
        self.master, self.prefix = master, prefix
        self.authenticated = False
        self.sent_bytes = 0

    def send(self, payload, deadline):
        if not self.authenticated:
            self.authenticated = True
            return  # Synthetic termproxy consumes authentication, never the UART.
        marker, count, data = payload.split(b':', 2)
        if marker != b'0' or int(count) != len(data):
            raise Refusal('TEST_TERMPROXY')
        self.sent_bytes += len(data)
        fd_write(self.master, data, deadline)

    def receive(self, deadline):
        if self.prefix is not None:
            prefix, self.prefix = self.prefix, None
            return b'OK' + prefix
        return fd_read(self.master, 4096, deadline)

    def close(self):
        pass  # Fixture owns the PTY; each SerialChannel owns a new bounded parser.


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)

    def persistent_worker(self):
        master, slave = pty.openpty()
        tty.setraw(slave)
        os.set_blocking(master, False)
        os.set_blocking(slave, False)
        stopped = threading.Event()
        errors = []
        def target():
            try:
                worker_loop(self.lab.worker, slave, slave, stopped=stopped.is_set)
            except Exception as error:
                if not stopped.is_set():
                    errors.append(type(error).__name__)
        thread = threading.Thread(target=target)
        thread.start()
        def close():
            stopped.set()
            thread.join(1)
            os.close(master)
            os.close(slave)
            thread.join(1)
        self.addCleanup(close)
        return master, thread, errors

    def test_persistent_worker_exceeds_old_lifetime_budget_and_reconnects(self):
        master, thread, errors = self.persistent_worker()
        adapters = []
        def open_serial(deadline):
            adapter = PTYWebSocket(master)
            adapters.append(adapter)
            return SerialChannel(adapter, 'g6k-bridge164@pve!serial', 'SYNTHETIC-TICKET', deadline)
        self.lab.pve.open_serial = open_serial
        # One worker, one PTY, distinct channels/requests. More than64KiB of
        # authenticated input; no fresh advertisement injected by the fixture.
        for number in range(140):
            request_id = f'{number + 1:032x}'
            answer = self.lab.call(request_id=request_id)
            self.assertEqual(answer['result'], 'REPORTED', (number, errors))
            self.lab.receipt(request_id)
        self.assertGreater(sum(a.sent_bytes for a in adapters), 65536)
        self.assertEqual(len(self.lab.inspector.calls), 140)
        self.assertTrue(thread.is_alive())
        self.assertEqual(errors, [])

    def test_attachment_at_every_fixed_beacon_boundary_and_retained_beacons(self):
        master, thread, errors = self.persistent_worker()
        for cut in range(len(BEACON)):
            # Retain a cut beacon followed by old complete beacons. The actual
            # fresh challenge response still comes from the persistent worker.
            prefix = b'starting serial terminal on interface serial0\r\n' + BEACON[cut:] + BEACON * 3
            def open_serial(deadline):
                return SerialChannel(PTYWebSocket(master, prefix),
                    'g6k-bridge164@pve!serial', 'SYNTHETIC-TICKET', deadline)
            self.lab.pve.open_serial = open_serial
            request_id = f'{cut + 1:032x}'
            answer = self.lab.call(request_id=request_id)
            self.assertEqual(answer['result'], 'REPORTED', (cut, errors))
            self.lab.receipt(request_id)
        self.assertTrue(thread.is_alive())
        self.assertEqual(errors, [])

    def test_more_than64_queued_beacons_before_fresh_sync_are_bounded_by_bytes(self):
        master, thread, errors = self.persistent_worker()
        prefix = b'starting serial terminal on interface serial0\n' + BEACON * 160
        self.lab.pve.open_serial = lambda d: SerialChannel(PTYWebSocket(master, prefix),
                'g6k-bridge164@pve!serial', 'SYNTHETIC-TICKET', d)
        answer = self.lab.call()
        self.assertEqual(answer['result'], 'REPORTED', errors)
        self.lab.receipt()
        self.assertEqual(self.lab.inspector.calls, ['kernel'])
        self.assertTrue(thread.is_alive())
        self.assertEqual(errors, [])

    def test_idle_output_backpressure_does_not_kill_or_reserve_worker(self):
        # Model an attached serial output with no reader using a filled pipe.
        read_fd, write_fd = os.pipe()
        input_read, input_write = os.pipe()
        os.set_blocking(write_fd, False)
        os.set_blocking(read_fd, False)
        os.set_blocking(input_read, False)
        fcntl.fcntl(write_fd, fcntl.F_SETPIPE_SZ, 4096)  # This fixture's own pipe only.
        while True:
            try:
                os.write(write_fd, BEACON * 64)
            except BlockingIOError:
                break
        stopped = threading.Event()
        errors = []
        def target():
            try:
                worker_loop(self.lab.worker, input_read, write_fd, stopped=stopped.is_set)
            except Exception as error:
                errors.append(type(error).__name__)
        thread = threading.Thread(target=target)
        thread.start()
        try:
            time.sleep(1.1)  # Exceeds the old one-second idle write deadline.
            self.assertTrue(thread.is_alive())
            self.assertEqual(self.lab.worker_ledger.conn.execute('SELECT count(*) FROM requests').fetchone(), (0,))
            self.assertEqual(errors, [])
            class PipeWebSocket:
                authenticated = False
                prefix = True
                def send(inner, data, deadline):
                    if not inner.authenticated:
                        inner.authenticated = True
                        return
                    marker, size, payload = data.split(b':', 2)
                    if marker != b'0' or len(payload) != int(size):
                        raise Refusal('TEST_TERMPROXY')
                    fd_write(input_write, payload, deadline)
                def receive(inner, deadline):
                    if inner.prefix:
                        inner.prefix = False
                        return b'OK'
                    return fd_read(read_fd, 4096, deadline)
                def close(inner): pass
            self.lab.pve.open_serial = lambda d: SerialChannel(PipeWebSocket(),
                    'g6k-bridge164@pve!serial', 'SYNTHETIC-TICKET', d)
            answer = self.lab.call()
            self.assertEqual(answer['result'], 'REPORTED', errors)
            self.lab.receipt()
            self.assertEqual(self.lab.inspector.calls, ['kernel'])
        finally:
            stopped.set()
            thread.join(1)
            for fd in (read_fd, write_fd, input_read, input_write):
                os.close(fd)

    def test_receipt_retains_operation_lock_against_real_contender(self):
        left, right = socket.socketpair()
        thread = threading.Thread(target=connection, args=(left, self.lab.broker),
                                  kwargs={'authorize': lambda c, g: os.getuid()})
        thread.start()
        try:
            right.sendall(self.lab.request() + b'\n')
            right.settimeout(2)
            answer = Lines(lambda d: right.recv(4096)).line(Deadline(2))
            self.assertEqual(answer['result'], 'REPORTED')
            # The server now waits for a receipt. Previously a contender could
            # acquire this lock and make the valid receipt fail BUSY.
            with self.assertRaises(Refusal):
                with self.lab.host_ledger.operation():
                    self.fail('request lock released before receipt')
            contender = self.lab.call(request_id='2' * 32)
            self.assertEqual(contender['result'], 'REJECTED')
            right.sendall(encode({'v': 1, 'type': 'receipt', 'request_id': '1' * 32}))
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(self.lab.host_ledger.conn.execute('SELECT state FROM requests').fetchall(), [('ACKED',)])
            self.assertEqual(self.lab.inspector.calls, ['kernel'])
        finally:
            right.close()
            thread.join(2)

    def test_stale_or_unsynchronized_ready_never_reserves_an_action(self):
        class Stream:
            def __init__(self, records): self.records = iter(records); self.sent = []
            def send(self, payload, deadline): self.sent.append(payload)
            def receive(self, deadline): return next(self.records)
            def close(self): pass
        request = json.loads(self.lab.request())
        stale = {'v': 1, 'type': 'synchronized', 'challenge': 'f' * 32,
                 'request_id': request['request_id'], 'ready': self.lab.worker.advertisement()}
        stream = Stream([b'OK' + BEACON, encode(stale)])
        channel = SerialChannel(stream, 'g6k-bridge164@pve!serial', 'SYNTHETIC-TICKET', Deadline())
        with self.assertRaises(Refusal):
            channel.synchronize(request, self.lab.grant, self.lab.grant['caller_uid'], '3' * 32, Deadline())
        self.assertEqual(self.lab.inspector.calls, [])
        # Only authentication and the non-executing hello were transmitted.
        self.assertEqual(len(stream.sent), 2)
        self.assertNotIn(b'"type":"inspect"', stream.sent[-1])

    def test_precheck_cannot_construct_or_read_real_transport_or_ledger(self):
        disabled = {**self.lab.grant, 'enabled': False}
        with patch('g6k_serial.runtime.HOST_STATE', self.lab.root), \
             patch('g6k_serial.runtime.read_checked', side_effect=AssertionError('NO_SECRET_READ')), \
             patch('g6k_serial.runtime.PVETransport', side_effect=AssertionError('NO_PVE_TRANSPORT')), \
             patch('g6k_serial.runtime.Ledger', side_effect=AssertionError('NO_STATE_OPEN')):
            broker = make_broker(disabled, lambda: None, precheck=True)
        self.assertIsNone(broker.ledger)
        self.assertIsInstance(broker.transport, DisabledTransport)
        for operation in (broker.transport.snapshot, broker.transport.open_serial):
            with self.assertRaises(Refusal): operation(Deadline())
        left, right = socket.socketpair()
        thread = threading.Thread(target=connection, args=(left, broker),
                                  kwargs={'authorize': lambda c, g: os.getuid(), 'precheck': True})
        thread.start()
        try:
            right.sendall(self.lab.request() + b'\n')
            right.settimeout(1)
            result = Lines(lambda d: right.recv(4096)).line(Deadline(1))
            self.assertEqual(result['result'], 'PRECHECK_AUTHENTICATED')
            self.assertEqual(result['caller_uid'], os.getuid())
            self.assertIs(result['transport_enabled'], False)
        finally:
            right.close()
            thread.join(2)


if __name__ == '__main__':
    unittest.main()

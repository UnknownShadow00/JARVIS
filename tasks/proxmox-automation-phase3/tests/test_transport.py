import base64
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import ssl
import struct
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from g6k_serial.protocol import Deadline, Refusal, TOKEN_ID, decode, encode
from g6k_serial.transport import (BASE, GETS, PVETransport, SerialChannel, WebSocket,
                                  Wire, http_body, http_head)
from support import Lab

SYNTHETIC_TOKEN = '12345678-1234-1234-1234-123456789abc'


def server_frame(payload, opcode=2, fin=True):
    header = (0x80 if fin else 0) | opcode
    if len(payload) < 126:
        return bytes((header, len(payload))) + payload
    return bytes((header, 126)) + struct.pack('!H', len(payload)) + payload


def client_frame(wire, deadline):
    first, second = wire.read(2, deadline)
    if not second & 128:
        raise AssertionError('Client WebSocket frame must be masked')
    length = second & 127
    if length == 126:
        length = struct.unpack('!H', wire.read(2, deadline))[0]
    mask = wire.read(4, deadline)
    payload = wire.read(length, deadline)
    return first & 15, bytes(b ^ mask[i % 4] for i, b in enumerate(payload))


class SimulatedPVE:
    """Real TLS over AF_UNIX socketpairs, synthetic management and guest state."""
    def __init__(self, lab, cert, key):
        self.lab = lab
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(cert, key)
        self.client_context = None
        self.threads = []
        self.requests = []
        self.errors = []
        self.corrupt_report = lambda value: value
        self.bad_handshake = False

    def dial(self, deadline):
        client, server = socket.socketpair()
        def peer():
            wire = None
            try:
                server.settimeout(3)
                wire = Wire(self.context.wrap_socket(server, server_side=True))
                raw = wire.until(b'\r\n\r\n', 16384, Deadline(3))
                lines = raw.decode('ascii').split('\r\n')
                method, path, version = lines[0].split(' ')
                headers = dict(line.split(': ', 1) for line in lines[1:])
                length = int(headers.get('Content-Length', '0'))
                body = wire.read(length, Deadline(3))
                self.requests.append((method, path.split('?')[0]))  # Never retain token/ticket values.
                if headers.get('Authorization') != 'PVEAPIToken=' + TOKEN_ID + '=' + SYNTHETIC_TOKEN:
                    raise AssertionError('Synthetic authentication mismatch')
                if path.startswith(BASE + '/vncwebsocket?'):
                    key = headers['Sec-WebSocket-Key']
                    expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
                    if self.bad_handshake:
                        expected = 'wrong'
                    wire.send(('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                               'Sec-WebSocket-Protocol: binary\r\nSec-WebSocket-Accept: ' + expected + '\r\n\r\n').encode(), Deadline(3))
                    if self.bad_handshake:
                        return
                    opcode, auth = client_frame(wire, Deadline(3))
                    if opcode != 2 or auth != (TOKEN_ID + ':SYNTHETIC-TICKET\n').encode():
                        raise AssertionError('Synthetic termproxy authentication mismatch')
                    advertisement = self.lab.worker.advertisement()
                    raw_ready = b'OKstarting serial terminal on interface serial0\r\n' + encode(advertisement)
                    # Split protocol auth and banner over independent WS messages.
                    wire.send(server_frame(raw_ready[:1]) + server_frame(raw_ready[1:17]) + server_frame(raw_ready[17:]), Deadline(3))
                    opcode, command = client_frame(wire, Deadline(3))
                    marker, size, payload = command.split(b':', 2)
                    if opcode != 2 or marker != b'0' or len(payload) != int(size):
                        raise AssertionError('Termproxy data framing mismatch')
                    report = self.lab.worker.process(decode(payload[:-1]))
                    report = self.corrupt_report(report)
                    raw_report = encode(report)
                    # Exercise RFC fragmentation and control-frame interleaving.
                    wire.send(server_frame(raw_report[:13], fin=False) + server_frame(b'ping', opcode=9) +
                              server_frame(raw_report[13:], opcode=0), Deadline(3))
                    opcode, pong = client_frame(wire, Deadline(3))
                    if opcode != 10 or pong != b'ping':
                        raise AssertionError('Pong mismatch')
                    return
                state = self.lab.pve.state
                if method == 'POST' and path == BASE + '/termproxy':
                    if body != b'serial=serial0':
                        raise AssertionError('Wrong channel')
                    value = {'user': TOKEN_ID, 'ticket': 'SYNTHETIC-TICKET', 'port': 5900,
                             'upid': 'OFFLINE-FIXTURE-NOT-PVE'}
                else:
                    table = {BASE + '/config?current=1': state['config'], BASE + '/status/current': state['status'],
                             BASE + '/pending': state['pending'], '/api2/json/access/permissions': state['permissions']}
                    value = table[path]
                payload = json.dumps({'data': value}, indent=2).encode()
                # Real chunked response parser, split across two chunks.
                split = len(payload) // 2
                chunks = payload[:split], payload[split:]
                encoded = b''.join(f'{len(chunk):x}\r\n'.encode() + chunk + b'\r\n' for chunk in chunks)
                wire.send(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n' + encoded + b'0\r\n\r\n', Deadline(3))
            except (BrokenPipeError, ConnectionResetError, ssl.SSLError):
                # Negative TLS tests deliberately close before authentication.
                pass
            except Exception as error:
                self.errors.append(type(error).__name__)
            finally:
                if wire:
                    wire.close()
                else:
                    server.close()
        thread = threading.Thread(target=peer)
        thread.start()
        self.threads.append(thread)
        client.settimeout(deadline.remaining())
        return Wire(self.client_context.wrap_socket(client, server_hostname='pve'))

    def join(self):
        for thread in self.threads:
            thread.join(4)


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which('openssl') is None:
            raise RuntimeError('Offline TLS validation requires existing openssl; do not install it automatically')
        cls.temp = tempfile.TemporaryDirectory(prefix='g6k-synthetic-tls-')
        cls.cert = Path(cls.temp.name) / 'ca.pem'
        cls.key = Path(cls.temp.name) / 'key.pem'
        result = subprocess.run(['openssl', 'req', '-x509', '-newkey', 'ed25519', '-nodes', '-days', '1',
                                 '-subj', '/CN=pve', '-addext', 'subjectAltName=DNS:pve',
                                 '-keyout', str(cls.key), '-out', str(cls.cert)], capture_output=True, timeout=10)
        if result.returncode:
            raise RuntimeError('Synthetic certificate generation failed')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lab = Lab()
        self.addCleanup(self.lab.close)
        ca = self.cert.read_bytes()
        self.lab.grant['ca_sha256'] = hashlib.sha256(ca).hexdigest()
        self.peer = SimulatedPVE(self.lab, self.cert, self.key)
        self.transport = PVETransport({'id': TOKEN_ID, 'secret': SYNTHETIC_TOKEN}, ca, self.lab.grant, dial=self.peer.dial)
        self.peer.client_context = self.transport.context
        self.addCleanup(self.peer.join)

    def test_full_broker_real_tls_http_websocket_termproxy_worker_exchange(self):
        self.lab.broker.transport = self.transport
        answer = self.lab.call()
        self.assertEqual(answer['result'], 'REPORTED')
        self.lab.receipt()
        self.peer.join()
        self.assertEqual(self.peer.errors, [])
        self.assertEqual(len(self.peer.requests), 10)
        self.assertEqual(sum(method == 'POST' for method, _ in self.peer.requests), 1)
        self.assertTrue(all('/qemu/' not in path or '/qemu/164/' in path for _, path in self.peer.requests))
        self.assertEqual(self.lab.inspector.calls, ['kernel'])

    def test_api_paths_cannot_address_guest_exec_other_guests_or_hosts(self):
        for method, path, body in [('POST', BASE + '/agent/exec', b'command=id'),
                                    ('GET', '/api2/json/nodes/pve/qemu/163/config', b''),
                                    ('GET', '/api2/json/nodes/pve/qemu/162/config', b''),
                                    ('GET', 'https://ai-server/', b''),
                                    ('POST', BASE + '/termproxy', b'serial=serial1'),
                                    ('POST', BASE + '/status/reboot', b'')]:
            with self.subTest(path=path), self.assertRaises(Refusal):
                self.transport._request(method, path, Deadline(), body)
        self.assertEqual(self.peer.requests, [])

    def test_wrong_websocket_accept_refuses_before_worker_action(self):
        self.peer.bad_handshake = True
        with self.assertRaises(Refusal):
            self.transport.open_serial(Deadline())
        self.assertEqual(self.lab.inspector.calls, [])

    def test_untrusted_tls_peer_certificate_rejected(self):
        self.peer.client_context = ssl.create_default_context()
        with self.assertRaises(ssl.SSLCertVerificationError):
            self.transport.snapshot(Deadline())
        self.assertEqual(self.peer.requests, [])

    def test_ca_pin_and_token_identity_do_not_accept_substitutions(self):
        ca = self.cert.read_bytes()
        for credential in ({'id': 'root@pam!admin', 'secret': SYNTHETIC_TOKEN},
                           {'id': TOKEN_ID, 'secret': SYNTHETIC_TOKEN + '\r\nAuthorization: evil'},
                           {'id': TOKEN_ID, 'secret': SYNTHETIC_TOKEN, 'root_password': 'fake'}):
            with self.subTest(keys=list(credential)), self.assertRaises(Refusal):
                PVETransport(credential, ca, self.lab.grant)
        with self.assertRaises(Refusal):
            PVETransport({'id': TOKEN_ID, 'secret': SYNTHETIC_TOKEN}, ca + b' ', self.lab.grant)

    def test_transport_abort_blocks_all_new_connections(self):
        self.transport.abort()
        with self.assertRaises(Refusal):
            self.transport.snapshot(Deadline())
        self.assertEqual(self.peer.requests, [])

    def test_transport_abort_closes_already_open_channel(self):
        left, right = socket.socketpair()
        wire = self.transport._register(Wire(left))
        finished = threading.Event()
        errors = []
        def waiting():
            try:
                wire.read(1, Deadline(2))
            except (OSError, Refusal):
                errors.append('CLOSED')
            finally:
                finished.set()
        thread = threading.Thread(target=waiting)
        thread.start()
        try:
            self.transport.abort()
            self.assertTrue(finished.wait(1))
            self.assertEqual(errors, ['CLOSED'])
        finally:
            right.close()
            thread.join(2)

    def test_http_duplicate_ambiguous_length_and_size_abuse(self):
        for raw in (b'HTTP/1.1 200 OK\r\nX: a\r\nX: b\r\n\r\n',
                    b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\n',
                    b'HTTP/1.1 200 OK\r\nBad Header: x\r\n\r\n'):
            left, right = socket.socketpair()
            try:
                right.sendall(raw)
                with self.assertRaises(Refusal):
                    http_head(Wire(left), Deadline(1))
            finally:
                left.close(); right.close()
        left, right = socket.socketpair()
        try:
            for headers in ({'content-length': '1', 'transfer-encoding': 'chunked'},
                            {'content-length': '9999999'}, {'content-length': '-1'},
                            {'transfer-encoding': 'gzip'}, {}):
                with self.subTest(headers=headers), self.assertRaises(Refusal):
                    http_body(Wire(left), headers, Deadline(1))
        finally:
            left.close(); right.close()

    def test_websocket_fragment_mask_control_and_size_abuse(self):
        frames = [b'\xc2\x00', b'\x82\x80', b'\x89\x7e\x00\x7e',
                  b'\x80\x00', b'\x83\x00', b'\x82\x7e\xff\xff',
                  b'\x82\x7f' + struct.pack('!Q', 2**63),
                  server_frame(b'\xff', opcode=1), server_frame(b'', opcode=8)]
        for frame in frames:
            left, right = socket.socketpair()
            try:
                right.sendall(frame)
                with self.subTest(frame=frame[:10]), self.assertRaises(Refusal):
                    WebSocket(Wire(left)).receive(Deadline(1))
            finally:
                left.close(); right.close()

    def test_proxy_banner_allowlist_never_skips_login_or_kernel_noise(self):
        class FakeWS:
            def __init__(self, payload): self.payload = payload
            def send(self, data, deadline): pass
            def receive(self, deadline): return self.payload
            def close(self): pass
        for noise in (b'login: \n', b'root@host#\n', b'\x1b[2J\n', b'[ 0.2] Linux\n',
                      b'starting serial terminal on interface serial1\n'):
            ws = FakeWS(b'OK' + noise)
            channel = SerialChannel(ws, TOKEN_ID, 'SYNTHETIC-TICKET', Deadline())
            with self.subTest(noise=noise), self.assertRaises(Refusal):
                channel.receive(Deadline())

    def test_socket_absolute_timeout_is_not_extended_by_trickled_bytes(self):
        left, right = socket.socketpair()
        stop = threading.Event()
        def trickle():
            while not stop.wait(0.02):
                try:
                    right.send(b'a')
                except OSError:
                    break
        thread = threading.Thread(target=trickle)
        thread.start()
        started = time.monotonic()
        try:
            with self.assertRaises((Refusal, TimeoutError)):
                Wire(left).until(b'\n', 1000, Deadline(0.12))
            self.assertLess(time.monotonic() - started, 0.5)
        finally:
            stop.set(); thread.join(); left.close(); right.close()


if __name__ == '__main__':
    unittest.main()

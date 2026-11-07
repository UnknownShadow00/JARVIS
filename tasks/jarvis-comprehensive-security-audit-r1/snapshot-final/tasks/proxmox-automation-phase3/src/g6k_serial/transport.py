"""Pinned TLS + bounded HTTP/WebSocket + Proxmox termproxy framing.

No import-time connections. No caller-provided URLs, ports, serial bytes or API
methods. The only management POST creates VM164's serial0 proxy, never exec.
"""
import base64
import hashlib
import os
import re
import socket
import ssl
import struct
import threading
from urllib.parse import urlencode

from .policy import token
from .protocol import (FRAME_BYTES, TOKEN_ID, Refusal, Lines, decode, encode, exact_dict, need)

ADDRESS = ('192.168.0.50', 8006)
SERVER_NAME = 'pve'
BASE = '/api2/json/nodes/pve/qemu/164'
GETS = frozenset((BASE + '/config?current=1', BASE + '/status/current', BASE + '/pending',
                  '/api2/json/access/permissions'))
MAX_HTTP = 1024 * 1024
MAX_HEADERS = 16384


class Wire:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = bytearray()
        self.on_close = lambda: None

    def close(self):
        try:
            self.sock.close()
        finally:
            self.on_close()

    def send(self, data, deadline):
        while data:
            self.sock.settimeout(deadline.remaining())
            sent = self.sock.send(data)
            need(sent > 0, 'CHANNEL')
            data = data[sent:]

    def read(self, size, deadline):
        need(0 <= size <= MAX_HTTP + MAX_HEADERS, 'READ_SIZE')
        while len(self.buffer) < size:
            self.sock.settimeout(deadline.remaining())
            chunk = self.sock.recv(min(8192, size - len(self.buffer)))
            need(bool(chunk), 'CHANNEL')
            self.buffer.extend(chunk)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def until(self, delimiter, limit, deadline):
        while delimiter not in self.buffer:
            need(len(self.buffer) < limit, 'HEADER_SIZE')
            self.sock.settimeout(deadline.remaining())
            chunk = self.sock.recv(min(4096, limit - len(self.buffer)))
            need(bool(chunk), 'CHANNEL')
            self.buffer.extend(chunk)
        pos = self.buffer.index(delimiter)
        need(pos + len(delimiter) <= limit, 'HEADER_SIZE')
        result = bytes(self.buffer[:pos])
        del self.buffer[:pos + len(delimiter)]
        return result


def http_head(wire, deadline):
    raw = wire.until(b'\r\n\r\n', MAX_HEADERS, deadline)
    need(all(b in (10, 13) or 32 <= b < 127 for b in raw), 'HTTP_ENCODING')
    lines = raw.decode('ascii').split('\r\n')
    need(re.fullmatch(r'HTTP/1\.[01] [0-9]{3}(?: [ -~]*)?', lines[0]), 'HTTP_STATUS')
    status = int(lines[0].split(' ')[1])
    headers = {}
    for line in lines[1:]:
        name, colon, value = line.partition(':')
        need(colon and re.fullmatch('[A-Za-z0-9-]+', name), 'HTTP_HEADER')
        name = name.lower()
        need(name not in headers, 'HTTP_DUPLICATE_HEADER')
        headers[name] = value.strip()
    need(headers.get('content-encoding', 'identity') == 'identity', 'HTTP_ENCODING')
    return status, headers


def http_body(wire, headers, deadline):
    need(not ('content-length' in headers and 'transfer-encoding' in headers), 'HTTP_LENGTH')
    if 'content-length' in headers:
        length = headers['content-length']
        need(re.fullmatch('[0-9]{1,7}', length) and int(length) <= MAX_HTTP, 'HTTP_LENGTH')
        return wire.read(int(length), deadline)
    need(headers.get('transfer-encoding') == 'chunked', 'HTTP_LENGTH')
    result = bytearray()
    for _ in range(1024):
        raw_length = wire.until(b'\r\n', 32, deadline)
        need(re.fullmatch(b'[0-9a-fA-F]{1,8}', raw_length), 'HTTP_CHUNK')
        length = int(raw_length, 16)
        if length == 0:
            need(wire.read(2, deadline) == b'\r\n', 'HTTP_TRAILER')
            return bytes(result)
        need(length <= MAX_HTTP - len(result), 'HTTP_LENGTH')
        result.extend(wire.read(length, deadline))
        need(wire.read(2, deadline) == b'\r\n', 'HTTP_CHUNK')
    raise Refusal('HTTP_CHUNKS')


class WebSocket:
    """RFC6455 client; bounded fragmentation/control frames; no extensions."""
    def __init__(self, wire):
        self.wire = wire
        self.budget = 65536

    def send(self, payload, deadline, opcode=2):
        need(len(payload) <= FRAME_BYTES, 'WS_SIZE')
        mask = os.urandom(4)
        length = len(payload)
        header = bytes((0x80 | opcode, 0x80 | length)) if length < 126 else bytes((0x80 | opcode, 0xFE)) + struct.pack('!H', length)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.wire.send(header + mask + masked, deadline)

    def receive(self, deadline):
        result = bytearray()
        in_fragment = False
        text = False
        for _ in range(128):
            first, second = self.wire.read(2, deadline)
            fin, opcode = bool(first & 0x80), first & 15
            need(not first & 0x70 and not second & 0x80, 'WS_FLAGS')
            length = second & 127
            if length == 126:
                length = struct.unpack('!H', self.wire.read(2, deadline))[0]
                need(length >= 126, 'WS_LENGTH')
            elif length == 127:
                length = struct.unpack('!Q', self.wire.read(8, deadline))[0]
                need(length >= 65536, 'WS_LENGTH')
            need(length <= min(FRAME_BYTES, self.budget), 'WS_SIZE')
            if opcode >= 8:
                need(fin and length <= 125 and opcode in (8, 9, 10), 'WS_CONTROL')
            data = self.wire.read(length, deadline)
            self.budget -= length + 2
            need(self.budget >= 0, 'WS_BUDGET')
            if opcode == 8:
                raise Refusal('WS_CLOSED')
            if opcode in (9, 10):
                if opcode == 9:
                    self.send(data, deadline, opcode=10)
                continue
            need(opcode in (0, 1, 2), 'WS_OPCODE')
            need((opcode == 0) == in_fragment, 'WS_FRAGMENT')
            if opcode in (1, 2):
                text = opcode == 1
            result.extend(data)
            need(len(result) <= FRAME_BYTES, 'WS_SIZE')
            if fin:
                if text:
                    try:
                        bytes(result).decode('utf-8')
                    except UnicodeError:
                        raise Refusal('WS_ENCODING') from None
                return bytes(result)
            in_fragment = True
        raise Refusal('WS_FRAME_COUNT')

    def close(self):
        # Closing TLS tears down the proxy; never transmit terminal control bytes.
        self.wire.close()


class SerialChannel:
    def __init__(self, websocket, username, ticket, deadline):
        self.websocket = websocket
        need(type(username) is str and re.fullmatch('[A-Za-z0-9@!._-]{1,128}', username), 'PROXY_USER')
        need(type(ticket) is str and re.fullmatch('[!-~]{1,4096}', ticket), 'PROXY_TICKET')
        websocket.send((username + ':' + ticket + '\n').encode('ascii'), deadline)
        answer = bytearray()
        while len(answer) < 2:
            answer.extend(websocket.receive(deadline))
            need(len(answer) <= FRAME_BYTES, 'AUTH_SIZE')
        need(answer[:2] == b'OK', 'PROXY_AUTH')
        self.initial = bytes(answer[2:])
        self.lines = Lines(self._receive)
        self.first = True

    def _receive(self, deadline):
        if self.initial:
            result, self.initial = self.initial, b''
            return result
        return self.websocket.receive(deadline)

    def receive(self, deadline):
        raw = self.lines.raw_line(deadline)
        if self.first:
            self.first = False
            # qm terminal --escape 0 emits this exact public startup line.
            # Never scan past arbitrary prompts, errors, kernel text or ANSI.
            if raw in (b'starting serial terminal on interface serial0',
                       b'starting serial terminal on interface serial0\r'):
                raw = self.lines.raw_line(deadline)
        return decode(raw)

    def send(self, value, deadline):
        # No raw serial send exposed to the broker's untrusted local client.
        data = encode(value)
        self.websocket.send(b'0:' + str(len(data)).encode() + b':' + data, deadline)

    def close(self):
        self.websocket.close()


class PVETransport:
    def __init__(self, credential, ca_bytes, grant, *, dial=None):
        token(credential)
        need(hashlib.sha256(ca_bytes).hexdigest() == grant['ca_sha256'], 'TLS_CA_PIN')
        self.authorization = 'PVEAPIToken=' + TOKEN_ID + '=' + credential['secret']
        self.context = ssl.create_default_context(cadata=ca_bytes.decode('ascii'))
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self._dial_override = dial  # Only direct dependency injection in offline tests.
        self._guard = threading.Lock()
        self._wires = set()
        self._aborted = False

    def abort(self):
        with self._guard:
            self._aborted = True
            wires = list(self._wires)
        for wire in wires:
            try:
                wire.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            wire.close()

    def _register(self, wire):
        def remove():
            with self._guard:
                self._wires.discard(wire)
        with self._guard:
            aborted = self._aborted
            if not aborted:
                wire.on_close = remove
                self._wires.add(wire)
        if aborted:
            wire.close()
            raise Refusal('REVOKED')
        return wire

    def _dial(self, deadline):
        with self._guard:
            need(not self._aborted, 'REVOKED')
        if self._dial_override is not None:
            return self._register(self._dial_override(deadline))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(deadline.remaining())
            sock.connect(ADDRESS)
            sock.settimeout(deadline.remaining())
            return self._register(Wire(self.context.wrap_socket(sock, server_hostname=SERVER_NAME)))
        except BaseException:
            sock.close()
            raise Refusal('TLS_CONNECTION') from None

    def _request(self, method, path, deadline, body=b''):
        need((method == 'GET' and path in GETS and not body) or
             (method == 'POST' and path == BASE + '/termproxy' and body == b'serial=serial0'), 'API_SCOPE')
        wire = self._dial(deadline)
        try:
            request = (method + ' ' + path + ' HTTP/1.1\r\nHost: pve:8006\r\nAuthorization: ' +
                       self.authorization + '\r\nAccept-Encoding: identity\r\nConnection: close\r\n' +
                       'Content-Type: application/x-www-form-urlencoded\r\nContent-Length: ' + str(len(body)) + '\r\n\r\n').encode('ascii')
            wire.send(request + body, deadline)
            status, headers = http_head(wire, deadline)
            need(status == 200, 'API_RESPONSE')
            # Management JSON may contain formatting whitespace. Strip only JSON
            # structural whitespace before strict decoding, never guest frames.
            raw = http_body(wire, headers, deadline)
            import json
            from .protocol import _pairs
            try:
                value = json.loads(raw, object_pairs_hook=_pairs,
                                   parse_constant=lambda _: (_ for _ in ()).throw(Refusal('JSON_CONSTANT')))
            except (ValueError, RecursionError):
                raise Refusal('API_JSON') from None
            need(type(value) is dict and 'data' in value, 'API_JSON')
            return value['data']
        finally:
            wire.close()

    def snapshot(self, deadline):
        return {'config': self._request('GET', BASE + '/config?current=1', deadline),
                'status': self._request('GET', BASE + '/status/current', deadline),
                'pending': self._request('GET', BASE + '/pending', deadline),
                'permissions': self._request('GET', '/api2/json/access/permissions', deadline)}

    def open_serial(self, deadline):
        proxy = self._request('POST', BASE + '/termproxy', deadline, b'serial=serial0')
        need(type(proxy) is dict and set(proxy) == {'user', 'ticket', 'port', 'upid'}, 'PROXY_SCHEMA')
        need(type(proxy['port']) is int and 5900 <= proxy['port'] <= 5999, 'PROXY_PORT')
        need(proxy['user'] == TOKEN_ID, 'PROXY_USER')
        need(type(proxy['ticket']) is str and re.fullmatch('[!-~]{1,4096}', proxy['ticket']), 'PROXY_TICKET')
        path = BASE + '/vncwebsocket?' + urlencode({'port': proxy['port'], 'vncticket': proxy['ticket']})
        wire = self._dial(deadline)
        try:
            key = base64.b64encode(os.urandom(16)).decode('ascii')
            request = ('GET ' + path + ' HTTP/1.1\r\nHost: pve:8006\r\nAuthorization: ' + self.authorization +
                       '\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Version: 13\r\n' +
                       'Sec-WebSocket-Protocol: binary\r\nSec-WebSocket-Key: ' + key + '\r\n\r\n').encode('ascii')
            wire.send(request, deadline)
            status, headers = http_head(wire, deadline)
            expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            need(status == 101 and headers.get('upgrade', '').lower() == 'websocket' and
                 'upgrade' in {v.strip().lower() for v in headers.get('connection', '').split(',')} and
                 headers.get('sec-websocket-accept') == expected and
                 headers.get('sec-websocket-protocol') == 'binary' and
                 'sec-websocket-extensions' not in headers, 'WS_HANDSHAKE')
            return SerialChannel(WebSocket(wire), proxy['user'], proxy['ticket'], deadline)
        except BaseException:
            wire.close()
            raise Refusal('SERIAL_CONNECTION') from None

"""Offline only: dummy files, AF_UNIX fake peers, and guarded ASGI fixtures."""
import base64
import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import socket
import stat
import threading
import time
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location(
    "human_gate5", Path(__file__).with_name("HUMAN-ONLY-GATE5-AUTH.py"))
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)  # Import never calls main or the private loader.
REAL_PRIVATE_LOADER = helper._load_private_credential
DUMMY = b"OFFLINE_DUMMY_ONLY_0123456789_abcdef"


@pytest.fixture(autouse=True)
def never_read_production(monkeypatch):
    def denied():
        raise AssertionError("PRIVATE_LOADER_FORBIDDEN_IN_TESTS")
    monkeypatch.setattr(helper, "_load_private_credential", denied)


def recv_until(sock, ending):
    data = bytearray()
    while not data.endswith(ending):
        part = sock.recv(1)
        if not part:
            break
        data.extend(part)
    return bytes(data)


@contextlib.contextmanager
def peers(monkeypatch, *, rest=404, ws=101, fault=None, token=DUMMY):
    # Real AF_UNIX socketpairs, created BEFORE replacing the INET constructor.
    pairs = [socket.socketpair(), socket.socketpair()]
    threads = []
    seen = {"requests": [], "frames": [], "destinations": [], "errors": []}

    def serve(peer):
        try:
            peer.settimeout(1)
            request = recv_until(peer, b"\r\n\r\n")
            seen["requests"].append(request)
            authorized = b"Authorization: Bearer " + DUMMY + b"\r\n" in request
            if request.startswith(b"GET /gate5-auth-inspection "):
                status = rest if authorized else 401
                if fault == "rest_timeout":
                    return
                extra = b"Location: http://example.invalid/secret\r\n" if status == 302 else b""
                if fault == "oversized":
                    peer.sendall(b"HTTP/1.1 404 Not Found\r\nX-Large: " + b"x" * 8300)
                    return
                if fault == "bad_status":
                    peer.sendall(b"INVALID " + DUMMY + b"\r\n\r\n")
                    return
                peer.sendall(b"HTTP/1.1 " + str(status).encode() + b" Result\r\n" +
                             extra + b"Content-Length: 0\r\n\r\n")
                return
            assert request.startswith(b"GET /ws HTTP/1.1\r\n")
            if not authorized or ws != 101:
                peer.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")
                return
            key = next(line.split(b": ", 1)[1] for line in request.split(b"\r\n")
                       if line.startswith(b"Sec-WebSocket-Key:"))
            accept = base64.b64encode(hashlib.sha1(
                key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
            if fault == "bad_accept":
                accept = DUMMY
            extra = b"Sec-WebSocket-Extensions: permessage-deflate\r\n" if fault == "extension" else b""
            if fault == "duplicate_accept":
                extra = b"Sec-WebSocket-Accept: " + accept + b"\r\n"
            peer.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                         b"Connection: Upgrade\r\nSec-WebSocket-Accept: " + accept + b"\r\n" + extra + b"\r\n")
            frame = b""
            while len(frame) < 8:
                data = peer.recv(8 - len(frame))
                if not data:
                    break
                frame += data
            if frame:
                seen["frames"].append(frame)
                response = b"\x88\x02\x03\xe8"
                if fault == "application_frame":
                    response = b"\x81\x02xx"
                if fault == "ping":
                    response = b"\x89\x02xx"
                if fault == "wrong_close":
                    response = b"\x88\x02\x03\xf0"
                if fault == "ws_timeout":
                    return
                peer.sendall(response)
                assert peer.recv(1) == b""  # No data/pong/reconnect after close.
        except (BrokenPipeError, ConnectionResetError):
            pass  # Expected rejection closes transport without any retry.
        except BaseException as exc:
            seen["errors"].append(type(exc).__name__)
        finally:
            peer.close()

    class Client:
        def __init__(self, index):
            self.sock, self.peer = pairs[index]

        def __enter__(self):
            return self

        def __exit__(self, *unused):
            self.sock.close()

        def connect(self, destination):
            assert destination == ("127.0.0.1", 8000)
            seen["destinations"].append(destination)
            thread = threading.Thread(target=serve, args=(self.peer,))
            threads.append(thread)
            thread.start()

        def settimeout(self, timeout):
            assert 0 < timeout <= 5
            self.sock.settimeout(min(timeout, 0.1))

        def sendall(self, data):
            self.sock.sendall(data)

        def recv(self, size):
            return self.sock.recv(size)

    index = 0

    def factory(family, kind):
        nonlocal index
        assert (family, kind) == (socket.AF_INET, socket.SOCK_STREAM)
        result = Client(index)
        index += 1
        return result

    with monkeypatch.context() as patch:
        patch.setattr(socket, "socket", factory)
        # Raw sockets must not resolve DNS or use environment proxy values.
        patch.setattr(socket, "getaddrinfo", lambda *a: pytest.fail("DNS_FORBIDDEN"))
        patch.setenv("HTTP_PROXY", "http://example.invalid:9999")
        patch.setenv("ALL_PROXY", "http://example.invalid:9999")
        patch.setenv("JARVIS_API_TOKEN", "ENVIRONMENT_TOKEN_MUST_NOT_BE_USED")
        try:
            yield seen, lambda: helper._checks(token)
        finally:
            for client, peer in pairs:
                client.close()
            for thread in threads:
                thread.join(2)
                assert not thread.is_alive()
            for client, peer in pairs:
                peer.close()


def test_exact_positive_wire_and_no_frames_or_proxy(monkeypatch, capsys):
    with peers(monkeypatch) as (seen, run):
        assert run() == ("REST=PASS_404 WS=PASS_101_CLOSE_1000", 0)
    assert not seen["errors"]
    assert len(seen["requests"]) == len(seen["destinations"]) == 2
    assert seen["requests"][0].count(b"GET ") == 1
    assert seen["requests"][0].endswith(b"\r\n\r\n")
    assert b"Content-Length" not in seen["requests"][0]
    assert b"?" not in seen["requests"][0].split(b"\r\n")[0]
    assert b"?" not in seen["requests"][1].split(b"\r\n")[0]
    assert len(seen["frames"]) == 1
    frame = seen["frames"][0]
    assert frame[:2] == b"\x88\x82" and len(frame) == 8
    assert bytes(frame[6 + i] ^ frame[2 + i] for i in range(2)) == b"\x03\xe8"
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("status", [200, 301, 302, 307, 308, 401, 403, 423, 500])
def test_rest_failure_prevents_ws_and_redirect_retry(monkeypatch, status):
    with peers(monkeypatch, rest=status) as (seen, run):
        assert run() == ("REST=FAIL WS=NOT_RUN", 1)
    assert len(seen["requests"]) == len(seen["destinations"]) == 1
    assert not seen["frames"]


def test_wrong_dummy_credential_rejected_without_ws(monkeypatch):
    with peers(monkeypatch, token=b"WRONG_DUMMY_ONLY_0123456789_abcdef") as (seen, run):
        assert run() == ("REST=FAIL WS=NOT_RUN", 1)
    assert len(seen["requests"]) == 1


@pytest.mark.parametrize("fault", ["rest_timeout", "oversized", "bad_status"])
def test_bad_rest_responses_sanitized(monkeypatch, fault, capsys):
    with peers(monkeypatch, fault=fault) as (seen, run):
        assert run() == ("REST=FAIL WS=NOT_RUN", 1)
    assert len(seen["requests"]) == 1
    assert DUMMY.decode() not in str(capsys.readouterr())


@pytest.mark.parametrize("fault", ["bad_accept", "extension", "duplicate_accept",
                                       "application_frame", "ping", "wrong_close", "ws_timeout"])
def test_ws_failures_no_reconnect_or_pong(monkeypatch, fault, capsys):
    with peers(monkeypatch, fault=fault) as (seen, run):
        assert run() == ("REST=PASS_404 WS=FAIL", 1)
    assert len(seen["requests"]) == len(seen["destinations"]) == 2
    assert len(seen["frames"]) <= 1
    assert DUMMY.decode() not in str(capsys.readouterr())


def test_ws_auth_denial_sanitized(monkeypatch):
    with peers(monkeypatch, ws=403) as (seen, run):
        assert run() == ("REST=PASS_404 WS=FAIL", 1)
    assert not seen["frames"]


@pytest.mark.parametrize("quote", [b"", b"'", b'"'])
def test_dummy_file_safe_parsing(tmp_path, quote):
    p = tmp_path / "p7-b2.env"
    p.write_bytes(b"JARVIS_API_TOKEN=" + quote + DUMMY + quote + b"\n")
    p.chmod(0o600)
    fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        assert helper._credential_from_directory(fd, identity=helper._identity(p.lstat())) == DUMMY
    finally:
        os.close(fd)


@pytest.mark.parametrize("raw", [b"", b"JARVIS_API_TOKEN=short\n", b"x" * 4097,
    b"JARVIS_API_TOKEN=" + DUMMY + b"\nOTHER=x\n",
    b"JARVIS_API_TOKEN=" + DUMMY + b"\r\nInjected: value\n",
    b"JARVIS_API_TOKEN=\"$(cat private)\"\n",
    b"JARVIS_API_TOKEN=" + DUMMY + b"\xff\n",
    b"JARVIS_API_TOKEN=" + DUMMY + b"=bad\n"])
def test_malformed_input_no_value_in_exception(tmp_path, raw):
    p = tmp_path / "p7-b2.env"
    p.write_bytes(raw)
    p.chmod(0o600)
    fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(ValueError, match="^LOCAL_REFUSAL$"):
            helper._credential_from_directory(fd, identity=helper._identity(p.lstat()))
    finally:
        os.close(fd)


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "fifo", "permissions", "directory"])
def test_unsafe_file_metadata_refused(tmp_path, kind):
    p = tmp_path / "p7-b2.env"
    if kind == "symlink":
        p.symlink_to(tmp_path / "dummy")
    elif kind == "fifo":
        os.mkfifo(p, 0o600)
    elif kind == "directory":
        p.mkdir(mode=0o600)
    else:
        p.write_bytes(b"JARVIS_API_TOKEN=" + DUMMY)
        p.chmod(0o600 if kind == "hardlink" else 0o640)
        if kind == "hardlink":
            os.link(p, tmp_path / "other")
    fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises((ValueError, OSError)):
            helper._credential_from_directory(fd, identity=helper._identity(p.lstat()))
    finally:
        os.close(fd)


def test_symlink_private_directory_refused(tmp_path):
    (tmp_path / "real").mkdir(mode=0o700)
    (tmp_path / "jarvis").symlink_to(tmp_path / "real")
    fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(OSError):
            helper._directory(fd, "jarvis", private=True)
    finally:
        os.close(fd)


@pytest.mark.parametrize("stage", ["REST", "WS"])
def test_exceptions_never_render_secrets(monkeypatch, stage, capsys):
    def explode(*args):
        raise RuntimeError("Authorization: Bearer " + DUMMY.decode())
    monkeypatch.setattr(helper, "_rest", explode if stage == "REST" else lambda token: None)
    monkeypatch.setattr(helper, "_websocket", explode)
    result, code = helper._checks(DUMMY)
    assert code == 1 and DUMMY.decode() not in result
    assert capsys.readouterr() == ("", "")


def test_deadline_expires_before_io():
    class NoIO:
        def settimeout(self, value):
            pytest.fail("IO_AFTER_DEADLINE")
    with pytest.raises(ValueError, match="LOCAL_REFUSAL"):
        helper._timeout(NoIO(), 0)


def test_cli_arguments_refused_before_credential_access(monkeypatch, capsys):
    monkeypatch.setattr(helper.resource, "setrlimit", lambda *a: None)
    monkeypatch.setattr(helper.sys, "argv", ["helper", "http://example.invalid"])
    assert helper.main() == 1
    assert capsys.readouterr().out == "REST=NOT_RUN WS=NOT_RUN LOCAL=REFUSED\n"


@pytest.mark.parametrize("substitution", [None, "private_directory", "credential", "config_directory"])
def test_complete_loader_with_dummy_root_and_identity_pins(tmp_path, monkeypatch, substitution):
    root = tmp_path / 'root'
    config = root / 'home/jarvis/.config'
    private = config / 'jarvis'
    private.mkdir(parents=True)
    for parent in (root, root / 'home', root / 'home/jarvis'):
        parent.chmod(0o755)
    config.chmod(0o775)
    private.chmod(0o700)
    p = private / 'p7-b2.env'
    p.write_bytes(b'JARVIS_API_TOKEN=' + DUMMY + b'\n')
    p.chmod(0o600)
    monkeypatch.setattr(helper, 'CONFIG_DIRECTORY_ID', (config.stat().st_dev, config.stat().st_ino))
    monkeypatch.setattr(helper, 'PRIVATE_DIRECTORY_ID', helper._identity(private.stat()))
    monkeypatch.setattr(helper, 'CREDENTIAL_ID', helper._identity(p.stat()))
    if substitution == 'private_directory':
        monkeypatch.setattr(helper, 'PRIVATE_DIRECTORY_ID', (0, 0, 0, 0))
    if substitution == 'credential':
        monkeypatch.setattr(helper, 'CREDENTIAL_ID', (0, 0, 0, 0))
    if substitution == 'config_directory':
        monkeypatch.setattr(helper, 'CONFIG_DIRECTORY_ID', (0, 0))
    real_open, real_fstat = os.open, os.fstat
    fds, opened = {}, []

    def fixture_open(name, flags, *, dir_fd=None):
        path = root if name == '/' and dir_fd is None else fds[dir_fd] / name
        assert path == root or root in path.parents
        assert flags & os.O_NOFOLLOW
        fd = real_open(path, flags)
        fds[fd] = path
        opened.append(path)
        return fd

    def fixture_stat(fd):
        info = real_fstat(fd)
        if fds.get(fd) in (root, root / 'home'):
            # Fixture files cannot be owned by root; simulate only those two UIDs.
            return SimpleNamespace(st_uid=0, st_mode=info.st_mode)
        return info

    monkeypatch.setattr(os, 'open', fixture_open)
    monkeypatch.setattr(os, 'fstat', fixture_stat)
    if substitution:
        with pytest.raises(ValueError, match='LOCAL_REFUSAL'):
            REAL_PRIVATE_LOADER()
    else:
        assert REAL_PRIVATE_LOADER() == DUMMY
        assert opened[-1] == p
        assert len(opened) == 6


def test_actual_timeout_exception_is_sanitized(monkeypatch, capsys):
    class TimeoutSocket:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def settimeout(self, value): assert 0 < value <= 5
        def connect(self, address): assert address == ('127.0.0.1', 8000)
        def sendall(self, data): pass
        def recv(self, size): raise socket.timeout(DUMMY.decode())
    count = []
    def factory(*args):
        count.append(1)
        return TimeoutSocket()
    monkeypatch.setattr(socket, 'socket', factory)
    assert helper._checks(DUMMY) == ('REST=FAIL WS=NOT_RUN', 1)
    assert len(count) == 1 and capsys.readouterr() == ('', '')


def test_cumulative_deadline_blocks_slow_drip(monkeypatch):
    class Drip:
        def settimeout(self, value): pass
        def recv(self, size): return b'x'
    ticks = iter([1, 2, 6])
    monkeypatch.setattr(helper.time, 'monotonic', lambda: next(ticks))
    with pytest.raises(ValueError, match='LOCAL_REFUSAL'):
        helper._read(Drip(), 3, 5)


@pytest.mark.parametrize('bad', ['uid', 'gid', 'xattr', 'race'])
def test_credential_metadata_and_read_race_refused(tmp_path, monkeypatch, bad):
    p = tmp_path / 'p7-b2.env'
    p.write_bytes(b'JARVIS_API_TOKEN=' + DUMMY)
    p.chmod(0o600)
    identity = helper._identity(p.stat())
    fd = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    actual = os.fstat
    calls = []
    def altered(n):
        s = actual(n)
        values = {key: getattr(s, key) for key in ['st_dev', 'st_ino', 'st_uid', 'st_gid',
                  'st_nlink', 'st_mode', 'st_size', 'st_mtime_ns', 'st_ctime_ns']}
        calls.append(n)
        if bad in ('uid', 'gid'): values['st_' + bad] = 999
        if bad == 'race' and len(calls) > 1: values['st_mtime_ns'] += 1
        return SimpleNamespace(**values)
    monkeypatch.setattr(os, 'fstat', altered)
    if bad == 'xattr': monkeypatch.setattr(os, 'listxattr', lambda n: ['system.posix_acl_access'])
    try:
        with pytest.raises(ValueError, match='LOCAL_REFUSAL'):
            helper._credential_from_directory(fd, identity=identity)
    finally:
        os.close(fd)


@pytest.mark.parametrize('condition', ['success', 'malformed', 'wrong_host', 'no_tty', 'no_ack', 'interrupted'])
def test_human_boundary_and_status_only_output(monkeypatch, condition):
    class Terminal(io.StringIO):
        def isatty(self): return condition != 'no_tty'
    stdin = Terminal('RUN GATE5 NO-MESSAGE CHECKS\n' if condition != 'no_ack' else 'no\n')
    stdout, stderr = Terminal(), Terminal()
    monkeypatch.setattr(helper.sys, 'stdin', stdin)
    monkeypatch.setattr(helper.sys, 'stdout', stdout)
    monkeypatch.setattr(helper.sys, 'stderr', stderr)
    monkeypatch.setattr(helper.sys, 'argv', ['helper'])
    monkeypatch.setattr(helper.resource, 'setrlimit', lambda *args: None)
    monkeypatch.setattr(helper.os, 'getuid', lambda: 1000)
    monkeypatch.setattr(helper.os, 'geteuid', lambda: 1000)
    monkeypatch.setattr(helper.socket, 'gethostname', lambda: 'jarvis' if condition != 'wrong_host' else 'nexus-services')
    reads, checks = [], []
    def dummy_loader():
        reads.append(1)
        if condition == 'malformed': raise ValueError(DUMMY.decode())
        return DUMMY
    def dummy_checks(token):
        assert token == DUMMY
        checks.append(1)
        if condition == 'interrupted': raise KeyboardInterrupt(DUMMY.decode())
        return 'REST=PASS_404 WS=PASS_101_CLOSE_1000', 0
    monkeypatch.setattr(helper, '_load_private_credential', dummy_loader)
    monkeypatch.setattr(helper, '_checks', dummy_checks)
    assert helper.main() == (0 if condition == 'success' else 1)
    assert DUMMY.decode() not in stdout.getvalue() + stderr.getvalue()
    assert not stderr.getvalue()
    assert len(reads) == (1 if condition in ('success', 'malformed', 'interrupted') else 0)
    assert len(checks) == (1 if condition in ('success', 'interrupted') else 0)
    if condition == 'interrupted':
        assert 'REST=UNKNOWN WS=UNKNOWN LOCAL=REFUSED' in stdout.getvalue()


def test_real_deployed_asgi_positive_and_negative_contract(tmp_path, monkeypatch):
    # Existing fixture builds a private PILOT controller with fake model transports.
    from tests.execution.shadow_pilot_server_test import pilot_server_fixture
    from tests.execution.shadow_pilot_test import rows
    auth = {"Authorization": "Bearer test-secret"}
    with pilot_server_fixture(tmp_path, monkeypatch, admissions_open=False) as (
            client, server, fake, legacy, spoken):
        rt = server._shadow_runtime
        before = rt.driver.owner.snapshot()
        assert client.get('/gate5-auth-inspection', headers=auth).status_code == 404
        with client.websocket_connect('/ws', headers=auth):
            pass
        assert rt.driver.stop_reason is None
        assert rt.driver.admission_fence.state.value == "PILOT_ADMISSION_CLOSED"
        assert rt.driver._accepted == 0 and not fake and not spoken
        assert legacy.await_count == 0 and rt.driver.owner.snapshot() == before
        for table in ('attempts', 'attempt_events', 'submissions', 'receipt_joins', 'pilot_events'):
            assert rows(tmp_path, 'SELECT count(*) FROM ' + table) == [(0,)]
        assert not list((tmp_path / 'data').rglob('*.jsonl'))
        assert client.get('/gate5-auth-inspection', headers={
            'Authorization': 'Bearer wrong-dummy'}).status_code == 401
        assert rt.driver.stop_reason == "AUTHENTICATION_MISMATCH"
        assert not rt.driver.admission_fence.allows_conversation()
        assert rt.driver._accepted == 0 and not fake


def test_real_uvicorn_wire_protocol_over_private_unix_socket(tmp_path, monkeypatch):
    """Exercise the installed production protocol engine without any TCP socket."""
    import uvicorn
    path = str(tmp_path / 'offline.sock')
    events = []

    async def app(scope, receive, send):
        assert dict(scope['headers']).get(b'authorization') == b'Bearer ' + DUMMY
        if scope['type'] == 'http':
            assert scope['method'] == 'GET' and scope['path'] == '/gate5-auth-inspection'
            assert not scope['query_string']
            events.append('REST')
            await send({'type': 'http.response.start', 'status': 404,
                        'headers': [(b'content-length', b'0')]})
            await send({'type': 'http.response.body', 'body': b''})
        else:
            assert scope['type'] == 'websocket' and scope['path'] == '/ws'
            assert (await receive())['type'] == 'websocket.connect'
            events.append('WS')
            await send({'type': 'websocket.accept'})
            message = await receive()
            assert message['type'] == 'websocket.disconnect' and message['code'] == 1000
            events.append('CLOSE_1000_NO_APPLICATION_FRAME')

    config = uvicorn.Config(app, uds=path, lifespan='off', loop='asyncio',
                            access_log=False, log_config=None, log_level='critical')
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()
    original = socket.socket
    connections = []

    class UnixClient:
        def __init__(self, family, kind):
            assert (family, kind) == (socket.AF_INET, socket.SOCK_STREAM)
            self.sock = original(socket.AF_UNIX, socket.SOCK_STREAM)
        def __enter__(self): return self
        def __exit__(self, *args): self.sock.close()
        def __getattr__(self, name): return getattr(self.sock, name)
        def connect(self, address):
            assert address == ('127.0.0.1', 8000)
            connections.append(address)
            self.sock.connect(path)
    try:
        deadline = time.monotonic() + 3
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        monkeypatch.setattr(helper, 'socket', SimpleNamespace(
            socket=UnixClient, AF_INET=socket.AF_INET, SOCK_STREAM=socket.SOCK_STREAM))
        assert helper._checks(DUMMY) == ('REST=PASS_404 WS=PASS_101_CLOSE_1000', 0)
    finally:
        server.should_exit = True
        thread.join(5)
        assert not thread.is_alive()
    assert len(connections) == 2
    assert events == ['REST', 'WS', 'CLOSE_1000_NO_APPLICATION_FRAME']

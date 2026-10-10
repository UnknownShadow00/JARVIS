#!/usr/bin/python3
"""Human-only, one-shot Gate 5 checks. NEVER run with the real file from Codex.

Review the procedure and SHA256 first. No arguments, environment configuration,
URL options, imports from JARVIS, retries, redirects, or application WS frames.
"""
import base64
import hashlib
import os
import re
import resource
import socket
import stat
import sys
import time

sys.dont_write_bytecode = True
# Nonsecret stat identities from this reviewed deployment; never token hashes.
CONFIG_DIRECTORY_ID = (64512, 2892909)
PRIVATE_DIRECTORY_ID = (64512, 2892922, 1791516329346331909, 1791516329346331909)
CREDENTIAL_ID = (64512, 2922135, 1791516329347490558, 1791516329347490558)


def _identity(info):
    return info.st_dev, info.st_ino, info.st_mtime_ns, info.st_ctime_ns


def _require(condition):
    if not condition:
        raise ValueError("LOCAL_REFUSAL")


def _directory(parent, name, private=False):
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                 dir_fd=parent)
    try:
        info = os.fstat(fd)
        _require(info.st_uid == (1000 if private else 0))
        _require(stat.S_IMODE(info.st_mode) == 0o700 if private
                 else not info.st_mode & 0o022)
        _require(not any(x in os.listxattr(fd) for x in
                         ("system.posix_acl_access", "system.posix_acl_default")))
        return fd
    except BaseException:
        os.close(fd)
        raise


def _credential_from_directory(directory, *, identity):
    # This function is exercised ONLY with dummy private directories in tests.
    fd = os.open("p7-b2.env", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                 dir_fd=directory)
    raw = bytearray()
    try:
        info = os.fstat(fd)
        _require(_identity(info) == identity)
        _require(stat.S_ISREG(info.st_mode) and info.st_uid == 1000
                 and info.st_gid == 1000 and info.st_nlink == 1
                 and stat.S_IMODE(info.st_mode) == 0o600)
        _require(not os.listxattr(fd))
        _require(0 < info.st_size <= 4096)
        while len(raw) <= 4096:
            chunk = os.read(fd, 4097 - len(raw))
            if not chunk:
                break
            raw.extend(chunk)
        after = os.fstat(fd)
        _require(len(raw) == info.st_size and
                 (info.st_size, info.st_mtime_ns, info.st_ctime_ns) ==
                 (after.st_size, after.st_mtime_ns, after.st_ctime_ns))
        # Deliberately narrower than systemd's env syntax. No eval or unescaping.
        match = re.fullmatch(
            rb'JARVIS_API_TOKEN=(?:([A-Za-z0-9._~+/=-]{32,512})|'
            rb'"([A-Za-z0-9._~+/=-]{32,512})"|'
            rb"'([A-Za-z0-9._~+/=-]{32,512})')\n?", raw)
        _require(match is not None)
        token = next(value for value in match.groups() if value is not None)
        _require(re.fullmatch(rb'[A-Za-z0-9._~+/-]+=*', token) is not None)
        return token
    finally:
        raw[:] = b"\0" * len(raw)
        os.close(fd)


def _load_private_credential():
    # Fixed chain; every component is opened without following symlinks.
    fds = []
    try:
        fds.append(_directory(None, "/"))
        fds.append(_directory(fds[-1], "home"))
        # The existing .config is0775. Pin it and the private child instead of
        # trusting a replaceable name or changing production permissions.
        for name in ("jarvis", ".config"):
            fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                         dir_fd=fds[-1])
            fds.append(fd)
            info = os.fstat(fd)
            _require(info.st_uid == 1000 and info.st_gid == 1000)
            if name == "jarvis":
                _require(not info.st_mode & 0o022)
            else:
                _require((info.st_dev, info.st_ino) == CONFIG_DIRECTORY_ID
                         and stat.S_IMODE(info.st_mode) == 0o775)
            _require(not any(x.startswith("system.posix_acl_")
                             for x in os.listxattr(fd)))
        fds.append(_directory(fds[-1], "jarvis", private=True))
        _require(_identity(os.fstat(fds[-1])) == PRIVATE_DIRECTORY_ID)
        return _credential_from_directory(fds[-1], identity=CREDENTIAL_ID)
    finally:
        for fd in reversed(fds):
            os.close(fd)


def _timeout(sock, deadline):
    remaining = deadline - time.monotonic()
    _require(remaining > 0)
    sock.settimeout(remaining)


def _read(sock, size, deadline):
    result = bytearray()
    while len(result) < size:
        _timeout(sock, deadline)
        part = sock.recv(size - len(result))
        _require(bool(part))
        result.extend(part)
    return bytes(result)


def _headers(sock, deadline):
    raw = bytearray()
    while not raw.endswith(b"\r\n\r\n"):
        _require(len(raw) < 8192)
        raw.extend(_read(sock, 1, deadline))
    lines = bytes(raw).split(b"\r\n")
    status = re.fullmatch(rb"HTTP/1\.1 ([0-9]{3}) [\x20-\x7e]*", lines[0])
    _require(status is not None)
    fields = {}
    for line in lines[1:-2]:
        name, value = line.split(b":", 1)
        _require(re.fullmatch(rb"[A-Za-z0-9-]+", name) is not None)
        name = name.lower()
        _require(name not in fields)
        fields[name] = value.strip().lower() if name in (b"upgrade", b"connection") else value.strip()
    return int(status[1]), fields


def _rest(token):
    deadline = time.monotonic() + 5
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        _timeout(sock, deadline)
        sock.connect(("127.0.0.1", 8000))
        _timeout(sock, deadline)
        sock.sendall(b"GET /gate5-auth-inspection HTTP/1.1\r\n"
                     b"Host: 127.0.0.1:8000\r\nAuthorization: Bearer " + token +
                     b"\r\nConnection: close\r\n\r\n")
        status, _ = _headers(sock, deadline)
        _require(status == 404)


def _websocket(token):
    deadline = time.monotonic() + 5
    nonce = base64.b64encode(os.urandom(16))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        _timeout(sock, deadline)
        sock.connect(("127.0.0.1", 8000))
        _timeout(sock, deadline)
        sock.sendall(b"GET /ws HTTP/1.1\r\nHost: 127.0.0.1:8000\r\n"
                     b"Authorization: Bearer " + token +
                     b"\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                     b"Sec-WebSocket-Version: 13\r\nSec-WebSocket-Key: " + nonce + b"\r\n\r\n")
        status, fields = _headers(sock, deadline)
        # SHA1 is solely the public WebSocket nonce proof, NEVER a token hash.
        expected = base64.b64encode(hashlib.sha1(
            nonce + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
        _require(status == 101 and fields.get(b"upgrade") == b"websocket"
                 and b"upgrade" in fields.get(b"connection", b"").split(b",")
                 and fields.get(b"sec-websocket-accept") == expected
                 and b"sec-websocket-extensions" not in fields
                 and b"sec-websocket-protocol" not in fields)
        mask = os.urandom(4)
        payload = b"\x03\xe8"  # Normal close1000, no reason or application data.
        _timeout(sock, deadline)
        sock.sendall(b"\x88\x82" + mask +
                     bytes(value ^ mask[i] for i, value in enumerate(payload)))
        # Require the exact normal-close echo; never answer ping or data frames.
        _require(_read(sock, 4, deadline) == b"\x88\x02\x03\xe8")


def _checks(token):
    try:
        _rest(token)
    except BaseException:
        return "REST=FAIL WS=NOT_RUN", 1
    try:
        _websocket(token)
    except BaseException:
        return "REST=PASS_404 WS=FAIL", 1
    return "REST=PASS_404 WS=PASS_101_CLOSE_1000", 0


def main():
    token = None
    started = False
    try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        _require(len(sys.argv) == 1 and os.getuid() == 1000 and os.geteuid() == 1000
                 and socket.gethostname() == "jarvis"
                 and all(stream.isatty() for stream in (sys.stdin, sys.stdout, sys.stderr)))
        # Human acknowledgement only. Never prompt for or accept a token.
        print("Type RUN GATE5 NO-MESSAGE CHECKS after completing the private preflight:")
        _require(sys.stdin.readline(80) == "RUN GATE5 NO-MESSAGE CHECKS\n")
        token = _load_private_credential()
        started = True
        result, code = _checks(token)
    except BaseException:
        result = ("REST=UNKNOWN WS=UNKNOWN LOCAL=REFUSED" if started
                  else "REST=NOT_RUN WS=NOT_RUN LOCAL=REFUSED")
        code = 1
    finally:
        token = None  # Python cannot guarantee erasure of immutable copies.
    print(result)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

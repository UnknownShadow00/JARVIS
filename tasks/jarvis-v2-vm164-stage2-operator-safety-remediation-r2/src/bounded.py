"""Bounded file/stream primitives; never opens a host path at import time."""
import zlib
import gzip
import io
import os
import stat
import time
from common import need, integer, digest, sha

MAX_INPUT = 32*1024*1024
MAX_OUTPUT = 8*1024*1024

def tick(deadline, clock=time.monotonic):
    need(type(deadline) in (int, float) and clock() < deadline, 'read deadline exceeded')

def read_stream(stream, limit, deadline, *, expected_size=None, clock=time.monotonic):
    integer(limit, 1, MAX_INPUT)
    if expected_size is not None:
        integer(expected_size, 0, limit)
    chunks = []
    total = 0
    try:
        while True:
            tick(deadline, clock)
            chunk = stream.read(min(65536, limit + 1 - total))
            need(type(chunk) is bytes, 'partial or invalid stream read')
            if not chunk:
                break
            total += len(chunk)
            need(total <= limit, 'input oversized')
            chunks.append(chunk)
        tick(deadline, clock)
        need(expected_size is None or total == expected_size, 'truncated or changed input')
        return b''.join(chunks)
    except MemoryError:
        raise ValueError('BLOCKED: allocation failure') from None

def identity(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            s.st_uid, s.st_gid, s.st_mode, s.st_nlink)

def read_fd(fd, limit, deadline, *, owner=0, expected_sha=None, clock=time.monotonic):
    integer(limit, 1, MAX_INPUT)
    before = os.fstat(fd)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'single-link regular file required')
    need(before.st_uid == owner and (owner != 0 or before.st_gid == 0) and not before.st_mode & 0o022, 'file custody')
    integer(before.st_size, 0, limit)  # before any data allocation
    with os.fdopen(os.dup(fd), 'rb', closefd=True) as stream:
        data = read_stream(stream, limit, deadline, expected_size=before.st_size, clock=clock)
    need(identity(before) == identity(os.fstat(fd)), 'file changed during read')
    if expected_sha is not None:
        need(sha(data) == digest(expected_sha), 'source digest mismatch')
    return data

def open_protected(path):
    """Every component no-follow, root-owned and nonwritable. Caller closes FD."""
    need(type(path) is str and path.startswith('/') and len(path) <= 4096, 'absolute path')
    parts = path.split('/')[1:]
    need(parts and all(p not in ('', '.', '..') for p in parts), 'canonical path')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            s = os.fstat(fd)
            need(s.st_uid == s.st_gid == 0 and not s.st_mode & 0o022, 'ancestor custody')
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        s = os.fstat(fd)
        need(s.st_uid == s.st_gid == 0 and not s.st_mode & 0o022, 'ancestor custody')
        return os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=fd)
    finally:
        os.close(fd)

def read_protected(path, limit, deadline, expected_sha=None):
    fd = open_protected(path)
    try:
        return read_fd(fd, limit, deadline, expected_sha=expected_sha)
    finally:
        os.close(fd)

def gunzip_bounded(raw, limit, deadline, *, clock=time.monotonic):
    """CRC/trailer validation through bounded GzipFile reads, including all members."""
    integer(limit, 1, MAX_OUTPUT)
    need(type(raw) is bytes and 18 <= len(raw) <= 1024*1024, 'compressed input bound')
    # Concatenated valid members are allowed only within the aggregate limits.
    limit = min(limit, len(raw)*128)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode='rb') as stream:
            return read_stream(stream, limit, deadline, clock=clock)
    except (OSError, EOFError, MemoryError, zlib.error) as exc:
        raise ValueError('BLOCKED: invalid compressed input') from None

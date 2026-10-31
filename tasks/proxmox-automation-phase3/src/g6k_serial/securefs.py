"""Descriptor-relative ownership checks; production anchors at filesystem root."""
import hashlib
import os
from pathlib import Path
import stat

from .protocol import Refusal, need


def open_checked(path, owners, *, mode=None, directory=False, anchor=Path('/')):
    path, anchor = Path(path), Path(anchor)
    need(path.is_absolute() and '..' not in path.parts, 'PATH')
    try:
        parts = path.relative_to(anchor).parts
    except ValueError:
        raise Refusal('PATH') from None
    fd = os.open(anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        initial = os.fstat(fd)
        need(initial.st_uid in owners and not initial.st_mode & 0o022, 'PARENT_OWNER')
        for index, part in enumerate(parts):
            last = index == len(parts) - 1
            flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
            if not last or directory:
                flags |= os.O_DIRECTORY
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
            current = os.fstat(fd)
            need(current.st_uid in owners and not current.st_mode & 0o022, 'FILE_OWNER')
            if last and not directory:
                need(stat.S_ISREG(current.st_mode) and current.st_nlink == 1, 'FILE_TYPE')
                need(mode is None or stat.S_IMODE(current.st_mode) == mode, 'FILE_MODE')
        result, fd = fd, -1
        return result
    except OSError:
        raise Refusal('PROTECTED_PATH') from None
    finally:
        if fd >= 0:
            os.close(fd)


def read_checked(path, owners=frozenset((0,)), *, mode=None, limit=65536, anchor=Path('/')):
    fd = open_checked(path, owners, mode=mode, anchor=anchor)
    try:
        raw = bytearray()
        while len(raw) <= limit:
            chunk = os.read(fd, min(8192, limit + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        need(len(raw) <= limit, 'FILE_SIZE')
        return bytes(raw)
    finally:
        os.close(fd)


SOURCE_FILES = ('entry.py', 'g6k_serial/__init__.py', 'g6k_serial/protocol.py',
                'g6k_serial/securefs.py', 'g6k_serial/policy.py', 'g6k_serial/journal.py',
                'g6k_serial/worker.py', 'g6k_serial/broker.py', 'g6k_serial/transport.py',
                'g6k_serial/runtime.py', 'g6k_serial/provision.py')
SOURCE_FILES += ('g6k_serial/hardening.py',)


def verify_release(root, expected, *, owners=frozenset((0,)), anchor=Path('/')):
    root = Path(root)
    need(set(os.listdir(root)) == {'entry.py', 'g6k_serial', 'SOURCE-SHA256SUMS'}, 'SOURCE_EXTRAS')
    need(set(os.listdir(root / 'g6k_serial')) == {
        name.split('/')[1] for name in SOURCE_FILES if name.startswith('g6k_serial/')}, 'SOURCE_EXTRAS')
    raw = read_checked(root / 'SOURCE-SHA256SUMS', owners, limit=8192, anchor=anchor)
    need(hashlib.sha256(raw).hexdigest() == expected, 'SOURCE_MANIFEST')
    lines = raw.decode('ascii').splitlines()
    need(len(lines) == len(SOURCE_FILES), 'SOURCE_MANIFEST')
    for name, line in zip(SOURCE_FILES, lines):
        digest, separator, recorded = line.partition('  ')
        need(separator == '  ' and recorded == name and len(digest) == 64, 'SOURCE_MANIFEST')
        content = read_checked(root / name, owners, limit=1024 * 1024, anchor=anchor)
        need(hashlib.sha256(content).hexdigest() == digest, 'SOURCE_DRIFT')

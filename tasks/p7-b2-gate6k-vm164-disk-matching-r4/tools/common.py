"""Pinned local public inputs only. No private infrastructure access."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess

TASK = Path(__file__).resolve().parents[1]
WORKSPACE = TASK.parent.parent
OLD_TASK = TASK.parent / 'p7-b2-gate6k-vm164-provisioning-r1'
OLD_BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1')
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-installer-r4')
R3 = OLD_BUILD / 'ubuntu-26.04.1-g6k-vm164-r3.iso'
R3_SHA = '4161509164bcaff08506ad2ffcd52a6782eb34eb4b08d47f1bb8754016a07346'
SNAP = OLD_BUILD / 'subiquity_7403.snap'
SNAP_SHA = 'ee9467fec724cf2a7f4fc61641a4a05d84f7730f06b8fefaceaf0b51a9a0331b'


def sha(path, algorithm='sha256'):
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('UNSAFE_PUBLIC_FILE')
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def require_hash(path, expected):
    if sha(path) != expected:
        raise ValueError('PUBLIC_INPUT_HASH_MISMATCH: ' + str(path))


def snap_source(path):
    require_hash(SNAP, SNAP_SHA)
    return subprocess.run(['unsquashfs', '-cat', str(SNAP), path],
                          capture_output=True, check=True, timeout=30).stdout


def old_iso_tools():
    path = OLD_TASK / 'tools/verify_derivative.py'
    spec = importlib.util.spec_from_file_location('retained_iso_verifier', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.tree, module.load_iso_reader()


def extract_iso_file(iso, wanted):
    _, entries = old_iso_tools()
    parts = wanted.strip('/').split('/')
    with iso.open('rb') as stream:
        stream.seek(16 * 2048)
        pvd = stream.read(2048)
        if pvd[:7] != b'\x01CD001\x01':
            raise ValueError('ISO_DESCRIPTOR')
        record = pvd[156:190]
        for part in parts:
            record = entries(stream, record)[part]
        length = int.from_bytes(record[10:14], 'little')
        if length > 2_000_000:
            raise ValueError('SMALL_ISO_FILE_LIMIT')
        stream.seek(int.from_bytes(record[2:6], 'little') * 2048)
        data = stream.read(length)
        if len(data) != length:
            raise ValueError('TRUNCATED_ISO')
        return data

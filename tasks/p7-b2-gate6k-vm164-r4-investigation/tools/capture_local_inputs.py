"""Read only retained public files; write only this investigation's evidence.

No ISO construction, mount, device command, SSH, network, or installer execution.
Existing evidence must match byte-for-byte; it is never overwritten.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

PACKET = Path(__file__).resolve().parents[1]
PREVIOUS = PACKET.parent / 'p7-b2-gate6k-vm164-disk-matching-r4'
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-installer-r4')
SNAP = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1/subiquity_7403.snap')


def digest(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('UNSAFE_LOCAL_INPUT')
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def retain(path, data):
    if path.exists():
        if path.is_symlink() or path.read_bytes() != data:
            raise RuntimeError('EVIDENCE_ALREADY_EXISTS_WITH_DIFFERENT_CONTENT')
    else:
        with path.open('xb') as stream:
            stream.write(data)


def main():
    # Authenticate prior packet before reusing its read-only ISO parser.
    seal = PREVIOUS.with_suffix('.seal').read_text().split()[0]
    assert digest(PREVIOUS / 'SHA256SUMS') == seal
    prior = []
    for line in (PREVIOUS / 'SHA256SUMS').read_text().splitlines():
        expected, rel = line.split('  ', 1)
        path = PREVIOUS / rel
        assert path.resolve().is_relative_to(PREVIOUS.resolve())
        assert digest(path) == expected, rel
        prior.append({'path': str(path), 'sha256': expected})
    assert digest(SNAP) == 'ee9467fec724cf2a7f4fc61641a4a05d84f7730f06b8fefaceaf0b51a9a0331b'
    iso = BUILD / 'ubuntu-26.04.1-g6k-vm164-r4.iso'
    assert digest(iso) == '050875e2f3ffd5a7711bb2f520bce98404416d2117faedf2ba608831e2a416f3'
    parser = PREVIOUS.parent / 'p7-b2-gate6k-vm164-provisioning-r1/tools/verify_derivative.py'
    # The helper is used only for parsing directory records, never main().
    oldsum = PREVIOUS.parent / 'p7-b2-gate6k-vm164-provisioning-r1/SHA256SUMS'
    matching = [line.split('  ', 1)[0] for line in oldsum.read_text().splitlines()
                if line.endswith('  tools/verify_derivative.py')]
    oldseal = oldsum.parent.with_suffix('.seal').read_text().split()[0]
    assert digest(oldsum) == oldseal
    assert matching == [digest(parser)]
    spec = importlib.util.spec_from_file_location('retained_iso_parser', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _, entries = module.tree, module.load_iso_reader()
    records = []
    with iso.open('rb') as stream:
        stream.seek(16 * 2048)
        pvd = stream.read(2048)
        assert pvd[:7] == b'\x01CD001\x01'
        for wanted in ('autoinstall.yaml', 'g6k-disk-guard-r4.py', 'boot/grub/grub.cfg'):
            record = pvd[156:190]
            for part in wanted.split('/'):
                record = entries(stream, record)[part]
            length = int.from_bytes(record[10:14], 'little')
            assert length < 2_000_000
            stream.seek(int.from_bytes(record[2:6], 'little') * 2048)
            data = stream.read(length)
            assert len(data) == length
            dest = PACKET / 'evidence' / wanted.replace('/', '-')
            retain(dest, data)
            records.append({'iso_path': '/' + wanted, 'retained_path': str(dest),
                            'sha256': hashlib.sha256(data).hexdigest()})
    assert (PACKET / 'evidence/autoinstall.yaml').read_bytes() == (BUILD / 'autoinstall-r4.yaml').read_bytes()
    assert (PACKET / 'evidence/g6k-disk-guard-r4.py').read_bytes() == (PREVIOUS / 'tools/disk_guard_r4.py').read_bytes()
    # Complete exact pinned source capture by re-reading all recorded snap paths.
    source_record = json.loads((PACKET / 'evidence/source-record.json').read_text())
    additional = {'boot.py': 'subiquity/common/filesystem/boot.py',
                  'manipulator.py': 'subiquity/common/filesystem/manipulator.py'}
    names = {r['retained_path'] for r in source_record['files']}
    for name, rel in additional.items():
        retained = 'evidence/pinned-source/' + name
        if retained not in names:
            source_record['files'].append({'snap_path': 'lib/python3.12/site-packages/' + rel,
                                          'retained_path': retained})
    for record in source_record['files']:
        data = subprocess.run(['unsquashfs', '-cat', str(SNAP), record['snap_path']],
                              capture_output=True, check=True, timeout=30).stdout
        actual = hashlib.sha256(data).hexdigest()
        assert record.get('sha256', actual) == actual
        retain(PACKET / record['retained_path'], data)
        record['sha256'] = actual
    # This index is extended once; previously retained SOURCE BYTES stay immutable.
    (PACKET / 'evidence/source-record.json').write_text(json.dumps(source_record, indent=2) + '\n')
    result = {'status': 'PASS_LOCAL_PINNED_INPUTS', 'r4_iso_sha256': digest(iso),
              'subiquity_snap_sha256': digest(SNAP), 'prior_manifest_sha256': seal,
              'prior_files': prior, 'iso_files': records,
              'snap_source_files': len(source_record['files']),
              'live_boot_media_verified': False,
              'vm_access': 'NONE', 'new_iso': 'NONE'}
    retain(PACKET / 'evidence/local-input-verification.json',
           (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps({k: v for k, v in result.items() if k not in ('prior_files', 'iso_files')}))


if __name__ == '__main__':
    main()

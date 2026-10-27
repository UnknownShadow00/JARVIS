"""Verify previous public staging and write nonbootable offline transport ISO."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

TASK = Path(__file__).resolve().parents[1]
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1')
PUBLIC = Path('/home/nexus/.local/share/jarvis-g6k-clean-replacement')
MANIFEST_SHA = '922b82cec3076e01577e410ac68c2d74f92d7d74f1886e215b1f83ed75ae1341'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    manifest = PUBLIC / 'PUBLIC-INPUTS-SHA256SUMS'
    if sha(manifest) != MANIFEST_SHA:
        raise ValueError('PREVIOUS_PUBLIC_MANIFEST_PIN')
    rows = {}
    for line in manifest.read_text().splitlines():
        expected, name = line.split('  ', 1)
        if Path(name).is_absolute() or '..' in Path(name).parts or name in rows:
            raise ValueError('PUBLIC_MANIFEST_PATH')
        path = PUBLIC / name
        if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1 or sha(path) != expected:
            raise ValueError('PUBLIC_INPUT_MISMATCH')
        rows[name] = expected
    expected_names = set(rows) | {manifest.name}
    actual = {str(p.relative_to(PUBLIC)) for p in PUBLIC.rglob('*') if not p.is_dir() or p.is_symlink()}
    if len(rows) != 139 or actual != expected_names:
        raise ValueError('PUBLIC_TRANSPORT_INVENTORY')
    output = BUILD / 'g6k-public-inputs-r1.iso'
    if output.exists():
        raise ValueError('EXISTING_PUBLIC_ISO')
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(BUILD),
           'LD_LIBRARY_PATH': str(BUILD / 'iso-tool/root/usr/lib/x86_64-linux-gnu')}
    with (TASK / 'evidence/public-iso-build.txt').open('x') as log:
        subprocess.run([str(BUILD / 'iso-tool/root/usr/bin/xorriso'), '-outdev', str(output),
                        '-volid', 'G6K_PUBLIC_INPUTS_R1', '-map', str(PUBLIC), '/', '-commit', '-end'],
                       env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
    # Independent extent reader verifies EVERY embedded payload against external pins.
    import sys
    sys.path.insert(0, str(TASK / 'tools'))
    from verify_derivative import tree, load_iso_reader
    embedded = tree(output, load_iso_reader())
    if set(embedded) != expected_names or embedded[manifest.name]['sha256'] != MANIFEST_SHA:
        raise ValueError('PUBLIC_ISO_INVENTORY')
    if any(embedded[name]['sha256'] != value for name, value in rows.items()):
        raise ValueError('PUBLIC_ISO_CONTENT')
    result = {'status': 'PASS_140_EMBEDDED_PUBLIC_FILES', 'path': str(output), 'sha256': sha(output),
              'bytes': output.stat().st_size, 'transport_manifest_sha256': MANIFEST_SHA,
              'public_input_files': len(rows), 'credentials_or_vm163_runtime_inputs': 'NONE',
              'bootable': False, 'guest_transfer': 'NOT_PERFORMED'}
    with (TASK / 'evidence/public-payload-iso.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

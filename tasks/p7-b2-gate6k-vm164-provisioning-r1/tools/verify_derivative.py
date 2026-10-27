"""Read-only ISO content comparison and literal schemas from the ISO-pinned installer."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import yaml
import jsonschema

TASK = Path(__file__).resolve().parents[1]
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1')
ORIGINAL = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/artifacts/os/ubuntu-26.04.1-live-server-amd64.iso')
REVISION = 'r3'


def load_iso_reader():
    path = TASK.parent / 'p7-b2-gate6k-clean-replacement/tools/inspect_iso.py'
    spec = importlib.util.spec_from_file_location('existing_pinned_iso_reader', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.entries


def tree(path, entries):
    result = {}
    with path.open('rb') as stream:
        stream.seek(16 * 2048)
        pvd = stream.read(2048)
        if pvd[:7] != b'\x01CD001\x01':
            raise ValueError('ISO_PRIMARY_DESCRIPTOR')
        def walk(record, prefix='', depth=0):
            if depth > 16:
                raise ValueError('ISO_DEPTH')
            for name, child in entries(stream, record).items():
                if '/' in name or name in ('.', '..'):
                    raise ValueError('ISO_NAME')
                full = prefix + name
                if child[25] & 2:
                    walk(child, full + '/', depth + 1)
                else:
                    offset = int.from_bytes(child[2:6], 'little') * 2048
                    length = int.from_bytes(child[10:14], 'little')
                    if child[25] & 128:
                        raise ValueError('MULTIEXTENT_UNSUPPORTED')
                    stream.seek(offset)
                    h = hashlib.sha256()
                    remaining = length
                    while remaining:
                        chunk = stream.read(min(remaining, 1024 * 1024))
                        if not chunk:
                            raise ValueError('TRUNCATED_ISO_FILE')
                        h.update(chunk)
                        remaining -= len(chunk)
                    result[full] = {'bytes': length, 'sha256': h.hexdigest()}
        walk(pvd[156:190])
    return result


def main():
    record = json.loads((TASK / f'evidence/derivative-iso-{REVISION}.json').read_text())
    destination = Path(record['path'])
    entries = load_iso_reader()
    before, after = tree(ORIGINAL, entries), tree(destination, entries)
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(name for name in set(before) & set(after) if before[name] != after[name])
    if added != ['autoinstall.yaml', 'g6k-firstboot-guard.py'] or removed:
        raise ValueError('UNEXPECTED_ISO_INVENTORY_DELTA')
    allowed = {'casper/ubuntu-server-minimal.squashfs', 'md5sum.txt', 'boot.catalog',
               'boot/grub/i386-pc/eltorito.img'}
    if set(changed) - allowed or not {'casper/ubuntu-server-minimal.squashfs', 'md5sum.txt'} <= set(changed):
        raise ValueError('UNEXPECTED_ISO_CONTENT_CHANGE: ' + repr(changed))
    expected = {'casper/ubuntu-server-minimal.squashfs': record['source_squashfs_sha256'],
                'md5sum.txt': record['md5sum_file_sha256'], 'autoinstall.yaml': record['autoinstall_sha256'],
                'g6k-firstboot-guard.py': record['target_guard_sha256']}
    for name, expected_hash in expected.items():
        if after[name]['sha256'] != expected_hash:
            raise ValueError('MAPPED_FILE_MISMATCH')
    snap = BUILD / 'subiquity_7403.snap'
    listing = subprocess.run(['unsquashfs', '-ll', str(snap)], capture_output=True, text=True, check=True).stdout
    schemas = {}
    for line in listing.splitlines():
        marker = 'squashfs-root/'
        if marker not in line:
            continue
        path = line.split(marker, 1)[1]
        if not path.startswith('lib/python3.12/site-packages/subiquity/server/controllers/') or not path.endswith('.py'):
            continue
        raw = subprocess.run(['unsquashfs', '-cat', str(snap), path], capture_output=True, check=True).stdout
        source = ast.parse(raw)
        for cls in (n for n in source.body if isinstance(n, ast.ClassDef)):
            values = {}
            for node in cls.body:
                if not isinstance(node, ast.Assign):
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        try:
                            values[target.id] = ast.literal_eval(node.value)
                        except (ValueError, TypeError):
                            pass
            if isinstance(values.get('autoinstall_key'), str) and isinstance(values.get('autoinstall_schema'), dict):
                schemas[values['autoinstall_key']] = values['autoinstall_schema']
    config = yaml.safe_load((BUILD / f'autoinstall-{REVISION}.yaml').read_text())['autoinstall']
    checked, remaining = [], []
    for key, value in config.items():
        if key in schemas:
            jsonschema.validate(value, schemas[key])
            checked.append(key)
        else:
            remaining.append(key)
    with (BUILD / f'iso-original-file-inventory-{REVISION}.json').open('x') as out:
        json.dump(before, out, sort_keys=True)
    with (BUILD / f'iso-derivative-file-inventory-{REVISION}.json').open('x') as out:
        json.dump(after, out, sort_keys=True)
    result = {'status': 'PASS_ISO_FILE_DELTA_AND_AVAILABLE_LITERAL_SCHEMAS',
              'original_files': len(before), 'derivative_files': len(after), 'added': added,
              'removed': removed, 'changed': changed, 'unchanged_file_records': len(set(before) & set(after)) - len(changed),
              'iso_pinned_subiquity_snap': '7403', 'snap_sha256': hashlib.sha256(snap.read_bytes()).hexdigest(),
              'literal_schema_sections_checked': sorted(checked), 'sections_requiring_other_validation': sorted(remaining),
              'installer_code_executed_for_schema_check': False,
              'full_installer_validation_and_guest_boot': 'NOT_RUN; required after memory gate',
              'content_inventory_scope': 'ISO regular data extents; filesystem metadata fully compared separately in source image'}
    with (TASK / f'evidence/derivative-validation-{REVISION}.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

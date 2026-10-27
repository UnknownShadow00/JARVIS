"""Verify fresh flat export and stage only pinned public transport inputs on Nexus."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_inputs import BASE, FIX, PIN, TASK, digest, match


def main():
    root = Path('/home/nexus/.local/share/jarvis-g6k-clean-replacement')
    if os.geteuid() == 0 or root.is_symlink() or root.stat().st_uid != os.geteuid() or root.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_UNPRIVILEGED_NEXUS_STAGE_REQUIRED')
    flat = root / 'public-artifacts'
    rows = json.loads((BASE / 'locks/gate6k-ARTIFACTS.json').read_text())
    match(flat / 'ARTIFACTS.json', PIN['artifacts'])
    expected = {'ARTIFACTS.json'} | {row['filename'] for row in rows.values()}
    if len(rows) != 131 or {p.name for p in flat.iterdir()} != expected:
        raise ValueError('FLAT_INVENTORY')
    inventory = {}
    for row in rows.values():
        match(flat / row['filename'], row['sha256'])
        inventory['public-artifacts/' + row['filename']] = row['sha256']
    inventory['public-artifacts/ARTIFACTS.json'] = PIN['artifacts']
    inputs = (
        (BASE.parent / 'gate6l-bundle-r1.tar', 'gate6l-bundle-r1.tar', PIN['bundle']),
        (BASE / 'tools/extract_bundle.py', 'extract_bundle.py', PIN['bundle_extractor']),
        (FIX / 'gate6k-vm163-preflight-r1.tar', 'gate6k-vm163-preflight-r1.tar', PIN['archive']),
        (FIX / 'safe_extract_vm163_r1.py', 'safe_extract_vm163_r1.py', PIN['extractor']),
    )
    if shutil.disk_usage(root).free < sum(p.stat().st_size for p, _, _ in inputs) + 1024 ** 3:
        raise ValueError('NEXUS_STAGING_CAPACITY')
    for source, name, expected_hash in inputs:
        match(source, expected_hash)
        with source.open('rb') as inp, (root / name).open('xb') as out:
            shutil.copyfileobj(inp, out, 1024 * 1024)
        (root / name).chmod(0o600)
        match(root / name, expected_hash)
        inventory[name] = expected_hash
    for name in ('ubuntu-SHA256SUMS', 'ubuntu-SHA256SUMS.gpg', 'ubuntu-key.asc'):
        source = TASK / 'evidence' / name
        expected_hash = digest(source)
        with source.open('rb') as inp, (root / name).open('xb') as out:
            shutil.copyfileobj(inp, out)
        (root / name).chmod(0o600)
        match(root / name, expected_hash)
        inventory[name] = expected_hash
    manifest = root / 'PUBLIC-INPUTS-SHA256SUMS'
    with manifest.open('x') as out:
        out.writelines(f'{sha}  {name}\n' for name, sha in sorted(inventory.items()))
    manifest.chmod(0o600)
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if not p.is_dir() or p.is_symlink()}
    if actual != set(inventory) | {manifest.name}:
        raise ValueError('TRANSPORT_INVENTORY')
    for name, expected_hash in inventory.items():
        match(root / name, expected_hash)
    result = {
        'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'PASS_PUBLIC_TRANSPORT_INTEGRITY_ONLY',
        'path': str(root), 'manifest_sha256': digest(manifest),
        'transport_files_excluding_manifest': len(inventory), 'artifact_records': len(rows),
        'artifact_bytes': sum((flat / row['filename']).stat().st_size for row in rows.values()),
        'total_staged_bytes': sum((root / name).stat().st_size for name in inventory) + manifest.stat().st_size,
        'all_files_regular_single_link': True,
        'stage_uid': root.stat().st_uid, 'stage_mode': oct(root.stat().st_mode & 0o777),
        'root_protected_guest_installation': False, 'vm_transfer': 'NOT_PERFORMED',
        'source': 'VERIFIED_NEXUS_PUBLIC_BUNDLE_AND_CORRECTED_RELEASE_ONLY',
        'qualification': 'NOT_RUN',
    }
    with (TASK / 'evidence/prepared-public-inputs.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

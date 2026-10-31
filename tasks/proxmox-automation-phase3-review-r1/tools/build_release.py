#!/usr/bin/env python3
"""Build/verify a deterministic public-only archive; never install or execute it."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from g6k_serial.securefs import SOURCE_FILES


def main():
    source_manifest = ''.join(hashlib.sha256((ROOT / 'src' / name).read_bytes()).hexdigest() +
                              '  ' + name + '\n' for name in SOURCE_FILES).encode()
    (ROOT / 'src/SOURCE-SHA256SUMS').write_bytes(source_manifest)
    source_hash = hashlib.sha256(source_manifest).hexdigest()
    template = json.loads((ROOT / 'approval.example.json').read_text())
    template['revised_source_manifest_sha256'] = source_hash
    (ROOT / 'approval.example.json').write_text(json.dumps(template, indent=2) + '\n')
    files = [ROOT / 'src' / name for name in SOURCE_FILES] + [ROOT / 'src/SOURCE-SHA256SUMS']
    files += sorted((ROOT / 'deploy').glob('*')) + sorted((ROOT / 'tests').glob('*.py'))
    files += [ROOT / name for name in ('README.md', 'INSTALLATION.md', 'LIVE-ACCEPTANCE.md',
              'STOP-AND-REVOKE.md', 'SECURITY-REVIEW.md', 'INDEPENDENT-REVIEW.md',
              'APPROVAL-PACKET.md', 'approval.example.json', 'PROGRESS.md')]
    members = {}
    archive_path = ROOT / 'artifacts/g6k-serial-review-r1.tar'
    archive_path.parent.mkdir(exist_ok=True)
    # Exclusive create: never replace a previously sealed release artifact.
    with archive_path.open('xb') as output, tarfile.open(fileobj=output, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for path in sorted(files):
            if path.is_symlink() or not path.is_file():
                raise SystemExit('Refuse nonregular public release input')
            relative = str(path.relative_to(ROOT))
            data = path.read_bytes()
            info = tarfile.TarInfo('g6k-phase3-reviewed/' + relative)
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            info.uid = info.gid = 0
            archive.addfile(info, io.BytesIO(data))
            members[info.name] = hashlib.sha256(data).hexdigest()
    # Independently reopen all bytes. No extraction, path traversal or executable use.
    with tarfile.open(archive_path, 'r:') as archive:
        entries = archive.getmembers()
        if len(entries) != len(members) or {m.name for m in entries} != set(members):
            raise SystemExit('Archive member identity mismatch')
        for info in entries:
            if not info.isfile() or info.size > 1024 * 1024 or '..' in Path(info.name).parts:
                raise SystemExit('Archive member type/path/size mismatch')
            if hashlib.sha256(archive.extractfile(info).read()).hexdigest() != members[info.name]:
                raise SystemExit('Archive content mismatch')
    record = {'status': 'CANDIDATE_NOT_AUTHORIZED_NOT_INSTALLED',
              'baseline_head': '7f4ae164261b792262eb9b818421c444c2d4ccff',
              'original_source_manifest_sha256': '58698f4cf814ef267ea010d44280c6bfdea2ce8f46486e51a18f3916d7ae24d5',
              'source_manifest_sha256': source_hash, 'source_file_count': len(SOURCE_FILES),
              'archive': str(archive_path.relative_to(ROOT)),
              'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
              'archive_member_sha256': members, 'archive_reopened_and_verified': True,
              'contains_runtime_credentials_or_private_state': False,
              'installation_or_activation_performed': False}
    (ROOT / 'RELEASE.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'archive_member_sha256'}, sort_keys=True))


if __name__ == '__main__':
    main()

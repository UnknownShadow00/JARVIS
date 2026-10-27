"""Unprivileged derivative of authenticated public OS data. No guest/evidence deletion."""
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

TASK = Path(__file__).resolve().parents[1]
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1')
ISO = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/artifacts/os/ubuntu-26.04.1-live-server-amd64.iso')
ISO_SHA = 'cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927'
MARK = b'#\n# START OF DATA - DO NOT MODIFY\n#\n'
SENTINEL = b'etc/cloud/cloud-init.disabled R 1787788900 644 0 0 0 0 0\n'


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def header(path):
    rows = []
    with path.open('rb') as f:
        while True:
            line = f.readline(1_000_000)
            if line == b'# START OF DATA - DO NOT MODIFY\n':
                if not rows or rows.pop() != b'#\n' or f.readline() != b'#\n':
                    raise ValueError('PSEUDO_SEPARATOR')
                return rows, f.tell()
            if not line or len(line) >= 1_000_000 or len(rows) > 200000:
                raise ValueError('PSEUDO_HEADER_LIMIT')
            if line != b'#\n' and not re.fullmatch(rb'.+ [DRSBCILx] .*\n', line):
                raise ValueError('PSEUDO_COMMAND_OR_UNKNOWN_TYPE')
            rows.append(line)


def fields(line):
    match = re.fullmatch(rb'(.*?) ([DRSBCILx]) (.*)\n', line)
    if not match:
        raise ValueError('PSEUDO_DEFINITION')
    return match.groups()


def transform(rows):
    selected = [r for r in rows if fields(r)[0] == b'root/.ssh']
    if len(selected) != 1 or not re.fullmatch(rb'root/\.ssh D [0-9]+ 700 0 0\n', selected[0]):
        raise ValueError('EXPECTED_ROOT_OWNED_EMPTY_SSH_DIRECTORY_REQUIRED')
    if any(fields(r)[0].startswith(b'root/.ssh/') for r in rows):
        raise ValueError('SSH_DIRECTORY_NOT_EMPTY')
    if any(fields(r)[0] == b'etc/cloud/cloud-init.disabled' for r in rows):
        raise ValueError('SENTINEL_ALREADY_EXISTS')
    # Omits a verified directory entry from a NEW image specification. No rmdir/unlink.
    return [r for r in rows if r != selected[0]] + [SENTINEL], selected[0]


def canonical(path):
    rows, start = header(path)
    result = []
    with path.open('rb') as stream:
        for line in rows:
            name, kind, rest = fields(line)
            if kind == b'R':
                values = rest.split()
                if len(values) != 7:
                    raise ValueError('REGULAR_METADATA')
                size, offset = int(values[4]), int(values[5])
                if size < 0 or offset < 0 or start + offset + size > path.stat().st_size:
                    raise ValueError('DATA_BOUNDS')
                stream.seek(start + offset)
                h = hashlib.sha256()
                remaining = size
                while remaining:
                    chunk = stream.read(min(remaining, 1024 * 1024))
                    if not chunk:
                        raise ValueError('TRUNCATED_DATA')
                    h.update(chunk)
                    remaining -= len(chunk)
                result.append([name.decode(), 'R', *[v.decode() for v in values[:5]],
                               values[6].decode(), h.hexdigest()])
            else:
                result.append([name.decode(), kind.decode(), rest.decode()])
    return sorted(result)


def main():
    if digest(ISO) != ISO_SHA:
        raise ValueError('ORIGINAL_ISO_PIN')
    source = BUILD / 'original.pseudo'
    rows, start = header(source)
    modified, omitted = transform(rows)
    spec = BUILD / 'clean.pseudo'
    with spec.open('xb') as out, source.open('rb') as inp:
        out.writelines(modified)
        out.write(MARK)
        inp.seek(start)
        shutil.copyfileobj(inp, out, 1024 * 1024)
    image = BUILD / 'ubuntu-server-minimal-g6k-r1.squashfs'
    if image.exists():
        raise ValueError('EXISTING_OUTPUT')
    with (TASK / 'evidence/mksquashfs.txt').open('x') as log:
        subprocess.run(['mksquashfs', '-', str(image), '-pf', str(spec), '-noappend',
                        '-comp', 'gzip', '-Xcompression-level', '1', '-processors', '2',
                        '-mem', '256M', '-mkfs-time', '1787788900', '-exit-on-error',
                        '-no-progress'], stdout=log, stderr=subprocess.STDOUT, check=True)
    rebuilt = BUILD / 'rebuilt.pseudo'
    subprocess.run(['unsquashfs', '-strict-errors', '-processors', '2', '-mem', '128M',
                    '-pf', str(rebuilt), str(image)], check=True, capture_output=True)
    before = canonical(source)
    after = canonical(rebuilt)
    expected = [row for row in before if row[0] != 'root/.ssh']
    expected.append(['etc/cloud/cloud-init.disabled', 'R', '1787788900', '644', '0', '0', '0', '0',
                     hashlib.sha256(b'').hexdigest()])
    if sorted(expected) != after:
        raise ValueError('UNEXPECTED_METADATA_OR_CONTENT_DELTA')
    with (BUILD / 'original-canonical.json').open('x') as out:
        json.dump(before, out, separators=(',', ':'))
    with (BUILD / 'clean-canonical.json').open('x') as out:
        json.dump(after, out, separators=(',', ':'))
    result = {
        'status': 'PASS_IMAGE_CONTENT_AND_METADATA_DELTA_ONLY',
        'original_iso_sha256': ISO_SHA, 'original_pseudo_sha256': digest(source),
        'derivative_image': str(image), 'derivative_image_sha256': digest(image),
        'derivative_bytes': image.stat().st_size, 'records_before': len(before), 'records_after': len(after),
        'regular_file_records_before': sum(row[1] == 'R' for row in before),
        'omitted_entry': omitted.decode().rstrip(),
        'added_entry': SENTINEL.decode().rstrip(),
        'all_other_content_ownership_modes_timestamps_links_special_nodes_xattrs': 'UNCHANGED_BY_CANONICAL_COMPARISON',
        'original_canonical_sha256': digest(BUILD / 'original-canonical.json'),
        'clean_canonical_sha256': digest(BUILD / 'clean-canonical.json'),
        'method': 'Pseudo-file image reconstruction, no mounted filesystem, no privileged extraction, no deletion',
        'gate6k_source_modified': False, 'guest_boot_or_installation_test': 'NOT_RUN',
        'installer_regeneration_checks': 'REQUIRED_BEFORE_FIRST_TARGET_BOOT',
    }
    with (TASK / 'evidence/clean-source-validation.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

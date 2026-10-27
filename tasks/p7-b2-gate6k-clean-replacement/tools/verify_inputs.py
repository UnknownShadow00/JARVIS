"""Nexus public-input verification only. Never connect to a VM or install code."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import urllib.request

TASK = Path(__file__).resolve().parents[1]
BASE = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1')
FIX = Path('/home/nexus/.local/share/jarvis-gate6k-preflight-fix')
PIN = {
    'iso': 'cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927',
    'bundle': '228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00',
    'bundle_manifest': '1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390',
    'archive': '15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55',
    'source_manifest': 'b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc',
    'artifacts': '9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837',
    'extractor': '31f77b42d6ee41f73abef56f8a59d5191a8695686cc2e79ced28236b623639d8',
    'bundle_extractor': '13792921e64036de94af62a95fddd343fbf37063b9dfd9c150764413edb2feeb',
}
FPR = '843938DF228D22F7B3742BC0D94AA3F0EFE21092'


def digest(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('SYMLINK_INPUT')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError('NONREGULAR_OR_HARDLINK_INPUT')
        result = hashlib.file_digest(stream, 'sha256').hexdigest()
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('CHANGED_INPUT')
        return result


def match(path, expected):
    actual = digest(path)
    if actual != expected:
        raise ValueError('HASH_MISMATCH: ' + str(path))
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': actual}


def inventory(root, manifest, expected, subtrees=None):
    match(root / manifest, expected)
    names = set()
    for line in (root / manifest).read_text().splitlines():
        sha, sep, name = line.partition('  ')
        if not sep or not re.fullmatch('[0-9a-f]{64}', sha) or name in names or name == manifest:
            raise ValueError('MANIFEST_ENTRY')
        if name.startswith('/') or '\\' in name or any(x in ('', '.', '..') for x in name.split('/')):
            raise ValueError('MANIFEST_PATH')
        match(root / name, sha)
        names.add(name)
    roots = [root / x for x in subtrees] if subtrees else [root]
    actual = {str(p.relative_to(root)) for start in roots for p in start.rglob('*')
              if not p.is_dir() or p.is_symlink()}
    if not subtrees:
        actual.discard(manifest)
    if actual != names:
        raise ValueError('MANIFEST_INVENTORY')
    return len(names)


def download(url, path, limit=1000000):
    with urllib.request.urlopen(url, timeout=30) as response:
        if not response.url.startswith('https://'):
            raise ValueError('NON_HTTPS_REDIRECT')
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('DOWNLOAD_LIMIT')
    with path.open('xb') as out:
        out.write(data)
    return {'url': url, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    evidence = TASK / 'evidence'
    evidence.mkdir(exist_ok=True)
    report = {'scope': 'PUBLIC_NEXUS_INPUTS_ONLY', 'qualification': 'NOT_RUN', 'checks': {}}
    report['checks']['source_entries'] = inventory(FIX / 'candidate-r1', 'SOURCE-SHA256SUMS', PIN['source_manifest'])
    report['checks']['bundle_entries'] = inventory(BASE, 'SHA256SUMS', PIN['bundle_manifest'],
        ('artifacts', 'metadata', 'locks', 'tools', 'source', 'results'))
    for key, path in (
        ('iso', BASE / 'artifacts/os/ubuntu-26.04.1-live-server-amd64.iso'),
        ('bundle', BASE.parent / 'gate6l-bundle-r1.tar'),
        ('archive', FIX / 'gate6k-vm163-preflight-r1.tar'),
        ('extractor', FIX / 'safe_extract_vm163_r1.py'),
        ('bundle_extractor', BASE / 'tools/extract_bundle.py'),
        ('artifacts', BASE / 'locks/gate6k-ARTIFACTS.json')):
        report['checks'][key] = match(path, PIN[key])
    rows = json.loads((BASE / 'locks/gate6k-ARTIFACTS.json').read_text())
    paths = json.loads((BASE / 'locks/gate6k-artifact-paths.json').read_text())
    for row in rows.values():
        relative = paths[row['filename']]
        if relative.startswith('/') or '..' in Path(relative).parts:
            raise ValueError('ARTIFACT_PATH')
        match(BASE / relative, row['sha256'])
    if len(rows) != 131:
        raise ValueError('ARTIFACT_COUNT')
    report['checks']['artifact_records'] = len(rows)
    with tempfile.TemporaryDirectory(prefix='g6k-public-signature-') as directory:
        home = Path(directory)
        urls = {
            'SHA256SUMS': 'https://releases.ubuntu.com/26.04.1/SHA256SUMS',
            'SHA256SUMS.gpg': 'https://releases.ubuntu.com/26.04.1/SHA256SUMS.gpg',
            'key.asc': 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x' + FPR,
        }
        report['independent_public_downloads'] = {n: download(u, home / n) for n, u in urls.items()}
        subprocess.run(['gpg', '--homedir', directory, '--batch', '--no-options', '--dearmor',
                        '--output', str(home / 'key.gpg'), str(home / 'key.asc')], check=True, capture_output=True)
        signature = subprocess.run(['gpgv', '--homedir', directory, '--status-fd', '1', '--keyring',
            str(home / 'key.gpg'), str(home / 'SHA256SUMS.gpg'), str(home / 'SHA256SUMS')],
            check=True, capture_output=True, text=True)
        if '[GNUPG:] VALIDSIG ' + FPR + ' ' not in signature.stdout:
            raise ValueError('UNEXPECTED_SIGNER')
        expected_line = PIN['iso'] + ' *ubuntu-26.04.1-live-server-amd64.iso'
        if expected_line not in (home / 'SHA256SUMS').read_text().splitlines():
            raise ValueError('SIGNED_ISO_HASH')
        report['checks']['iso_signature'] = {'signer': FPR, 'status': signature.stdout,
            'fingerprint_reference': 'https://ubuntu.com/tutorials/how-to-verify-ubuntu'}
        for name in urls:
            with (evidence / ('ubuntu-' + name)).open('xb') as out:
                out.write((home / name).read_bytes())
    report['status'] = 'PASS_PUBLIC_INPUT_INTEGRITY_AND_OS_SIGNATURE'
    with (evidence / 'input-verification.json').open('x') as out:
        json.dump(report, out, indent=2)
        out.write('\n')
    print(json.dumps({'status': report['status'], 'source_entries': report['checks']['source_entries'],
                      'bundle_entries': report['checks']['bundle_entries'], 'artifact_records': len(rows)}))


if __name__ == '__main__':
    main()

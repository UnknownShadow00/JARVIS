"""Acquire signed-index Ubuntu ISO tooling into an unprivileged private directory."""
import hashlib
import json
import lzma
from pathlib import Path
import re
import subprocess
import urllib.request

TASK = Path(__file__).resolve().parents[1]
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1')
META = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/metadata/ubuntu')
FPR = 'F6ECB3762474EDA9D21B7022871920D1991BC93C'


def main():
    tools = BUILD / 'iso-tool'
    tools.mkdir(mode=0o700)
    signature = subprocess.run(['gpgv', '--status-fd', '1', '--keyring', str(META / 'archive-key.gpg'),
        str(META / 'resolute-InRelease')], capture_output=True, text=True, check=True)
    if '[GNUPG:] VALIDSIG ' + FPR + ' ' not in signature.stdout:
        raise ValueError('ARCHIVE_SIGNER')
    index = META / 'resolute-main-Packages.xz'
    expected = re.findall(r'^ ([a-f0-9]{64}) +([0-9]+) main/binary-amd64/Packages.xz$',
                          (META / 'resolute-InRelease').read_text(), re.M)
    if len(expected) != 1 or hashlib.sha256(index.read_bytes()).hexdigest() != expected[0][0] or index.stat().st_size != int(expected[0][1]):
        raise ValueError('SIGNED_INDEX_BINDING')
    names = {'xorriso', 'libisoburn1t64', 'libisofs6t64', 'libburn4t64'}
    rows = []
    for paragraph in lzma.decompress(index.read_bytes()).decode().split('\n\n'):
        record = {line.split(': ', 1)[0]: line.split(': ', 1)[1] for line in paragraph.splitlines()
                  if line and not line[0].isspace() and ': ' in line}
        if record.get('Package') in names and record.get('Architecture') == 'amd64':
            rows.append(record)
    if {r['Package'] for r in rows} != names or len(rows) != len(names):
        raise ValueError('EXACT_TOOL_INVENTORY')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    results = []
    for row in rows:
        url = 'https://archive.ubuntu.com/ubuntu/' + row['Filename']
        with opener.open(url, timeout=30) as response:
            if not response.url.startswith('https://archive.ubuntu.com/'):
                raise ValueError('TOOL_REDIRECT')
            data = response.read(20_000_001)
        if len(data) > 20_000_000 or hashlib.sha256(data).hexdigest() != row['SHA256']:
            raise ValueError('TOOL_PACKAGE_HASH')
        path = tools / Path(row['Filename']).name
        with path.open('xb') as out:
            out.write(data)
        subprocess.run(['dpkg-deb', '-x', str(path), str(tools / 'root')], check=True)
        results.append({k: row[k] for k in ('Package', 'Version', 'Filename', 'SHA256', 'Depends')})
    result = {'status': 'PASS_SIGNED_INDEX_AND_TOOL_PACKAGE_HASHES', 'signer': FPR,
              'index_sha256': expected[0][0], 'packages': results,
              'method': 'Unprivileged dpkg-deb data extraction only; no package installation/maintainer scripts',
              'tool_executable_sha256': hashlib.sha256((tools / 'root/usr/bin/xorriso').read_bytes()).hexdigest()}
    with (TASK / 'evidence/iso-tool-provenance.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

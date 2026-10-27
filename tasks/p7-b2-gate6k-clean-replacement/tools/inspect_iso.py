"""Read metadata/public OS defaults from the pinned ISO, without mounting it."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_inputs import BASE, PIN, TASK, match


def entries(stream, record):
    offset = int.from_bytes(record[2:6], 'little') * 2048
    size = int.from_bytes(record[10:14], 'little')
    if size > 2_000_000:
        raise ValueError('DIRECTORY_LIMIT')
    stream.seek(offset)
    data = stream.read(size)
    pos = 0
    rows = {}
    while pos < len(data):
        length = data[pos]
        if not length:
            pos = (pos // 2048 + 1) * 2048
            continue
        rec = data[pos:pos + length]
        pos += length
        if len(rec) < 34 or rec[32] + 33 > len(rec):
            raise ValueError('DIRECTORY_RECORD')
        count = rec[32]
        name = rec[33:33 + count].decode('ascii')
        extra = rec[33 + count + (count % 2 == 0):]
        cursor = 0
        while cursor + 4 <= len(extra) and extra[cursor + 2] >= 4:
            item = extra[cursor:cursor + extra[cursor + 2]]
            cursor += extra[cursor + 2]
            if item[:2] == b'NM' and len(item) > 5:
                name = item[5:].decode('utf-8')
        if name not in ('\0', '\1'):
            if name in rows:
                raise ValueError('DUPLICATE_NAME')
            rows[name] = rec
    return rows


def main():
    iso = BASE / 'artifacts/os/ubuntu-26.04.1-live-server-amd64.iso'
    match(iso, PIN['iso'])
    output = TASK / 'evidence/iso-public-defaults'
    output.mkdir(mode=0o700)
    result = {'iso_sha256': PIN['iso'], 'method': 'ISO9660 metadata and unsquashfs read-only, no mounts', 'layers': {}}
    with iso.open('rb') as stream:
        stream.seek(16 * 2048)
        volume = stream.read(2048)
        if volume[:7] != b'\x01CD001\x01':
            raise ValueError('PRIMARY_VOLUME_DESCRIPTOR')
        root = entries(stream, volume[156:190])
        casper = entries(stream, root['casper'])
        for name in ('install-sources.yaml', 'ubuntu-server-minimal.manifest',
                     'ubuntu-server-minimal.ubuntu-server.manifest.full'):
            record = casper[name]
            size = int.from_bytes(record[10:14], 'little')
            if size > 2_000_000:
                raise ValueError('METADATA_LIMIT')
            stream.seek(int.from_bytes(record[2:6], 'little') * 2048)
            with (output / name).open('xb') as target:
                target.write(stream.read(size))
        for name in ('ubuntu-server-minimal.squashfs',
                     'ubuntu-server-minimal.ubuntu-server.squashfs'):
            record = casper[name]
            offset = int.from_bytes(record[2:6], 'little') * 2048
            proc = subprocess.run(['unsquashfs', '-ll', '-o', str(offset), str(iso)],
                                  capture_output=True, text=True, check=True, timeout=60)
            selected = [line for line in proc.stdout.splitlines() if any(
                token in line for token in ('squashfs-root/root', 'squashfs-root/home',
                    'squashfs-root/var/lib/cloud', 'squashfs-root/etc/ssh',
                    'squashfs-root/etc/skel', 'squashfs-root/etc/credstore',
                    'squashfs-root/usr/lib/credstore', 'squashfs-root/run/credentials'))]
            result['layers'][name] = {'offset': offset, 'bytes': int.from_bytes(record[10:14], 'little'),
                                    'selected_public_image_metadata': selected}
            if name == 'ubuntu-server-minimal.squashfs':
                for path in ('etc/cloud/cloud.cfg', 'usr/lib/python3/dist-packages/cloudinit/ssh_util.py',
                             'usr/lib/python3/dist-packages/cloudinit/config/cc_ssh.py',
                             'usr/lib/python3/dist-packages/cloudinit/config/cc_users_groups.py'):
                    proc = subprocess.run(['unsquashfs', '-cat', '-o', str(offset), str(iso), path],
                                          capture_output=True, check=True, timeout=60)
                    if len(proc.stdout) > 2_000_000:
                        raise ValueError('SOURCE_LIMIT')
                    with (output / path.replace('/', '__')).open('xb') as target:
                        target.write(proc.stdout)
    with (TASK / 'evidence/iso-inspection.json').open('x') as target:
        json.dump(result, target, indent=2)
        target.write('\n')
    print('PUBLIC_OS_DEFAULTS_RECORDED; NO_INSTALLATION_OR_BOOT')


if __name__ == '__main__':
    main()

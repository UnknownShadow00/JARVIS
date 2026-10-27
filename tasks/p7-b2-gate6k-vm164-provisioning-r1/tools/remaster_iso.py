"""Create a separately identified derivative ISO; no mounting, booting or VM access."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import yaml

TASK = Path(__file__).resolve().parents[1]
BUILD = Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1')
ORIGINAL = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/artifacts/os/ubuntu-26.04.1-live-server-amd64.iso')
ORIGINAL_SHA = 'cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927'
REVISION = 'r3'


def sha(path, algorithm='sha256'):
    with path.open('rb') as inp:
        return hashlib.file_digest(inp, algorithm).hexdigest()


def main():
    if sha(ORIGINAL) != ORIGINAL_SHA:
        raise ValueError('ORIGINAL_ISO_IDENTITY')
    plan = json.loads((TASK / 'VM164-PLAN.json').read_text())
    source = BUILD / 'ubuntu-server-minimal-g6k-r1.squashfs'
    source_record = json.loads((TASK / 'evidence/clean-source-validation.json').read_text())
    if sha(source) != source_record['derivative_image_sha256']:
        raise ValueError('DERIVATIVE_SOURCE_IDENTITY')
    early_code = (
        "import json,os,subprocess;from pathlib import Path;"
        f"assert os.geteuid()==0 and Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()=={plan['vm_uuid']!r};"
        "assert {p.name for p in Path('/sys/class/net').iterdir()}=={'lo'};"
        "r=json.loads(subprocess.check_output(['lsblk','-J','-b','-d','-o','NAME,TYPE,SIZE,SERIAL']));"
        "d=[v for v in r['blockdevices'] if v['type']=='disk'];"
        f"assert len(d)==1 and d[0]['name']=='sda' and d[0]['serial']=={plan['disk_serial']!r} and int(d[0]['size'])==68719476736;"
        "s=json.loads(subprocess.check_output(['wipefs','--json','--no-act','/dev/sda']));assert isinstance(s,dict) and s.get('signatures')==[]"
    )
    config = {'autoinstall': {
        'version': 1, 'locale': 'en_US.UTF-8', 'keyboard': {'layout': 'us'},
        'refresh-installer': {'update': False},
        'source': {'id': 'ubuntu-server-minimal', 'search_drivers': False},
        'network': {'version': 2, 'ethernets': {}},
        'apt': {'geoip': False, 'fallback': 'offline-install'},
        'storage': {'layout': {'name': 'direct', 'match': {'serial': plan['disk_serial']}}},
        'identity': {'hostname': plan['hostname'], 'username': 'jarvis', 'password': '!', 'groups': []},
        'ssh': {'install-server': False, 'authorized-keys': [], 'allow-pw': False},
        'oem': {'install': False}, 'drivers': {'install': False},
        'kernel-crash-dumps': {'enabled': False},
        'early-commands': [['/usr/bin/python3', '-I', '-B', '-c', early_code]],
        'late-commands': [['/usr/bin/python3', '-I', '-B', '/cdrom/g6k-firstboot-guard.py']],
        'shutdown': 'poweroff',
    }}
    auto = BUILD / f'autoinstall-{REVISION}.yaml'
    with auto.open('x') as out:
        yaml.safe_dump(config, out, sort_keys=False)
    if yaml.safe_load(auto.read_text()) != config:
        raise ValueError('YAML_ROUND_TRIP')
    tool = BUILD / 'iso-tool/root/usr/bin/xorriso'
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(BUILD),
           'LD_LIBRARY_PATH': str(BUILD / 'iso-tool/root/usr/lib/x86_64-linux-gnu')}
    def run(args, logname):
        with (TASK / 'evidence' / logname).open('x') as out:
            subprocess.run([str(tool), *args], env=env, stdout=out, stderr=subprocess.STDOUT,
                           check=True, timeout=300)
    original_md5 = BUILD / 'original-md5sum.txt'
    if not original_md5.exists():
        run(['-osirrox', 'on', '-indev', str(ORIGINAL), '-extract', '/md5sum.txt', str(original_md5)], 'iso-original-extract.txt')
    lines = original_md5.read_text().splitlines()
    matches = [i for i, line in enumerate(lines) if line.endswith(' ./casper/ubuntu-server-minimal.squashfs') or line.endswith(' *./casper/ubuntu-server-minimal.squashfs')]
    if len(matches) != 1:
        raise ValueError('ORIGINAL_MD5_ENTRY')
    lines[matches[0]] = sha(source, 'md5') + '  ./casper/ubuntu-server-minimal.squashfs'
    guard = TASK / 'tools/installer_target_guard.py'
    lines.extend([sha(auto, 'md5') + '  ./autoinstall.yaml', sha(guard, 'md5') + '  ./g6k-firstboot-guard.py'])
    new_md5 = BUILD / f'md5sum-{REVISION}.txt'
    with new_md5.open('x') as out:
        out.write('\n'.join(lines) + '\n')
    destination = BUILD / f'ubuntu-26.04.1-g6k-vm164-{REVISION}.iso'
    if destination.exists():
        raise ValueError('EXISTING_DERIVATIVE_ISO')
    run(['-indev', str(ORIGINAL), '-outdev', str(destination), '-boot_image', 'any', 'replay',
         '-map', str(source), '/casper/ubuntu-server-minimal.squashfs',
         '-map', str(auto), '/autoinstall.yaml', '-map', str(guard), '/g6k-firstboot-guard.py',
         '-map', str(new_md5), '/md5sum.txt', '-commit', '-end'], f'iso-remaster-{REVISION}.txt')
    run(['-indev', str(destination), '-report_el_torito', 'plain', '-report_system_area', 'plain'], f'iso-boot-catalog-{REVISION}.txt')
    result = {'status': 'DERIVATIVE_ISO_BUILT_NOT_BOOT_VALIDATED', 'original_iso_sha256': ORIGINAL_SHA,
              'path': str(destination), 'sha256': sha(destination), 'bytes': destination.stat().st_size,
              'source_squashfs_sha256': sha(source), 'autoinstall_sha256': sha(auto),
              'target_guard_sha256': sha(guard), 'md5sum_file_sha256': sha(new_md5),
              'autoinstall_schema_validation': 'PENDING_ISO_PINNED_SCHEMA_CHECK',
              'planned_vm_uuid': plan['vm_uuid'], 'planned_disk_serial': plan['disk_serial'],
              'trust': 'Ubuntu-signed original plus documented locally built derivative; derivative has no Ubuntu signature',
              'scope': 'No VM creation, installation, boot, qualification or final approval marker'}
    with (TASK / f'evidence/derivative-iso-{REVISION}.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

"""Bounded r3→r4 offline ISO transformation. No guest/device operations."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (BUILD, OLD_BUILD, OLD_TASK, R3, R3_SHA, TASK,
                    extract_iso_file, require_hash, sha)
from disk_guard_r4 import MATCH


def main():
    require_hash(R3, R3_SHA)
    old = yaml.safe_load((TASK / 'evidence/autoinstall-r3.yaml').read_text())
    if old != yaml.safe_load(extract_iso_file(R3, '/autoinstall.yaml')):
        raise ValueError('R3_CONFIG_NOT_ISO_BOUND')
    if old['autoinstall']['storage']['layout']['match'] != {'serial': 'g6k164-12821f6b54a2'}:
        raise ValueError('UNEXPECTED_R3_MATCH')
    config = copy.deepcopy(old)
    config['autoinstall']['storage']['layout']['match'] = dict(MATCH)
    config['autoinstall']['early-commands'] = [
        ['/usr/bin/python3', '-I', '-B', '/cdrom/g6k-disk-guard-r4.py']]
    check = copy.deepcopy(config)
    check['autoinstall']['storage']['layout']['match'] = old['autoinstall']['storage']['layout']['match']
    check['autoinstall']['early-commands'] = old['autoinstall']['early-commands']
    if check != old:
        raise ValueError('UNEXPECTED_CONFIG_CHANGE')
    auto = BUILD / 'autoinstall-r4.yaml'
    with auto.open('x') as out:
        yaml.safe_dump(config, out, sort_keys=False)
    if yaml.safe_load(auto.read_text()) != config:
        raise ValueError('YAML_ROUND_TRIP')
    guard = TASK / 'tools/disk_guard_r4.py'
    late = extract_iso_file(R3, '/g6k-firstboot-guard.py')
    if late != (TASK / 'evidence/g6k-firstboot-guard.py').read_bytes():
        raise ValueError('LATE_GUARD_CHANGED')
    lines = extract_iso_file(R3, '/md5sum.txt').decode().splitlines()
    match = [i for i, line in enumerate(lines) if line.endswith('  ./autoinstall.yaml')]
    if len(match) != 1 or any('g6k-disk-guard-r4.py' in line for line in lines):
        raise ValueError('R3_CHECKSUM_INVENTORY')
    lines[match[0]] = sha(auto, 'md5') + '  ./autoinstall.yaml'
    lines.append(sha(guard, 'md5') + '  ./g6k-disk-guard-r4.py')
    sums = BUILD / 'md5sum-r4.txt'
    with sums.open('x') as out:
        out.write('\n'.join(lines) + '\n')
    provenance = json.loads((OLD_TASK / 'evidence/iso-tool-provenance.json').read_text())
    toolroot = OLD_BUILD / 'iso-tool'
    tool = toolroot / 'root/usr/bin/xorriso'
    require_hash(tool, provenance['tool_executable_sha256'])
    for package in provenance['packages']:
        require_hash(toolroot / Path(package['Filename']).name, package['SHA256'])
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(BUILD),
           'LD_LIBRARY_PATH': str(toolroot / 'root/usr/lib/x86_64-linux-gnu')}
    destination = BUILD / 'ubuntu-26.04.1-g6k-vm164-r4.iso'
    if destination.exists() or destination.is_symlink():
        raise ValueError('EXISTING_OUTPUT_PRESERVE_AND_STOP')
    argv = [str(tool), '-indev', str(R3), '-outdev', str(destination), '-boot_image', 'any', 'replay',
            '-map', str(auto), '/autoinstall.yaml', '-map', str(guard), '/g6k-disk-guard-r4.py',
            '-map', str(sums), '/md5sum.txt', '-commit', '-end']
    with (TASK / 'evidence/iso-build.txt').open('x') as out:
        subprocess.run(argv, env=env, stdout=out, stderr=subprocess.STDOUT, check=True, timeout=300)
    with (TASK / 'evidence/boot-catalog-r4.txt').open('x') as out:
        subprocess.run([str(tool), '-indev', str(destination), '-report_el_torito', 'plain',
                        '-report_system_area', 'plain'], env=env, stdout=out,
                       stderr=subprocess.STDOUT, check=True, timeout=60)
    result = {'status': 'R4_BUILT_NOT_VM_INSTALLED', 'path': str(destination),
              'sha256': sha(destination), 'bytes': destination.stat().st_size,
              'r3_sha256': R3_SHA, 'autoinstall_sha256': sha(auto), 'early_guard_sha256': sha(guard),
              'late_guard': 'UNCHANGED_BYTE_FOR_BYTE_FROM_R3', 'md5sum_file_sha256': sha(sums),
              'match': MATCH, 'xorriso_sha256': sha(tool),
              'changed_configuration': ['storage.layout.match', 'early-commands'],
              'credential_or_mount_policy_change': False,
              'vm_access': 'NONE', 'disk_format_reset_replace': 'NONE',
              'qualification': 'NOT_RUN', 'final_marker': 'NOT_CREATED',
              'trust': 'Local derivative of retained authenticated-input r3; no new Ubuntu signature'}
    with (TASK / 'evidence/iso-r4.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

"""Independent extent-hash comparisons against r3 and original public media."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (BUILD, OLD_BUILD, R3, R3_SHA, TASK, extract_iso_file,
                    old_iso_tools, require_hash, sha)
from disk_guard_r4 import MATCH


def efi_images(path):
    catalog = extract_iso_file(path, '/boot.catalog')
    platform = catalog[1]
    results = []
    with path.open('rb') as stream:
        for pos in range(32, len(catalog), 32):
            entry = catalog[pos:pos + 32]
            if len(entry) != 32:
                raise ValueError('BOOT_CATALOG_ENTRY')
            if entry[0] in (0x90, 0x91):
                platform = entry[1]
            elif entry[0] == 0x88 and platform == 0xEF:
                length = int.from_bytes(entry[6:8], 'little') * 512
                offset = int.from_bytes(entry[8:12], 'little') * 2048
                if not 0 < length < 100_000_000:
                    raise ValueError('EFI_IMAGE_LENGTH')
                stream.seek(offset)
                data = stream.read(length)
                if len(data) != length:
                    raise ValueError('EFI_IMAGE_TRUNCATED')
                results.append({'bytes': length, 'sha256': hashlib.sha256(data).hexdigest()})
    if not results:
        raise ValueError('EFI_BOOT_IMAGE_MISSING')
    return results


def main():
    require_hash(R3, R3_SHA)
    record = json.loads((TASK / 'evidence/iso-r4.json').read_text())
    output = Path(record['path'])
    require_hash(output, record['sha256'])
    tree, entries = old_iso_tools()
    before, after = tree(R3, entries), tree(output, entries)
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(n for n in set(before) & set(after) if before[n] != after[n])
    allowed = {'autoinstall.yaml', 'md5sum.txt', 'boot.catalog', 'boot/grub/i386-pc/eltorito.img'}
    if added != ['g6k-disk-guard-r4.py'] or removed or set(changed) - allowed:
        raise ValueError('UNEXPECTED_R3_TO_R4_PAYLOAD_CHANGE')
    if not {'autoinstall.yaml', 'md5sum.txt'} <= set(changed):
        raise ValueError('EXPECTED_PATCH_MISSING')
    for name, expected in (('autoinstall.yaml', record['autoinstall_sha256']),
                           ('g6k-disk-guard-r4.py', record['early_guard_sha256']),
                           ('md5sum.txt', record['md5sum_file_sha256'])):
        if after[name]['sha256'] != expected:
            raise ValueError('MAPPED_PATCH_HASH')
    old_config = yaml.safe_load(extract_iso_file(R3, '/autoinstall.yaml'))
    config = yaml.safe_load(extract_iso_file(output, '/autoinstall.yaml'))
    if config['autoinstall']['storage']['layout']['match'] != MATCH:
        raise ValueError('WRONG_MATCH_SPEC')
    if config['autoinstall']['early-commands'] != [['/usr/bin/python3', '-I', '-B', '/cdrom/g6k-disk-guard-r4.py']]:
        raise ValueError('WRONG_GUARD_INVOCATION')
    restored = copy.deepcopy(config)
    restored['autoinstall']['storage']['layout']['match'] = old_config['autoinstall']['storage']['layout']['match']
    restored['autoinstall']['early-commands'] = old_config['autoinstall']['early-commands']
    if restored != old_config:
        raise ValueError('OTHER_INSTALLATION_POLICY_CHANGED')
    if after['g6k-firstboot-guard.py'] != before['g6k-firstboot-guard.py']:
        raise ValueError('LATE_GUARD_CHANGED')
    bios_old = extract_iso_file(R3, '/boot/grub/i386-pc/eltorito.img')
    bios_new = extract_iso_file(output, '/boot/grub/i386-pc/eltorito.img')
    if len(bios_old) != len(bios_new):
        raise ValueError('BIOS_IMAGE_LENGTH_CHANGED')
    bios_changes = [i for i, (old, new) in enumerate(zip(bios_old, bios_new)) if old != new]
    if any(not (8 <= i < 64 or 2548 <= i < 2556) for i in bios_changes):
        raise ValueError('UNEXPECTED_BIOS_BOOT_PROGRAM_CHANGE')
    old_efi, new_efi = efi_images(R3), efi_images(output)
    if old_efi != new_efi:
        raise ValueError('EFI_PAYLOAD_CHANGED')
    # The previously recorded original inventory is independently tied to the
    # original ISO by its retained task seal; compare every original file again.
    original = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/artifacts/os/ubuntu-26.04.1-live-server-amd64.iso')
    require_hash(original, 'cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927')
    original_tree = tree(original, entries)
    original_changed = sorted(n for n in original_tree if original_tree[n] != after.get(n))
    original_allowed = {'casper/ubuntu-server-minimal.squashfs', 'md5sum.txt',
                        'boot.catalog', 'boot/grub/i386-pc/eltorito.img'}
    if set(original_changed) - original_allowed:
        raise ValueError('UNEXPECTED_ORIGINAL_OS_PAYLOAD_CHANGE')
    if before['casper/ubuntu-server-minimal.squashfs'] != after['casper/ubuntu-server-minimal.squashfs']:
        raise ValueError('CREDENTIAL_FREE_SOURCE_IMAGE_CHANGED')
    (BUILD / 'r3-file-inventory.json').write_text(json.dumps(before, sort_keys=True) + '\n')
    (BUILD / 'r4-file-inventory.json').write_text(json.dumps(after, sort_keys=True) + '\n')
    result = {'status': 'PASS_BOUNDED_R4_ISO_PATCH_AND_UNCHANGED_PUBLIC_OS_PAYLOADS',
              'r3_files': len(before), 'r4_files': len(after), 'added': added, 'removed': removed,
              'changed_from_r3': changed, 'unchanged_from_r3': len(before) - len(changed),
              'original_iso_files': len(original_tree), 'original_file_deltas': original_changed,
              'original_unchanged_files': len(original_tree) - len(original_changed),
              'late_target_guard': 'BYTE_IDENTICAL', 'source_squashfs': 'BYTE_IDENTICAL_TO_R3',
              'bios_changed_offsets': bios_changes, 'bios_change_scope': 'Boot info/LBA relocation fields only',
              'efi_boot_images': new_efi, 'efi_boot_payload': 'BYTE_IDENTICAL_TO_R3',
              'other_autoinstall_configuration': 'SEMANTICALLY_IDENTICAL_TO_R3',
              'actual_vm_or_installation_test': 'NOT_RUN', 'r4_sha256': sha(output)}
    with (TASK / 'evidence/iso-verification-final.json').open('x') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

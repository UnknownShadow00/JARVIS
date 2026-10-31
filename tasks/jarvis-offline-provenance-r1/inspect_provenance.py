#!/usr/bin/env python3
"""Read-only public artifact inspection; never import or execute inspected payloads.

Tar members are hashed by bounded byte ranges in an uncompressed tar. Nothing is
extracted, installed, launched, or copied into a runtime. Only this new evidence
packet receives writes. Fixed roots and expected identities come from retained
Gate6K/Gate6L public handoff records, not a colocated artifact's claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
K_ROOT = Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2')
K_TAR = K_ROOT.parent / 'gate6k-release-r2.tar'
L_ROOT = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1')
L_TAR = L_ROOT.parent / 'gate6l-bundle-r1.tar'
K_DIGEST = 'ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d'
K_MANIFEST = '5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03'
L_DIGEST = '228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00'
L_MANIFEST = '1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390'
L_RECORD = '9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837'
K_EVIDENCE = '5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6'
L_EVIDENCE = 'ff82e29f529e9ba1861747cfabe73edb7ac840036f1a1c2301c65fa361ab6b33'
CHUNK = 1024 * 1024
MAX_ARCHIVE = 4 * 1024**3
MAX_MEMBER = 3 * 1024**3
MAX_TOTAL = 4 * 1024**3
MAX_MEMBERS = 2048
MAX_TEXT = 1024 * 1024
MAX_SOURCE = 8 * 1024 * 1024


class InspectionError(Exception):
    pass


def stamp():
    return datetime.now(UTC).isoformat()


def safe_name(value):
    if (type(value) is not str or not value or len(value) > 4096 or '\\' in value or
            any(ord(c) < 32 for c in value)):
        raise InspectionError('unsafe member name')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('', '.', '..') for part in value.split('/')):
        raise InspectionError('unsafe member name')
    if any(part in ('.git', '.env', '.venv', 'credentials', 'secrets') for part in path.parts):
        raise InspectionError('nonpublic member name')
    return value


def open_regular(path, *, maximum):
    """No-follow each path component; require a bounded regular final file."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise InspectionError('absolute public path required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for index, component in enumerate(path.parts[1:]):
            last = index == len(path.parts[1:]) - 1
            flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
            if not last:
                flags |= os.O_DIRECTORY
            next_fd = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        observed = os.fstat(fd)
        if not stat.S_ISREG(observed.st_mode) or not 0 <= observed.st_size <= maximum:
            raise InspectionError('not a bounded regular public file')
        stream = os.fdopen(fd, 'rb')
        fd = -1
        return stream
    finally:
        if fd >= 0:
            os.close(fd)


def identity(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns)


def observe(path, *, maximum=MAX_SOURCE, capture=False):
    observed_at = stamp()
    try:
        with open_regular(path, maximum=maximum) as stream:
            before = os.fstat(stream.fileno())
            digest = hashlib.sha256()
            contents = bytearray()
            count = 0
            while chunk := stream.read(CHUNK):
                count += len(chunk)
                if count > maximum:
                    raise InspectionError('file grew beyond bound')
                digest.update(chunk)
                if capture:
                    contents.extend(chunk)
            after = os.fstat(stream.fileno())
        row = {'path': str(path), 'observed_at': observed_at, 'finished_at': stamp(),
               'bytes': count, 'sha256': digest.hexdigest(),
               'file_identity': list(identity(before)),
               'stable_during_read': identity(before) == identity(after) and count == before.st_size}
        return row, bytes(contents) if capture else None
    except (OSError, InspectionError) as exc:
        return {'path': str(path), 'observed_at': observed_at, 'finished_at': stamp(),
                'error': type(exc).__name__}, None


def manifest(raw):
    result = {}
    if raw is None or len(raw) > MAX_TEXT:
        raise InspectionError('manifest unavailable or oversized')
    for line in raw.decode('utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if not match:
            raise InspectionError('invalid manifest line')
        digest, name = match.groups()
        safe_name(name)
        if name in result or len(result) >= MAX_MEMBERS:
            raise InspectionError('duplicate or oversized manifest')
        result[name] = digest
    if not result:
        raise InspectionError('empty manifest')
    return result


def inspect_tar(path, expected_digest, manifest_name, expected_manifest):
    result, _ = observe(path, maximum=MAX_ARCHIVE)
    result['expected_sha256'] = expected_digest
    result['archive_matches_expected'] = result.get('sha256') == expected_digest
    if not result['archive_matches_expected'] or not result.get('stable_during_read'):
        result['blocker'] = 'archive missing, unstable, or identity mismatch; members not read'
        return result, {}, {}
    members = {}
    captured = {}
    try:
        with open_regular(path, maximum=MAX_ARCHIVE) as stream:
            before = identity(os.fstat(stream.fileno()))
            if list(before) != result['file_identity']:
                raise InspectionError('archive changed after whole-file hashing')
            with tarfile.open(fileobj=stream, mode='r:') as archive:
                total = 0
                for item in archive:
                    safe_name(item.name)
                    # The approved bundle has long public wheel names encoded as
                    # PAX path headers. Accept only that exact bounded override.
                    valid_pax = not item.pax_headers or (
                        set(item.pax_headers) == {'path'} and item.pax_headers['path'] == item.name)
                    if (not item.isfile() or item.issparse() or not valid_pax or
                            item.name in members or len(members) >= MAX_MEMBERS or
                            not 0 <= item.size <= MAX_MEMBER):
                        raise InspectionError('nonregular, duplicate, extended, or oversized tar member')
                    total += item.size
                    if total > MAX_TOTAL or item.offset_data + item.size > result['bytes']:
                        raise InspectionError('tar byte budget exceeded')
                    members[item.name] = {'bytes': item.size, 'offset': item.offset_data}
            if not members:
                raise InspectionError('empty archive')
        # A separate no-follow descriptor reads only approved regular member byte
        # ranges. No tar extraction APIs or nested archive/package readers are used.
        with open_regular(path, maximum=MAX_ARCHIVE) as stream:
            if identity(os.fstat(stream.fileno())) != before:
                raise InspectionError('archive changed before member hashing')
            for name, row in members.items():
                stream.seek(row.pop('offset'))
                remaining = row['bytes']
                digest = hashlib.sha256()
                capture = name in {manifest_name, 'locks/gate6k-ARTIFACTS.json',
                                   'locks/dependency-versions.json', 'results/selected-artifacts.json'}
                if capture and remaining > MAX_TEXT:
                    raise InspectionError('text member exceeds capture bound')
                contents = bytearray()
                while remaining:
                    chunk = stream.read(min(CHUNK, remaining))
                    if not chunk:
                        raise InspectionError('truncated member')
                    remaining -= len(chunk)
                    digest.update(chunk)
                    if capture:
                        contents.extend(chunk)
                row['sha256'] = digest.hexdigest()
                if capture:
                    captured[name] = bytes(contents)
            if identity(os.fstat(stream.fileno())) != before:
                raise InspectionError('archive changed while member hashing')
        actual_manifest = captured.get(manifest_name)
        result['manifest_sha256'] = hashlib.sha256(actual_manifest or b'').hexdigest()
        result['expected_manifest_sha256'] = expected_manifest
        result['manifest_matches_expected'] = result['manifest_sha256'] == expected_manifest
        if not result['manifest_matches_expected']:
            raise InspectionError('manifest identity mismatch')
        entries = manifest(actual_manifest)
        differences = [{'name': name, 'expected': digest,
                        'actual': members.get(name, {}).get('sha256')}
                       for name, digest in entries.items()
                       if members.get(name, {}).get('sha256') != digest]
        extras = sorted(set(members) - set(entries) - {manifest_name})
        result.update({'member_count': len(members), 'manifest_entries': len(entries),
                       'member_bytes': sum(row['bytes'] for row in members.values()),
                       'mismatches_or_missing': differences, 'unmanifested_members': extras,
                       'all_member_hashes_match': not differences and not extras,
                       'member_hashes': members, 'finished_member_verification_at': stamp()})
        return result, entries, captured
    except (OSError, InspectionError, ValueError, tarfile.TarError) as exc:
        result['blocker'] = str(exc) if isinstance(exc, InspectionError) else type(exc).__name__
        return result, {}, {}


def loose_manifest(root, entries, *, maximum=MAX_SOURCE):
    rows = []
    total = 0
    for name, digest in entries.items():
        row, _ = observe(root / name, maximum=maximum)
        row.update({'name': name, 'expected_sha256': digest,
                    'matches_expected': row.get('sha256') == digest and row.get('stable_during_read', False)})
        rows.append(row)
        total += row.get('bytes', 0)
        if total > MAX_TOTAL:
            raise InspectionError('loose-manifest byte budget exceeded')
    return {'entries': len(rows), 'matched': sum(row['matches_expected'] for row in rows),
            'mismatched_or_missing': [row for row in rows if not row['matches_expected']], 'observations': rows}


def sealed_public_packet(root, expected):
    row, raw = observe(root / 'SHA256SUMS', maximum=MAX_TEXT, capture=True)
    row['expected_sha256'] = expected
    row['manifest_matches_expected'] = row.get('sha256') == expected
    if not row['manifest_matches_expected'] or not row.get('stable_during_read'):
        row['blocker'] = 'public evidence manifest missing, changed, or unstable'
        return row
    row['files'] = loose_manifest(root, manifest(raw))
    return row


def public_current_sources():
    """Limited source discovery, excluding state and all task/history trees."""
    result = set()
    for root_name in ('app', 'tests', 'scripts', 'candidate_v3'):
        top = ROOT / root_name
        if not top.is_dir() or top.is_symlink():
            continue
        for directory, subdirectories, filenames in os.walk(top, followlinks=False):
            subdirectories[:] = [name for name in subdirectories if not name.startswith('.') and
                                 name not in ('__pycache__', 'data', 'state', 'secrets', 'credentials') and
                                 not (Path(directory) / name).is_symlink()]
            for name in filenames:
                if name.endswith('.py'):
                    result.add((Path(directory) / name).relative_to(ROOT).as_posix())
                    if len(result) > MAX_MEMBERS:
                        raise InspectionError('current source discovery budget exceeded')
    return result


def distribution_pins(value):
    if (type(value) is not dict or set(value) != {'cryptography', 'packages', 'python', 'sqlite'} or
            type(value['packages']) is not dict or not 0 < len(value['packages']) <= MAX_MEMBERS or
            not all(type(name) is str and type(version) is str
                    for name, version in value['packages'].items())):
        raise InspectionError('unexpected dependency pin schema')
    return value['packages']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    started = stamp()
    inspector, _ = observe(Path(__file__).resolve())
    queue_entry, _ = observe(ROOT / 'app/agent/task_queue.py')
    k, sources, _ = inspect_tar(K_TAR, K_DIGEST, 'SOURCE-SHA256SUMS', K_MANIFEST)
    loose_k = loose_manifest(K_ROOT, sources)
    manifest_k, _ = observe(K_ROOT / 'SOURCE-SHA256SUMS', maximum=MAX_TEXT)
    workspace = []
    for name, expected in sources.items():
        if not name.startswith('repo/'):
            continue
        relative = name.removeprefix('repo/')
        row, _ = observe(ROOT / relative)
        row.update({'relative_path': relative, 'gate6k_sha256': expected,
                    'comparison': ('missing_or_unreadable' if 'error' in row else
                                   'unstable' if not row['stable_during_read'] else
                                   'same' if row['sha256'] == expected else 'different')})
        workspace.append(row)
    baseline_names = {row['relative_path'] for row in workspace}
    new_sources = []
    for relative in sorted(public_current_sources() - baseline_names):
        row, _ = observe(ROOT / relative)
        row['relative_path'] = relative
        new_sources.append(row)
    l, artifacts, captured = inspect_tar(L_TAR, L_DIGEST, 'SHA256SUMS', L_MANIFEST)
    loose_l = loose_manifest(L_ROOT, artifacts, maximum=MAX_MEMBER)
    manifest_l, _ = observe(L_ROOT / 'SHA256SUMS', maximum=MAX_TEXT)
    dependency = {'record_expected_sha256': L_RECORD}
    record_raw = captured.get('locks/gate6k-ARTIFACTS.json')
    if record_raw:
        record = json.loads(record_raw)
        dependency['record_actual_sha256'] = hashlib.sha256(record_raw).hexdigest()
        dependency['record_matches_expected'] = dependency['record_actual_sha256'] == L_RECORD
        dependency['record_entries'] = len(record)
        pin_document = json.loads(captured['locks/dependency-versions.json'])
        pins = distribution_pins(pin_document)
        dependency['distribution_pins'] = len(pins)
        dependency['runtime_pin_versions'] = {
            key: pin_document[key] for key in ('python', 'sqlite', 'cryptography')}
        dependency['runtime_pins_match_record'] = (
            record.get('interpreter:cpython', {}).get('version') == '.'.join(map(str, pin_document['python'])) and
            record.get('library:sqlite', {}).get('version') == pin_document['sqlite'] and
            record.get('distribution:cryptography', {}).get('version') == pin_document['cryptography'])
        dependency['artifact_record_missing_distributions'] = sorted(
            name for name in pins if 'distribution:' + name not in record)
        dependency['artifact_record_version_mismatches'] = [
            name for name, version in pins.items()
            if record.get('distribution:' + name, {}).get('version') != version]
        by_hash = {}
        for name, row in l.get('member_hashes', {}).items():
            by_hash.setdefault(row['sha256'], []).append(name)
        dependency['artifact_record_missing_payload_hashes'] = [
            name for name, row in record.items() if row.get('sha256') not in by_hash]
        dependency['wheel_members'] = {name: row for name, row in l.get('member_hashes', {}).items()
                                       if name.endswith('.whl')}
        dependency['wheel_count'] = len(dependency['wheel_members'])
        dependency['artifact_categories'] = dict(Counter(
            name.split('/')[1] for name in artifacts if name.startswith('artifacts/')))
        dependency['locks_equal_gate6k'] = {
            name: artifacts.get('locks/' + name) == sources.get('disposable/' + name)
            for name in ('dependency-versions.json', 'requirements-versions.txt')}
    queue_exit, _ = observe(ROOT / 'app/agent/task_queue.py')
    sealed_evidence = {
        'gate6k': sealed_public_packet(ROOT / 'tasks/p7-b2-gate6k-disposable-multiuid-qualification', K_EVIDENCE),
        'gate6l': sealed_public_packet(ROOT / 'tasks/p7-b2-gate6l-offline-dependency-bundle', L_EVIDENCE),
    }
    summary = dict(Counter(row['comparison'] for row in workspace))
    result = {'started_at': started, 'finished_at': stamp(),
              'inspector_source': inspector,
              'scope': 'public byte identity only; no imports/execution/extraction/install/network/VM access',
              'limits': {'max_archive': MAX_ARCHIVE, 'max_member': MAX_MEMBER, 'max_total': MAX_TOTAL,
                         'max_members': MAX_MEMBERS, 'max_captured_text': MAX_TEXT,
                         'max_current_source': MAX_SOURCE, 'read_chunk': CHUNK},
              'gate6k_archive': k, 'gate6k_loose_source': loose_k,
              'gate6k_loose_manifest': manifest_k, 'workspace_comparison_counts': summary,
              'workspace_comparison': workspace, 'new_current_python_sources': new_sources,
              'gate6l_archive': l, 'gate6l_loose_bundle': loose_l,
              'gate6l_loose_manifest': manifest_l, 'dependency_checks': dependency,
              'historical_public_evidence_packets': sealed_evidence,
              'task_queue_observations': {'entry': queue_entry, 'exit': queue_exit,
                                        'same_hash_at_both_observations': queue_entry.get('sha256') == queue_exit.get('sha256')},
              'historical_regression': {'reported_passed': 7741, 'reported_deselected': 11,
                                        'rerun': False, 'applies_to_current_workspace': False},
              'approval': 'No operator approval inferred; Gate6L report retains operator-review-pending provenance.'}
    name = 'evidence-' + datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ') + '.json'
    with (PACKET / name).open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'evidence': name, 'workspace': summary,
                      'gate6k_member_count': k.get('member_count'),
                      'gate6l_member_count': l.get('member_count'),
                      'gate6k_blocker': k.get('blocker'), 'gate6l_blocker': l.get('blocker'),
                      'dependency': {key: value for key, value in dependency.items() if key != 'wheel_members'}}, indent=2))


if __name__ == '__main__':
    main()

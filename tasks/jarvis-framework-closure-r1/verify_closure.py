#!/usr/bin/env python3
"""Validate a fixed-pin wheel closure as data, using already installed packaging."""
from __future__ import annotations

import base64
from collections import deque
import csv
from datetime import UTC, datetime
from email.parser import BytesParser
from email.policy import default
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import socket
import stat
import struct
import sys
import sysconfig
import zipfile

# These are normal installed tool modules. Candidate payloads are never imported.
import packaging
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.tags import parse_tag, sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
BUNDLE = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1')
CAP = 50 * 1024 * 1024
ENTRY_CAP = 1024 * 1024
ROOTS = ('fastapi', 'pydantic', 'APScheduler', 'pytest', 'pytest-asyncio', 'httpx')
PROVENANCE = ROOT / 'tasks/jarvis-offline-provenance-r1'
FORBIDDEN_IMPORTS = {'fastapi', 'starlette', 'pydantic', 'pydantic_core', 'pydantic_settings', 'apscheduler', 'pytest', 'pytest_asyncio', 'httpx', 'app'}


class Blocker(RuntimeError):
    def __init__(self, code, detail):
        super().__init__(f'{code}: {detail}')
        self.code, self.detail = code, detail


class Budget:
    def __init__(self, limit=CAP):
        self.limit, self.used = limit, 0

    def take(self, size):
        if size < 0 or self.used + size > self.limit:
            raise Blocker('read_budget', f'{self.used}+{size}>{self.limit}')
        self.used += size


class LimitedFile:
    def __init__(self, opened, budget):
        self.opened, self.budget = opened, budget

    def read(self, size=-1):
        remaining = self.budget.limit - self.budget.used
        result = self.opened.read(min(size, remaining + 1) if size >= 0 else remaining + 1)
        self.budget.take(len(result))
        return result

    def seek(self, *args):
        return self.opened.seek(*args)

    def tell(self):
        return self.opened.tell()

    def seekable(self):
        return True


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name, *, directory=False):
    if not isinstance(name, str) or not name or '\\' in name or '\x00' in name:
        raise Blocker('unsafe_path', repr(name))
    trimmed = name[:-1] if directory and name.endswith('/') else name
    parts = trimmed.split('/')
    if any(part in {'', '.', '..'} or ':' in part for part in parts) or PurePosixPath(trimmed).is_absolute():
        raise Blocker('unsafe_path', repr(name))
    return trimmed


def open_regular(path):
    path = Path(path)
    for ancestor in [*reversed(path.parents), path]:
        if ancestor.is_symlink():
            raise Blocker('symlink_path', str(path))
    descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise Blocker('nonregular_input', str(path))
    return os.fdopen(descriptor, 'rb')


def read_data(path, budget, maximum=ENTRY_CAP, expected=None):
    with open_regular(path) as opened:
        if os.fstat(opened.fileno()).st_size > maximum:
            raise Blocker('input_size', str(path))
        result = LimitedFile(opened, budget).read(maximum + 1)
    if len(result) > maximum:
        raise Blocker('input_size', str(path))
    if expected and sha(result) != expected:
        raise Blocker('input_hash', str(path))
    return result


def headers(data, label):
    if any(len(line) > 65536 for line in data.splitlines()):
        raise Blocker('metadata_line_size', label)
    message = BytesParser(policy=default).parsebytes(data, headersonly=True)
    if message.defects:
        raise Blocker('metadata_headers', label)
    return message


def exactly_one(message, field, label, *, required=True):
    values = message.get_all(field, [])
    if len(values) > 1 or (required and not values):
        raise Blocker('metadata_field', f'{label}: {field} count={len(values)}')
    return str(values[0]) if values else None


def inspect_wheel(path, filename, expected_hash, budget, accepted_tags, python_version):
    """Hash whole artifact, inspect all ZIP structure, verify every RECORD payload as data."""
    name, version, build, file_tags = parse_wheel_filename(filename)
    matches = sorted(str(tag) for tag in file_tags & accepted_tags)
    if not matches:
        raise Blocker('wheel_tag', filename)
    with open_regular(path) as opened:
        before = os.fstat(opened.fileno())
        fingerprint = hashlib.sha256()
        for chunk in iter(lambda: opened.read(1024 * 1024), b''):
            fingerprint.update(chunk)  # Streamed whole-artifact hash is outside metadata read quota.
        if fingerprint.hexdigest() != expected_hash:
            raise Blocker('artifact_hash', filename)
        bounded = LimitedFile(opened, budget)
        if before.st_size < 22:
            raise Blocker('zip_eocd', filename)
        bounded.seek(max(0, before.st_size - 65557))
        tail = bounded.read(65557)
        position = tail.rfind(b'PK\x05\x06')
        if position < 0 or len(tail) - position < 22:
            raise Blocker('zip_eocd', filename)
        _, disk, directory_disk, disk_count, count, size, offset, comment = struct.unpack('<4s4H2LH', tail[position:position + 22])
        if disk or directory_disk or disk_count != count or count == 65535 or size == 0xffffffff or offset == 0xffffffff:
            raise Blocker('zip_multidisk_or_zip64', filename)
        eocd_offset = before.st_size - len(tail) + position
        if position + 22 + comment != len(tail) or size > 2 * ENTRY_CAP or count > 10000 or offset + size != eocd_offset:
            raise Blocker('zip_directory_bounds', filename)
        bounded.seek(0)
        with zipfile.ZipFile(bounded) as archive:
            infos = archive.infolist()
            if len(infos) != count:
                raise Blocker('zip_member_count', filename)
            members, directories, total_size = {}, set(), 0
            for item in infos:
                canonical = safe_name(item.filename, directory=item.is_dir())
                mode = (item.external_attr >> 16) & 0xffff
                if stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR} or item.flag_bits & 1:
                    raise Blocker('zip_link_or_encrypted', item.filename)
                if canonical in members or canonical in directories:
                    raise Blocker('zip_duplicate', item.filename)
                if item.file_size > 128 * ENTRY_CAP or item.compress_size > 128 * ENTRY_CAP or item.header_offset < 0 or item.header_offset >= offset:
                    raise Blocker('zip_entry_bounds', item.filename)
                if item.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    raise Blocker('zip_compression', item.filename)
                total_size += item.file_size
                if total_size > 256 * ENTRY_CAP:
                    raise Blocker('zip_expansion_bounds', filename)
                if item.is_dir():
                    directories.add(canonical)
                else:
                    members[canonical] = item
            # Reject file/directory prefix collisions, not just duplicate strings.
            for member in [*members, *directories]:
                for parent in PurePosixPath(member).parents:
                    if str(parent) in members:
                        raise Blocker('zip_prefix_collision', member)
            metadata_paths = [key for key in members if key.endswith('.dist-info/METADATA')]
            if len(metadata_paths) != 1:
                raise Blocker('wheel_metadata_count', filename)
            prefix = metadata_paths[0].rsplit('/', 1)[0]
            dist_name, dist_version = prefix[:-len('.dist-info')].rsplit('-', 1)
            if canonicalize_name(dist_name) != canonicalize_name(name) or Version(dist_version) != version:
                raise Blocker('dist_info_identity', filename)

            def member_data(key):
                if key not in members or members[key].file_size > ENTRY_CAP or members[key].compress_size > ENTRY_CAP:
                    raise Blocker('metadata_entry_size_or_missing', key)
                data = archive.read(key)
                budget.take(len(data))
                if len(data) > ENTRY_CAP:
                    raise Blocker('metadata_entry_size', key)
                return data

            metadata_data = member_data(prefix + '/METADATA')
            wheel_data = member_data(prefix + '/WHEEL')
            record_data = member_data(prefix + '/RECORD')
            metadata = headers(metadata_data, filename)
            if canonicalize_name(exactly_one(metadata, 'Name', filename)) != canonicalize_name(name) or Version(exactly_one(metadata, 'Version', filename)) != version:
                raise Blocker('metadata_identity', filename)
            metadata_version = exactly_one(metadata, 'Metadata-Version', filename)
            if metadata_version not in {'2.1', '2.2', '2.3', '2.4', '2.5'}:
                raise Blocker('metadata_version', metadata_version)
            requires_python = exactly_one(metadata, 'Requires-Python', filename, required=False)
            if requires_python and not SpecifierSet(requires_python).contains(python_version, prereleases=True):
                raise Blocker('requires_python', f'{filename}: {requires_python}')
            wheel = headers(wheel_data, filename)
            if exactly_one(wheel, 'Wheel-Version', filename) != '1.0':
                raise Blocker('wheel_version', filename)
            if exactly_one(wheel, 'Root-Is-Purelib', filename).lower() not in {'true', 'false'}:
                raise Blocker('wheel_purelib', filename)
            declared_tags = set()
            for tag in wheel.get_all('Tag', []):
                declared_tags.update(parse_tag(str(tag)))
            if declared_tags != file_tags:
                raise Blocker('wheel_tag_identity', filename)
            rows = {}
            for row in csv.reader(io.StringIO(record_data.decode('utf-8'), newline='')):
                if len(row) != 3:
                    raise Blocker('record_columns', filename)
                key, recorded_hash, recorded_size = row
                safe_name(key)
                if key in rows or key not in members:
                    raise Blocker('record_duplicate_or_unknown', key)
                rows[key] = (recorded_hash, recorded_size)
            optional_signatures = {prefix + '/RECORD.jws', prefix + '/RECORD.p7s'}
            if set(members) - set(rows) - optional_signatures:
                raise Blocker('record_missing_members', filename)
            record_key = prefix + '/RECORD'
            if rows.get(record_key) != ('', ''):
                raise Blocker('record_self', filename)
            verified = 0
            for key, (recorded_hash, recorded_size) in rows.items():
                if key == record_key:
                    continue
                if not recorded_size.isdecimal() or int(recorded_size) != members[key].file_size or '=' not in recorded_hash:
                    raise Blocker('record_size_or_hash', key)
                algorithm, encoded = recorded_hash.split('=', 1)
                if algorithm not in {'sha256', 'sha384', 'sha512'}:
                    raise Blocker('record_weak_hash', key)
                expected = base64.b64decode(encoded + '=' * (-len(encoded) % 4), altchars=b'-_', validate=True)
                computed = hashlib.new(algorithm)
                with archive.open(key) as payload:
                    for chunk in iter(lambda: payload.read(65536), b''):
                        budget.take(len(chunk))
                        computed.update(chunk)  # Hash bytes only; never extract/import them.
                if computed.digest() != expected:
                    raise Blocker('record_payload_hash', key)
                verified += 1
            after = os.fstat(opened.fileno())
            identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
            if identity(before) != identity(after):
                raise Blocker('artifact_changed_during_read', filename)
    return {
        'name': canonicalize_name(name), 'version': str(version), 'filename': filename,
        'artifact_sha256': expected_hash, 'artifact_bytes': before.st_size,
        'matched_tags': matches, 'requires_python': requires_python,
        'metadata_version': metadata_version,
        'requires_dist': [str(value) for value in metadata.get_all('Requires-Dist', [])],
        'provides_extra': sorted(canonicalize_name(str(value)) for value in metadata.get_all('Provides-Extra', [])),
        'metadata_sha256': sha(metadata_data), 'wheel_sha256': sha(wheel_data), 'record_sha256': sha(record_data),
        'record_payloads_verified': verified, 'zip_members': len(infos),
        'optional_signature_files': sorted(set(members) & optional_signatures),
        'declared_uncompressed_bytes': total_size,
    }


def fixed_closure(roots, pins, obtain, environment):
    """Validate the single fixed version per name; no version search/substitution."""
    selected, extras, evidence, pending, previous_active = {}, {}, {}, deque(), {}

    def require(requirement, parent):
        if requirement.url:
            raise Blocker('direct_url_dependency', str(requirement))
        name = canonicalize_name(requirement.name)
        if name not in pins:
            raise Blocker('missing_locked_distribution', f'{parent}: {requirement}')
        version = Version(pins[name])
        if not requirement.specifier.contains(version):
            raise Blocker('version_constraint', f'{parent}: {requirement}; pinned {version}')
        requested = {canonicalize_name(extra) for extra in requirement.extras}
        old = extras.get(name)
        if old is None or not requested <= old:
            extras[name] = (old or set()) | requested
            pending.append(name)
        return name

    for root in roots:
        require(Requirement(root), '<test-scope-root>')
    iterations = 0
    while pending:
        iterations += 1
        if iterations > 1000:
            raise Blocker('closure_iterations', 'fixed-point bound exceeded')
        name = pending.popleft()
        if name not in selected:
            selected[name] = obtain(name, pins[name])
            if selected[name]['name'] != name or Version(selected[name]['version']) != Version(pins[name]):
                raise Blocker('selected_identity', name)
        record = selected[name]
        if not extras[name] <= set(record['provides_extra']):
            raise Blocker('unknown_requested_extra', name)
        rows, active_requirements = [], set()
        for text in record['requires_dist']:
            requirement = Requirement(text)
            evaluations = {extra: requirement.marker.evaluate({**environment, 'extra': extra}, context='metadata') if requirement.marker else True for extra in sorted(extras[name]) or ['']}
            active = any(evaluations.values())
            rows.append({'requirement': text, 'marker_evaluations': evaluations, 'active': active,
                         'target': canonicalize_name(requirement.name), 'locked_version': pins.get(canonicalize_name(requirement.name))})
            if active:
                active_requirements.add(text)
                require(requirement, name)
        if not previous_active.get(name, set()) <= active_requirements:
            raise Blocker('nonmonotone_extra_closure', name)
        previous_active[name] = active_requirements
        evidence[name] = rows
    return selected, evidence, {name: sorted(value) for name, value in extras.items()}


def main():
    sys.dont_write_bytecode = True
    budget, attempted_network = Budget(), []

    def guard(event, arguments):
        forbidden = event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo'}
        if event == 'socket.__new__' and len(arguments) > 1:
            forbidden = arguments[1] in {socket.AF_INET, socket.AF_INET6}
        if forbidden:
            attempted_network.append(event)
            raise Blocker('network_attempt', event)

    sys.addaudithook(guard)
    report = {'started_at': datetime.now(UTC).isoformat(), 'status': 'INCOMPLETE', 'limits': {'read_and_evidence_bytes': CAP, 'metadata_entry_bytes': ENTRY_CAP, 'wheel_inventory_count': 141}, 'roots': list(ROOTS)}
    inspected, inventory = {}, []
    try:
        manifest = read_data(PROVENANCE / 'SHA256SUMS', budget, expected='85637a307d48615233471efb342c0e6faad55ef8efa146c5ed6850eb44f11da4')
        evidence_name = 'evidence-20261030T222449706209Z.json'
        expected_evidence = next(line.split('  ', 1)[0] for line in manifest.decode().splitlines() if line.endswith('  ' + evidence_name))
        provenance_raw = read_data(PROVENANCE / evidence_name, budget, maximum=2 * ENTRY_CAP, expected=expected_evidence)
        provenance = json.loads(provenance_raw)
        record_raw = read_data(BUNDLE / 'locks/gate6k-ARTIFACTS.json', budget, expected='9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837')
        lock_raw = read_data(BUNDLE / 'locks/requirements-versions.txt', budget, expected='b07d5613eb50547b99229b2230bf90bd9d884dfcc869ecc025ffb003449d680a')
        records, pins = json.loads(record_raw), {}
        for line in lock_raw.decode().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            requirement = Requirement(line)
            specs = list(requirement.specifier)
            name = canonicalize_name(requirement.name)
            if len(specs) != 1 or specs[0].operator != '==' or '*' in specs[0].version or requirement.marker or requirement.extras or requirement.url or name in pins:
                raise Blocker('exact_version_lock', line)
            pins[name] = str(Version(specs[0].version))
        if len(pins) != 127:
            raise Blocker('pin_inventory_count', str(len(pins)))
        record_by_name = {canonicalize_name(key.split(':', 1)[1]): row for key, row in records.items() if key.startswith('distribution:')}
        if len(record_by_name) != 127:
            raise Blocker('artifact_record_count', str(len(record_by_name)))
        wheels = provenance['dependency_checks']['wheel_members']
        if len(wheels) != 141:
            raise Blocker('wheel_inventory_count', str(len(wheels)))
        by_digest = {}
        for relative, row in sorted(wheels.items()):
            safe_name(relative)
            filename = PurePosixPath(relative).name
            name, version, build, tags = parse_wheel_filename(filename)
            inventory.append({'relative_path': relative, 'name': canonicalize_name(name), 'version': str(version), 'sha256': row['sha256'], 'bytes': row['bytes'], 'filename_tags': sorted(str(tag) for tag in tags)})
            by_digest.setdefault(row['sha256'], []).append(relative)
        environment, tags = default_environment(), set(sys_tags())
        report.update({'environment': environment, 'python': sys.version, 'executable': sys.executable, 'soabi': sysconfig.get_config_var('SOABI'),
                       'packaging_tool': {'version': importlib.metadata.version('packaging'), 'origin': packaging.__file__},
                       'supported_tags': sorted(str(tag) for tag in tags), 'inputs': {'artifact_record_sha256': sha(record_raw), 'version_lock_sha256': sha(lock_raw), 'provenance_evidence_sha256': sha(provenance_raw)}, 'inventory': inventory})

        def obtain(name, version):
            row = record_by_name.get(name)
            if not row or Version(row['version']) != Version(version):
                raise Blocker('artifact_pin_identity', name)
            choices = by_digest.get(row['sha256'], [])
            if not choices:
                raise Blocker('pinned_wheel_missing', name)
            # Identical pinned bytes may be retained in target and verifier-tool
            # directories. Choose one target copy before hashing; never fall back
            # to another artifact if that selected copy fails verification.
            relative = sorted(choices, key=lambda value: (not value.startswith('artifacts/wheels/'), value))[0]
            entry = inspect_wheel(BUNDLE / relative, PurePosixPath(relative).name, row['sha256'], budget, tags, Version(environment['python_full_version']))
            entry['relative_path'] = relative
            entry['same_pinned_hash_paths_in_retained_inventory'] = sorted(choices)
            entry['record_provenance'] = row.get('provenance_record')
            inspected[name] = entry
            return entry

        root_requirements = [f'{name}=={pins[canonicalize_name(name)]}' for name in ROOTS]
        selected, edges, extras = fixed_closure(root_requirements, pins, obtain, environment)
        report.update({'status': 'METADATA_CLOSURE_VALIDATED_NOT_INSTALLED', 'root_requirements': root_requirements, 'selected': selected, 'dependency_edges': edges, 'activated_extras': extras,
                       'selected_count': len(selected), 'selected_artifact_bytes': sum(row['artifact_bytes'] for row in selected.values()), 'declared_uncompressed_bytes': sum(row['declared_uncompressed_bytes'] for row in selected.values())})
    except Exception as error:
        report.update({'status': 'BLOCKED_NO_COMPLETE_LOCK', 'blocker': {'code': error.code if isinstance(error, Blocker) else type(error).__name__, 'detail': error.detail if isinstance(error, Blocker) else str(error)}, 'inspected_before_blocker': inspected, 'inventory': inventory})
    report.update({'finished_at': datetime.now(UTC).isoformat(), 'bounded_read_bytes': budget.used, 'network_attempts': attempted_network,
                   'forbidden_modules_imported': sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN_IMPORTS),
                   'limits_of_claim': ['No install/extraction/sys.path injection/payload import or runtime integration.', 'Tag/marker/RECORD compatibility does not qualify native libraries, ABI execution, installed origin, publisher signatures or current application behavior.']})
    if report['forbidden_modules_imported']:
        report['status'] = 'BLOCKED_NO_COMPLETE_LOCK'
        report['blocker'] = {'code': 'forbidden_payload_import', 'detail': str(report['forbidden_modules_imported'])}
    tool_files = {}
    for name, module in sorted(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if name == 'packaging' or name.startswith('packaging.'):
            if path:
                tool_files[name] = {'path': path, 'sha256': sha(read_data(path, budget))}
    report['normal_tool_module_identities'] = tool_files
    report['bounded_read_bytes'] = budget.used
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
    encoded = (json.dumps(report, indent=2) + '\n').encode()
    budget.take(len(encoded))
    target = PACKET / f'evidence-{stamp}.json'
    with target.open('xb') as handle:
        handle.write(encoded)
    if report['status'] == 'METADATA_CLOSURE_VALIDATED_NOT_INSTALLED':
        lines = ['# PROPOSED metadata-validated fixed closure only; not installed or authorized for execution.\n', '# Use --require-hashes and --no-index only in a separately scoped bounded integration unit.\n']
        for name, row in sorted(report['selected'].items()):
            lines.append(f"{name}=={row['version']} --hash=sha256:{row['artifact_sha256']}\n")
        payload = ''.join(lines).encode()
        budget.take(len(payload))
        with (PACKET / f'proposed-closure-{stamp}.lock').open('xb') as handle:
            handle.write(payload)
    print(json.dumps({'evidence': target.name, 'status': report['status'], 'selected_count': report.get('selected_count'), 'bounded_read_and_evidence_bytes': budget.used, 'blocker': report.get('blocker')}, indent=2))
    return 0 if report['status'] == 'METADATA_CLOSURE_VALIDATED_NOT_INSTALLED' else 2


if __name__ == '__main__':
    raise SystemExit(main())

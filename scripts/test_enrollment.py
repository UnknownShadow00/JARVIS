"""Reviewed coverage of all Python files under tests; no discovery execution."""
import hashlib
import json
from gauntlet_protocol import InvalidEvidence

ENROLLMENT_SHA256 = '54b44473166f3cd674c5dd5022870c334c378029e68cf2112470f27d2cb7b28b'

def check_enrollment(root, path, expected_digest=ENROLLMENT_SHA256):
    try:
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected_digest:
            raise ValueError()
        policy=json.loads(raw)
        if set(policy)!= {'version','modules'} or policy['version']!=1:
            raise ValueError()
        actual={str(p.relative_to(root)) for p in (root/'tests').rglob('*.py') if '__pycache__' not in p.parts}
        if actual!=set(policy['modules']):
            raise ValueError()
        for name,entry in policy['modules'].items():
            if not name.startswith('tests/') or '..' in name.split('/') or any((root.joinpath(*name.split('/')[:i])).is_symlink() for i in range(1, len(name.split('/'))+1)):
                raise ValueError()
            if set(entry)!= {'disposition','reason','sha256'} or entry['disposition'] not in {'required','negative_fixture','support','excluded_offline_scope','excluded_live_or_hardware'} or not entry['reason']:
                raise ValueError()
            if hashlib.sha256((root/name).read_bytes()).hexdigest()!=entry['sha256']:
                raise ValueError()
        return policy
    except (OSError,ValueError,KeyError,TypeError):
        raise InvalidEvidence('test_enrollment_mismatch') from None

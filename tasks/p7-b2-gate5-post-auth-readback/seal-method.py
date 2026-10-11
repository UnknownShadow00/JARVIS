"""Seal only the new Gate5C evidence/task directories; preserve earlier packets."""
from pathlib import Path
import hashlib
import json
import subprocess

R = Path('/home/jarvis/JARVIS')
E = Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate5-post-auth-readback')
T = R / 'tasks/p7-b2-gate5-post-auth-readback'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def seal(directory):
    members = sorted(p for p in directory.iterdir() if p.name != 'SHA256SUMS')
    assert all(p.is_file() and not p.is_symlink() for p in members)
    index = directory / 'SHA256SUMS'
    assert not index.exists()
    index.write_text(''.join(digest(p) + '  ' + p.name + '\n' for p in members))
    checks = {}
    for line in index.read_text().splitlines():
        h, name = line.split(None, 1)
        p = directory / name
        assert p.parent == directory
        checks[name] = digest(p) == h
    assert all(checks.values()) and len(checks) == len(members)
    return {'sha256_of_SHA256SUMS': digest(index), 'members': len(members), 'verified': True}


(E / 'final-git-status.txt').write_text(subprocess.check_output(
    ['git', 'status', '--short'], cwd=R, text=True))
proof = json.loads((E / 'decision-checks.json').read_text())
assert all(proof['mandatory_closed_state_requirements'].values())
assert proof['Gate6_authorized'] is False
evidence = seal(E)
(T / 'SEAL.txt').write_text(
    'Canonical evidence: ' + str(E) + '\nSHA256(SHA256SUMS): ' +
    evidence['sha256_of_SHA256SUMS'] + '\nMembers: ' + str(evidence['members']) +
    '\nAll members and seal verified. Prior evidence preserved.\n')
task = seal(T)
for directory in (E, T):
    for p in directory.iterdir():
        p.chmod(0o400)
    directory.chmod(0o500)
print(json.dumps({'evidence': evidence, 'task': task}, indent=2))

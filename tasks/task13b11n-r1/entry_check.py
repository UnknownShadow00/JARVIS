"""Read-only canonical baseline verification. Prints only identity/hash evidence."""
import hashlib
import json
from pathlib import Path
import subprocess

PROD = Path('/home/jarvis/JARVIS')
EVIDENCE = Path('/home/jarvis/.hermes-poc/evidence')
HERMES = Path('/home/jarvis/.hermes-poc/hermes-agent')


def run(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    expected = '4885c4f7ca35f2395fab3497e6ce009d36b742be'
    assert run('git', 'rev-parse', 'HEAD', cwd=PROD) == expected
    assert run('git', 'rev-parse', 'HEAD^', cwd=PROD) == '8a70d179c527f2912522920918f70a68ee213386'
    assert not run('git', 'status', '--porcelain', cwd=PROD)
    assert not (PROD / 'app/brain/hermes_adapter.py').exists()
    assert not (PROD / 'app/execution/pipeline.py').exists()
    assert run('git', 'rev-parse', 'HEAD', cwd=HERMES) == '2237be355906fbe6065ce1815711eee52b2d646e'
    assert not run('git', 'status', '--porcelain', cwd=HERMES)
    processes = [p for p in run('ps', '-eo', 'comm=').splitlines() if 'hermes' in p.lower() or 'ollama' in p.lower()]
    assert not processes
    config = (PROD / 'config.yaml').read_text()
    assert 'mode: "legacy"' in config and 'hermes_brain: false' in config and 'hermes_enabled: false' in config
    manifest = EVIDENCE / 'task13b11m-response-builder/SHA256SUMS'
    assert sha(manifest) == '503644df20a56b6ce631aec17ce91b24b87e93427b9f2b1e9b947e0a3f213d28'
    assert len(manifest.read_text().splitlines()) == 44
    assert len([p for p in manifest.parent.rglob('*') if p.is_file()]) == 45
    seals = {}
    for seal in sorted(EVIDENCE.rglob('SHA256SUMS')):
        subprocess.run(['sha256sum', '-c', '--quiet', 'SHA256SUMS'], cwd=seal.parent, check=True)
        seals[str(seal.relative_to(EVIDENCE))] = sha(seal)
    tracked = run('git', 'ls-files', cwd=PROD).splitlines()
    hashes = {name: sha(PROD / name) for name in tracked if (PROD / name).is_file()}
    print(json.dumps({'production_head': expected, 'clean': True, 'adapter_absent': True,
        'pipeline_absent': True, 'mode': 'legacy', 'hermes_flags': False,
        'hermes_head': run('git', 'rev-parse', 'HEAD', cwd=HERMES), 'hermes_processes': processes,
        'verified_seals': seals, 'tracked_hashes': hashes}, indent=2, sort_keys=True))

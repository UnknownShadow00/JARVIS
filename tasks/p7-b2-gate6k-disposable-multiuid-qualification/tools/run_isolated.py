"""Copy only the isolated candidate to a fresh Core /tmp test stage.
No production application writes, package installation or credential environment.
"""
import json, os, shlex, subprocess, sys, tarfile
from pathlib import Path

SOURCE = Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r1')
EVIDENCE = Path(__file__).resolve().parent.parent/'evidence'
if (EVIDENCE.parent/'SHA256SUMS').exists():raise RuntimeError('sealed packet; use a new versioned task')
label = sys.argv[1]
if not label.replace('-','').isalnum():raise ValueError('label')
stage_parent = os.environ.get('STAGE_PARENT','/home/jarvis')
if stage_parent not in ('/tmp','/home/jarvis'):raise ValueError('stage parent')
archive = SOURCE.parent/(label+'.tar')
if archive.exists() or (EVIDENCE/(label+'-launch.txt')).exists():raise FileExistsError('use a unique run label')
with tarfile.open(archive,'w') as tar:
    for p in sorted(SOURCE.rglob('*')):
        if p.is_symlink():raise ValueError('symlink')
        if p.is_file():tar.add(p,arcname=str(p.relative_to(SOURCE)),recursive=False)
    extra=Path(__file__).resolve().parent/'gate6j_wire_test.py'
    if extra.exists():tar.add(extra,arcname='gate6j_wire_test.py',recursive=False)
args = ' '.join(shlex.quote(a) for a in sys.argv[2:])
remote = f'''set -u
stage=$(mktemp -d {stage_parent}/jarvis-gate6k-{label}-XXXXXXXX)
chmod 700 "$stage"
tar -xf - -C "$stage"
mkdir -m 700 "$stage/home"
env -i PATH=/usr/bin:/bin HOME="$stage/home" TMPDIR="$stage" P7_OFFLINE_STAGE="$stage" PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/jarvis/JARVIS/.venv/bin/python -B "$stage/supervise_tests.py" {shlex.quote(label)} {args} > "$stage/{label}-stdout.txt" 2>&1
rc=$?
printf 'STAGE=%s RC=%s\\n' "$stage" "$rc"
cat "$stage/{label}-stdout.txt"
exit "$rc"
'''
with archive.open('rb') as inp, (EVIDENCE/(label+'-launch.txt')).open('w') as log:
    result = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','jarvis@192.168.0.162',remote],stdin=inp,stdout=log,stderr=subprocess.STDOUT)
print((EVIDENCE/(label+'-launch.txt')).read_text())
sys.exit(result.returncode)

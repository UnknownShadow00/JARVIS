"""Collect bounded, known offline-test artifacts and verify each run's source."""
from pathlib import Path
import hashlib,io,json,re,shlex,subprocess,tarfile

TASK=Path(__file__).resolve().parent.parent
if (TASK/'SHA256SUMS').exists():raise RuntimeError('sealed packet; use a new versioned task')
ROOT=Path('/home/nexus/.local/share/jarvis-gate6g-hardening')
labels=__import__('sys').argv[1:] or ('g6g-new-1','g6g-focused-1','g6g-full-1','g6g-focused-final','g6g-full-final')
for label in labels:
    launch=(TASK/'evidence'/(label+'-launch.txt')).read_text()
    stage=re.search(r'^STAGE=((?:/tmp|/home/jarvis)/jarvis-gate6g-[A-Za-z0-9-]+) RC=\d+$',launch,re.M).group(1)
    expected={}
    with tarfile.open(ROOT/(label+'.tar')) as tar:
        for member in tar.getmembers():
            if member.isfile():expected[member.name]=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    script=f'''import hashlib,json,sys,tarfile
from pathlib import Path
stage=Path({stage!r});expected=json.loads({json.dumps(expected)!r})
bad=[n for n,h in expected.items() if not (stage/n).is_file() or hashlib.sha256((stage/n).read_bytes()).hexdigest()!=h]
result={{'files':len(expected),'mismatches':bad}}
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as tar:
 import io
 raw=(json.dumps(result,indent=2)+'\\n').encode();m=tarfile.TarInfo('source-verification.json');m.size=len(raw);tar.addfile(m,io.BytesIO(raw))
 paths=sorted(set(stage.glob('*.json'))|set(stage.glob('*.txt'))|set((stage/'g6f-artifacts').glob('*.json')))
 for p in paths:
  if p.is_file() and not p.is_symlink():tar.add(p,arcname=str(p.relative_to(stage)),recursive=False)
'''
    result=subprocess.run(['ssh','-o','BatchMode=yes','jarvis@192.168.0.162','python3 -B -c '+shlex.quote(script)],capture_output=True,check=True)
    dest=TASK/'evidence'/'runs'/label
    dest.mkdir(parents=True,exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as tar:
        tar.extractall(dest,filter='data')
    summary={'label':label,'stage':stage,'expected_source_files':len(expected),**json.loads((dest/'source-verification.json').read_text())}
    print(json.dumps(summary))

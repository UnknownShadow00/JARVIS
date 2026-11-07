"""Exclusive artifact manifest publication after completed read-only verification."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent
assert json.loads((P/'FINAL-VERIFICATION.json').read_text())['status']=='PASS'
links={str(f.relative_to(P)):str(f.readlink()) for f in P.rglob('*') if f.is_symlink()}
with (P/'SYMLINKS.json').open('x') as f:json.dump(links,f,indent=2,sort_keys=True);f.write('\n')
rows=[]
for f in sorted(P.rglob('*')):
 if f.is_symlink():continue
 if f.is_file() and f!=P/'SHA256SUMS':rows.append((str(f.relative_to(P)),hashlib.sha256(f.read_bytes()).hexdigest()))
raw=''.join(h+'  '+n+'\n' for n,h in rows).encode()
fd=os.open(P/'SHA256SUMS',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
print(json.dumps({'sealed_artifact_files':len(rows),'SHA256SUMS_sha256':hashlib.sha256(raw).hexdigest()},indent=2))

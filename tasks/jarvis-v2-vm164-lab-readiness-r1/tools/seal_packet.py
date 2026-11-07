"""Exclusive new-packet seal; never replaces a published manifest."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parents[1]
assert json.loads((P/'evidence/final-verification.json').read_text())['status']=='PASS_PREPARATION_ENGINEERING_ONLY'
assert (P/'COMPLETION-LOG.json').is_file()
links={str(f.relative_to(P)):str(f.readlink()) for f in P.rglob('*') if f.is_symlink()}
with (P/'SYMLINKS.json').open('x') as f:json.dump(links,f,indent=2,sort_keys=True);f.write('\n')
# Restrict the newly produced delivery archive against accidental edits. This
# changes no existing source, credential, principal or protected installation.
build=json.loads((P/'BUNDLE.json').read_text());(P/build['bundle']).chmod(0o444)
rows={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and not f.is_symlink() and f!=P/'SHA256SUMS'}
raw=''.join(h+'  '+n+'\n' for n,h in rows.items()).encode();fd=os.open(P/'SHA256SUMS',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
print(json.dumps({'sealed_files':len(rows),'symlinks_recorded':len(links),'artifact_manifest_sha256':hashlib.sha256(raw).hexdigest()},indent=2))

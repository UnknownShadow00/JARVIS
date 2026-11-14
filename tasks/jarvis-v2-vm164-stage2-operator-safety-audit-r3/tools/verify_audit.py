"""Read-only local audit seal verification; no host operations or authorization."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def verify():
 declared={}
 for line in (P/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);q=Path(n)
  assert not q.is_absolute() and '..' not in q.parts and n not in declared
  f=P/q;assert not f.is_symlink() and sha(f.read_bytes())==h,n
  declared[n]=h
 actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS'}
 assert actual==set(declared)
 manifest=json.loads((P/'MANIFEST.json').read_text())
 assert set(manifest['files'])==actual-{'MANIFEST.json'}
 for n,r in manifest['files'].items():
  raw=(P/n).read_bytes();assert r==dict(bytes=len(raw),sha256=sha(raw))
 result=json.loads((P/'RESULT.json').read_text());assert result['verdict']=='REJECT' and result['stage2_authorized'] is False
 return dict(status='PASS_LOCAL_AUDIT_INTEGRITY',files=len(actual)+1,verdict=result['verdict'],stage2_authorized=False,external_custody_verified=False)
if __name__=='__main__':print(json.dumps(verify(),indent=2))

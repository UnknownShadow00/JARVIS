"""Read/hash/parse only. Verifies this offline packet and unchanged R3 bytes."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OMIT={'MANIFEST.json','SEAL.json'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def inventory():
 result={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_symlink():raise ValueError('symlink not allowed')
  if p.is_file() and str(p.relative_to(ROOT)) not in OMIT:
   raw=p.read_bytes();result[str(p.relative_to(ROOT))]={'sha256':sha(raw),'bytes':len(raw)}
 return result

def verify():
 manifest_raw=(ROOT/'MANIFEST.json').read_bytes()
 manifest=json.loads(manifest_raw);seal=json.loads((ROOT/'SEAL.json').read_bytes())
 if sha(manifest_raw)!=seal['manifest_sha256'] or inventory()!=manifest['files']:raise ValueError('packet changed')
 index=json.loads((ROOT/'evidence/R3-READ-INDEX.json').read_bytes())
 r3=ROOT.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3'
 actual={str(p.relative_to(r3)) for p in r3.rglob('*') if p.is_file()}
 if actual!=set(index):raise ValueError('R3 inventory changed')
 for name,row in index.items():
  path=r3/name;raw=path.read_bytes()
  if path.is_symlink() or sha(raw)!=row['sha256'] or len(raw)!=row['bytes']:raise ValueError('R3 bytes changed')
 for p in ROOT.rglob('*.py'):ast.parse(p.read_bytes())
 for p in ROOT.rglob('*.json'):json.loads(p.read_bytes())
 result=json.loads((ROOT/'evidence/OFFLINE-RESULTS.json').read_bytes())
 if result['status']!='PASS' or any(result[k] for k in ('failures','errors','skips')):raise ValueError('offline test result')
 for path,digest in result['source_sha256'].items():
  if sha((ROOT/path).read_bytes())!=digest:raise ValueError('source changed after tests')
 return {'status':'PASS_OFFLINE_PACKET_INTEGRITY','r3_files_unchanged':len(index),
 'packet_files':len(manifest['files']),'offline_tests':result['tests_run'],
 'manifest_sha256':seal['manifest_sha256'],'stage2_authorized':False,
 'live_qualification':False,'expiration_guaranteed':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))

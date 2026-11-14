"""Read-only offline content/provenance verification. Never runs host commands."""
import hashlib,json,stat,subprocess,sys
from pathlib import Path
REPORT=Path(__file__).resolve().parents[1]
AUDIT='tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2'
R2='tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r2'
AUDIT_PIN='e721c7769c3644fe8d6f7ef74d66d7e1c2e99b1614f9a841c8aba2bcf0db0ddf'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(value,message):
 if not value:raise ValueError(message)
def verify(checkout,commit):
 root=Path(checkout).resolve();inventory=json.loads((REPORT/'VERIFIED-FILE-INVENTORY.json').read_bytes())
 def git(*args):return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True,timeout=30).stdout
 need(git('rev-parse','HEAD').decode().strip()==commit,'checkout HEAD mismatch')
 need(not git('status','--porcelain'),'checkout not clean')
 need(git('show','-s','--format=%P',commit).decode().strip()==inventory['parent'],'wrong parent')
 raw=(root/AUDIT/'MANIFEST.json').read_bytes();need(sha(raw)==AUDIT_PIN,'independent audit manifest pin')
 audit=json.loads(raw)['files']
 for rel,rec in audit.items():
  b=(root/AUDIT/rel).read_bytes();need(sha(b)==rec['sha256'] and len(b)==rec['bytes'],'audit payload changed: '+rel)
 reviewed=json.loads((root/AUDIT/'evidence/INPUT-INVENTORY.json').read_bytes())
 for name,files in reviewed.items():
  folder=root/'tasks'/name
  actual={str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
  need(actual==set(files),'missing/unexpected reviewed files: '+name)
  for rel,rec in files.items():
   p=folder/rel;need(stat.S_ISREG(p.lstat().st_mode),'nonregular reviewed file')
   for a in [p,*p.parents]:
    if a==root:break
    need(not a.is_symlink(),'symlink ancestry')
   b=p.read_bytes();need(sha(b)==rec['sha256'] and len(b)==rec['bytes'],'independent digest mismatch: '+str(p))
 rows=inventory['records'];expected={r['path'] for r in rows}
 changed=set(git('diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines())
 need(changed==expected,'commit inventory mismatch')
 for r in rows:
  b=git('cat-file','blob',commit+':'+r['path']);need(sha(b)==r['expected_sha256'],'committed content differs')
  need((root/r['path']).read_bytes()==b,'checkout differs from commit')
  mode=git('ls-tree',commit,'--',r['path']).decode().split()[0];need(mode==r['git_mode'],'Git mode mismatch')
  need(bool((root/r['path']).stat().st_mode&0o111)==(mode=='100755'),'executable bit mismatch')
 return {'status':'PASS_OFFLINE_BASELINE_INTEGRITY','commit':commit,'tree':git('rev-parse',commit+'^{tree}').decode().strip(),'parent':inventory['parent'],'added_files':len(rows),'reviewed_packet_files':sum(map(len,reviewed.values())),'r2_files':len(reviewed[Path(R2).name]),'source_modules':14,'audit_manifest_sha256':AUDIT_PIN,'clean_checkout':True}
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: verify_baseline.py CHECKOUT COMMIT')
 print(json.dumps(verify(sys.argv[1],sys.argv[2]),indent=2))

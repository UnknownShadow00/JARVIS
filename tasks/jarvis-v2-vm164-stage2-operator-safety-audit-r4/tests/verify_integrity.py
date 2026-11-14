"""Independent local file/Git verification. Never executes proposed host argv."""
from pathlib import Path
import json,hashlib,stat,os,subprocess,collections
A=Path(__file__).resolve().parents[1];cfg=json.loads((A/'evidence/WORKSPACE.json').read_bytes());W=Path(cfg['reviewed_worktree']);P=Path(cfg['reviewed_packet']);C=A.parents[1]
def sha(x):return hashlib.sha256(x).hexdigest()
def git(*a,cwd=W):
 r=subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stderr;return r.stdout.strip()
assert git('rev-parse','HEAD')=='5c5d5c2543ed469025ec6cf06b0545c9bdb5eaa6'
assert git('rev-parse','HEAD^{tree}')=='b0bfd1ea642a9d51ac580b152f2aa50c60aceb87'
assert git('rev-parse','HEAD^')=='d153ccd001d1f673b6110782da288e6d114d8762'
assert git('rev-parse','HEAD^^')=='5088a240943f2d39b67ca7d528ea8e5f7e51d6f9'
assert git('rev-parse','HEAD^^{tree}')=='20bb80f857ff9e205488f5e4eaa23d5f6a213e69'
assert not git('status','--porcelain=v1')
expected={}
for line in (P/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);assert name not in expected and not Path(name).is_absolute() and '..' not in Path(name).parts;expected[name]=digest;f=P/name;assert f.is_file() and not f.is_symlink() and sha(f.read_bytes())==digest
assert set(expected)=={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS'}
source=json.loads((P/'SOURCE-MANIFEST.json').read_bytes());src={f.name:sha(f.read_bytes()) for f in sorted((P/'src').glob('*.py'))};assert source['files']==src
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
assert sha(canonical(src))==source['stage2_source_sha256']
snapshot=json.loads((P/'evidence/PRESERVATION-BEFORE.json').read_bytes());coverage=collections.Counter();links=0;failed=[]
for name,record in snapshot.items():
 f=Path(name)
 try:
  if f.is_symlink():actual={'link':os.readlink(f)};links+=1
  else:actual={'mode':stat.S_IMODE(f.stat().st_mode),'sha256':sha(f.read_bytes())}
  if actual!=record:failed.append(name)
 except Exception:failed.append(name)
 rel=f.relative_to(C.parent);coverage['/'.join(rel.parts[:3])]+=1
assert len(snapshot)==49248 and not failed
changes=git('diff-tree','--no-commit-id','--name-only','-r','HEAD').splitlines();assert len(changes)==238 and all(n.startswith('tasks/'+P.name+'/') or n=='tasks/loop-log.md' for n in changes)
assert git('diff','--name-only',cwd=C)=='tasks/loop-log.md'
before=json.loads((A/'evidence/GIT-IDENTITY.json').read_bytes())
if (A/'evidence/LOG-APPEND-PROOF.json').exists():
 proof=json.loads((A/'evidence/LOG-APPEND-PROOF.json').read_bytes());log=(C/'tasks/loop-log.md').read_bytes()
 assert sha(log)==proof['result_sha256'] and sha(log[:proof['prefix_bytes']])==before['canonical_log_sha256']
else:assert sha(git('diff','--binary',cwd=C).encode()+b'\n')==before['canonical_diff_sha256'] # git helper strips final newline
assert (P/'FIRST-SUPERVISED-ACTION.json').read_bytes()==(A/'evidence/R3-FIRST-SUPERVISED-ACTION.json').read_bytes()
# Read all R4 text/source/test artifacts for content inventory, not an authenticity claim.
read_inventory={str(f.relative_to(P)):{'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in P.rglob('*') if f.is_file()}
(A/'evidence/REVIEWED-INPUT-INVENTORY.json').write_text(json.dumps(read_inventory,indent=2)+'\n')
a=['python3','-I','-B','-S',str(P/'src/verify_packet.py')];r=subprocess.run(a,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stderr
out={'status':'PASS_LOCAL_INTEGRITY','commit':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),'parent':git('rev-parse','HEAD^'),'reviewed_worktree_clean':True,'source_sha256':source['stage2_source_sha256'],'packet_files':len(read_inventory),'packet_manifest_sha256':sha((P/'SHA256SUMS').read_bytes()),'snapshot_entries':len(snapshot),'snapshot_symlinks':links,'snapshot_regular_files':len(snapshot)-links,'coverage':dict(sorted(coverage.items())),'mismatches':failed,'git_changed_paths':changes,'canonical_tracked_change':'preexisting loop-log plus verified audit-only append; original prefix hash preserved' if (A/'evidence/LOG-APPEND-PROOF.json').exists() else 'preexisting loop-log only; exact preaudit diff hash equal','first_action_equal':True,'candidate_integrity_helper':{'argv':a,'exit':r.returncode,'result':json.loads(r.stdout)},'limitations':['Snapshot covers enumerated VM164 task files in three repositories, not 49248 unique application files or the whole host.','Regular file digests/modes and literal link targets only. No independently protected evidence custody or proof of absence of past host activity.','Tracked application preservation supported by Git scope/status; untracked application files outside snapshot have no independent historical digest here.']}
(A/'evidence/INTEGRITY-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('git_changed_paths','coverage')},indent=2))

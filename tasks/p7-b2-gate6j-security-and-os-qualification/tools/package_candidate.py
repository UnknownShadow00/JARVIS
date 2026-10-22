from pathlib import Path
import hashlib,json,tarfile,difflib,shutil
TASK=Path(__file__).resolve().parent.parent
OLD=Path('/home/nexus/.local/share/jarvis-gate6i-runtime/release-r2')
NEW=Path('/home/nexus/.local/share/jarvis-gate6j-redteam/release-r2')
assert not (TASK/'SHA256SUMS').exists()
def inventory(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
old=inventory(OLD);new=inventory(NEW)
changed=[n for n in new if old.get(n)!=new[n]]
removed=sorted(set(old)-set(new));assert not removed
archive=NEW.parent/'gate6j-release-r2.tar';assert not archive.exists()
with tarfile.open(archive,'w') as tar:
 for n in new:tar.add(NEW/n,arcname=n,recursive=False)
with tarfile.open(archive) as tar:
 actual={m.name:hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in tar.getmembers() if m.isfile()}
assert actual==new
out=TASK/'evidence';patch=[]
for n in changed:
 dest=out/'source'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(NEW/n,dest)
 previous=(OLD/n).read_text().splitlines(True) if n in old else []
 patch.extend(difflib.unified_diff(previous,(NEW/n).read_text().splitlines(True),fromfile='gate6i/'+n,tofile='gate6j/'+n))
(out/'gate6i-to-gate6j.patch').write_text(''.join(patch))
(out/'FULL-SOURCE-SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in new.items()))
shutil.copyfile(NEW/'SOURCE-SHA256SUMS',out/'SOURCE-SHA256SUMS')
result={'candidate':str(NEW/'repo'),'source_manifest':hashlib.sha256((NEW/'SOURCE-SHA256SUMS').read_bytes()).hexdigest(),'source_members':len(new)-1,'inventory_members':len(new),'inventory_digest':hashlib.sha256((out/'FULL-SOURCE-SHA256SUMS').read_bytes()).hexdigest(),'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'changed':changed,'production_app_changes':[n for n in changed if n.startswith('repo/app/')]}
(out/'candidate-identity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

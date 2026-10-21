"""Versioned source identity and review patch; does not touch historical archives."""
from pathlib import Path
import difflib,hashlib,json,tarfile
root=Path('/home/nexus/.local/share/jarvis-gate6g-hardening/release-r1')
out=Path(__file__).resolve().parent.parent/'evidence'
if (out.parent/'SHA256SUMS').exists():raise RuntimeError('sealed packet; use a new versioned task')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(p for p in root.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in root.rglob('*'))
assert not any(set(p.relative_to(root).parts)&{'.git','.venv','__pycache__','.env'} for p in files)
assert not any(p.relative_to(root/'repo').parts[0] in ('data','logs') for p in files if root/'repo' in p.parents)
qual=[root/n for n in ('guard/sitecustomize.py','kernel_guard.py','offline_fixtures.py','run_tests.py','supervise_tests.py')]
source=sorted([(str(p.relative_to(root/'repo')),p) for p in files if root/'repo' in p.parents and (p.parent==root/'repo/candidate_v3' or p.parent==root/'repo/tests/execution' and p.name.startswith('v3') and p.suffix=='.py')]+[('qualification/'+str(p.relative_to(root)),p) for p in qual])
manifest=''.join(sha(p)+'  '+n+'\n' for n,p in source)
(out/'CANDIDATE-SOURCE-SHA256SUMS').write_text(manifest)
full=''.join(sha(p)+'  '+str(p.relative_to(root))+'\n' for p in files)
(out/'FULL-SOURCE-SHA256SUMS').write_text(full)
old={}
with tarfile.open(root.parent/'gate6f-release-r1.tar') as t:
 for m in t.getmembers():
  if m.isfile():old[m.name.removeprefix('./')]=t.extractfile(m).read()
changes=[];patch=[]
for p in files:
 n=str(p.relative_to(root));a=old.get(n);b=p.read_bytes()
 if a!=b:
  changes.append({'path':n,'before':hashlib.sha256(a).hexdigest() if a is not None else None,'after':sha(p)})
  patch.extend(difflib.unified_diff((a or b'').decode().splitlines(True),b.decode().splitlines(True),fromfile='gate6f/'+n,tofile='gate6g/'+n))
removed=sorted(set(old)-{str(p.relative_to(root)) for p in files})
assert not removed
(out/'source-changes.json').write_text(json.dumps(changes,indent=2)+'\n')
(out/'candidate-vs-gate6f.patch').write_text(''.join(patch))
archive=root.parent/'gate6g-release-r1.tar'
with tarfile.open(archive,'w') as tar:
 for p in files:tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
record={'revision':'Gate 6G release-r1','candidate_digest':hashlib.sha256(manifest.encode()).hexdigest(),'manifest_members':len(source),'full_manifest_digest':hashlib.sha256(full.encode()).hexdigest(),'full_manifest_members':len(files),'changed_files':len(changes),'removed_files':removed,'archive_sha256':sha(archive),'local_candidate_path':str(root/'repo'),'core_candidate_path':'/home/jarvis/.hermes-poc/gate6g-candidates/release-r1/repo','predecessor_candidate':'ff2444df135fcf8027d36cca9fa02fd7000884f88f78f76d74ddc68707dce733','kind':'SHA256 of sorted source/qualification SHA256SUMS bytes; NOT a Git commit','protection':'private same-UID isolated candidate; not immutable or a protected authority','no_runtime_or_credential_files':True}
(out/'candidate-identity.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))

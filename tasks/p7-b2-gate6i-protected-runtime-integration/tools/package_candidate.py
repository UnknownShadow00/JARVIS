from pathlib import Path
import hashlib,json,tarfile,difflib,shutil
P=Path(__file__).resolve().parent.parent
if (P/'SHA256SUMS').exists():raise RuntimeError('sealed packet')
old=Path('/home/nexus/.local/share/jarvis-gate6h-authority/release-r1')
root=Path('/home/nexus/.local/share/jarvis-gate6i-runtime/release-r2')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(p for p in root.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in root.rglob('*'))
full=''.join(f'{H(p)}  {p.relative_to(root)}\n' for p in files)
(P/'evidence/FULL-SOURCE-SHA256SUMS').write_text(full)
selected=[]
for p in files:
 n=p.relative_to(root).as_posix()
 if n.startswith('repo/candidate_v3/') or n.startswith('repo/tests/execution/v3_') or n.startswith('disposable/') or not n.startswith('repo/'):
  label=n[5:] if n.startswith('repo/') else n if n.startswith('disposable/') else 'qualification/'+n
  selected.append((label,p))
source=''.join(f'{H(p)}  {label}\n' for label,p in sorted(selected))
(P/'evidence/CANDIDATE-SOURCE-SHA256SUMS').write_text(source)
changes=[];patch=[]
for p in files:
 n=p.relative_to(root);previous=old/n
 if previous.exists() and H(previous)==H(p):continue
 changes.append(str(n));out=P/'evidence/source'/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
 patch.extend(difflib.unified_diff(previous.read_text().splitlines(True) if previous.exists() else [],p.read_text().splitlines(True),fromfile='gate6h/'+str(n),tofile='gate6i/'+str(n)))
assert not any(n.startswith('repo/app/') for n in changes)
(P/'evidence/gate6h-to-gate6i.patch').write_text(''.join(patch))
archive=root.parent/'gate6i-release-r2.tar'
if archive.exists():raise FileExistsError('archive already exists')
with tarfile.open(archive,'w') as tar:
 for p in files:tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
compiled=[]
for p in [*(root/'repo/app').rglob('*.py'),*(root/'repo/candidate_v3').glob('*.py'),*(root/'disposable').glob('*.py')]:compile(p.read_text(),str(p),'exec');compiled.append(str(p.relative_to(root)))
identity=dict(revision='Gate6I release-r2',candidate_path=str(root/'repo'),source_manifest_sha256=H(P/'evidence/CANDIDATE-SOURCE-SHA256SUMS'),source_members=len(selected),inventory_sha256=H(P/'evidence/FULL-SOURCE-SHA256SUMS'),inventory_members=len(files),archive_path=str(archive),archive_sha256=H(archive),source_changes=changes,compiled_modules=len(compiled),production_app_changes=0,predecessor_source_manifest='c874b50719a599e4e6a18f051b0395fb45e0b7cc3f0a8338aeca8206cddd9da2',protection='ISOLATED SAME-UID; actual multi-UID NOT RUN',production_factory='REFUSES')
(P/'evidence/candidate-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps(identity,indent=2))

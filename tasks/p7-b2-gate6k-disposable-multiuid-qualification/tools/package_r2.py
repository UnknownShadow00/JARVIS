from pathlib import Path
import ast,hashlib,json,tarfile,difflib,shutil
P=Path(__file__).resolve().parent.parent;E=P/'evidence';R=Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2');OLD=Path('/home/nexus/.local/share/jarvis-gate6j-redteam/release-r2')
if (P/'SHA256SUMS').exists():raise RuntimeError('SEALED')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name in ('SOURCE-SHA256SUMS','gate6j-to-gate6k.patch','archive-final.json','final-source-static-association.json'):
 target=E/('r1-'+name)
 if not target.exists():shutil.copyfile(E/name,target)
files=[f for f in sorted(R.rglob('*')) if f.is_file() and f.name!='SOURCE-SHA256SUMS'];assert not any('__pycache__' in str(f) for f in files)
manifest=''.join(sha(f)+'  '+str(f.relative_to(R))+'\n' for f in files);(R/'SOURCE-SHA256SUMS').write_text(manifest)
archive=R.parent/'gate6k-release-r2.tar'
with tarfile.open(archive,'x',format=tarfile.USTAR_FORMAT) as t:
 for f in sorted(R.rglob('*')):
  if f.is_file():
   m=t.gettarinfo(str(f),str(f.relative_to(R)));m.uid=m.gid=0;m.uname=m.gname='';m.mode=0o644;m.mtime=0
   with f.open('rb') as stream:t.addfile(m,stream)
identity=dict(candidate=str(R/'repo'),release=str(R),source_manifest=sha(R/'SOURCE-SHA256SUMS'),source_members=len(files),archive=str(archive),archive_sha256=sha(archive),archive_members=len(files)+1)
(E/'candidate-identity.json').write_text(json.dumps(identity,indent=2)+'\n');(E/'SOURCE-SHA256SUMS').write_text(manifest)
changed=[];diff=[]
for f in sorted(R.rglob('*')):
 if not f.is_file():continue
 name=str(f.relative_to(R));prior=OLD/name
 if not prior.exists() or prior.read_bytes()!=f.read_bytes():
  changed.append(name);diff.extend(difflib.unified_diff(prior.read_text().splitlines(True) if prior.exists() else [],f.read_text().splitlines(True),fromfile='gate6j/'+name,tofile='gate6k/'+name))
  target=E/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
(E/'changed-files.json').write_text(json.dumps(changed,indent=2)+'\n');(E/'gate6j-to-gate6k.patch').write_text(''.join(diff))
for f in files:
 if f.suffix=='.py':ast.parse(f.read_bytes(),filename=str(f))
(E/'syntax.json').write_text(json.dumps({'python_modules_parsed':sum(f.suffix=='.py' for f in files),'result':'PASS'})+'\n')
(P/'tools/run_r2.py').write_text((P/'tools/run_isolated.py').read_text().replace('release-r1','release-r2'))
print(json.dumps(identity))

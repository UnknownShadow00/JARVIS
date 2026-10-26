"""Create an exclusive source-only candidate; never package test runtime state."""
import ast,difflib,hashlib,io,json,os,shutil,sys,tarfile
from pathlib import Path
BASE=Path('/home/nexus/.local/share/jarvis-gate6k-preflight-fix')
OLD=Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2')
WORK=BASE/'release-r1';FINAL=BASE/'candidate-r1'
PACKET=Path(__file__).resolve().parent.parent;E=PACKET/'evidence'
if (PACKET/'SHA256SUMS').exists():raise RuntimeError('SEALED_PACKET')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
oldrows=dict((n,h) for h,n in (r.split('  ',1) for r in (OLD/'SOURCE-SHA256SUMS').read_text().splitlines()))
assert all(sha(OLD/n)==h for n,h in oldrows.items())
assert sha(OLD/'SOURCE-SHA256SUMS')=='5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03'
names=sorted(set(oldrows)|{'disposable/environment_probe.py','disposable/compatibility_tests.py','disposable/preflight_report.py'})
os.umask(0o022)
FINAL.mkdir(mode=0o700)
diff=[];changed=[]
for name in names:
    src=WORK/name
    assert src.is_file() and not src.is_symlink() and src.stat().st_nlink==1
    dest=FINAL/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());dest.chmod(0o644)
    if src.suffix=='.py':ast.parse(src.read_bytes(),filename=name)
    if name not in oldrows or sha(src)!=oldrows[name]:
        changed.append(name)
        before=(OLD/name).read_text().splitlines(True) if name in oldrows else []
        diff.extend(difflib.unified_diff(before,src.read_text().splitlines(True),fromfile='gate6k/'+name,tofile='vm163-fix/'+name))
        copy=E/'changed-source'/name;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(src.read_bytes())
assert all(not n.startswith('repo/') for n in changed),'APPLICATION_CHANGE_FORBIDDEN'
manifest=''.join(sha(FINAL/n)+'  '+n+'\n' for n in names)
(FINAL/'SOURCE-SHA256SUMS').write_text(manifest);(FINAL/'SOURCE-SHA256SUMS').chmod(0o644)
archive=BASE/'gate6k-vm163-preflight-r1.tar'
with tarfile.open(archive,'x',format=tarfile.USTAR_FORMAT) as t:
    for name in sorted([*names,'SOURCE-SHA256SUMS']):
        data=(FINAL/name).read_bytes();m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o644;m.uid=m.gid=0;m.mtime=0
        t.addfile(m,io.BytesIO(data))
bootstrap=BASE/'safe_extract_vm163_r1.py';bootstrap.write_bytes((FINAL/'disposable/safe_extract.py').read_bytes());bootstrap.chmod(0o600)
sys.path.insert(0,str(FINAL/'disposable'))
from safe_extract import inspect_archive,extract
inspected=inspect_archive(archive,sha(archive),sha(FINAL/'SOURCE-SHA256SUMS'))
assert len(inspected)==len(names)+1
# Actual unprivileged extraction of the reviewed source archive; no qualification.
extracted=BASE/'extraction-check-r1'
result=extract(archive,extracted,sha(archive),sha(FINAL/'SOURCE-SHA256SUMS'))
assert all(sha(extracted/n)==sha(FINAL/n) for n in [*names,'SOURCE-SHA256SUMS'])
identity=dict(candidate=str(FINAL),working_test_copy=str(WORK),source_manifest_sha256=sha(FINAL/'SOURCE-SHA256SUMS'),source_files=len(names),archive=str(archive),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=len(inspected),bootstrap=str(bootstrap),bootstrap_sha256=sha(bootstrap),changed_files=changed,application_files_unchanged=True,extraction_result=result)
(E/'candidate-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
(E/'SOURCE-SHA256SUMS').write_text(manifest)
(E/'gate6k-to-vm163-fix.patch').write_text(''.join(diff))
(BASE/'REPLACEMENT-ARTIFACTS-SHA256SUMS').write_text(sha(archive)+'  '+archive.name+'\n'+sha(bootstrap)+'  '+bootstrap.name+'\n')
print(json.dumps(identity,indent=2))

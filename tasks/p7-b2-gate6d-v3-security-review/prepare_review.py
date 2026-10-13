"""Trusted source-only preservation. Run on Core via stdin; never import candidate."""
import hashlib, json, os, shutil, stat, subprocess
from pathlib import Path
os.umask(0o077)
P=Path('/home/jarvis/JARVIS')
S=Path('/tmp/jarvis-gate6c-candidate-thseen50')
R=S/'repo'
B=Path('/home/jarvis/.hermes-poc/evidence')
E=B/'p7-b2-gate6d-v3-security-review'
E.mkdir(mode=0o700,exist_ok=True)
assert not E.is_symlink() and E.stat().st_uid==os.getuid()
C=B/'p7-b2-gate6c-isolated-v3-engineering'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
    data=json.dumps(v,indent=2)+'\n'
    if (E/n).exists(): assert (E/n).read_text()==data
    else:
        with (E/n).open('x') as f: f.write(data)
assert sha(C/'SHA256SUMS')=='dca9b64c69a4f290582f2f75a99d0655ae76048622fc6b9d54d42b28b8da1d8e'
prior=json.loads((C/'source-and-seal-review.json').read_text())
pins={n:v['expected'] for n,v in prior['pinned_seals'].items()}
pins[C.name]=sha(C/'SHA256SUMS')
verified={}
for name,pin in pins.items():
    root=B/name
    assert sha(root/'SHA256SUMS')==pin
    checks={}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        h,n=line.split(None,1); p=root/n.lstrip('*')
        assert root in p.resolve().parents and not p.is_symlink()
        checks[n]=sha(p)==h
    assert all(checks.values())
    verified[name]={'seal':pin,'members':len(checks),'verified':True}
save('prior-evidence-verification.json',verified)
manifest=json.loads((C/'candidate-manifest.json').read_text())
assert sha(C/'CANDIDATE-SOURCE-SHA256SUMS')==manifest['revision']=='0d81f9fd49217ac0ac672aeefd1abb0190071c93da291a0ad92947636f8e738c'
inventory=[]
for p in sorted(R.rglob('*')):
    s=p.lstat(); n=str(p.relative_to(R))
    item={'path':n,'mode':oct(stat.S_IMODE(s.st_mode)),'size':s.st_size,'type':'directory' if p.is_dir() else 'file','links':s.st_nlink}
    assert not p.is_symlink(), 'SYMLINK: '+n
    assert stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode)
    assert p.is_dir() or s.st_nlink==1
    inventory.append(item)
save('original-complete-file-inventory.json',inventory)
base=json.loads((C/'candidate-location.json').read_text())
files={}
for n,h in base['source_manifest'].items():
    p=R/n
    assert not n.startswith(('data/','logs/','.git/')) and Path(n).name not in ('.env','jarvis.env','p7-b2.env')
    expected=manifest['fixture_config_sha256'] if n=='config.yaml' else h
    assert p.is_file() and not p.is_symlink() and sha(p)==expected, n
    files['repo/'+n]=p
for n,h in manifest['files'].items():
    p=S/n.removeprefix('qualification/') if n.startswith('qualification/') else R/n
    assert sha(p)==h,n
    files[n.removeprefix('qualification/') if n.startswith('qualification/') else 'repo/'+n]=p
omitted=[v for v in inventory if v['type']=='file' and 'repo/'+v['path'] not in files]
save('excluded-generated-files.json',omitted)
# No runtime/log/cache copying, including fixture-generated output under original repo.
assert all(v['path'].startswith(('data/','logs/')) or '__pycache__' in v['path'] or '.pytest_cache' in v['path'] or (v['path'].startswith('tasks/tmp') and v['path'].endswith('.wav') and v['size']==3) for v in omitted), omitted
secret_markers=[]
for n,p in files.items():
    if p.suffix in ('.py','.yaml','.yml','.json','.md','.txt','.toml','.ini','.example','.sh'):
        raw=p.read_bytes()
        for marker in (b'-----BEGIN PRIVATE KEY-----',b'-----BEGIN OPENSSH PRIVATE KEY-----',b'-----BEGIN RSA PRIVATE KEY-----'):
            if marker in raw:secret_markers.append(n)
assert not secret_markers
archive=Path('/home/jarvis/.hermes-poc/gate6d-candidates')
archive.mkdir(mode=0o700,exist_ok=False)
original=archive/'original-0d81f9fd4921'; original.mkdir(mode=0o700)
for n,p in files.items():
    q=original/n;q.parent.mkdir(parents=True,exist_ok=True)
    with q.open('xb') as f: f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
    q.chmod(stat.S_IMODE(p.stat().st_mode)&0o700)
    assert sha(q)==sha(p)
source_manifest=''.join(sha(p)+'  '+n+'\n' for n,p in sorted(files.items()))
(original/'SOURCE-SHA256SUMS').write_text(source_manifest)
for d in sorted([original,*[p for p in original.rglob('*') if p.is_dir()]],key=lambda p:len(p.parts),reverse=True):
    fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
work=archive/'engineering-r1';shutil.copytree(original,work)
# Compare all preserved source bytes with approved V2 Git objects (no checkout).
tree=subprocess.check_output(['git','ls-tree','-r','--name-only','bd53dbc799fb9284a21fae8cce3f5d9539e31141'],cwd=P,text=True).splitlines()
deltas=[]
for name,p in sorted(files.items()):
    if not name.startswith('repo/'):continue
    n=name[5:]
    if n not in tree: deltas.append({'path':n,'status':'added'});continue
    raw=subprocess.check_output(['git','show','bd53dbc799fb9284a21fae8cce3f5d9539e31141:'+n],cwd=P)
    if hashlib.sha256(raw).hexdigest()!=sha(p):deltas.append({'path':n,'status':'modified'})
save('source-deltas-from-v2.json',deltas)
save('preservation.json',{'original':str(original),'engineering':str(work),'original_revision':manifest['revision'],'revision_type':'SHA256 of 13-file source-and-qualification manifest; not Git','full_source_manifest_sha256':sha(original/'SOURCE-SHA256SUMS'),'preserved_files':len(files),'omitted_generated_files':len(omitted),'private_key_markers':secret_markers,'immutable':False,'same_uid_tamper_resistant':False,'base_head':base['base_head']})
shutil.copyfile(original/'SOURCE-SHA256SUMS',E/'ORIGINAL-FULL-SOURCE-SHA256SUMS')
# Reuse reviewed read-only observer/validator, output redirected only to new evidence.
for n in ('post-state.py','continuity.py'):
    shutil.copyfile(C/n,E/n)
print(json.dumps({'archive':str(original),'work':str(work),'files':len(files),'excluded':len(omitted),'deltas':deltas,'seals':len(verified)}))

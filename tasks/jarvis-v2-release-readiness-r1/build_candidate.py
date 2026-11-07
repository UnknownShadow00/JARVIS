"""Deterministic, no-replace publication of an inert public-source candidate."""
import gzip,hashlib,io,json,os,tarfile
from pathlib import Path
PACKET=Path(__file__).resolve().parent
MAIN=PACKET.parents[1]
SOURCE=MAIN.parent/'JARVIS-release-r1'
DIRECTORIES=('app','tests','docs','scripts','evals','frontend','.github','assets','config')
ROOT_FILES=('AGENTS.md','README.md','PROJECT_STATUS.md','LICENSE','pytest.ini','Dockerfile','.dockerignore','docker-compose.yml','config.yaml.example','requirements.txt','requirements-core.txt','requirements-desktop.txt','jarvis.py','jarvis.cmd','jarvis.ps1')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def serialize(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def sources():
    result={}
    for directory in DIRECTORIES:
        for p in sorted((SOURCE/directory).rglob('*')):
            if p.is_symlink():raise RuntimeError('source symlink refused: '+str(p))
            if p.is_file() and not set(p.parts)&{'__pycache__','node_modules','.pytest_cache'} and p.suffix not in ('.pyc','.pyo'):
                name=str(p.relative_to(SOURCE));assert p.name!='config.yaml' and not p.name.startswith('.env')
                data=p.read_bytes();assert len(data)<=16*1024**2
                result[name]=data
    for name in ROOT_FILES:
        p=SOURCE/name
        if p.exists():assert not p.is_symlink();result[name]=p.read_bytes()
    assert sum(map(len,result.values()))<32*1024**2
    return result

def lock():
    plan=json.loads((MAIN/'tasks/jarvis-authority-readiness-r1/DEPENDENCY-PLAN.json').read_text())
    optional=json.loads((PACKET/'OPTIONAL-DEPENDENCIES.json').read_text())
    packages={name:(v['version'],v['artifact_sha256'],v['official_source_url']) for name,v in plan['selected'].items()}
    for a in optional['artifacts']:
        name,version=a['filename'].split('-')[:2];packages[name]=(version,a['sha256'],a['url'])
    assert len(packages)==31
    text='# Exact offline application/test closure; excludes optional live desktop/providers.\n'
    text+=''.join(name+'=='+version+' --hash=sha256:'+sha+'\n' for name,(version,sha,url) in sorted(packages.items()))
    return text.encode(),{name:{'version':v,'wheel_sha256':h,'retained_upstream_url':u} for name,(v,h,u) in packages.items()}

def archive(files):
    out=io.BytesIO()
    with gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0,compresslevel=9) as zipped:
        with tarfile.open(fileobj=zipped,mode='w',format=tarfile.USTAR_FORMAT) as tar:
            for name,data in sorted(files.items()):
                member=tarfile.TarInfo(name);member.size=len(data);member.mode=0o644
                member.uid=member.gid=member.mtime=0;member.uname=member.gname=''
                tar.addfile(member,io.BytesIO(data))
    return out.getvalue()

def main():
    directory=PACKET/'release';directory.mkdir(exist_ok=False)
    files=sources();identity={n:digest(b) for n,b in files.items()};manifest=serialize(identity)
    release_id='jarvis-v2-offline-rc1-'+digest(manifest)[:16]
    requirement,packages=lock()
    files['_release/SOURCE-SHA256.json']=manifest
    files['_release/requirements-offline.lock']=requirement
    files['_release/CANDIDATE.json']=serialize({'release_id':release_id,'real_execution_enabled':False,'source_manifest_sha256':digest(manifest),'scope':'offline synthetic controlled security testing only','production_authorized':False})
    data=archive(files);assert data==archive(files),'nonreproducible archive'
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
        members=tar.getmembers();assert [m.name for m in members]==sorted(files)
        for m in members:
            assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
            assert tar.extractfile(m).read()==files[m.name]
    target=directory/(release_id+'.tar.gz')
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    finally:pass
    dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(dfd)
    finally:os.close(dfd)
    (directory/'SOURCE-SHA256.json').write_bytes(manifest)
    (directory/'requirements-offline.lock').write_bytes(requirement)
    build={'release_id':release_id,'archive':str(target.relative_to(PACKET)),'archive_sha256':digest(data),'archive_bytes':len(data),'public_source_files':len(identity),'source_sha256':identity,'source_manifest_sha256':digest(manifest),'dependencies':packages,'reproducible_rebuild_identical':True,'archive_members_verified':True,'archive_no_replace_publication':True,'real_execution_enabled':False,'host_packages_modified':False,'production_config_included':False,'WORM_or_public_key_signature_claimed':False}
    (directory/'BUILD.json').write_bytes(serialize(build))
    for item in directory.iterdir():item.chmod(0o444)
    directory.chmod(0o555)
    print(json.dumps({k:build[k] for k in ['release_id','archive_sha256','archive_bytes','public_source_files','reproducible_rebuild_identical']},indent=2))
if __name__=='__main__':main()

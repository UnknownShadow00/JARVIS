"""Publish exact committed public source deterministically, refusing replacement."""
from pathlib import Path
import gzip,hashlib,io,json,os,subprocess,tarfile
P=Path(__file__).resolve().parent;MAIN=P.parents[1];W=MAIN.parent/'JARVIS-unified-rc1';R=MAIN/'tasks/jarvis-v2-release-readiness-r1';S=MAIN/'tasks/jarvis-security-remediation-r1'
def digest(b):return hashlib.sha256(b).hexdigest()
def js(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
def archive(files):
 out=io.BytesIO()
 with gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0,compresslevel=9) as gz:
  with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as t:
   for n,b in sorted(files.items()):
    m=tarfile.TarInfo(n);m.size=len(b);m.mode=0o644;m.uid=m.gid=m.mtime=0;m.uname=m.gname='';t.addfile(m,io.BytesIO(b))
 return out.getvalue()

def main():
 assert subprocess.check_output(['git','status','--porcelain'],cwd=W)==b''
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()
 base='f4cac30259a7bf4610add2063679ae49138ee637'
 old=json.loads((R/'release/BUILD.json').read_text());selection=set(old['source_sha256'])|{'docs/security_baseline.md','tests/test_ready_client.py'}
 security=json.loads((S/'final-2-manifest.json').read_text())
 selection|={r['path'] for r in security['files'] if r['path'].startswith('tasks/') and '/' not in r['path'][6:]}
 files={}
 for n in sorted(selection):
  f=W/n;assert not f.is_symlink() and f.is_file(),n
  parts=Path(n).parts
  assert parts[0] not in {'data','logs','models','piper','jarvis-vault'}
  assert f.name!='config.yaml' and not f.name.startswith('.env') and f.suffix not in {'.key','.pem','.db','.sqlite','.pyc'}
  b=f.read_bytes();assert b==subprocess.check_output(['git','show',revision+':'+n],cwd=W),n
  files[n]=b
 source={n:digest(b) for n,b in files.items()};manifest=js(source);identity=digest(manifest)
 for n,h in json.loads((P/'INDEPENDENT-REVIEW-PINS.json').read_text()).items():assert source[n]==h,n
 release_id='jarvis-v2-unified-rc1-'+identity[:16]
 lock=(R/'release/requirements-offline.lock').read_bytes()
 files['_release/SOURCE-SHA256.json']=manifest
 files['_release/requirements-offline.lock']=lock
 files['_release/CANDIDATE.json']=js({'release_id':release_id,'git_revision':revision,'base_revision':base,'source_manifest_sha256':identity,'real_execution_enabled':False,'production_authorized':False,'scope':'controlled offline synthetic lab testing only'})
 data=archive(files);assert data==archive(files)
 directory=P/'release';directory.mkdir(exist_ok=False)
 target=directory/(release_id+'.tar.gz')
 fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 dfd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(dfd)
 finally:os.close(dfd)
 build={'release_id':release_id,'git_revision':revision,'base_revision':base,'branch':'release/jarvis-v2-unified-rc1','worktree':str(W),'archive':str(target.relative_to(P)),'archive_sha256':digest(data),'archive_bytes':len(data),'public_source_files':len(source),'source_manifest_sha256':identity,'source_sha256':source,'reproducible_second_build_identical':True,'source_members_match_committed_bytes':True,'source_only_archive':True,'real_execution_enabled':False,'dependencies':old['dependencies'],'dependency_lock_sha256':digest(lock),'evidence_and_retained_dependencies_required_for_reproduction':True,'public_key_signature_or_WORM_claimed':False}
 (directory/'BUILD.json').write_bytes(js(build));(directory/'SOURCE-SHA256.json').write_bytes(manifest);(directory/'requirements-offline.lock').write_bytes(lock)
 (P/'SOURCE-SHA256.json').write_bytes(manifest)
 (P/'SOURCE-REVISION.json').write_bytes(js({k:build[k] for k in ['git_revision','base_revision','branch','worktree','source_manifest_sha256','public_source_files']}))
 patch=subprocess.check_output(['git','diff','--binary',base,revision,'--',*sorted(selection)],cwd=W)
 (P/'SOURCE.patch').write_bytes(patch)
 basis={'codex1':{'git_base':base,'source_manifest_sha256':old['source_manifest_sha256'],'archive_sha256':old['archive_sha256'],'archive':str(R/old['archive'])},'codex2':json.loads((S/'SOURCE-IDENTITY.json').read_text()),'predecessor_evidence_files_preserved':len(json.loads((P/'PREDECESSOR-SHA256.json').read_text()))}
 (P/'BASIS.json').write_bytes(js(basis))
 for f in directory.iterdir():f.chmod(0o444)
 print(json.dumps({k:build[k] for k in ['release_id','git_revision','archive','archive_sha256','archive_bytes','public_source_files','source_manifest_sha256']},indent=2))
if __name__=='__main__':main()

"""Prepare flat Gate6K evidence input; never provision privileged paths."""
import hashlib,json,os,pathlib,shutil,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from verify_bundle import verify
def main():
    if len(sys.argv)!=3:raise ValueError('usage: NEW_PRIVATE_DIRECTORY EXPECTED_BUNDLE_MANIFEST_HASH')
    if os.geteuid()==0:raise ValueError('ROOT_EXPORT_FORBIDDEN')
    base=pathlib.Path(__file__).resolve().parents[1];verify(base,sys.argv[2])
    dest=pathlib.Path(sys.argv[1]).absolute()
    if dest.exists() or dest.is_symlink() or dest.parent.stat().st_uid!=os.geteuid() or dest.parent.stat().st_mode&0o022:raise ValueError('UNSAFE_OR_EXISTING_DESTINATION')
    dest.mkdir(mode=0o700)
    rows=json.loads((base/'locks/gate6k-ARTIFACTS.json').read_text());paths=json.loads((base/'locks/gate6k-artifact-paths.json').read_text())
    for row in rows.values():
        source=base/paths[row['filename']];target=dest/row['filename']
        with source.open('rb') as src,target.open('xb') as out:shutil.copyfileobj(src,out,1024*1024)
        target.chmod(0o600)
        with target.open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=row['sha256']:raise ValueError('COPY_HASH')
    shutil.copyfile(base/'locks/gate6k-ARTIFACTS.json',dest/'ARTIFACTS.json');(dest/'ARTIFACTS.json').chmod(0o600)
    print('131 artifacts exported; no privileged provisioning or independent human approval inferred')
if __name__=='__main__':main()

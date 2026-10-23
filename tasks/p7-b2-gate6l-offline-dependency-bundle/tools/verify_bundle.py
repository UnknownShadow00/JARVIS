"""Integrity requires an expected manifest digest retained outside this bundle."""
import hashlib,json,os,pathlib,re,stat,sys
def digest(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        before=os.fstat(f.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1:raise ValueError('NONREGULAR_ARTIFACT')
        h=hashlib.file_digest(f,'sha256').hexdigest();after=os.fstat(f.fileno())
        if (before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('ARTIFACT_CHANGED')
        return h
def verify(root,expected):
    root=pathlib.Path(root)
    if not re.fullmatch('[a-f0-9]{64}',expected):raise ValueError('EXPECTED_MANIFEST_DIGEST_REQUIRED')
    manifest=root/'SHA256SUMS'
    if digest(manifest)!=expected:raise ValueError('MANIFEST_MISMATCH')
    seen=set()
    for line in manifest.read_text().splitlines():
        h,sep,n=line.partition('  ')
        if not sep or not re.fullmatch('[a-f0-9]{64}',h) or n in seen:raise ValueError('MANIFEST_ENTRY')
        if n.startswith('/') or '\\'in n or any(p in ('','.','..') for p in n.split('/')) or n=='SHA256SUMS':raise ValueError('MANIFEST_PATH')
        p=root/n
        if any(x.is_symlink() for x in (p,*p.parents)) or digest(p)!=h:raise ValueError('ARTIFACT_MISMATCH '+n)
        seen.add(n)
    actual={str(p.relative_to(root)) for d in ('artifacts','metadata','locks','tools','source','results') for p in (root/d).rglob('*') if p.is_file() or p.is_symlink()}
    # Work is explicitly derived and excluded, never an installation artifact source.
    if actual!=seen:raise ValueError('UNEXPECTED_OR_MISSING_ARTIFACT')
    return len(seen)
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: verify_bundle.py BUNDLE EXPECTED_SHA256SUMS_SHA256')
    print(json.dumps({'status':'PASS','entries':verify(sys.argv[1],sys.argv[2])}))

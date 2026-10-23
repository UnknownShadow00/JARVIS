"""Unprivileged bootstrap extractor. Pin this script and archive hashes externally."""
import hashlib,os,pathlib,re,sys,tarfile
def extract(archive,destination,expected):
    if os.geteuid()==0:raise ValueError('ROOT_EXTRACTION_FORBIDDEN')
    if not re.fullmatch('[a-f0-9]{64}',expected):raise ValueError('EXPECTED_HASH')
    dest=pathlib.Path(destination).absolute();parent=dest.parent
    if dest.exists() or dest.is_symlink():raise ValueError('PREEXISTING_DESTINATION')
    if parent.stat().st_uid!=os.geteuid() or parent.stat().st_mode&0o022 or any(p.is_symlink() for p in (parent,*parent.parents)):raise ValueError('UNSAFE_PARENT')
    fd=os.open(archive,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    import stat
    with os.fdopen(fd,'rb') as f:
        st=os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or st.st_size>5_000_000_000:raise ValueError('ARCHIVE_TYPE_OR_SIZE')
        if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('ARCHIVE_HASH')
        f.seek(0)
        with tarfile.open(fileobj=f,mode='r:') as t:
            names=set();members=[];total=0
            for m in t:
                n=m.name
                if n.startswith('/') or '\\'in n or any(p in ('','.','..') for p in n.split('/')) or len(n)>300 or n in names:raise ValueError('ARCHIVE_PATH')
                if not m.isfile() or m.issparse() or m.mode!=0o600 or m.uid or m.gid:raise ValueError('ARCHIVE_METADATA')
                if set(m.pax_headers)-{'path'} or ('path' in m.pax_headers and m.pax_headers['path']!=n):raise ValueError('UNEXPECTED_PAX_METADATA')
                if m.size>3_500_000_000:raise ValueError('MEMBER_SIZE')
                total+=m.size
                if total>4_500_000_000 or len(names)>=4000:raise ValueError('ARCHIVE_LIMIT')
                names.add(n);members.append(m)
            if 'SHA256SUMS' not in names:raise ValueError('MISSING_MANIFEST')
            for n in names:
                if any(str(p) in names for p in pathlib.PurePosixPath(n).parents):raise ValueError('PATH_CONFLICT')
            now=os.fstat(f.fileno())
            if (st.st_size,st.st_mtime_ns,st.st_ctime_ns)!=(now.st_size,now.st_mtime_ns,now.st_ctime_ns):raise ValueError('ARCHIVE_CHANGED')
            dest.mkdir(mode=0o700)
            import shutil
            for m in members:
                p=dest/m.name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                with p.open('xb') as out:shutil.copyfileobj(t.extractfile(m),out,1024*1024)
                p.chmod(0o600)
            end=os.fstat(f.fileno())
            if (st.st_size,st.st_mtime_ns,st.st_ctime_ns)!=(end.st_size,end.st_mtime_ns,end.st_ctime_ns):raise ValueError('ARCHIVE_CHANGED_DURING_COPY')
    return len(members)
if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('usage: extract_bundle.py ARCHIVE NEW_DEST EXPECTED_ARCHIVE_SHA256')
    print(extract(*sys.argv[1:]),'regular files extracted; next verify SHA256SUMS against independent digest')

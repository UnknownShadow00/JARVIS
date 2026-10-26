"""Strict offline release extraction. No tar.extract*, metadata restoration or cleanup.

Expected hashes must come from the independently retained human approval record.
The archive, including its manifest, is fully validated before destination creation.
"""
import argparse, hashlib, io, json, os, re, stat, tarfile
from pathlib import Path

MAX_ARCHIVE=32*1024*1024
MAX_FILE=8*1024*1024
MAX_TOTAL=16*1024*1024
MAX_MEMBERS=2000
MANIFEST='SOURCE-SHA256SUMS'


def bounded_file(path, limit):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>limit:
            raise ValueError('INPUT_FILE_TYPE_OR_SIZE')
        data=bytearray()
        while len(data)<=limit:
            chunk=os.read(fd,min(65536,limit+1-len(data)))
            if not chunk:break
            data.extend(chunk)
        after=os.fstat(fd)
        if len(data)>limit or len(data)!=before.st_size or (before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise ValueError('INPUT_CHANGED_OR_OVERSIZED')
        return bytes(data)
    finally:os.close(fd)


def valid_name(name):
    if (type(name) is not str or len(name)>240 or not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*',name)
        or any(p in ('.','..') for p in name.split('/'))):raise ValueError('ARCHIVE_PATH')
    return name


def inspect_archive(path, archive_sha, manifest_sha):
    raw=bounded_file(path,MAX_ARCHIVE)
    if hashlib.sha256(raw).hexdigest()!=archive_sha:raise ValueError('ARCHIVE_DIGEST')
    files={};total=0
    # Only uncompressed tar, regular files, and harmless PAX mtime are accepted.
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
        for member in archive:
            name=valid_name(member.name)
            if name in files:raise ValueError('DUPLICATE_MEMBER')
            if not member.isreg() or member.linkname or member.sparse is not None:raise ValueError('SPECIAL_OR_LINK_MEMBER')
            if set(member.pax_headers)-{'mtime'}:raise ValueError('PAX_METADATA')
            if member.mode&~0o777 or member.mode&0o002:raise ValueError('UNSAFE_MODE')
            if member.uid<0 or member.gid<0:raise ValueError('UNSAFE_OWNER')
            if not 0<=member.size<=MAX_FILE:raise ValueError('MEMBER_SIZE')
            total+=member.size
            if total>MAX_TOTAL or len(files)>=MAX_MEMBERS:raise ValueError('ARCHIVE_BUDGET')
            files[name]=archive.extractfile(member).read(MAX_FILE+1)
            if len(files[name])!=member.size:raise ValueError('MEMBER_TRUNCATED')
    for name in files:
        if any('/'.join(name.split('/')[:i]) in files for i in range(1,len(name.split('/')))):
            raise ValueError('FILE_DIRECTORY_CONFLICT')
    manifest=files.get(MANIFEST,b'')
    if not manifest or len(manifest)>1024*1024 or hashlib.sha256(manifest).hexdigest()!=manifest_sha:raise ValueError('MANIFEST_DIGEST')
    inventory={}
    for row in manifest.decode('ascii').splitlines():
        digest,name=row.split('  ',1);valid_name(name)
        if name==MANIFEST or name in inventory or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('MANIFEST_ENTRY')
        inventory[name]=digest
    if set(inventory)!=set(files)-{MANIFEST}:raise ValueError('MANIFEST_INVENTORY')
    if any(hashlib.sha256(files[n]).hexdigest()!=h for n,h in inventory.items()):raise ValueError('MEMBER_DIGEST')
    return files


def safe_parent(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('DESTINATION_PATH')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=child
            st=os.fstat(fd)
            if st.st_uid not in (0,os.geteuid()) or st.st_mode&0o022:raise ValueError('DESTINATION_PARENT_NOT_PROTECTED')
        return fd
    except BaseException:os.close(fd);raise


def extract(path,destination,archive_sha,manifest_sha):
    files=inspect_archive(path,archive_sha,manifest_sha)
    dest=Path(destination);parent=safe_parent(dest.parent)
    root=None
    try:
        # Exclusive mkdir; never reuse, repair or delete an existing destination.
        os.mkdir(dest.name,0o700,dir_fd=parent)
        root=os.open(dest.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
        for name,data in sorted(files.items()):
            fd=os.dup(root)
            try:
                for part in name.split('/')[:-1]:
                    created=False
                    try:os.mkdir(part,0o755,dir_fd=fd);created=True
                    except FileExistsError:pass
                    child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                    if created:os.fchmod(child,0o755)
                    os.close(fd);fd=child
                out=os.open(name.split('/')[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
                try:
                    with os.fdopen(os.dup(out),'wb') as writer:writer.write(data);writer.flush();os.fsync(writer.fileno())
                    os.fchmod(out,0o644);os.fsync(out)
                finally:os.close(out)
                os.fsync(fd)
            finally:os.close(fd)
        # Publish traversal only after all bytes and metadata are durable.
        os.fchmod(root,0o755);os.fsync(root);os.fsync(parent)
    finally:
        if root is not None:os.close(root)
        os.close(parent)
    return {'result':'PASS','members':len(files),'archive_sha256':archive_sha,'manifest_sha256':manifest_sha}


def main():
    p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('archive_sha');p.add_argument('manifest_sha');p.add_argument('--destination')
    a=p.parse_args()
    if a.destination:
        if os.geteuid()==0:
            # Additional guard only. Does not replace human VM-specific approval.
            if os.uname().nodename.lower().split('.')[0] in {'jarvis','jarvis-core','nexus-services','nexus','pve','proxmox','ai','ai-server','ollama'} or {x.name for x in Path('/sys/class/net').iterdir()}!={'lo'} or a.destination!='/opt/g6k-preflight-r1':
                raise ValueError('ROOT_EXTRACTION_TARGET_REFUSED')
        result=extract(a.archive,a.destination,a.archive_sha,a.manifest_sha)
    else:result={'result':'PASS','members':len(inspect_archive(a.archive,a.archive_sha,a.manifest_sha)),'extracted':False}
    print(json.dumps(result))
if __name__=='__main__':main()

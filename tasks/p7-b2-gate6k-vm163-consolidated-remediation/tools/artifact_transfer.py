"""PROPOSED offline artifact transfer library; no executable main or auto-repair.

Only public hash-pinned package artifacts may be read. Human authorization and
absence of writers/open writable FDs are external prerequisites, not inferred.
Tests exercise synthetic files as the same unprivileged UID, never real artifacts.
"""
import ctypes,errno,hashlib,json,os,re,stat
from pathlib import Path
from metadata_only import open_directory
MIN_FREE=20*1024**3

def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('DUPLICATE_KEY')
        result[key]=value
    return result

def _plain(st,owners):
    if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or st.st_uid not in owners or stat.S_IMODE(st.st_mode) not in (0o400,0o444,0o600,0o644) or st.st_size>4*1024**3:raise ValueError('ARTIFACT_METADATA')

def _read(fd,*,retain=False):
    st=os.fstat(fd)
    if retain and st.st_size>512*1024:raise ValueError('MANIFEST_BOUND')
    digest=hashlib.sha256();count=0;data=[]
    while chunk:=os.read(fd,1024*1024):
        count+=len(chunk)
        if count>st.st_size:raise ValueError('CHANGING_ARTIFACT')
        digest.update(chunk)
        if retain:data.append(chunk)
    after=os.fstat(fd)
    if count!=st.st_size or (st.st_mtime_ns,st.st_ctime_ns)!=(after.st_mtime_ns,after.st_ctime_ns):raise ValueError('CHANGING_ARTIFACT')
    return digest.hexdigest(),b''.join(data)

def inspect_export(path,expected,required,*,owners):
    fd=open_directory(path)
    try:
        root=os.fstat(fd)
        if root.st_uid not in owners or root.st_mode&0o022:raise ValueError('DIRECTORY_METADATA')
        if os.listxattr(fd):raise ValueError('UNREVIEWED_DIRECTORY_XATTRS')
        manifest=os.open('ARTIFACTS.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
        try:
            _plain(os.fstat(manifest),owners);digest,raw=_read(manifest,retain=True)
            if digest!=expected:raise ValueError('MANIFEST_HASH')
        finally:os.close(manifest)
        rows=json.loads(raw,object_pairs_hook=unique)
        if type(rows) is not dict or set(rows)!=set(required):raise ValueError('REQUIRED_INVENTORY')
        names={'ARTIFACTS.json'};hashes={'ARTIFACTS.json':expected}
        for identity,version in required.items():
            row=rows[identity]
            if type(row) is not dict or set(row)!={'version','filename','sha256','provenance_record'} or row['version']!=version:raise ValueError('ARTIFACT_SCHEMA_VERSION')
            name=row['filename']
            if type(name) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]+',name) or name in ('.','..') or name in names:raise ValueError('ARTIFACT_NAME')
            if type(row['sha256']) is not str or not re.fullmatch('[a-f0-9]{64}',row['sha256']) or type(row['provenance_record']) is not str or not 1<=len(row['provenance_record'])<=512:raise ValueError('PROVENANCE_REFERENCE')
            names.add(name);hashes[name]=row['sha256']
        if set(os.listdir(fd))!=names:raise ValueError('EXACT_FLAT_INVENTORY')
        metadata={}
        for name in sorted(names):
            item=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
            try:
                st=os.fstat(item);_plain(st,owners)
                if os.listxattr(item):raise ValueError('UNREVIEWED_ARTIFACT_XATTRS')
                if _read(item)[0]!=hashes[name]:raise ValueError('ARTIFACT_HASH')
                metadata[name]=(st.st_dev,st.st_ino,st.st_size,st.st_blocks)
            finally:os.close(item)
        return {'directory':(root.st_dev,root.st_ino),'files':metadata,'count':len(rows)}
    finally:os.close(fd)

def rename_no_replace(source_parent,source_name,target_parent,target_name):
    lib=ctypes.CDLL(None,use_errno=True)
    fn=lib.renameat2;fn.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];fn.restype=ctypes.c_int
    if fn(source_parent,os.fsencode(source_name),target_parent,os.fsencode(target_name),1):
        code=ctypes.get_errno();raise OSError(code,os.strerror(code))

def free_bytes(fd):
    st=os.fstatvfs(fd);return st.f_bavail*st.f_frsize

def promote(source,destination,expected,required,*,source_uid,owner_uid,owner_gid):
    """Human-reviewed call only. No fallback copy, overwrites, cleanup or retry.

    Ownership conversion is limited to the exact verified flat inventory.
    Any error after rename leaves the protected staging/final path for review.
    """
    source=Path(source);destination=Path(destination)
    owners={source_uid,owner_uid}
    before=inspect_export(source,expected,required,owners=owners)
    src=open_directory(source.parent);dst=open_directory(destination.parent)
    staging='.'+destination.name+'-stage-r1'
    try:
        dst_stat=os.fstat(dst)
        if dst_stat.st_uid!=owner_uid or dst_stat.st_mode&0o022:raise ValueError('UNPROTECTED_DESTINATION_PARENT')
        if before['directory'][0]!=dst_stat.st_dev:raise OSError(errno.EXDEV,'CROSS_FILESYSTEM_REFUSED')
        if free_bytes(dst)<MIN_FREE+64*1024**2:raise ValueError('FREE_SPACE_HEADROOM')
        for name in (staging,destination.name):
            try:os.stat(name,dir_fd=dst,follow_symlinks=False)
            except FileNotFoundError:continue
            raise FileExistsError('DESTINATION_OR_STAGE_EXISTS')
        actual=os.stat(source.name,dir_fd=src,follow_symlinks=False)
        if not stat.S_ISDIR(actual.st_mode) or (actual.st_dev,actual.st_ino)!=before['directory']:raise ValueError('SOURCE_CHANGED')
        rename_no_replace(src,source.name,dst,staging)
        os.fsync(src);os.fsync(dst)
        root=os.open(staging,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=dst)
        try:
            os.fchown(root,owner_uid,owner_gid);os.fchmod(root,0o700)
            for name,identity in before['files'].items():
                fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=root)
                try:
                    st=os.fstat(fd);_plain(st,owners)
                    if (st.st_dev,st.st_ino,st.st_size,st.st_blocks)!=identity:raise ValueError('SOURCE_FILE_CHANGED')
                    os.fchown(fd,owner_uid,owner_gid);os.fchmod(fd,0o444);os.fsync(fd)
                finally:os.close(fd)
            after=inspect_export(destination.parent/staging,expected,required,owners={owner_uid})
            if before['files']!=after['files']:raise ValueError('INODE_IDENTITY_CHANGED')
            os.fchmod(root,0o555);os.fsync(root)
        finally:os.close(root)
        if free_bytes(dst)<MIN_FREE:raise ValueError('FINAL_FREE_SPACE')
        rename_no_replace(dst,staging,dst,destination.name);os.fsync(dst)
        final=inspect_export(destination,expected,required,owners={owner_uid})
        if before['files']!=final['files']:raise ValueError('FINAL_IDENTITY')
        available=free_bytes(dst)
        if available<MIN_FREE:raise ValueError('FINAL_FREE_SPACE')
        return {'integrity':'VERIFIED','artifact_count':final['count'],'same_inodes':True,'file_data_copy':False,'available_bytes':available,'qualification':'NOT_RUN','writable_fd_quiescence':'EXTERNAL_HUMAN_PREREQUISITE'}
    finally:os.close(src);os.close(dst)

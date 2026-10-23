"""Inspect untrusted archives and copy regular data only into a fresh private tree.

No tar extraction APIs, owners, special files, links, modes, or scripts are applied.
"""
import pathlib,stat,tarfile
def path_name(name):
    if name.startswith('./'):name=name[2:]
    name=name.rstrip('/')
    if not name or name.startswith('/') or '\\' in name or any(p in ('','.','..') for p in name.split('/')):
        raise ValueError('ARCHIVE_PATH')
    if len(name)>400:raise ValueError('ARCHIVE_PATH_LENGTH')
    return name
def validate(t, allow_links=False):
    entries={};total=0
    for m in t:
        if m.name in ('.','./') and m.isdir():continue
        n=path_name(m.name)
        if n in entries:raise ValueError('ARCHIVE_DUPLICATE')
        if m.mode&0o7002 or m.uid<0 or m.gid<0:raise ValueError('ARCHIVE_MODE')
        if m.issym() and allow_links:
            # Only same-directory SONAME links; caller materializes reviewed bytes.
            if '/' in m.linkname or m.linkname in ('','.','..'):raise ValueError('ARCHIVE_LINK')
        elif not (m.isfile() or m.isdir()) or m.issparse():raise ValueError('ARCHIVE_SPECIAL')
        if m.size>100_000_000:raise ValueError('ARCHIVE_MEMBER_SIZE')
        total+=m.size
        if total>500_000_000 or len(entries)>20000:raise ValueError('ARCHIVE_SIZE')
        entries[n]=m
    for n,m in entries.items():
        for p in pathlib.PurePosixPath(n).parents:
            if str(p) in entries and not entries[str(p)].isdir():raise ValueError('ARCHIVE_CONFLICT')
        if m.issym():
            target=str(pathlib.PurePosixPath(n).parent/m.linkname)
            if target not in entries or not entries[target].isfile():raise ValueError('ARCHIVE_LINK_TARGET')
    return entries
def materialize(t,dest,allow_links=False):
    entries=validate(t,allow_links)
    dest=pathlib.Path(dest)
    # The parent must be an already private, trusted workspace.
    if dest.parent.is_symlink() or dest.parent.stat().st_mode&0o022:raise ValueError('UNSAFE_PARENT')
    dest.mkdir(mode=0o700)
    for n,m in entries.items():
        p=dest/n
        if m.isdir():p.mkdir(parents=True,exist_ok=True,mode=0o700);continue
        p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        if m.issym():m=entries[str(pathlib.PurePosixPath(n).parent/m.linkname)]
        with p.open('xb') as out:out.write(t.extractfile(m).read())
        p.chmod(0o700 if m.mode&0o111 else 0o600)
    return len(entries)

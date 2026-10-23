"""Build private runtime from hash-bound signed Ubuntu payloads without package scripts."""
import hashlib,io,json,pathlib,subprocess,tarfile
from acquire import BASE
from safe_payload import path_name
NAMES={'python3.14-minimal','libpython3.14-minimal','libpython3.14-stdlib','libsqlite3-0',
 'libseccomp2','libbz2-1.0','liblzma5','libffi8','libssl3t64','libexpat1','libzstd1',
 'zlib1g','libreadline8t64','libtinfo6','libuuid1','libcrypt1'}
def main():
    rows=json.loads((BASE/'results/ubuntu-artifacts.json').read_text())['packages']
    retry={r['package']:r['artifact'] for r in json.loads((BASE/'results/ubuntu-retries.json').read_text()) if 'artifact'in r}
    root=BASE/'work/downloaded-runtime';root.mkdir(mode=0o700)
    records=[];links=[];found=set()
    for row in rows:
        if row['Package'] not in NAMES:continue
        a=retry.get(row['Package'],row.get('artifact'));p=BASE/a['path']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('DEB_HASH')
        raw=subprocess.run(['dpkg-deb','--fsys-tarfile',str(p)],capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            seen=set()
            for m in t:
                if not m.name.startswith(('./usr/lib/python3.14/','./usr/lib/x86_64-linux-gnu/','./usr/bin/python3.14')):continue
                n=path_name(m.name)
                if n in seen:raise ValueError('DUPLICATE_PAYLOAD')
                seen.add(n);dest=root/n
                if m.isfile():
                    if m.issparse() or m.mode&0o7002 or m.size>100_000_000:raise ValueError('UNSAFE_RUNTIME_PAYLOAD')
                    dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True);data=t.extractfile(m).read()
                    if dest.exists():
                        if dest.read_bytes()!=data:raise ValueError('RUNTIME_COLLISION')
                    else:
                        with dest.open('xb') as f:f.write(data)
                        dest.chmod(0o700 if m.mode&0o111 else 0o600)
                elif m.issym():links.append((n,m.linkname))
                elif not m.isdir():raise ValueError('SPECIAL_RUNTIME_PAYLOAD')
        found.add(row['Package']);records.append(a)
    # Library SONAME links are represented by copies of already verified regular bytes.
    copied=[]
    for n,target in links:
        if '/' in target or target in ('','.','..'):continue
        p=root/n;src=p.parent/target
        if src.is_file() and not p.exists():
            with p.open('xb') as f:f.write(src.read_bytes())
            p.chmod(0o700);copied.append((n,target))
    if not {'python3.14-minimal','libpython3.14-minimal','libpython3.14-stdlib','libsqlite3-0','libseccomp2'}<=found:raise ValueError('MISSING_RUNTIME_PACKAGE')
    (BASE/'work/runtime-materialization.json').write_text(json.dumps({'artifacts':records,'copied_aliases':copied,'missing_optional':sorted(NAMES-found)},indent=2)+'\n')
if __name__=='__main__':main()

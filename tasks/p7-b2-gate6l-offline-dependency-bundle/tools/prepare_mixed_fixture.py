"""Unprivileged experiment only: materialize selected signed Debian Python data.

Does not run dpkg installation, hooks, commands, services, or package code.
"""
import email,hashlib,io,json,pathlib,subprocess,sys,tarfile
from acquire import BASE
from safe_payload import path_name
NAMES={'PyGObject','bcc','command-not-found','dbus-python','distro-info','lazr.uri',
 'netifaces','python-apt','python-debian','sos','ssh-import-id','systemd-python',
 'ubuntu-drivers-common','ubuntu-pro-client','ufw','unattended-upgrades','xkit','cryptography'}
def main():
    pins=json.loads((BASE/'locks/dependency-versions.json').read_text())['packages']
    env=BASE/'work/mixed-env-r2'
    if env.exists():raise ValueError('FIXTURE_ALREADY_EXISTS')
    subprocess.run([sys.executable,'-m','venv','--without-pip',str(env)],check=True)
    site=env/'lib/python3.14/site-packages'
    rows=json.loads((BASE/'results/ubuntu-artifacts.json').read_text())['packages']
    retry={r['package']:r['artifact'] for r in json.loads((BASE/'results/ubuntu-retries.json').read_text()) if 'artifact'in r}
    rows.append(json.loads((BASE/'results/sos-exact.json').read_text()))
    rows.append(json.loads((BASE/'results/cffi-backend.json').read_text()))
    outputs=[];found=set()
    for row in rows:
        a=retry.get(row['Package'],row.get('artifact'))
        if not a:continue
        p=BASE/a['path']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('DEB_HASH')
        raw=subprocess.run(['dpkg-deb','--fsys-tarfile',str(p)],capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            identities=[]
            for m in t:
                if m.isfile() and m.name.endswith(('PKG-INFO','METADATA','.egg-info')):
                    meta=email.message_from_bytes(t.extractfile(m).read());n=meta['Name'];v=meta['Version']
                    if n in NAMES and pins[n]==v:identities.append((n,v))
            backend=row['Package']=='python3-cffi-backend'
            if not identities and not backend:continue
            # No broad package extraction. Only regular files within this exact Python prefix.
            copied=[]
            for m in t:
                prefix='./usr/lib/python3/dist-packages/'
                if not m.name.startswith(prefix) or m.isdir():continue
                n=path_name(m.name[len(prefix):])
                if not m.isfile() or m.issparse() or m.mode&0o7002:raise ValueError('UNSAFE_PYTHON_PAYLOAD')
                dest=site/n
                if dest.exists():raise ValueError('PAYLOAD_COLLISION '+n)
                dest.parent.mkdir(parents=True,exist_ok=True)
                with dest.open('xb') as f:f.write(t.extractfile(m).read())
                dest.chmod(0o600);copied.append(n)
            found.update(n for n,v in identities)
            outputs.append({'package':row['Package'],'artifact':a,'identities':identities,'files':copied})
    (BASE/'work/mixed-payloads.json').write_text(json.dumps({'found':sorted(found),'missing':sorted(NAMES-found),'packages':outputs},indent=2)+'\n')
    if found!=NAMES:raise ValueError('MISSING_DEB_IDENTITIES')
    lines=(BASE/'locks/all-wheels-hashed.txt').read_text().splitlines()
    expected='\n'.join(l for l in lines if not l.lower().startswith('cryptography=='))+'\n'
    if (BASE/'locks/mixed-wheels-hashed.txt').read_text()!=expected:raise ValueError('MIXED_LOCK_MISMATCH')
    print(len(found),'exact Debian Python distributions plus native CFFI backend')
if __name__=='__main__':main()

"""Download signed-index artifacts; no package installation or maintainer scripts."""
import concurrent.futures,json,lzma,re,subprocess
from acquire import BASE,fetch
ROOTS=['python3.14','python3.14-minimal','libpython3.14-stdlib','python3.14-venv',
 'libsqlite3-0','libseccomp2','libmagic1t64','python3-gi','python3-dbus','python3-netifaces',
 'python3-systemd','python3-lazr.uri','ssh-import-id','python3-bpfcc','command-not-found',
 'python3-distro-info','python3-apt','python3-debian','sosreport','ubuntu-drivers-common',
 'ubuntu-pro-client','ufw','unattended-upgrades','python3-xkit','ubuntu-keyring']
def main():
    db={}
    for p in sorted((BASE/'metadata/ubuntu').glob('*Packages.xz')):
        for para in lzma.decompress(p.read_bytes()).decode().split('\n\n'):
            d={}
            for line in para.splitlines():
                if line and not line[0].isspace() and ': ' in line:k,v=line.split(': ',1);d[k]=v
            if 'Package' in d:d['index']=p.name;db.setdefault(d['Package'],[]).append(d)
    # Exact historical upstream versions, never substitute newer sosreport or Python.
    forced={'sosreport':'4.10.2-1','python3-apt':'3.1.0ubuntu1.1'}
    selected={}; unresolved=[]
    def choose(name):
        candidates=db.get(name,[])
        if name in forced:candidates=[x for x in candidates if x['Version']==forced[name]]
        if not candidates:return None
        best=candidates[0]
        for x in candidates[1:]:
            if subprocess.run(['dpkg','--compare-versions',x['Version'],'gt',best['Version']]).returncode==0:best=x
        return best
    queue=ROOTS[:]
    while queue:
        name=queue.pop(0)
        if name in selected:continue
        row=choose(name)
        if row is None:unresolved.append({'name':name,'reason':'missing or virtual'});continue
        selected[name]=row
        for dep in (row.get('Pre-Depends','')+','+row.get('Depends','')).split(','):
            if not dep.strip():continue
            alts=[x.strip() for x in dep.split('|')];pick=None
            for alt in alts:
                m=re.fullmatch(r'([a-z0-9+.-]+)(?::\w+)?(?:\s*\((<<|<=|=|>=|>>)\s*([^ )]+)\))?',alt)
                if not m:continue
                d=choose(m[1])
                if d and (not m[2] or subprocess.run(['dpkg','--compare-versions',d['Version'],m[2],m[3]]).returncode==0):pick=m[1];break
            if pick:queue.append(pick)
            else:unresolved.append({'package':name,'dependency':dep,'reason':'no satisfiable concrete alternative'})
    def get(r):
        host='security.ubuntu.com' if 'security' in r['index'] else 'archive.ubuntu.com'
        try:r['artifact']=fetch('https://'+host+'/ubuntu/'+r['Filename'],'artifacts/debs/'+r['Filename'].split('/')[-1],r['SHA256'])
        except Exception as e:r['error']=str(e)
        return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(get,selected.values()))
    (BASE/'results/ubuntu-artifacts.json').write_text(json.dumps({'roots':ROOTS,'unresolved':unresolved,'packages':rows},indent=2)+'\n')
    print(json.dumps({'packages':len(rows),'failed':[r['Package'] for r in rows if 'error'in r],'unresolved':unresolved},indent=2))
if __name__=='__main__':main()

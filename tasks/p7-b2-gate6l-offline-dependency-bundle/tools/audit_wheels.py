import base64,csv,email,hashlib,io,json,pathlib,re,stat,zipfile
from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.utils import canonicalize_name,parse_wheel_filename
from packaging.tags import sys_tags
from acquire import BASE
def inspect(path):
    with zipfile.ZipFile(path) as z:
        infos=z.infolist();names=[i.filename for i in infos]
        if len(names)!=len(set(names)):raise ValueError('duplicate wheel member')
        if sum(i.file_size for i in infos)>500_000_000:raise ValueError('wheel expanded size')
        hooks=[]
        for i in infos:
            n=i.filename.rstrip('/')
            if not n or n.startswith('/') or '\\' in n or any(x in ('','.','..') for x in n.split('/')):raise ValueError('unsafe wheel path')
            mode=i.external_attr>>16
            if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0,stat.S_IFREG,stat.S_IFDIR)):raise ValueError('special wheel entry')
            if mode&0o6000:raise ValueError('privileged wheel mode')
            if n.endswith('.pth') or '.data/scripts/' in n:hooks.append(n)
        records=[n for n in names if n.count('/')==1 and n.endswith('.dist-info/RECORD')]
        if len(records)!=1:raise ValueError('RECORD count')
        seen=set()
        for n,h,size in csv.reader(io.StringIO(z.read(records[0]).decode())):
            if n in seen or n not in names:raise ValueError('invalid RECORD member')
            seen.add(n)
            if not h:
                if n!=records[0]:raise ValueError('unhashed RECORD entry')
                continue
            alg,digest=h.split('=',1)
            if alg!='sha256':raise ValueError('unexpected RECORD algorithm')
            raw=z.read(n)
            if str(len(raw))!=size or base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).rstrip(b'=').decode()!=digest:raise ValueError('RECORD mismatch')
        if {i.filename for i in infos if not i.is_dir()}!=seen:raise ValueError('unlisted wheel payload')
        meta=email.message_from_bytes(z.read(records[0].rsplit('/',1)[0]+'/METADATA'))
        _,_,_,tags=parse_wheel_filename(path.name)
        return {'file':path.name,'name':meta['Name'],'version':meta['Version'],
                'requires_dist':meta.get_all('Requires-Dist',[]),'requires_python':meta['Requires-Python'],
                'tags':sorted(map(str,tags)),'tag_compatible':bool(tags&set(sys_tags())),
                'hooks':hooks,'record':'PASS'}
def main():
    pins=json.loads((BASE/'locks/dependency-versions.json').read_text())['packages']
    pins={canonicalize_name(n):v for n,v in pins.items()}
    env=default_environment();env['extra']='';rows=[];gaps=[]
    for p in sorted((BASE/'artifacts/wheels').glob('*.whl')):
        row=inspect(p);rows.append(row)
        if pins.get(canonicalize_name(row['name']))!=row['version']:raise ValueError('pin mismatch')
        for dep in row['requires_dist']:
            r=Requirement(dep)
            if r.marker and not r.marker.evaluate(env):continue
            found=pins.get(canonicalize_name(r.name))
            if found is None or not r.specifier.contains(found):gaps.append({'requiring':row['name'],'requirement':dep,'locked_version':found})
    (BASE/'results/wheel-audit.json').write_text(json.dumps({'wheels':rows,'closure_gaps':gaps,'environment':env},indent=2)+'\n')
    print(json.dumps({'audited':len(rows),'closure_gaps':gaps,'hooks':[r['file'] for r in rows if r['hooks']]},indent=2))
if __name__=='__main__':main()

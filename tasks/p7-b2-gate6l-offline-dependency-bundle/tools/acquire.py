"""Public artifacts only. Never install, execute, overwrite, or follow off-list redirects."""
import concurrent.futures, hashlib, json, os, pathlib, re, ssl, urllib.request, urllib.parse
BASE = pathlib.Path(__file__).resolve().parents[1]
HOSTS = {'pypi.org','files.pythonhosted.org','www.python.org','www.sqlite.org',
         'archive.ubuntu.com','security.ubuntu.com','releases.ubuntu.com',
         'cdimage.ubuntu.com','keyserver.ubuntu.com'}
def valid_url(url):
    u=urllib.parse.urlsplit(url)
    if u.scheme!='https' or u.hostname not in HOSTS or u.username or u.password or u.port not in (None,443):
        raise ValueError('unapproved URL')
class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        valid_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(url, rel, expected=None, limit=200_000_000):
    valid_url(url)
    dest=BASE/rel
    if dest.exists(): raise FileExistsError(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}),Redirect(),
            urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    digest=hashlib.sha256(); count=0
    with op.open(urllib.request.Request(url,headers={'User-Agent':'JARVIS-Gate6L-artifact-verifier/1'}),timeout=45) as r:
        valid_url(r.url)
        with dest.open('xb') as out:
            while chunk:=r.read(1024*1024):
                count+=len(chunk)
                if count>limit: raise ValueError('artifact size bound')
                digest.update(chunk); out.write(chunk)
            out.flush(); os.fsync(out.fileno())
    record={'url':url,'path':str(rel),'bytes':count,'sha256':digest.hexdigest(),
            'expected_sha256':expected,'hash_matches':None if expected is None else digest.hexdigest()==expected}
    if expected is not None and not record['hash_matches']: raise ValueError('HASH MISMATCH '+str(rel))
    return record
def metadata_one(item):
    name,version=item; norm=re.sub(r'[-_.]+','-',name).lower()
    url=f'https://pypi.org/pypi/{urllib.parse.quote(name)}/{urllib.parse.quote(version)}/json'
    try:
        record=fetch(url,'metadata/pypi/'+norm+'.json',limit=12_000_000)
        data=json.loads((BASE/record['path']).read_text())
        return {'name':name,'version':version,'status':'FOUND','metadata':record,
                'summary':data['info'].get('summary'),'requires_python':data['info'].get('requires_python'),
                'requires_dist':data['info'].get('requires_dist'),'urls':data['urls']}
    except Exception as exc:
        return {'name':name,'version':version,'status':'UNAVAILABLE','error':str(exc),'url':url}
def main():
    pins=json.loads((BASE/'locks/dependency-versions.json').read_text())['packages']
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows=list(pool.map(metadata_one,pins.items()))
    (BASE/'results/pypi-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps({'total':len(rows),'found':sum(r['status']=='FOUND' for r in rows),
                      'unavailable':[r['name']+'=='+r['version'] for r in rows if r['status']!='FOUND']}))
if __name__=='__main__':main()

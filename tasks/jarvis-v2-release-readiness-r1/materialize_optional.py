"""Materialize three retained wheels for offline regressions; no pip or network."""
import base64,csv,hashlib,io,json,stat,zipfile
from pathlib import Path
PACKET=Path(__file__).resolve().parent
BUNDLE=Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1')
WHEELS={
'beautifulsoup4-4.15.0-py3-none-any.whl':'d6f88de62e1d4e38ecb1077eb9724cd0eff29d2a08ca16a401e9b9e93f117cf9',
'numpy-2.5.3-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl':'b0521d0f4aebb6e06189451025fa17a913287b13c03d5fe05c017333b654ea5b',
'soupsieve-2.9.2-py3-none-any.whl':'8089a26fd974ca7a1f30276d3d8492ab266ab15af581642dfe8aa162e0c1c823'}
def main():
    dest=PACKET/'optional-target';dest.mkdir(exist_ok=False)
    artifacts=[];inventory={};total=0
    for filename,digest in WHEELS.items():
        wheel=BUNDLE/'artifacts/wheels'/filename;raw=wheel.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
        name=filename.split('-')[0];metadata=BUNDLE/'metadata/pypi'/(name+'.json');meta=json.loads(metadata.read_text())
        urls=meta.get('urls',[])+[v for values in meta.get('releases',{}).values() for v in values]
        match=[u for u in urls if u['filename']==filename and u['digests']['sha256']==digest]
        assert match and match[0]['url'].startswith('https://files.pythonhosted.org/')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            members={i.filename:i for i in z.infolist() if not i.is_dir()};records=[n for n in members if n.endswith('.dist-info/RECORD')];assert len(records)==1
            table={r[0]:r[1:] for r in csv.reader(io.StringIO(z.read(records[0]).decode()))}
            assert set(table)==set(members)
            for n,item in members.items():
                p=Path(n);assert not p.is_absolute() and '..' not in p.parts and not stat.S_ISLNK(item.external_attr>>16)
                data=z.read(n);total+=len(data);assert len(data)<=64*1024**2 and total<=128*1024**2
                recorded,size=table[n]
                if n!=records[0]:
                    algorithm,value=recorded.split('=',1);assert algorithm=='sha256'
                    assert base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()==value and int(size)==len(data)
                target=dest/n;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
                inventory[n]=hashlib.sha256(data).hexdigest()
        meta_dest=PACKET/'dependency-metadata'/metadata.name;meta_dest.parent.mkdir(exist_ok=True);meta_dest.write_bytes(metadata.read_bytes())
        artifacts.append({'filename':filename,'sha256':digest,'url':match[0]['url'],'retained_metadata_sha256':hashlib.sha256(metadata.read_bytes()).hexdigest(),'upstream_freshness':'retained offline snapshot; no current advisory claim'})
    (PACKET/'OPTIONAL-DEPENDENCIES.json').write_text(json.dumps({'artifacts':artifacts,'files':inventory,'bytes':total,'network_used':False,'installed_environment_modified':False,'RECORDs_verified':True},indent=2)+'\n')
    print(json.dumps({'files':len(inventory),'bytes':total}))
if __name__=='__main__':main()

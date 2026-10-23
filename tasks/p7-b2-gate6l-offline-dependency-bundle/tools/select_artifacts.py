import concurrent.futures,json
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename
from packaging.specifiers import SpecifierSet
from acquire import BASE,fetch
def main():
    tags=list(sys_tags()); rank={t:i for i,t in enumerate(tags)}
    rows=json.loads((BASE/'results/pypi-inventory.json').read_text())
    def one(row):
        if row['status']!='FOUND':return row
        wheels=[]
        for a in row['urls']:
            if a['yanked'] or (a.get('requires_python') and not SpecifierSet(a['requires_python']).contains('3.14.4')):continue
            if a['packagetype']=='bdist_wheel':
                _,_,_,ts=parse_wheel_filename(a['filename']); matches=ts&rank.keys()
                if matches:wheels.append((min(rank[t] for t in matches),a))
        sources=[a for a in row['urls'] if a['packagetype']=='sdist' and not a['yanked']]
        a=min(wheels,key=lambda x:x[0])[1] if wheels else (sources[0] if sources else None)
        if not a:row['artifact_status']='NO_COMPATIBLE_ARTIFACT';return row
        kind='wheels' if wheels else 'sdists'
        try:
            row['artifact']=fetch(a['url'],'artifacts/'+kind+'/'+a['filename'],a['digests']['sha256'])
            row['artifact_status']='WHEEL' if wheels else 'SOURCE_ONLY'
        except Exception as e:row['artifact_status']='DOWNLOAD_FAILED';row['artifact_error']=str(e)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:out=list(pool.map(one,rows))
    (BASE/'results/artifact-inventory.json').write_text(json.dumps(out,indent=2)+'\n')
    from collections import Counter
    print(Counter(r.get('artifact_status',r['status']) for r in out))
    print([(r['name'],r.get('artifact_status',r['status'])) for r in out if r.get('artifact_status')!='WHEEL'])
if __name__=='__main__':main()

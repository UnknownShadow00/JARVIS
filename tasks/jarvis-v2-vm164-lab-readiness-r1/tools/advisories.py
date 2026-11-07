"""Fresh bounded OSV queries for exact public pins; no installer or secret inputs."""
from pathlib import Path
from datetime import datetime,UTC
import hashlib,json,urllib.request,urllib.error,time
P=Path(__file__).resolve().parents[1];MAIN=P.parents[1]
def main():
 build=json.loads((MAIN/'tasks/jarvis-v2-unified-rc1/release/BUILD.json').read_text())
 queries=[{'package':{'ecosystem':'PyPI','name':n},'version':d['version']} for n,d in sorted(build['dependencies'].items())]
 lock=json.loads((MAIN.parent/'JARVIS-unified-rc1/frontend/electron/package-lock.json').read_text())
 seen=set()
 for path,p in sorted(lock.get('packages',{}).items()):
  if not path or 'node_modules/' not in path or 'version' not in p:continue
  name=p.get('name',path.rsplit('node_modules/',1)[1]);k=(name,p['version'])
  if k not in seen:queries.append({'package':{'ecosystem':'npm','name':name},'version':p['version']});seen.add(k)
 out=P/'evidence/advisories';out.mkdir(exist_ok=False)
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[];start=time.monotonic()
 for offset in range(0,len(queries),100):
  batch=queries[offset:offset+100];payload=json.dumps({'queries':batch}).encode()
  request=urllib.request.Request('https://api.osv.dev/v1/querybatch',data=payload,headers={'Content-Type':'application/json','User-Agent':'JARVIS-offline-lab-preparation/1'},method='POST')
  record={'offset':offset,'queried_at_utc':datetime.now(UTC).isoformat(),'queries':batch,'source':'https://api.osv.dev/v1/querybatch'}
  try:
   if time.monotonic()-start>60:raise TimeoutError()
   with opener.open(request,timeout=12) as r:
    raw=r.read(4*1024**2+1);assert len(raw)<=4*1024**2 and r.status==200
   (out/f'batch-{offset}.json').write_bytes(raw);response=json.loads(raw);assert len(response['results'])==len(batch)
   record['raw_sha256']=hashlib.sha256(raw).hexdigest();record['results']=response['results']
   record['status']='INCOMPLETE_PAGINATION' if any(x.get('next_page_token') for x in response['results']) else 'QUERIED'
  except Exception as e:record.update(status='UNAVAILABLE',failure_class=type(e).__name__,http_status=getattr(e,'code',None))
  rows.append(record)
 result={'checked_at_utc':datetime.now(UTC).isoformat(),'pypi_queries':31,'npm_queries':len(seen),'batches':rows,'all_queries_complete':all(r['status']=='QUERIED' for r in rows),'vulnerability_records':sum(len(x.get('vulns',[])) for r in rows for x in r.get('results',[])),'scope':'Exact pinned Python offline closure and locked Electron dependency versions only; absence in OSV is not a complete security or native OS audit. Pagination/unavailability blocks a clean verdict. No upgrades or installation.'}
 (P/'ADVISORY-RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='batches'},indent=2))
if __name__=='__main__':main()

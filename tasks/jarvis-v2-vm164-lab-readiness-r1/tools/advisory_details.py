from pathlib import Path
import concurrent.futures,json,urllib.request,hashlib,re
P=Path(__file__).resolve().parents[1];r=json.loads((P/'ADVISORY-RESULTS.json').read_text())
items={v['id'] for b in r['batches'] for x in b.get('results',[]) for v in x.get('vulns',[])}
out=P/'evidence/advisory-records';out.mkdir(exist_ok=False)
def get(ident):
 assert re.fullmatch('[A-Za-z0-9-]{5,80}',ident)
 try:
  url='https://api.osv.dev/v1/vulns/'+ident
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with opener.open(url,timeout=12) as response:raw=response.read(1024**2+1);assert len(raw)<=1024**2
  d=json.loads(raw);assert d['id']==ident;(out/(ident+'.json')).write_bytes(raw)
  return {'id':ident,'status':'RETRIEVED','sha256':hashlib.sha256(raw).hexdigest(),'summary':d.get('summary'),'severity':d.get('severity',[]),'database_specific':d.get('database_specific',{}),'withdrawn':d.get('withdrawn'),'affected':d.get('affected',[]),'references':d.get('references',[])}
 except Exception as e:return {'id':ident,'status':'UNAVAILABLE','failure_class':type(e).__name__}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(get,sorted(items)))
(P/'ADVISORY-DETAILS.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
for d in rows:
 print(json.dumps({k:v for k,v in d.items() if k in ['id','status','summary','severity','withdrawn']},sort_keys=True))

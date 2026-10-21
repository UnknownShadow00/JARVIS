"""Read-only Core terminal/live identity check. Stdout only, no app imports."""
import hashlib,json,os,sqlite3,sys
from pathlib import Path

def guard(event,args):
    if event in ('socket.connect','socket.bind','socket.getaddrinfo'):raise RuntimeError('NETWORK_FORBIDDEN')
    if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
        p=Path(os.fsdecode(args[0])).absolute()
        if Path('/home/jarvis/.config') in p.parents:raise RuntimeError('CREDENTIAL_OPEN_FORBIDDEN')
        if (args[2] or 0)&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):raise RuntimeError('WRITE_FORBIDDEN')
sys.addaudithook(guard)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def logical(p):
    db=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        schema=db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall()
        tables={}
        for kind,name,_,_ in schema:
            if kind!='table':continue
            rows=db.execute('SELECT * FROM "'+name.replace('"','""')+'"').fetchall()
            typed=[[['blob',x.hex()] if isinstance(x,bytes) else [type(x).__name__,x] for x in row] for row in rows]
            tables[name]=sorted(typed,key=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False))
        body={'schema':schema,'tables':tables,'user_version':db.execute('PRAGMA user_version').fetchone()[0]}
        return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    finally:db.close()
b=Path('/home/jarvis/.hermes-poc/backups/p7-b2/62f417a21a524499b92316b58f6fbd64')
m=json.loads((b/'manifest.json').read_bytes());bad=[]
for name,want in m['files'].items():
    if Path(name).name!=name or (b/name).is_symlink() or sha(b/name)!=want:bad.append(name)
live=Path('/home/jarvis/JARVIS/data/p7-b2-pilot-controller-v1/controller.sqlite3')
a=logical(b/'controller.sqlite3');v=logical(live)
print(json.dumps({'bundle':str(b),'manifest_sha256':sha(b/'manifest.json'),'members':len(m['files']),'mismatches':bad,'live_logical_sha256':v,'archive_logical_sha256':a,'live_matches_archive':a==v,'source_implementation_sha256':m['source']['implementation_sha256'],'writes':0,'provider_requests':0},indent=2))

"""Addendum V2 current-state readback. stdout only: every write and every socket is refused."""
import os,sys,json,subprocess,hashlib,sqlite3,collections,stat
from pathlib import Path
from datetime import datetime,UTC
sys.dont_write_bytecode=True
R=Path('/home/jarvis/JARVIS'); G=Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate4-v2-supervised-startup'); B=Path('/home/jarvis/.hermes-poc/backups/p7-b2')
CRED=Path('/home/jarvis/.config/jarvis')
def guard(event,args):
 if event in ('socket.connect','socket.bind','socket.getaddrinfo'):raise RuntimeError('NETWORK_FORBIDDEN')
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).absolute()
  if p==CRED or CRED in p.parents:raise RuntimeError('CREDENTIAL_OPEN_FORBIDDEN')
  if (args[2] or 0)&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):raise RuntimeError('WRITE_FORBIDDEN '+str(p))
sys.addaudithook(guard)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
def meta(p):
 s=p.lstat();return {'mode':oct(stat.S_IMODE(s.st_mode)),'uid':s.st_uid,'inode':s.st_ino,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
r={'utc':datetime.now(UTC).isoformat(),'host':run(['hostname']),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
props=['ActiveState','SubState','MainPID','InvocationID','NRestarts','Restart','UnitFileState','NeedDaemonReload','ExecMainStartTimestamp','ExecMainExitTimestamp','ExecMainStatus','Result','InactiveEnterTimestamp']
r['service']=dict(x.split('=',1) for x in run(['systemctl','--user','show','jarvis.service',*[v for n in props for v in ['-p',n]]]).splitlines())
r['source_head']=run(['git','rev-parse','HEAD'],R); r['working_tree_short']=run(['git','status','--short'],R)
r['config_sha256']=sha(R/'config.yaml')
r['source_mismatches']=[n for n,h in json.loads((G/'installed-source-sha256.json').read_text()).items() if sha(R/n)!=h]
r['identity_ok']=r['source_head']=='bd53dbc799fb9284a21fae8cce3f5d9539e31141' and r['config_sha256']=='00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c' and not r['source_mismatches']
cm={str(p):meta(p) for p in [CRED,CRED/'jarvis.env',CRED/'p7-b2.env']}  # lstat only, never opened
prior=json.loads((G/'startup-association-verification.json').read_text())['credential_metadata_unchanged']
r['credential_metadata_matches_gate4']=all(all(cm[p].get(k,v)==v for k,v in vals.items() if k in cm[p]) for p,vals in prior.items())
d06=R/'data/model-ownership-v1'
r['D06_state']=json.loads((d06/'state.json').read_text())
dbp=R/'data/p7-b2-pilot-controller-v1/controller.sqlite3'
r['D09_file']={n:meta(dbp.parent/n) for n in os.listdir(dbp.parent)}
db=sqlite3.connect(dbp.as_uri()+'?mode=ro',uri=True,timeout=2)
try:
 db.execute('PRAGMA query_only=ON')
 tables=[x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
 def rows(sql):
  c=db.execute(sql);cols=[d[0] for d in c.description];return [dict(zip(cols,x)) for x in c.fetchall()]
 r['D09']={'journal_mode':db.execute('PRAGMA journal_mode').fetchone()[0],'quick_check':db.execute('PRAGMA quick_check').fetchall(),'table_counts':{n:db.execute('SELECT count(*) FROM "'+n.replace('"','""')+'"').fetchone()[0] for n in tables},
  'epochs':rows('SELECT * FROM epochs'),'pilot_events':rows('SELECT * FROM pilot_events'),'pilot_context':rows('SELECT purpose,resource,profile,accepted_limit FROM pilot_context')}
finally:db.close()
d04=R/'data/p7-shadow-evidence-v1'
r['D04']={'namespace_exists':d04.exists(),'files':[{'name':p.name,'size':p.stat().st_size} for p in d04.iterdir()] if d04.exists() else []}
r['backups']={}
for name,want in [('baseline-5244a125c27e41bb844781032d4f59ff','7b5837b43255b2a64e54756ad56f436e808d5e6c6465817fcb36f3d61ad83125'),('9315a199492449709dfd6bd51b2666a5','e6847c5043b28da9c6e7a3f1d18869bcfe5529c2fcc3867fe53fa00474527f64')]:
 b=B/name;m=json.loads((b/'manifest.json').read_text());h=sha(b/'manifest.json')
 r['backups'][name]={'manifest_match':h==want,'components_ok':all(sha(b/n)==v for n,v in m['files'].items()),'n':len(m['files'])}
r['backup_directories']=sorted(p.name for p in B.iterdir() if p.is_dir())
boundary=json.loads((G/'prestart-observation-boundary.json').read_text())['audit'];ap=Path(boundary['path']);s=ap.stat()
ev=[]
if s.st_ino==boundary['inode'] and s.st_size>=boundary['size']:
 with ap.open('rb') as f:f.seek(boundary['size']);data=f.read(1048576)
 for line in data.splitlines():
  try:v=json.loads(line)
  except ValueError:ev.append({'event_type':'UNPARSEABLE'});continue
  ev.append({'event_type':v.get('event_type'),'ts':v.get('timestamp') or v.get('ts') or v.get('time')})
r['audit_since_gate4_boundary']={'rotated':s.st_ino!=boundary['inode'],'events':ev,'counts':dict(collections.Counter(e['event_type'] for e in ev))}
q=subprocess.run(['journalctl','--user','-u','jarvis.service','--since','2026-10-09 21:25:32 UTC','-o','json','--no-pager'],capture_output=True,text=True)
jc=collections.Counter();starts=[]
for line in q.stdout.splitlines():
 try:v=json.loads(line)
 except ValueError:continue
 msg=v.get('MESSAGE','');msg=msg if isinstance(msg,str) else ''
 for k in ['Started server process','Application startup complete','Application startup failed','Traceback','Finished server process','Starting jarvis.service','Stopped jarvis.service','Failed']:
  if k in msg:jc[k]+=1
 if 'Started server process' in msg or 'Finished server process' in msg:starts.append((v.get('_BOOT_ID'),datetime.fromtimestamp(int(v['__REALTIME_TIMESTAMP'])/1e6,UTC).isoformat(),msg[:60]))
r['user_journal_since_gate4']={'markers':dict(jc),'server_process_lines':starts}
r['python_processes']=[l for l in run(['ps','-eo','pid,user,lstart,comm']).splitlines() if 'python' in l.lower() or 'uvicorn' in l.lower()]
r['listening_8000']=run(['ss','-Htln','( sport = :8000 )'])
r['http_ws_probes']=0;r['provider_requests']=0;r['writes']=0
print(json.dumps(r,indent=1,default=str))

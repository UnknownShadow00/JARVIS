from pathlib import Path
import os,json,hashlib,stat,subprocess,datetime,sys
R=Path.cwd();O=R/'tasks/jarvis-comprehensive-security-audit-r1';label=sys.argv[1] if len(sys.argv)>1 else 'current';assert label in ('current','final');S=O/('snapshot-'+label);S.mkdir(exist_ok=False)
roots=['app','frontend','scripts','config','.github','tests','docs','tools','evals','assets','tasks/proxmox-automation-phase2','tasks/proxmox-automation-phase3'];files=[]
for root in roots:
 for base,ds,fs in os.walk(R/root,followlinks=False):
  ds[:]=[d for d in ds if d not in ['__pycache__','node_modules','.git','evidence','runs','artifacts']]
  for f in fs:
   p=Path(base)/f
   if p.is_symlink() or p.stat().st_size>2_000_000:continue
   if root in ['assets','evals'] and p.suffix.lower() not in ['.py','.js','.html','.css','.json','.jsonl','.md','.yaml','.yml','.txt','.toml']:continue
   if p.suffix.lower() not in ['.pyc','.png','.jpg','.ico','.wav','.db','.sqlite','.sqlite3','.pem','.key']:files.append(p)
for p in R.iterdir():
 if p.is_file() and (p.suffix in ['.md','.txt','.yml','.toml'] or p.name in ['Dockerfile','pytest.ini','.gitignore','config.yaml.example','.env.example','jarvis.py','jarvis.cmd','Modelfile.nothink']):files.append(p)
files.extend(p for p in (R/'tasks').iterdir() if p.is_file() and p.suffix in ['.py','.sh','.ps1'])
m=[]
for p in sorted(set(files)):
 rel=p.relative_to(R);b=p.stat();raw=p.read_bytes();a=p.stat()
 if (a.st_mtime_ns,a.st_size)!=(b.st_mtime_ns,b.st_size):raise SystemExit('changed during capture '+str(rel))
 q=S/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);q.chmod(0o444)
 m.append({'path':str(rel),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'source_mode':oct(stat.S_IMODE(a.st_mode))})
unstable=[v['path'] for v in m if hashlib.sha256((R/v['path']).read_bytes()).hexdigest()!=v['sha256']]
for base,ds,fs in os.walk(S,topdown=False):Path(base).chmod(0o555)
old=json.loads((O/('source-manifest-current.json' if label=='final' else 'source-manifest.json')).read_text());prev={v['path']:v for v in old};now={v['path']:v for v in m}
changed=[p for p in now if p not in prev or now[p]['sha256']!=prev[p]['sha256']];deleted=[p for p in prev if p not in now]
(O/('source-manifest-'+label+'.json')).write_text(json.dumps(m,indent=2)+'\n');sha=''.join(v['sha256']+'  snapshot-'+label+'/'+v['path']+'\n' for v in m);(O/('source-'+label+'.sha256')).write_text(sha)
delta={'capture_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_manifest_sha256':hashlib.sha256(sha.encode()).hexdigest(),'changed_or_added_paths':changed,'removed_paths':deleted,'unstable_paths':unstable,'files':len(m),'consistency':'Per-file stable reads plus immediate rehash; not atomic cross-file capture; original immutable snapshot preserved.'}
(O/('source-delta-final.json' if label=='final' else 'source-delta.json')).write_text(json.dumps(delta,indent=2)+'\n');print(json.dumps(delta,indent=2))

"""Bytes/AST-only local verification. No subprocess, network, timers or VM calls."""
import ast,gzip,hashlib,io,json,os,stat,tarfile
from pathlib import Path
TASK=Path(__file__).resolve().parents[1];ROOT=TASK.parents[1]
OMIT={'MANIFEST.json','SEAL.json'}
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(d):return json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def inventory():
 files={};links={}
 for p in sorted(TASK.rglob('*')):
  n=str(p.relative_to(TASK));st=p.lstat()
  if n in OMIT:continue
  if stat.S_ISLNK(st.st_mode):links[n]=os.readlink(p)
  elif stat.S_ISREG(st.st_mode):files[n]={'sha256':sha(p.read_bytes()),'bytes':st.st_size}
  elif not stat.S_ISDIR(st.st_mode):raise ValueError('unexpected_special_file')
 return {'format':'vm164-r3-stage1-local-integrity','files':files,'symlinks':links}
def predecessors():
 e=json.loads((TASK/'evidence/ENTRY.json').read_bytes())
 for n,h in e['predecessor_files'].items():
  p=ROOT/n
  if p.is_symlink() or sha(p.read_bytes())!=h:raise ValueError('predecessor_changed:'+n)
 for n,target in e['predecessor_symlinks'].items():
  if not (ROOT/n).is_symlink() or os.readlink(ROOT/n)!=target:raise ValueError('predecessor_symlink_changed')
 raw=(ROOT/'tasks/loop-log.md').read_bytes()
 if sha(raw[:e['log_prefix_bytes']])!=e['log_prefix_sha256']:raise ValueError('original_log_prefix_changed')
 for folder in ('jarvis-v2-vm164-trusted-bootstrap-r1','jarvis-v2-vm164-trusted-bootstrap-remediation-r2'):
  old=TASK.parent/folder;seal=json.loads((old/'SEAL.json').read_bytes());m=(old/'MANIFEST.json').read_bytes()
  if sha(m)!=seal['manifest_sha256']:raise ValueError('predecessor_manifest_seal')
  declared=json.loads(m)
  for name,info in declared['files'].items():
   p=Path(name)
   if p.is_absolute() or '..' in p.parts or (old/p).is_symlink():raise ValueError('predecessor_manifest_path')
   data=(old/p).read_bytes()
   if sha(data)!=info['sha256'] or len(data)!=info['bytes']:raise ValueError('predecessor_declared_pin')
  for name,target in declared['symlinks'].items():
   if not (old/name).is_symlink() or os.readlink(old/name)!=target:raise ValueError('predecessor_declared_link')
  actual={str(p.relative_to(old)) for p in old.rglob('*') if p.is_file() and not p.is_symlink()}
  if actual!=set(declared['files'])|{'MANIFEST.json','SEAL.json'}:raise ValueError('predecessor_inventory')
 audit=TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1'
 for line in (audit/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1)
  if Path(n).is_absolute() or '..' in Path(n).parts or sha((audit/n).read_bytes())!=h:raise ValueError('audit_manifest')
 return {'predecessor_files_preserved':len(e['predecessor_files']),'predecessor_symlinks_preserved':len(e['predecessor_symlinks']),'original_log_prefix_preserved':True}
def source_and_archive():
 m=json.loads((TASK/'SOURCE-MANIFEST.json').read_bytes());f=m['files']
 hashes={n:sha((TASK/'src'/n).read_bytes()) for n in f}
 if any(hashes[n]!=f[n]['sha256'] or (TASK/'src'/n).stat().st_size!=f[n]['bytes'] for n in f):raise ValueError('source_changed')
 if sha(canonical(hashes))!=m['source_tree_sha256']:raise ValueError('source_tree_hash')
 for p in (TASK/'src').iterdir():
  if p.name not in f:raise ValueError('unexpected_source_file')
 tree=ast.parse((TASK/'src/model.py').read_text());flag=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FORCE_RUNTIME_ENABLED' for t in n.targets))
 if not isinstance(flag.value,ast.Constant) or flag.value.value is not False:raise ValueError('force_disabled_invariant')
 source=ast.parse((TASK/'src/host_adapter.py').read_text())
 native=next(n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='NativeBackend')
 force=next(n for n in native.body if isinstance(n,ast.FunctionDef) and n.name=='force')
 if len(force.body)!=1 or not isinstance(force.body[0],ast.Raise):raise ValueError('force_transport_must_remain_absent')
 d=json.loads((TASK/'candidate/ARTIFACT.json').read_bytes());blob=(TASK/'candidate/host-enforcement-r3-offline-source.tar.gz').read_bytes()
 if len(blob)!=d['archive_bytes'] or sha(blob)!=d['archive_sha256']:raise ValueError('archive_pin')
 raw=gzip.decompress(blob)
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
  members=archive.getmembers();expected=set(f)|{'SOURCE-MANIFEST.json'}
  if len(members)!=len(expected) or set(x.name for x in members)!=expected:raise ValueError('archive_inventory')
  for item in members:
   if not item.isfile() or item.uid!=0 or item.gid!=0 or item.mode!=0o444 or item.mtime!=0:raise ValueError('archive_metadata')
   data=archive.extractfile(item).read()
   want=(TASK/'SOURCE-MANIFEST.json').read_bytes() if item.name=='SOURCE-MANIFEST.json' else (TASK/'src'/item.name).read_bytes()
   if data!=want:raise ValueError('archive_source_mismatch')
 # Independent rebuild, no extraction or privileged destination.
 buffer=io.BytesIO()
 with tarfile.open(fileobj=buffer,mode='w',format=tarfile.USTAR_FORMAT) as archive:
  for name in [*sorted(f),'SOURCE-MANIFEST.json']:
   data=(TASK/name).read_bytes() if name=='SOURCE-MANIFEST.json' else (TASK/'src'/name).read_bytes()
   item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o444;item.uid=item.gid=0;item.uname=item.gname='root';item.mtime=0;archive.addfile(item,io.BytesIO(data))
 if gzip.compress(buffer.getvalue(),mtime=0)!=blob:raise ValueError('archive_rebuild')
 return {'source_tree_sha256':m['source_tree_sha256'],'archive_sha256':d['archive_sha256'],'source_files':len(f),'archive_rebuilt_identically':True}
def verify():
 seal=json.loads((TASK/'SEAL.json').read_bytes());raw=(TASK/'MANIFEST.json').read_bytes()
 if sha(raw)!=seal['manifest_sha256'] or inventory()!=json.loads(raw):raise ValueError('packet_inventory_or_seal')
 prior=predecessors();source=source_and_archive()
 r=json.loads((TASK/'evidence/regression-release/RESULTS.json').read_bytes())
 if r['status']!='PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY' or any(r[k] for k in ('failures','errors','skips')):raise ValueError('offline_test_record')
 for name,suite in r['suites'].items():
  paths={'r3_author_enforcement':TASK/'tests/test_enforcement.py','r3_author_adapter':TASK/'tests/test_host_adapter.py','r3_independent_review':TASK/'tests/test_independent_review.py'}
  if name in paths and sha(paths[name].read_bytes())!=suite['source_sha256']:raise ValueError('tests_changed_after_run')
 replay=json.loads((TASK/'evidence/fixture-replay-1/RESULTS.json').read_bytes())
 if replay['status']!='PASS_OFFLINE_FIXTURE_REPLAY_ONLY':raise ValueError('fixture_record')
 return {'status':'PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY',**source,**prior,
         'test_methods':r['actual_unique_test_methods'],'r3_methods':sum(x['tests'] for n,x in r['suites'].items() if n.startswith('r3_')),
         'failures':r['failures'],'errors':r['errors'],'skips':r['skips'],
         'snapshot_fixtures':replay['snapshot_count'],'cli_checks':replay['cli_count'],
         'root_boot_go':False,'live_host_qualified':False,'expiration_guaranteed':False,
         'forced_stop_authorized_or_runtime_enabled':False,'stage2_stage3_stage4_authorized':False,
         'manifest_sha256':seal['manifest_sha256']}
if __name__=='__main__':print(json.dumps(verify(),indent=2))

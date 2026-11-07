"""Read-only verifier; never imports app, provisions trust or opens runtime stores."""
from pathlib import Path
import argparse,ast,gzip,hashlib,io,json,subprocess,tarfile
P=Path(__file__).resolve().parent;MAIN=P.parents[1];W=MAIN.parent/'JARVIS-unified-rc1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((P/n).read_text())
def safe(n):return not Path(n).is_absolute() and '..' not in Path(n).parts

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--archive-only',action='store_true');ap.add_argument('--check-working-source',action='store_true');ap.add_argument('--preseal',action='store_true');args=ap.parse_args()
 build=read('release/BUILD.json');source=read('release/SOURCE-SHA256.json');raw=(P/'release/SOURCE-SHA256.json').read_bytes()
 assert source==build['source_sha256']==read('SOURCE-SHA256.json')
 assert hashlib.sha256(raw).hexdigest()==build['source_manifest_sha256']
 assert build['release_id']=='jarvis-v2-unified-rc1-'+build['source_manifest_sha256'][:16]
 path=P/build['archive'];assert sha(path)==build['archive_sha256'] and path.stat().st_mode&0o222==0
 files={}
 with tarfile.open(path) as tar:
  members=tar.getmembers();assert [m.name for m in members]==sorted(set(m.name for m in members))
  for m in members:
   assert m.isfile() and safe(m.name) and m.uid==m.gid==m.mtime==0 and m.mode==0o644
   files[m.name]=tar.extractfile(m).read();assert len(files[m.name])==m.size
 assert set(files)==set(source)|{'_release/SOURCE-SHA256.json','_release/requirements-offline.lock','_release/CANDIDATE.json'}
 for n,h in source.items():
  assert hashlib.sha256(files[n]).hexdigest()==h,n
  assert safe(n) and Path(n).name!='config.yaml' and not Path(n).name.startswith('.env')
  assert Path(n).suffix not in {'.key','.pem','.db','.sqlite','.pyc'}
  assert Path(n).parts[0] not in {'data','logs','models','piper','jarvis-vault'}
  if n.endswith('.py'):ast.parse(files[n],filename=n)
 assert files['_release/SOURCE-SHA256.json']==raw
 assert files['_release/requirements-offline.lock']==(P/'release/requirements-offline.lock').read_bytes()
 info=json.loads(files['_release/CANDIDATE.json']);assert info['git_revision']==build['git_revision'] and not info['real_execution_enabled'] and not info['production_authorized']
 # Reconstruct deterministic USTAR/gzip without extracting any member.
 out=io.BytesIO()
 with gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0,compresslevel=9) as gz:
  with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as tar:
   for n,b in sorted(files.items()):
    m=tarfile.TarInfo(n);m.size=len(b);m.mode=0o644;m.uid=m.gid=m.mtime=0;m.uname=m.gname='';tar.addfile(m,io.BytesIO(b))
 assert out.getvalue()==path.read_bytes()
 result={'status':'PASS','release_id':build['release_id'],'git_revision':build['git_revision'],'archive_sha256':build['archive_sha256'],'public_source_files':len(source),'deterministic_archive_rebuilt_identically':True,'real_execution_enabled':False}
 if args.archive_only:print(json.dumps(result,indent=2));return
 for n,h in read('INDEPENDENT-REVIEW-PINS.json').items():assert source[n]==h,n
 app={n:h for n,h in source.items() if n.startswith('app/') and n.endswith('.py')};assert len(app)==102
 results=read('RESULTS.json');assert results['source_sha256']==app
 for mode,info in results['final_runs'].items():
  d=P/'runs'/info['run'];r=json.loads((d/'RUN.json').read_text())
  assert r['status']=='PASS' and not r['guard_stop'] and r['source_sha256']==app
  assert sha(P/'run_checks.py')==r['runner_sha256']==info['runner_sha256']
  assert sha(d/'INPUT-SHA256SUMS')==r['input_manifest_sha256']==info['input_manifest_sha256']
  for line in (d/'INPUT-SHA256SUMS').read_text().splitlines():
   h,n=line.split('  ',1);assert safe(n) and not (d/'input'/n).is_symlink() and sha(d/'input'/n)==h,n
  for folder in ['tests','regressions','repository/tests']:
   for f in (d/'input'/folder).rglob('*.py'):
    n='tests/'+str(f.relative_to(d/'input'/folder))
    if n in source:assert sha(f)==source[n],str(f)
  c=r['child'];assert all(x['outcome']=='passed' for x in c.get('outcomes',c.get('node_outcomes',[])))
 assert results['actual_unique_pytest_passed']==1023 and results['repository_collected']==952 and results['repository_passed']==943 and results['repository_excluded']==9
 assert results['final_failures']==results['final_skips']==0
 assert results['application_scenario_groups']==20 and results['benchmark_cases']==13
 inventory=read('TEST-INVENTORY.json');assert len(inventory['passed_unique_normalized_nodeids'])==len(set(inventory['passed_unique_normalized_nodeids']))==1023
 assert len(inventory['supplemental_packet_nodeids'])==80 and len(inventory['excluded'])==9
 security=read('SECURITY-SELECTED-RESULTS.json');assert security['unique_cases']==179
 invocations=read('SECURITY-PINNED-INVOCATIONS.json');assert len(invocations)==7
 for invocation in invocations:
  assert invocation['exitcode']==0
  f=P/'runs'/(invocation['owner']+'-'+invocation['harness']+'_pinned.json');r=json.loads(f.read_text())
  assert r['exit_code']==0 and r['runner_sha256']==sha(P/'security_runner.py')
  assert r['dependency_manifest_sha256']==sha(P/'SECURITY-DEPENDENCY-SHA256.json')
  for entry in r['snapshot_files']:
   n=entry['path'];assert source[n]==entry['sha256'],n
 assert not read('DEPENDENCY-CONFIGURATION.json')['unsatisfied_metadata_dependencies']
 crash=read('CRASH-RECOVERY.json');assert crash['total']==37 and len(crash['fresh_current_source_cases']['signed_transport'])==15 and len(crash['fresh_current_source_cases']['registry_witness'])==22
 proposal=read('LIVE-READONLY-PROPOSAL.json');assert proposal['candidate_git_revision']==build['git_revision'] and proposal['candidate_archive_sha256']==build['archive_sha256']
 assert proposal['request_id'] is None and proposal['maximum_guest_actions']==1 and not proposal['privileged_Gate6K_authorized'] and not proposal['credential_or_permission_creation_authorized']
 initial=read('INITIAL-STATE.json');baseline=read('PREDECESSOR-SHA256.json');preserved=0
 for n,h in baseline.items():
  f=MAIN/n
  if n=='tasks/loop-log.md':assert hashlib.sha256(f.read_bytes()[:initial['log_bytes']]).hexdigest()==h
  else:assert not f.is_symlink() and sha(f)==h,n
  preserved+=1
 for n,target in read('PREDECESSOR-SYMLINKS.json').items():assert (MAIN/n).is_symlink() and str((MAIN/n).readlink())==target,n
 for n,h in initial['shared_public_hashes'].items():assert sha(MAIN/n)==h,n
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=MAIN,text=True).strip()==initial['head']
 old=MAIN/'tasks/jarvis-v2-release-readiness-r1/release/BUILD.json';oldbuild=json.loads(old.read_text())
 oldworktree=MAIN.parent/'JARVIS-release-r1'
 for n,h in oldbuild['source_sha256'].items():assert sha(oldworktree/n)==h,n
 assert (P/'REPORT.md').is_file()
 if (P/'COMPLETION-LOG.json').exists():
  completion=read('COMPLETION-LOG.json');b=completion['entry'].encode();assert (MAIN/'tasks/loop-log.md').read_bytes()[completion['offset']:completion['offset']+len(b)]==b
 elif not args.preseal:raise AssertionError('canonical completion entry missing')
 if args.check_working_source:
  assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()==build['git_revision']
  assert subprocess.check_output(['git','status','--porcelain'],cwd=W)==b''
  for n,h in source.items():assert sha(W/n)==h and hashlib.sha256(subprocess.check_output(['git','show',build['git_revision']+':'+n],cwd=W)).hexdigest()==h,n
 if not args.preseal:
  assert {str(f.relative_to(P)):str(f.readlink()) for f in P.rglob('*') if f.is_symlink()}==read('SYMLINKS.json')
  manifest={}
  for line in (P/'SHA256SUMS').read_text().splitlines():
   h,n=line.split('  ',1);assert safe(n) and n not in manifest;manifest[n]=h
  actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and not f.is_symlink() and f!=P/'SHA256SUMS'}
  assert actual==set(manifest),'evidence inventory drift'
  for n,h in manifest.items():assert not (P/n).is_symlink() and sha(P/n)==h,n
  result['artifact_files_verified']=len(manifest);result['artifact_manifest_sha256']=sha(P/'SHA256SUMS')
 result.update(actual_unique_pytest_passed=1023,selected_security_repeated_cases=179,crash_cases=37,predecessor_files_preserved=preserved,independent_review_pins=len(read('INDEPENDENT-REVIEW-PINS.json')),live_authorization=False)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()

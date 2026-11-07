"""Read-only package, test, SBOM, advisory and sealed-history verification."""
from pathlib import Path
import argparse,gzip,hashlib,io,json,os,subprocess,sys,tarfile,ast
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lab_package import load_bundle,verify_tar,digest,encoded
P=Path(__file__).resolve().parents[1];MAIN=P.parents[1];RC=MAIN/'tasks/jarvis-v2-unified-rc1'
def read(n):return json.loads((P/n).read_text())
def sha(p):return digest(p.read_bytes())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preseal',action='store_true');args=parser.parse_args()
 b=read('BUNDLE.json');raw=(P/b['bundle']).read_bytes();assert digest(raw)==b['bundle_sha256'];m,installed=load_bundle(P/b['bundle'],b['bundle_sha256'])
 assert digest(installed['INSTALL-MANIFEST.json'])==b['installed_manifest_sha256']
 rc=json.loads((RC/'release/BUILD.json').read_text());assert m['source_sha256']==rc['source_sha256'] and b['source_archive_sha256']==rc['archive_sha256']
 assert m['source_git_revision']=='e9b4734740070b9e7c990735e43801e592c114c6'
 for n in ['lab_package.py','smoke_runner.py','worker_preflight.py']:assert installed['tools/'+n]==(P/'tools'/n).read_bytes()
 assert b['bootstrap_tool_sha256']==sha(P/'tools/lab_package.py')
 # Independent deterministic reconstruction of all published package members.
 files=verify_tar(raw);out=io.BytesIO()
 with gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0,compresslevel=9) as gz:
  with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as t:
   for n,data in sorted(files.items()):
    v=tarfile.TarInfo(n);v.size=len(data);v.uid=v.gid=v.mtime=0;v.mode=0o644;v.uname=v.gname='';t.addfile(v,io.BytesIO(data))
 assert out.getvalue()==raw
 inst=read('INSTALLATION-TEST-RESULTS.json');assert inst['exitcode']==0 and inst['bundle']['bundle_sha256']==b['bundle_sha256'];assert inst['tests']['tests']==67 and inst['tests']['failures']==inst['tests']['errors']==inst['tests']['skips']==0
 for n,h in inst['input_sha256'].items():
  if n.startswith('tests/') or n in ('tools/lab_package.py','tools/worker_preflight.py','tools/run_install_tests.py'):assert sha(P/n)==h,n
 smoke_inv=read('SMOKE-INVOCATION.json');assert smoke_inv['exitcode']==0 and smoke_inv['bundle_sha256']==b['bundle_sha256'] and smoke_inv['installed_manifest_sha256']==b['installed_manifest_sha256']
 smoke=read(smoke_inv['run']+'/SMOKE-RESULT.json');assert smoke['status']=='PASS' and not smoke['guard_stop'];assert smoke['child']['regressions']=={'collected':210,'failed':0,'skipped':0,'exitstatus':0}
 assert len(smoke['child']['cases'])==20
 assert smoke['source_sha256']=={n:h for n,h in m['source_sha256'].items() if n.startswith('app/') and n.endswith('.py')}
 for n,h in read(smoke_inv['run']+'/INPUT-SHA256.json').items():assert sha(P/smoke_inv['run']/'input'/n)==h,n
 for n,h in smoke['source_sha256'].items():assert sha(P/smoke_inv['run']/'input/source'/n)==h,n
 dependencies=read(smoke_inv['run']+'/work/DEPENDENCY-CHECK.json');assert dependencies['status']=='PASS' and len(dependencies['distributions'])==31 and len(dependencies['active_metadata_edges_checked'])==33
 assert dependencies['distributions']=={d['name'].lower().replace('_','-'):d['version'] for d in m['dependencies']}
 rollback=read('FULL-ROLLBACK-RESULT.json');assert rollback['status']=='PASS_FULL_RELEASE_QUARANTINE' and rollback['preserved_files']==len(installed)==2444
 preserved=P/rollback['original_install_run']/'work'/rollback['preserved_relative_path']
 for n,data in installed.items():assert sha(preserved/n)==digest(data),n
 broker=read('BROKER-TEST-RESULTS.json');assert broker['exitcode']==0 and broker['tests']['methods']==71 and broker['tests']['subtests']==305 and not broker['tests']['failures'] and not broker['tests']['errors'] and not broker['tests']['skipped']
 assert broker['source_manifest_sha256']==b['broker_source_manifest_sha256']
 for n,data in installed.items():
  if n.startswith('serial-candidate/') and n.endswith('.py'):assert sha(P/broker['run']/'work/candidate'/n[len('serial-candidate/'):])==digest(data),n
 assert read('SBOM-VALIDATION.json')['result']['status']=='PASS_CYCLONEDX_1_6_SCHEMA';assert installed['SBOM.cdx.json']==(P/'SBOM.cdx.json').read_bytes()
 adv=read('ADVISORY-RESULTS.json');assert adv['all_queries_complete'] and adv['pypi_queries']==31 and adv['npm_queries']==13 and adv['vulnerability_records']==28
 details=read('ADVISORY-DETAILS.json');assert len(details)==28 and all(x['status']=='RETRIEVED' for x in details)
 for d in details:assert sha(P/'evidence/advisory-records'/(d['id']+'.json'))==d['sha256']
 obs=read('evidence/observer-classified.json');assert obs['status']=='BLOCKED' and obs['http_statuses']==[401] and obs['guest_console_or_mutation_calls']==0
 assert obs['client_sha256']==sha(Path('/home/nexus/.local/bin/g6k-pve164-readonly'))
 approval=read('approval.example.json');assert approval['bundle_sha256']==b['bundle_sha256'] and approval['operator_reference'] is None and approval['expires_at_utc'] is None and all(v is None for v in approval['target'].values())
 for f in list((P/'tools').glob('*.py'))+list((P/'tests').glob('*.py')):ast.parse(f.read_text(),filename=str(f))
 # Reverify the entire original RC1 and its historical predecessor chain without
 # importing application code or modifying the sealed packet.
 result=subprocess.run(['/usr/bin/python3.14','-I','-B','-S',str(RC/'verify_release.py'),'--check-working-source'],cwd=MAIN,capture_output=True,text=True,timeout=120)
 assert result.returncode==0,result.stderr[-1000:];history=json.loads(result.stdout)
 assert history['artifact_files_verified']==18582 and history['predecessor_files_preserved']==177460
 initial=read('INITIAL-STATE.json');log=(MAIN/'tasks/loop-log.md').read_bytes();assert digest(log[:initial['log_prefix_bytes']])==initial['log_prefix_sha256']
 if (P/'COMPLETION-LOG.json').exists():
  completion=read('COMPLETION-LOG.json');entry=completion['entry'].encode();assert log[completion['offset']:completion['offset']+len(entry)]==entry
 elif not args.preseal:raise AssertionError('canonical completion log missing')
 if not args.preseal:
  expected={}
  for line in (P/'SHA256SUMS').read_text().splitlines():
   h,n=line.split('  ',1);assert not Path(n).is_absolute() and '..' not in Path(n).parts;expected[n]=h
  actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and not f.is_symlink() and f!=P/'SHA256SUMS'}
  assert set(expected)==actual
  for n,h in expected.items():assert sha(P/n)==h,n
  assert {str(f.relative_to(P)):str(f.readlink()) for f in P.rglob('*') if f.is_symlink()}==read('SYMLINKS.json')
 print(json.dumps({'status':'PASS_PREPARATION_ENGINEERING_ONLY','bundle_sha256':b['bundle_sha256'],'bundle_bytes':b['bundle_bytes'],'source_files':315,'wheel_count':31,'installed_files':2444,'installation_tests':67,'application_tests':210,'application_groups':20,'broker_methods':71,'broker_subtests':305,'full_release_rollback_preserved':True,'sbom_schema_validated':True,'advisory_records':28,'observer_HTTP':401,'historical_RC1_evidence_files_verified':18582,'prior_files_verified':177460,'protected_installation_authorized_or_performed':False,'live_readiness':'BLOCKED'},indent=2))
if __name__=='__main__':main()

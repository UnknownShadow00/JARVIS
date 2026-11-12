"""Independent stdlib-only reconstruction; imports no target/verifier/test code."""
from pathlib import Path
import collections, hashlib, importlib.metadata, json, os, platform, re, subprocess
A=Path(__file__).resolve().parent
R=A.parents[1]
W=R.parent/'JARVIS-v2-canonical-integration-safety-r2'
P=W/'tasks/jarvis-v2-canonical-integration-safety-r2'
C=Path(json.loads((A/'CHECKOUT.json').read_text())['path'])
S='32bc552e033a0bc3cf46135c084f399a371e2244';T='10f1c51d6c0fedbc70ce51cf108a7f89f9c7b64a';D='0bc7e3cdf5fe99cfc499b8275a5be9a8a7d112d3'
M='6341648131cec7318ea961c3b081878fb86c4fe7';CP='b09fa10a661c9704f51e900ec857a51153cbcbbe';RP='674aff2c25d050420145f9b102808f194f0544fa';E='2af89d5a5521aa0c1237417a5fd98b1081dabcbc'
TECH='3e04d53c848467db6450f76132ad77295391b9128c37eaf3a0cb9445cb3d0d5d'
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def filehash(p):return sha(p.read_bytes())
def git_hashes(commit,names):
 names=list(names);raw=subprocess.check_output(['git','-C',str(R),'cat-file','--batch'],input=('\n'.join(commit+':'+n for n in names)+'\n').encode())
 pos=0;out={}
 for name in names:
  end=raw.index(b'\n',pos);head=raw[pos:end].split();assert head[1]==b'blob',(name,head)
  length=int(head[2]);data=raw[end+1:end+1+length];out[name]=sha(data);pos=end+length+2
 return out

def seal(folder,name,count):
 lines=(folder/name).read_text().splitlines();assert len(lines)==count
 checked=[]
 for line in lines:
  digest,rel=line.split('  ',1);p=folder/rel
  assert not Path(rel).is_absolute() and '..' not in Path(rel).parts and not p.is_symlink() and filehash(p)==digest,(folder,rel)
  checked.append(rel)
 assert len(set(checked))==len(checked)
 return {'entries':len(lines),'sha256':filehash(folder/name)}

result={}
assert git('show','-s','--format=%T',S)==T
assert git('show','-s','--format=%P',S)==D
assert git('show','-s','--format=%P',M)==CP+' '+RP
assert git('show','-s','--format=%P',E)==S
assert git('rev-parse','HEAD')==CP
assert subprocess.run(['git','-C',str(R),'merge-base','--is-ancestor',M,S]).returncode==0
for n in (CP,RP):assert subprocess.run(['git','-C',str(R),'merge-base','--is-ancestor',n,S]).returncode==0
assert subprocess.run(['git','-C',str(R),'merge-base','--is-ancestor','ddf7b89f',S]).returncode==1
assert subprocess.check_output(['git','-C',str(C),'status','--porcelain'],text=True)==''
assert subprocess.check_output(['git','-C',str(W),'status','--porcelain'],text=True)==''
result['git']={'source':S,'tree':T,'parent':D,'original_merge':M,'merge_parents':[CP,RP],'evidence_only_child':E,'canonical_head':CP,'canonical_branch':git('branch','--show-current')}
changes=git('diff','--name-only',M,S).splitlines();assert len(changes)==15
assert not any(n.startswith(('app/','tasks/')) for n in changes)
result['source_changes']={n:filehash(C/n) for n in changes}
child=git('diff','--name-only',S,E).splitlines();assert len(child)==958 and all(n.startswith('tasks/jarvis-v2-canonical-integration-safety-r2/') for n in child)
assert git_hashes(E,child)=={n:filehash(W/n) for n in child}
result['evidence_child_files']=len(child)
result['technical_seal']=seal(P,'EVIDENCE-SHA256SUMS',943);assert result['technical_seal']['sha256']==TECH
result['outer_seal']=seal(P,'SHA256SUMS',957)
assert set((P/'SHA256SUMS').read_text().split('  ',1)[-1]) # seal checks above
manifest=read(C/'scripts/required_tests.json');policy=read(C/'scripts/test_enrollment.json')['modules']
assert filehash(C/'scripts/required_tests.json')=='c62ffae6ff57487af4aeeff9b8cb0dad3c47ac933c17b017f7fc31198772af52'
assert filehash(C/'scripts/test_enrollment.json')=='da49ec83861d077578daea20d7cfc168b6af3feabd2d16949a2040914ec1eb98'
actual={str(p.relative_to(C)) for p in (C/'tests').rglob('*.py')};assert actual==set(policy)
assert all(filehash(C/n)==v['sha256'] for n,v in policy.items())
counts=dict(collections.Counter(v['disposition'] for v in policy.values()))
assert counts=={'required':68,'support':17,'negative_fixture':2,'excluded_offline_scope':39,'excluded_live_or_hardware':11}
modes={'safety':36,'coverage':217,'reconciliation':66,'r3':19,'r2':45,'new':32,'existing':507}
nodes=[n for mode in modes for n in manifest['suites'][mode]['nodeids']]
assert len(nodes)==len(set(nodes))==922
assert {n.split('::',1)[0] for n in nodes}=={n for n,v in policy.items() if v['disposition']=='required'}
old=read(C/'scripts/required_nodes_6341648.json')['nodeids'];old_manifest=json.loads(subprocess.check_output(['git','-C',str(R),'show',M+':scripts/required_tests.json']))
old_real=[n for k,v in old_manifest['suites'].items() if k not in ['probe'] and not k.startswith('case:') for n in v['nodeids']]
assert len(old)==886 and set(old)==set(old_real) and set(old)<=set(nodes)
assert set(nodes)-set(old)==set(manifest['suites']['safety']['nodeids'])
for mode in modes:
 suite=manifest['suites'][mode];assert len(suite['nodeids'])==modes[mode]
 assert len(suite['nodeids'])==len(set(suite['nodeids'])) and suite['nodeids']==sorted(suite['nodeids'])
 assert all(filehash(C/n)==d for n,d in suite['sources'].items())
result['enrollment']={'python_files':len(actual),'dispositions':counts,'required_cases':len(nodes),'retained_original_ids':len(old),'new_ids':36,'inventory_sha256':filehash(C/'scripts/required_tests.json'),'module_policy_sha256':filehash(C/'scripts/test_enrollment.json')}
history=read(C/'scripts/historical_packet_inventory.json');hist=history['files'];assert len(hist)==883
assert git_hashes(M,hist)==hist=={n:filehash(C/n) for n in hist}
actualhist={str(p.relative_to(C)) for folder in history['folders'] for p in (C/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts};assert actualhist==set(hist)
archives=[n for n in hist if '/preserved-development-tests/test_' in n and n.endswith('.py')];assert len(archives)==12
assert all('tests/'+Path(n).name in policy and policy['tests/'+Path(n).name]['disposition']=='required' for n in archives)
old_test_hashes=git_hashes(CP,['tests/'+Path(n).name for n in archives]);assert all(hist[n]==old_test_hashes['tests/'+Path(n).name] for n in archives)
entries=git('ls-tree','-r',S,'--',*history['folders']).splitlines();assert len(entries)==883 and all(line.startswith('100644 blob ') for line in entries)
assert all(not p.is_symlink() for folder in history['folders'] for p in (C/folder).rglob('*'))
result['historical']={'files':883,'bytes':sum((C/n).stat().st_size for n in hist),'all_modes':'100644','symlinks':0,'test_modules':archives,'python_tools':[n for n in hist if n.endswith('.py') and n not in archives]}
qualified=read(C/'scripts/offline_environment.json')
deps=Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages')
packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[str(deps)])}
assert packages==qualified['packages'] and platform.python_version()==qualified['python']
assert subprocess.check_output(['/usr/bin/bwrap','--version'],text=True).strip()==qualified['bwrap']
assert packages['APScheduler']=='3.11.3';result['environment']={'python':platform.python_version(),'bwrap':qualified['bwrap'],'package_count':len(packages),'packages':packages}

def ids_for(nodes):
 seen={};ids={}
 for n in nodes:
  base=n.split('[',1)[0];idx=seen.get(base,0);seen[base]=idx+1;ids[n]=sha((base+'#'+str(idx)).encode())
 return ids

def verify_run(folder):
 b=read(folder/'RESULT.json');assert b['status']=='PASS' and b['source_commit']==S and b['git_tree']==T
 before=b['source_sha256'];assert len(before)==274
 assert before==b['source_after_sha256']==b['snapshot_after_sha256']==git_hashes(S,before)=={n:filehash(C/n) for n in before}
 snapshot=Path(b['source_snapshot']);assert {n:filehash(snapshot/n) for n in before}==before
 assert all((snapshot/n).stat().st_mode&0o222==0 for n in before)
 assert snapshot.stat().st_mode&0o222==0
 assert b['environment']['packages']==packages and b['historical_sha256']==hist
 assert b['inventory_sha256']==result['enrollment']['inventory_sha256']
 assert b['content_tree_sha256']==sha(json.dumps(before,sort_keys=True).encode())
 runs=read(folder/'RUNS.json');assert len(runs)==17 and all(r['exit']==0 for r in runs) and runs==b['runs']
 all_ids=[];executed=[];repeat=0;summaries=[]
 for mode,count in modes.items():
  mapping=ids_for(manifest['suites'][mode]['nodeids'])
  for suffix in (['','-seed42'] if mode!='existing' else ['']):
   q=read(folder/(mode+suffix+'.json'));observed=[s['id'] for s in q['scenarios']]
   assert len(observed)==len(set(observed))==count and set(observed)==set(mapping.values())
   assert q['status']=='PASS' and q['child_exit_code']==q['gate_exit_code']==0
   assert q['counts']==dict(PASS=count,FAIL=0,ERROR=0,SKIP=0,INCOMPLETE=0)
   assert q['required_count']==q['collected']==q['attempted']==q['executed']==count
   assert q['required_missing']==q['unexpected_collected']==0 and q['collection']==dict(skipped=0,deselected=0)
   s=q['session'];assert all(s[k] is True for k in ['started','collected','finished']) and not any(s[k] for k in ['interrupted','internal_error','collection_error','unexpected_report'])
   assert s['pytest_exit_code']==0 and s['collected_count']==count
   assert q['seed']==(42 if suffix else 16401)
   for s in q['scenarios']:
    assert s['complete'] and not s['timed_out'] and s['status']=='PASS'
    assert [p['phase'] for p in s['phases']]==['setup','call','teardown'] and all(p['outcome']=='passed' for p in s['phases'])
   if suffix:repeat+=count
   else:
    all_ids.extend(observed);executed += [{'mode':mode,'nodeid':n,'id':i} for n,i in mapping.items()];summaries.append(dict(mode=mode,counts=q['counts'],missing=0,incomplete=0,gate_exit=0,child_exit=0))
 assert len(all_ids)==len(set(all_ids))==922 and repeat==415
 contractcounts={}
 for kind,count,key in [('gate22',22,'contract_pass'),('adversaries11',11,'passed')]:
  rows=read(folder/kind/'SUMMARY.json');assert len(rows)==count and all(r[key] for r in rows);contractcounts[kind]=len(rows)
 rows=read(folder/'negative14/SUMMARY.json')['checks'];assert len(rows)==14 and all(r['status']=='PASS' and r['gate_exit']!=0 and r['gate_status']!='PASS' for r in rows);contractcounts['negative14']=14
 rows=read(folder/'attacks12/SUMMARY.json');assert len(rows)==12 and all(r['exit']!=0 and r['status']!='PASS' and not r['secret_leaked'] for r in rows);contractcounts['attacks12']=12
 seal_info=seal(folder,'SHA256SUMS',155)
 return dict(path=str(folder),suites=summaries,distinct=922,seeded_repeats=415,positive_executions=1337,completed_test_identities=executed,contracts=contractcounts,source_inputs=len(before),input_fingerprint=b['content_tree_sha256'],snapshot=str(snapshot),manifest=seal_info,result_sha256=filehash(folder/'RESULT.json'))
result['fresh']=[verify_run(A/'acceptance-script'),verify_run(A/'acceptance-module')]
result['reported']=[verify_run(P/'qualified-ci-final/jarvis-offline-acceptance'),verify_run(P/'qualified-module-final')]
assert all(r['exit']==0 for r in read(A/'EXECUTIONS.json'))
extra=read(A/'entrypoint-contracts/SUMMARY.json');assert len(extra)==7 and all(r['passed'] for r in extra);result['additional_entrypoint_contracts']=7
result['status']='PASS'
(A/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k in ['git','technical_seal','outer_seal','enrollment','status']},indent=2))

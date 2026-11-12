"""Independent reconstruction of exact merge/child/acceptance evidence.

No application, engineering verifier or inventory loader is imported.
All outputs go to this separate audit directory, never the reviewed checkout.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.metadata
import json
import subprocess

OUT=Path(__file__).resolve().parent
CANON=OUT.parents[1]
WORK=CANON.parent/'JARVIS-v2-canonical-integration-proposal-r1'
PACKET=WORK/'tasks/jarvis-v2-canonical-integration-proposal-r1'
M='6341648131cec7318ea961c3b081878fb86c4fe7'
C='b09fa10a661c9704f51e900ec857a51153cbcbbe'
R='674aff2c25d050420145f9b102808f194f0544fa'
A='ddf7b89f0e55269f337cd05c19b6ee915dd31dcd'
T='8838c386db3bbe2d4b6e51d0ef884bdc844bc99d'
E='c2ebb33e9c88fa62afc5f6cb9efc1de6c5c2e65557fa7d4a7e68ae78cf9895a7'
MODES={'coverage':217,'reconciliation':66,'r3':19,'r2':45,'original':32,'existing':507}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def git(*args):return subprocess.check_output(['git',*args],cwd=WORK,text=True).strip()
def blob(ref,name):return subprocess.check_output(['git','show',ref+':'+name],cwd=WORK)
def seal(root,name):
    seen=set()
    for line in (root/name).read_text().splitlines():
        digest,path=line.split('  ',1)
        assert path not in seen and not Path(path).is_absolute() and '..' not in Path(path).parts
        assert sha(root/path)==digest;seen.add(path)
    return seen
def mapping(nodes):
    counters,result={},{}
    for n in nodes:
        base=n.split('[',1)[0];ordinal=counters.get(base,0);counters[base]=ordinal+1
        key=hashlib.sha256(f'{base}#{ordinal}'.encode()).hexdigest();assert key not in result;result[key]=n
    return result

def suite_set(folder):
    r=read(folder/'RESULT.json');assert r['source_commit']==M and r['git_tree']==T and r['status']=='PASS'
    hashes=r['source_sha256'];snapshot=Path(r['source_snapshot'])
    assert len(hashes)==266 and hashes==r['source_after_sha256']==r['snapshot_after_sha256']
    for n,d in hashes.items():
        assert sha(WORK/n)==sha(snapshot/n)==hashlib.sha256(blob(M,n)).hexdigest()==d
        assert hashlib.sha256(blob('da67d936',n)).hexdigest()==d
        assert not (snapshot/n).stat().st_mode & 0o222
    assert not snapshot.stat().st_mode & 0o222
    assert all(not p.stat().st_mode & 0o222 for p in snapshot.rglob('*') if p.is_dir())
    fingerprint=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    assert fingerprint==r['content_tree_sha256']=='da3f737d827f7e33cc18e82a6dee65808af399823a8ac7b9a1db829055667373'
    unique,repeat,summary,executed=set(),0,[],{}
    for mode,count in MODES.items():
        required=mapping(manifest['suites']['new' if mode=='original' else mode]['nodeids'])
        assert len(required)==count
        for suffix in ('','-seed42') if mode!='existing' else ('',):
            d=read(folder/(mode+suffix+'.json'));scenarios=d['scenarios'];ids=[s['id'] for s in scenarios]
            assert len(ids)==len(set(ids))==count and set(ids)==set(required)
            assert d['status']=='PASS' and d['gate_exit_code']==d['child_exit_code']==0
            assert d['required_missing']==d['unexpected_collected']==0 and d['collection']=={'skipped':0,'deselected':0}
            assert d['required_count']==d['collected']==d['executed']==d['attempted']==count
            assert d['counts']=={'PASS':count,'FAIL':0,'ERROR':0,'SKIP':0,'INCOMPLETE':0}
            assert d['seed']==(42 if suffix else 16401)
            session=d['session'];assert all(session[k] for k in ('started','collected','finished'))
            assert not any(session[k] for k in ('interrupted','internal_error','collection_error','unexpected_report'))
            assert session['collected_count']==count and session['pytest_exit_code']==0
            for s in scenarios:
                assert s['status']=='PASS' and s['complete'] and not s['timed_out']
                assert [p['phase'] for p in s['phases']]==['setup','call','teardown'] and all(p['outcome']=='passed' for p in s['phases'])
            if suffix:repeat+=count
            else:
                assert not unique.intersection(ids);unique.update(ids);executed[mode]=sorted(required.values());summary.append({'suite':mode,'pass':count,'fail':0,'error':0,'skip':0,'missing':0,'incomplete':0,'child_exit':0,'gate_exit':0})
    assert len(unique)==r['distinct_positive']==886 and repeat==r['repeat_executions']==379
    assert len(r['runs'])==14 and all(x['exit']==0 for x in r['runs'])
    for group,count,key in [('gate22',22,'contract_pass'),('adversaries11',11,'passed')]:
        rows=read(folder/group/'SUMMARY.json');assert len(rows)==count and all(x[key] for x in rows)
    rows=read(folder/'negative14/SUMMARY.json')['checks'];assert len(rows)==14 and all(x['status']=='PASS' and x['gate_status']!='PASS' and x['gate_exit']!=0 for x in rows)
    old,new=read(folder/'gate22/before-astra.json'),read(folder/'gate22/astra.json')
    assert old['status']=='PASS' and old['gate_exit_code']==0 and old['executed']==31 and old['counts']['SKIP']==0
    assert new['status']=='FAIL' and new['gate_exit_code']==1 and new['child_exit_code']==0 and new['required_count']==45 and new['executed']==31 and new['required_missing']==14
    hashes_verified=len(seal(folder,'SHA256SUMS'));assert hashes_verified==123
    assert folder.stat().st_mode & 0o077==0 and all(p.stat().st_mode & 0o077==0 for p in folder.rglob('*') if p.is_file())
    return {'source_commit':M,'tree':T,'status':'PASS','input_count':266,'fingerprint':fingerprint,'snapshot':str(snapshot),'distinct_positive':886,'seeded_repeats':379,'suites':summary,'completed_nodeids':executed,'acceptance_hashes':hashes_verified}

if __name__=='__main__':
    assert git('rev-parse','HEAD')==A and not git('status','--porcelain')
    assert git('show','-s','--format=%P',M).split()==[C,R] and git('rev-parse',M+'^{tree}')==T
    assert git('show','-s','--format=%P',A)==M
    assert sha(PACKET/'EVIDENCE-SHA256SUMS')==E
    technical=seal(PACKET,'EVIDENCE-SHA256SUMS');outer=seal(PACKET,'SHA256SUMS');assert len(technical)==187 and len(outer)==200
    files={str(p.relative_to(WORK)) for p in PACKET.rglob('*') if p.is_file()}
    assert len(files)==201 and files==set(git('diff','--name-only',M,A).splitlines())
    assert files=={x['path'] for x in read(PACKET/'CHANGED-FILES.json')['later_evidence_only_changes']}
    for n in files:assert hashlib.sha256(blob(A,n)).hexdigest()==sha(WORK/n)
    policy=read(WORK/'scripts/test_enrollment.json')['modules'];manifest=read(WORK/'scripts/required_tests.json')
    assert sha(WORK/'scripts/test_enrollment.json')=='287ab432aa03ac8750a6c58257627077c097e80f98794eaf25c058d6acbdcd1f'
    assert sha(WORK/'scripts/required_tests.json')=='bc7359fc23710f82d780943e15c10a45d4df53380884c84c92699c3bc6139f15'
    actual={str(p.relative_to(WORK)) for p in (WORK/'tests').rglob('*.py') if '__pycache__' not in p.parts};assert actual==set(policy) and len(actual)==136
    counts=dict(Counter(e['disposition'] for e in policy.values()));assert counts=={'required':67,'support':17,'negative_fixture':2,'excluded_offline_scope':39,'excluded_live_or_hardware':11}
    nodes=[]
    for mode,count in MODES.items():
        s=manifest['suites']['new' if mode=='original' else mode];assert s['nodeids']==sorted(set(s['nodeids'])) and len(s['nodeids'])==count;nodes+=s['nodeids']
        for n,d in s['sources'].items():assert sha(WORK/n)==d
    assert len(nodes)==len(set(nodes))==886
    assert {n.split('::')[0] for n in nodes}=={n for n,e in policy.items() if e['disposition']=='required'}
    for n,e in policy.items():assert sha(WORK/n)==e['sha256'] and e['reason']
    initial=read(PACKET/'INITIAL-STATE.json')
    for ref,paths in ((C,initial['canonical_changed_paths']),(R,initial['candidate_changed_paths'])):
        for n in paths:assert blob(ref,n)==blob(M,n)
    assert set(git('diff','--name-only',C,M).splitlines())==set(initial['candidate_changed_paths']) and len(initial['candidate_changed_paths'])==932
    assert set(git('diff','--name-only',R,M).splitlines())==set(initial['canonical_changed_paths']) and len(initial['canonical_changed_paths'])==128
    assert not git('diff','--name-only','b0c8865a',M,'--','app')
    old=suite_set(PACKET/'acceptance');fresh=suite_set(OUT/'acceptance');assert old['completed_nodeids']==fresh['completed_nodeids']
    for folder in (PACKET/'audit-attacks12',OUT/'attacks12'):
        rows=read(folder/'SUMMARY.json');assert len(rows)==12 and all(x['exit']!=0 and x['status']!='PASS' and not x['secret_leaked'] for x in rows)
    for folder in (PACKET/'additional-probes',OUT/'additional-probes'):
        extra=read(folder/'SUMMARY.json');assert len(extra['cli'])==6 and len(extra['tampering'])==3 and all(x['passed'] for x in extra['cli']+extra['tampering'])
    assert read(OUT/'EXECUTION.json')['exit']==0 and all(x['exit']==0 for x in read(OUT/'ADVERSARIAL-EXECUTIONS.json'))
    dep=read(PACKET/'QUALIFIED-DEPENDENCIES.json');current={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[dep['dependency_directory']])};assert current==dep['versions'] and current['APScheduler']=='3.11.3'
    result={'status':'PASS','merge':M,'parents':[C,R],'tree':T,'evidence_child':A,'technical_digest':E,'technical_entries':187,'outer_entries':200,'evidence_child_paths':201,'preserved_canonical_paths':128,'reviewed_import_paths':932,'source_inputs':266,'enrollment':counts,'original':old,'fresh':fresh,'gate_contracts':22,'negative_contracts':14,'enrollment_adversaries':11,'replayed_attacks':12,'additional_cli':6,'report_tamper':3,'supplemental_positive_control':217,'qualified_dependency_versions_match':True,'dependency_versions':current,'independent_custody':False,'context_note':'Inherited implementation context; separate verifier and fresh execution, not fresh-context organizational custody.'}
    with (OUT/'VERIFICATION.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k not in ('original','fresh','dependency_versions')}))

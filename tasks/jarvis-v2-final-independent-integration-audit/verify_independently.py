"""Independent read-only reconstruction of original and fresh acceptance evidence.

Does not import the engineering verifier, test inventory loaders or application.
Writes only a NEW audit result. Retained snapshots and trusted Git objects required.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
WORK = ROOT.parent / 'JARVIS-v2-final-integration-rehearsal-r2'
PACKET = WORK / 'tasks/jarvis-v2-final-integration-rehearsal-r2'
SOURCE = 'da67d936566d330fad02fa8f23f8e1be2d4b80ad'
REVIEW = '674aff2c25d050420145f9b102808f194f0544fa'
MANIFEST = 'bc7359fc23710f82d780943e15c10a45d4df53380884c84c92699c3bc6139f15'
POLICY = '287ab432aa03ac8750a6c58257627077c097e80f98794eaf25c058d6acbdcd1f'
MODES = [('coverage',217), ('reconciliation',66), ('r3',19), ('r2',45), ('original',32), ('existing',507)]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=WORK, text=True).strip()

def read(path):
    return json.loads(path.read_text())

def seal(root):
    listed = {}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert name not in listed and sha(root/name) == expected
        listed[name] = expected
    return listed

def mapping(nodes):
    seen, result = {}, {}
    for node in nodes:
        name = node.split('[', 1)[0]
        ordinal = seen.get(name, 0)
        seen[name] = ordinal + 1
        key = hashlib.sha256(f'{name}#{ordinal}'.encode()).hexdigest()
        assert key not in result
        result[key] = node
    return result

def verify_set(directory):
    result = read(directory/'RESULT.json')
    assert result['status'] == 'PASS'
    assert result['source_sha256'] == result['source_after_sha256'] == result['snapshot_after_sha256']
    snapshot = Path(result['source_snapshot'])
    inputs = result['source_sha256']
    assert len(inputs) == 266
    assert result['source_commit'] == (SOURCE if directory == PACKET/'acceptance' else REVIEW)
    assert result['git_tree'] == git('rev-parse', result['source_commit']+'^{tree}')
    for name, value in inputs.items():
        assert sha(WORK/name) == sha(snapshot/name) == value
        blob = subprocess.check_output(['git','show',SOURCE+':'+name], cwd=WORK)
        assert hashlib.sha256(blob).hexdigest() == value
        assert not (snapshot/name).stat().st_mode & 0o222
    assert not snapshot.stat().st_mode & 0o222
    assert all(not p.stat().st_mode & 0o222 for p in snapshot.rglob('*') if p.is_dir())
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    assert result['content_tree_sha256'] == fingerprint == 'da3f737d827f7e33cc18e82a6dee65808af399823a8ac7b9a1db829055667373'
    unique, repeat, summary, completed = set(), 0, [], {}
    for suite, count in MODES:
        mode = 'new' if suite == 'original' else suite
        required = mapping(inventory['suites'][mode]['nodeids'])
        for suffix in ('', '-seed42') if suite != 'existing' else ('',):
            body = read(directory/(suite+suffix+'.json'))
            scenarios = body['scenarios']
            ids = [s['id'] for s in scenarios]
            assert len(ids) == len(set(ids)) == len(required) == count
            assert set(ids) == set(required)
            assert body['counts'] == {'PASS':count,'FAIL':0,'ERROR':0,'SKIP':0,'INCOMPLETE':0}
            assert body['status'] == 'PASS' and body['gate_exit_code'] == body['child_exit_code'] == 0
            assert body['required_count'] == body['collected'] == body['attempted'] == body['executed'] == count
            assert body['required_missing'] == body['unexpected_collected'] == 0
            assert body['collection'] == {'skipped':0,'deselected':0}
            assert body['inventory_sha256'] == MANIFEST
            assert body['seed'] == (42 if suffix else 16401)
            session = body['session']
            assert all(session[k] is True for k in ('started','collected','finished'))
            assert all(session[k] is False for k in ('interrupted','internal_error','collection_error','unexpected_report'))
            assert session['pytest_exit_code'] == 0 and session['collected_count'] == count
            for s in scenarios:
                assert s['status'] == 'PASS' and s['complete'] is True and s['timed_out'] is False
                assert [p['phase'] for p in s['phases']] == ['setup','call','teardown']
                assert all(p['outcome'] == 'passed' and p['category'] is None for p in s['phases'])
            if suffix:
                repeat += len(ids)
            else:
                assert not unique.intersection(ids)
                unique.update(ids)
                completed[suite] = sorted(required.values())
                summary.append({'suite':suite,'pass':count,'fail':0,'error':0,'skip':0,'missing':0,'incomplete':0,'gate_exit':0,'child_exit':0})
    assert len(unique) == result['distinct_positive'] == 886
    assert repeat == result['repeat_executions'] == 379
    assert len(result['runs']) == 14 and all(r['exit'] == 0 for r in result['runs'])
    assert {r['name'] for r in result['runs']} == {n+s for n,_ in MODES for s in ('','-seed42') if not (n=='existing' and s)} | {'gate22','negative14','adversaries11'}
    for group, count, key in [('gate22',22,'contract_pass'),('adversaries11',11,'passed')]:
        rows = read(directory/group/'SUMMARY.json')
        assert len(rows) == count and all(row[key] is True for row in rows)
    negatives = read(directory/'negative14/SUMMARY.json')['checks']
    assert len(negatives) == 14 and all(n['status']=='PASS' and n['gate_exit']!=0 and n['gate_status']!='PASS' for n in negatives)
    old, new = read(directory/'gate22/before-astra.json'), read(directory/'gate22/astra.json')
    assert old['status']=='PASS' and old['gate_exit_code']==0 and old['executed']==31 and old['counts']['SKIP']==0
    assert new['status']=='FAIL' and new['gate_exit_code']==1 and new['child_exit_code']==0 and new['executed']==31 and new['required_count']==45 and new['required_missing']==14
    absent = sorted(set(mapping(inventory['suites']['r2']['nodeids'])) - {s['id'] for s in new['scenarios']})
    assert len(absent)==14
    assert directory.stat().st_mode & 0o077 == 0
    assert all(p.stat().st_mode & 0o077 == 0 for p in directory.rglob('*') if p.is_file())
    return {'status':'PASS','source_commit':result['source_commit'],'git_tree':result['git_tree'],'input_fingerprint':fingerprint,'input_count':len(inputs),'distinct_positive':len(unique),'seeded_repeat_executions':repeat,'suites':summary,'completed_nodeids':completed,'contracts':{'gate':22,'negative':14,'enrollment_adversaries':11},'acceptance_hashes':len(seal(directory)),'snapshot':str(snapshot),'missing_astra_nodeids':[mapping(inventory['suites']['r2']['nodeids'])[key] for key in absent]}

if __name__=='__main__':
    assert git('rev-parse','HEAD') == REVIEW and git('rev-parse','HEAD^') == SOURCE
    assert not git('status','--porcelain')
    assert sha(WORK/'scripts/required_tests.json') == MANIFEST
    assert sha(WORK/'scripts/test_enrollment.json') == POLICY
    inventory=read(WORK/'scripts/required_tests.json')
    policy=read(WORK/'scripts/test_enrollment.json')['modules']
    actual={str(p.relative_to(WORK)) for p in (WORK/'tests').rglob('*.py') if '__pycache__' not in p.parts}
    assert actual==set(policy)
    counts=dict(Counter(e['disposition'] for e in policy.values()))
    assert counts=={'required':67,'support':17,'negative_fixture':2,'excluded_offline_scope':39,'excluded_live_or_hardware':11}
    required_nodes=[]
    for mode,count in MODES:
        suite=inventory['suites']['new' if mode=='original' else mode]
        assert suite['nodeids']==sorted(set(suite['nodeids'])) and len(suite['nodeids'])==count
        required_nodes+=suite['nodeids']
        for name,digest in suite['sources'].items():assert sha(WORK/name)==digest
    assert len(required_nodes)==len(set(required_nodes))==886
    assert {n.split('::')[0] for n in required_nodes}=={n for n,e in policy.items() if e['disposition']=='required'}
    for name,e in policy.items():assert e['reason'] and sha(WORK/name)==e['sha256']
    changed=set(git('diff','--name-only',SOURCE,REVIEW).splitlines())
    declared={f['path'] for f in read(PACKET/'CHANGED-FILES.json')['files']}
    files={str(p.relative_to(WORK)) for p in PACKET.rglob('*') if p.is_file()}
    assert changed==declared==files and len(files)==171
    assert all(p.startswith('tasks/jarvis-v2-final-integration-rehearsal-r2/') for p in changed)
    outer=seal(PACKET)
    assert len(outer)==170 and set(outer)=={str(p.relative_to(PACKET)) for p in PACKET.rglob('*') if p.is_file() and p!=PACKET/'SHA256SUMS'}
    for name in files:
        assert hashlib.sha256(subprocess.check_output(['git','show',REVIEW+':'+name],cwd=WORK)).hexdigest()==sha(WORK/name)
    assert not git('diff','--name-only','b0c8865a',SOURCE,'--','app')
    original=verify_set(PACKET/'acceptance');fresh=verify_set(OUT/'acceptance')
    assert original['completed_nodeids']==fresh['completed_nodeids']
    old12=read(PACKET/'audit-attacks12/SUMMARY.json');fresh12=read(OUT/'attacks12/SUMMARY.json')
    assert len(old12)==len(fresh12)==12
    assert {r['case'] for r in old12}=={r['case'] for r in fresh12}
    assert all(r['exit']!=0 and r['status']!='PASS' and r['secret_leaked'] is False for r in old12+fresh12)
    assert read(OUT/'EXECUTION.json')['exit']==read(OUT/'ATTACK-EXECUTION.json')['exit']==0
    summary={'status':'PASS','reviewed_commit':REVIEW,'approved_application_source':SOURCE,'rehearsal_only_added_packet':True,'rehearsal_outer_hashes':len(outer),'rehearsal_outer_manifest_sha256':sha(PACKET/'SHA256SUMS'),'original':original,'fresh':fresh,'all_test_python_files':len(actual),'enrollment':counts,'manifest_sha256':MANIFEST,'policy_sha256':POLICY,'fresh_audit_attacks':12,'independent_custody':False,'context_note':'Earlier engineering context was inherited; fresh execution and separate verifier do not constitute a fresh-context organizational audit.'}
    with (OUT/'VERIFICATION.json').open('x') as stream:json.dump(summary,stream,indent=2)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('original','fresh')}))

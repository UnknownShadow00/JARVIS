"""Independent inventory constraints, in addition to actual adversarial CLI runs."""
from copy import deepcopy
import json
import pytest
from gauntlet_protocol import InvalidEvidence, validate, case_id
from required_test_inventory import load_inventory

def evidence():
    ids=[case_id('required-'+str(i)) for i in range(45)]
    return ids,dict(protocol=2,run_id='r3',seed=42,mode='r2',completion='pytest-returned-v2',
        expected=ids[:],collection=dict(skipped=0,deselected=0),
        session=dict(started=True,collected=True,finished=True,interrupted=False,internal_error=False,collection_error=False,unexpected_report=False,pytest_exit_code=0,collected_count=45),
        scenarios=[dict(id=i,timed_out=False,phases=[dict(phase=p,outcome='passed',duration_seconds=0,category=None) for p in ('setup','call','teardown')]) for i in ids])

def check(body,ids):return validate(body,run_id='r3',seed=42,mode='r2',returncode=0,required=ids)

@pytest.mark.parametrize('fault',['astra14','module','parameter','skip','ignore','marker','duplicate','substitution','exit0_missing','truncated','no_collection_finish','interrupt','empty','xfail'])
def test_required_collection_and_execution_never_shrink(fault):
    ids,body=evidence()
    n=14 if fault=='astra14' else 1
    if fault in {'astra14','module','parameter','ignore','marker','exit0_missing','empty'}:
        n=45 if fault=='empty' else n
        body['expected']=body['expected'][n:];body['scenarios']=body['scenarios'][n:];body['session']['collected_count']-=n
    elif fault=='skip':body['collection']['skipped']=1
    elif fault=='duplicate':body['expected'][1]=ids[0]
    elif fault=='substitution':body['expected'][0]=case_id('replacement');body['scenarios'][0]['id']=body['expected'][0]
    elif fault=='truncated':body['scenarios'][0]['phases'].pop()
    elif fault=='no_collection_finish':body['session']['collected']=False
    elif fault=='interrupt':body['session']['interrupted']=True
    elif fault=='xfail':body['scenarios'][0]['phases'][1]['outcome']='skipped'
    try:result=check(body,ids)
    except InvalidEvidence:return
    assert result['gate_exit_code']!=0 and result['status']!='PASS'
    if fault=='astra14':assert result['counts']['PASS']==31 and result['required_missing']==14

def test_legitimate_full_suite():
    ids,body=evidence();assert check(body,ids)['gate_exit_code']==0

@pytest.mark.parametrize('tamper',['duplicate','bad_schema','source','wrong_baseline'])
def test_inventory_tampering_refuses(tmp_path,tamper):
    source=tmp_path/'tests';source.mkdir();(source/'test_one.py').write_text('')
    import hashlib
    body=dict(version=1,baseline='b199acede69962919933d5bca364a587b1a2e8ca',suites={'r3':dict(nodeids=['tests/test_one.py::test_one'],sources={'tests/test_one.py':hashlib.sha256(b'').hexdigest()})})
    if tamper=='duplicate':body['suites']['r3']['nodeids']*=2
    if tamper=='bad_schema':body['private']='SYNTHETIC_PRIVATE'
    if tamper=='source':body['suites']['r3']['sources']['tests/test_one.py']='0'*64
    if tamper=='wrong_baseline':body['baseline']='unknown'
    path=tmp_path/'inventory.json';path.write_text(json.dumps(body))
    with pytest.raises(InvalidEvidence):load_inventory(path,tmp_path,'r3',expected_digest=None)

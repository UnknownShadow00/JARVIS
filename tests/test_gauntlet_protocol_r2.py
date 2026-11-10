"""Validate terminal evidence rather than trusting process exit or summary counts."""
from copy import deepcopy
import json
import pytest
from gauntlet_protocol import VERSION, InvalidEvidence, case_id, category, validate


def evidence():
    identity = case_id('tests/review.py::test_public')
    return dict(protocol=VERSION, run_id='review-run', seed=42, mode='r2', completion='pytest-returned-v2',
        expected=[identity], session=dict(started=True,collected=True,finished=True,interrupted=False,
        internal_error=False,collection_error=False,unexpected_report=False,pytest_exit_code=0,collected_count=1),
        scenarios=[dict(id=identity,timed_out=False,phases=[dict(phase=p,outcome='passed',duration_seconds=.01,category=None) for p in ('setup','call','teardown')])])


def check(body, returncode=0):
    return validate(body,run_id='review-run',seed=42,mode='r2',returncode=returncode)


def test_complete_protocol_accepts_and_counts_completed_calls():
    result = check(evidence())
    assert result['gate_exit_code'] == 0 and result['executed'] == 1
    assert result['counts']['PASS'] == 1


@pytest.mark.parametrize('phases', [[], ['setup'], ['setup','call']])
def test_successful_exit_without_complete_phases_never_passes(phases):
    body = evidence()
    body['scenarios'][0]['phases'] = [p for p in body['scenarios'][0]['phases'] if p['phase'] in phases]
    result = check(body)
    assert result['gate_exit_code'] == 1 and result['executed'] == 0
    assert result['counts']['INCOMPLETE'] == 1


@pytest.mark.parametrize('field', ['finished','collected','started'])
def test_missing_session_completion_never_passes(field):
    body=evidence();body['session'][field]=False
    assert check(body)['gate_exit_code'] == 1


@pytest.mark.parametrize('field', ['interrupted','internal_error','collection_error','unexpected_report'])
def test_session_failure_never_passes_even_with_passing_phases(field):
    body=evidence();body['session'][field]=True
    assert check(body)['gate_exit_code'] == 1


@pytest.mark.parametrize('mutation', ['missing_marker','count','missing_case','duplicate_case','wrong_run','wrong_order','extra_payload'])
def test_malformed_or_mismatched_evidence_is_rejected(mutation):
    body=evidence()
    if mutation=='missing_marker':del body['completion']
    if mutation=='count':body['session']['collected_count']=2
    if mutation=='missing_case':body['scenarios']=[]
    if mutation=='duplicate_case':body['expected']*=2;body['scenarios']*=2
    if mutation=='wrong_run':body['run_id']='stale'
    if mutation=='wrong_order':body['scenarios'][0]['phases'].reverse()
    if mutation=='extra_payload':body['secret']='SYNTHETIC_PRIVATE_PROBE'
    with pytest.raises(InvalidEvidence):check(body)


@pytest.mark.parametrize('outcome', ['failed','skipped'])
def test_nonpassing_phase_never_passes(outcome):
    body=evidence();body['scenarios'][0]['phases'][1]['outcome']=outcome
    assert check(body)['gate_exit_code'] == 1


def test_empty_collection_never_passes():
    body=evidence();body.update(expected=[],scenarios=[]);body['session']['collected_count']=0
    result=check(body)
    assert result['gate_exit_code']==1 and result['reason']=='no_tests_collected'


def test_caught_timeout_never_passes():
    body=evidence();body['scenarios'][0]['timed_out']=True
    assert check(body)['gate_exit_code']==1


def test_nonzero_process_exit_never_passes():
    assert check(evidence(),returncode=9)['gate_exit_code']==1


@pytest.mark.parametrize('error', [RuntimeError("No module named 'SYNTHETIC_PRIVATE_PROBE'"),
    ImportError('SYNTHETIC_PRIVATE_PROBE',name='SYNTHETIC_PRIVATE_PROBE'),
    OSError('SYNTHETIC_PRIVATE_PROBE'), type('SYNTHETIC_PRIVATE_PROBE',(Exception,),{})('SYNTHETIC_PRIVATE_PROBE')])
def test_exception_category_has_no_sensitive_text_or_dynamic_type(error):
    assert 'SYNTHETIC_PRIVATE_PROBE' not in json.dumps(dict(category=category(error)))


def test_parameter_values_do_not_enter_identifiers_even_as_hash_input():
    from gauntlet_protocol import case_identifiers
    left=case_identifiers(['test_public.py::test_value[SYNTHETIC_PRIVATE_PROBE]', 'test_public.py::test_value[other]'])
    right=case_identifiers(['test_public.py::test_value[replaced]', 'test_public.py::test_value[changed]'])
    assert list(left.values())==list(right.values())
    assert len(set(left.values()))==2


@pytest.mark.parametrize('duration', [10**1000, float('nan'), -1])
def test_invalid_durations_fail_with_structured_evidence_error(duration):
    body=evidence();body['scenarios'][0]['phases'][0]['duration_seconds']=duration
    with pytest.raises(InvalidEvidence):check(body)

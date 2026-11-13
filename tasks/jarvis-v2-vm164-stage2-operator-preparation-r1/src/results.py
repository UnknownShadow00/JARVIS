"""Pure structural guard for result records; cannot authenticate host evidence."""
import re
from packet import CASES,SOURCE_PIN,CALLBACK_PIN,require,utc
STATUSES={'NOT_RUN','UNKNOWN','FAIL','EXPECTED_OBSERVATION','EXPECTED_NEGATIVE',
          'CREATION_REFUSED_EXEC_NOT_OBSERVED','LIVE_FAILED_TIMER_STATE_UNOBSERVED',
          'EXPECTED_LATE_REJECTED_NOT_TIMING_PASS'}

def validate(record):
    require(record.get('kind')=='CAPTURED_STAGE2_LIMITED_RESULT','not captured results')
    require(record.get('source_pin')==SOURCE_PIN and record.get('callback_pin')==CALLBACK_PIN,'source binding')
    require(record.get('expiration_guaranteed') is False and record.get('live_qualification') is False,
            'no blanket qualification/guarantee')
    require(record.get('result') in ('INCOMPLETE','FAILED','LIMITED_OBSERVATIONS_REVIEWED'), 'overclaim')
    require(set(record.get('cases',{}))==set(CASES), 'missing case disposition')
    start=utc(record['session']['starts_utc']);end=utc(record['session']['expires_utc'])
    require(0<(end-start).total_seconds()<=2700,'window')
    for case,row in record['cases'].items():
        require(row.get('status') in STATUSES,'case status')
        if row['status'] != 'NOT_RUN':
            require(type(row.get('evidence')) is list and len(row['evidence'])>0,'missing raw evidence')
            require(type(row.get('argv_sha256')) is str and re.fullmatch('[0-9a-f]{64}',row['argv_sha256']), 'argv digest')
            for e in row['evidence']:
                require(type(e) is dict and set(e)=={'path','sha256','bytes'},'artifact schema')
                path=e['path']
                require(type(path) is str and path and not path.startswith('/') and
                        all(x not in ('','.', '..') for x in path.split('/')),'artifact relative path')
                require(type(e['sha256']) is str and re.fullmatch('[0-9a-f]{64}',e['sha256']), 'artifact digest')
                require(type(e['bytes']) is int and e['bytes']>=0,'artifact byte count')
    require(set(record.get('unqualified',[])) >= {'manager_reexec','host_reboot','physical_suspend_wake','VM_termination','root_bootstrap'}, 'excluded qualifications')
    if record['result']=='LIMITED_OBSERVATIONS_REVIEWED':
        require(type(record.get('independent_reviewer')) is str and record['independent_reviewer'].strip(), 'independent review missing')
        require(record.get('clock_domain') in ('CLOCK_MONOTONIC','CLOCK_BOOTTIME') and bool(record.get('clock_domain_basis')), 'clock unresolved')
        require(record.get('cleanup',{}).get('status')=='CLOSED_EVIDENCE_RETAINED' and
                bool(record['cleanup'].get('inactive_evidence')), 'cleanup incomplete')
        require(all(r['status'] in ('EXPECTED_OBSERVATION','EXPECTED_NEGATIVE','EXPECTED_LATE_REJECTED_NOT_TIMING_PASS') for r in record['cases'].values()),'unresolved cases')
    return {'status':'PASS_RECORD_STRUCTURE_ONLY','authenticity_verified':False,'authorization_granted':False}

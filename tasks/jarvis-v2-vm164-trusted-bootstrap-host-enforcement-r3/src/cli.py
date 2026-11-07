"""Default OFFLINE dry-run. Host execution needs explicit flag, installed root
custody, finite reviewed Stage3/A approval and independently reviewed Stage2 data.
Policy B runtime and ALL root boot authorization are absent from this build.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,secrets,subprocess
from model import *
from host_adapter import authorize,source_digest,NativeBackend,Clock
from store import FileStore,bounded_read
from preflight import assess

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',nargs='?',default='plan',choices=['plan','simulate','prerequisites','prepare','start','worker','verify','observe','cleanup','retire','selfcheck'])
    p.add_argument('--dry-run',action='store_true');p.add_argument('--execute-reviewed-host',action='store_true')
    p.add_argument('--fixture',type=Path);p.add_argument('--session');p.add_argument('--phase',choices=PHASES)
    a=p.parse_args();h=source_digest(Path(__file__).resolve().parent)
    if not a.execute_reviewed_host:
        if a.action=='prerequisites':
            need(a.fixture is not None,'prerequisite_fixture_required')
            result=assess(parse(bounded_read(a.fixture,32768)),h)
            print(json.dumps(result,indent=2));return 0 if not result['missing'] else 1
        if a.action=='simulate':
            from sim import FakeClock,FixtureBackend,approval
            from store import MemoryStore
            need(a.fixture is not None,'explicit_synthetic_fixture_required')
            f=parse(bounded_read(a.fixture,32768));need(f.get('kind')=='synthetic','synthetic_only')
            clock=FakeClock();b=FixtureBackend(clock);s=MemoryStore();e=Engine(b,s,clock,h)
            grant=approval(clock,h,f.get('policy','A'))
            e.prepare(grant,'1'*32)
            if grant['policy']=='B':b.force_grant=s.plan()['force_grant_sha256']
            e.start();b.grace_stops=f.get('grace_stops',True)
            clock.value=s.plan()['grace_us'];e.expire('grace')
            clock.value=s.plan()['deadline_us'];r=e.expire('deadline')
            r.update(expiration_result=r['status'],status='PASS_SYNTHETIC_SCENARIO_ONLY',actions=b.actions,termination_state=b.status,
                     **{'scenario_outcome':e.receipt(s.plan(),'OBSERVATION')['phase']})
            print(json.dumps(r,indent=2));return 0
        print(json.dumps({'status':'DRY_RUN_NO_ACTION','requested_action':a.action,'source_sha256':h,
            'operator_reported_target':{'node':'pve','vmid':164,'uuid':UUID,'disk':DISK,'serial':SERIAL,'iso':ISO},
            'host_actions_executed':False,'root_boot_go':False,'forced_stop_runtime_enabled':False,
            'live_qualification':False},indent=2));return 0
    need(not a.dry_run and a.fixture is None,'no_mixed_execution_modes')
    need(a.action in ('prepare','start','worker','verify','observe','cleanup','retire','selfcheck'),'explicit_host_action_required')
    clock=Clock();budget=25 if a.action=='worker' and a.phase=='deadline' else 40
    absolute_deadline=clock.us()+budget*1_000_000
    permit=authorize(__file__,deadline_us=absolute_deadline)
    need(permit.source_hash==h,'source_changed_during_authorization')
    if a.action=='selfcheck':
        print(json.dumps({'selfcheck':'root_custody_and_prerequisites_only','vm_operations':False,'root_boot_go':False}));return 0
    backend=NativeBackend(permit,clock,budget,deadline_us=absolute_deadline)
    store=FileStore(STATE,owner=0)
    e=Engine(backend,store,clock,h,expected_session=a.session if a.action=='worker' else None,
             expected_approval_sha256=sha(canonical(permit.approval)) if a.action in ('start','worker','verify','observe') else None)
    if a.action=='worker':
        names(a.session)
        # Timer workers do not wait for the operator's global lock.
        r=e.expire(a.phase)
    else:
        with store:
            if a.action=='prepare':r=e.prepare(permit.approval,secrets.token_hex(16))
            elif a.action=='start':r=e.start()
            elif a.action=='verify':r=e.verify()
            elif a.action=='observe':r=e.observe()
            elif a.action=='retire':r=e.retire(permit.approval)
            else:r=e.cleanup()
    print(json.dumps(r,indent=2))
    return 0 if r['status'] in ('ARMED_NOT_TERMINATION_PROOF','START_ACK_NOT_ROOT_AUTHORITY',
        'STOPPED_OBSERVED','CLOSED_EVIDENCE_RETAINED','ALREADY_CLOSED_NO_ACTION','READBACK_CONSISTENCY_ONLY',
        'DUPLICATE_WORKER_NO_ACTION','RETIRED_REGISTRY_EVIDENCE_PRESERVED','OBSERVATION_NOT_QUALIFICATION') and r['evidence_healthy'] else 1
if __name__=='__main__':
    try:raise SystemExit(main())
    except (Refusal,OSError,KeyError,TypeError,ValueError,TimeoutError,subprocess.SubprocessError,KeyboardInterrupt) as exc:
        print(json.dumps({'status':'FENCE_BLOCKER_NO_GO','reason':str(exc) if isinstance(exc,Refusal) else type(exc).__name__,
                          'root_boot_go':False,'live_qualification':False,'forced_stop_runtime_enabled':False}));raise SystemExit(1)

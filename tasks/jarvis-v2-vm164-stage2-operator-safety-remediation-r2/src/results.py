"""Pure R2 result verification. Captured files are mandatory; no live authenticity claim."""
from common import need, canonical, sha, decode, integer, digest
import packet as p
import binding as b
import collision

EXPECTED={c:'EXPECTED_OBSERVATION' for c in p.CASES}
EXPECTED.update({c:'EXPECTED_NEGATIVE' for c in ('cancel','inactive','rearm-a','failedtimer')})
EXPECTED['late']='EXPECTED_LATE_REJECTED_NOT_TIMING_PASS'

def validate(record, artifacts=None, *, expected_manifest_sha256=None, expected_packet_manifest_sha256=None):
    need(type(record) is dict and record.get('kind') in ('SYNTHETIC_STAGE2_R2_RESULT','CAPTURED_STAGE2_R2_RESULT'),'R2 result kind')
    synthetic=record['kind'].startswith('SYNTHETIC')
    need(digest(record.get('packet_manifest_sha256'))==digest(expected_packet_manifest_sha256),'independent packet seal required')
    need(record.get('expiration_guaranteed') is False and record.get('live_qualification') is False,'no qualification upgrade')
    need(record.get('stage2_sha256')==p.source_hash() and record.get('source_pin')==p.SOURCE_PIN and record.get('callback_pin')==p.CALLBACK_PIN,'result source pins')
    session=record.get('session');p.validate_session(session)
    identity=record.get('identity');p.validate_identity(identity)
    need(record.get('operator')==session['operator'] and record.get('independent_reviewer')==session['reviewer'] and
         record.get('authorization_reference')==session['authorization_reference'],'review/authorization binding')
    need(record.get('failures')==[] and record.get('result')=='LIMITED_OBSERVATIONS_REVIEWED','failure cannot be erased by rearm')
    domain=record.get('clock_domain');need(domain in ('CLOCK_MONOTONIC','CLOCK_BOOTTIME'),'UNKNOWN clock')
    digest(record.get('clock_domain_basis_sha256'))
    cases=record.get('cases');need(type(cases) is dict and set(cases)==set(p.CASES),'exact twelve cases')
    need(digest(expected_manifest_sha256)==record.get('evidence_manifest_sha256'),'external evidence seal required')
    manifest=record.get('evidence_manifest');need(type(manifest) is dict and len(manifest)==12,'complete evidence manifest')
    need(record.get('evidence_manifest_sha256')==sha(canonical(manifest)),'manifest tampering')
    need(type(artifacts) is dict and set(artifacts)==set(manifest),'actual evidence files required')
    for path,entry in manifest.items():
        need(type(path) is str and path.startswith('cases/') and path.count('/')==1 and path.endswith('.json'),'evidence path')
        raw=artifacts[path];need(type(raw) is bytes and len(raw)<=1048576,'artifact bound')
        need(type(entry) is dict and set(entry)=={'sha256','bytes'} and entry=={'sha256':sha(raw),'bytes':len(raw)},'artifact digest/size')
    closure=record.get('closure');p.window(session,closure,creation=False)
    invocations=set();generations=set()
    for case in p.CASES:
        row=cases[case];need(type(row) is dict,'case schema')
        need(row==decode(artifacts['cases/'+case+'.json'],1048576),'case summary not backed by file')
        plan=row.get('plan');p.check_plan(plan)
        need(plan['case']==case and plan['session']==session,'case generation/session')
        collision.absent(session,case,row.get('collision_preflight'))
        need(row['collision_preflight']['sample']['boot_us']==plan['deadline_boot_us']-30000000,'stale collision inventory')
        need(plan['generation'] not in generations,'duplicate generation');generations.add(plan['generation'])
        need(row.get('status')==EXPECTED[case] and row.get('failures')==[],'wrong case disposition')
        waiting=row.get('waiting');need(type(waiting) is list and len(waiting)==(0 if case=='failedtimer' else 2),'waiting observations required')
        for obs in waiting:b.waiting(plan,obs,domain)
        if waiting:need(waiting[0]['sample']['boot_us']<waiting[1]['sample']['boot_us']<plan['deadline_boot_us'],'waiting order')
        final=row.get('final');b.final_inactive(plan,final)
        need(0<=closure['boot_us']-final['sample']['boot_us']<=180000000,'stale final closure')
        events=row.get('events');need(events==b.journal_events(plan,row.get('raw_journal')),'journal selection differs from raw evidence')
        guards,callbacks=b.validate_events(plan,events,final['service'])
        jr=row.get('journal_receipt');need(type(jr) is dict,'journal receipt required')
        ja=p.observation_commands(session['nonce'],case,session['boot_id'])['journal']
        need(jr.get('argv')==ja and jr.get('raw_stdout')==row['raw_journal'],'raw journal receipt binding')
        need(p.command_receipt(p.command_envelope(ja,'journal',session,jr.get('sample')),jr)==0,'journal capture failed')
        journal=row.get('journal_interval')
        need(type(journal) is dict and journal.get('complete') is True and journal.get('boot_id')==session['boot_id'] and journal.get('unit')==plan['service'],'complete journal required')
        need(integer(journal.get('from_boot_us'))<=plan['deadline_boot_us']-30000000 and
             integer(journal.get('through_boot_us'))==final['sample']['boot_us'],'journal covers creation through closure')
        receipts=row.get('receipts');need(type(receipts) is list and len(receipts)>=1,'command receipts')
        create=receipts[0];need(create.get('operation')=='create' and create.get('argv')==plan['argv'],'create receipt')
        for receipt in receipts:
            env=p.command_envelope(receipt.get('argv'),receipt.get('operation'),session,receipt.get('sample'))
            code=p.command_receipt(env,receipt)
            if receipt['operation']=='duplicate':
                need(case=='collision' and receipt['argv']==plan['argv'] and code!=0,'duplicate must fail')
            elif receipt['operation']=='create':
                need(receipt is create and receipt['argv']==plan['argv'],'duplicate create receipt')
                need(code==0 or case=='failedtimer','creation failed')
            elif receipt['operation']=='stop':
                need(receipt['argv'] in [["/usr/bin/systemctl","--system","--no-ask-password","stop",u] for u in (plan['timer'],plan['service'])] and code==0,'foreign or failed stop')
            else:need(False,'unreviewed mutation receipt')
        stops=[r['argv'][-1] for r in receipts if r['operation']=='stop']
        need(stops==[plan['timer'],plan['service']],'bounded timer-then-service cleanup receipts')
        need(row.get('cleanup_complete') is True,'cleanup interrupted')
        if case in ('cancel','inactive','rearm-a'):
            b.cancellation(plan,row,final)
        elif case=='failedtimer':
            # A create rejection alone never proves a failed timer. Require recorded loaded failure.
            failure=row.get('timer_failure');need(type(failure) is dict,'failed timer observation missing')
            t,s=b.verify_pair(plan,failure)
            need(t['ActiveState']=='failed' and t['Result']!='success' and events==[] and s['InvocationID']=='','failed timer not observed')
        else:
            need(len(guards)==1,'exactly one bound guard event')
            if case=='timeout':need(sum(e['payload'].get('kind')=='STAGE2_TIMEOUT_PROBE' for e in events)==1,'timeout payload not observed')
            if case=='missingexec':need('EXEC' in row['raw_journal'],'missing exec diagnostic')
            if case=='missingdep':need('ModuleNotFoundError' in row['raw_journal'] and 'jarvis_stage2_intentionally_absent_dependency_'+session['nonce'] in row['raw_journal'],'missing import diagnostic')
            inv=final['service']['InvocationID'];need(inv and inv not in invocations,'duplicate invocation');invocations.add(inv)
            need(len(callbacks)==(1 if case in ('success','exit7','late','collision','rearm-b') else 0),'missing/unexpected callback')
            s=final['service']
            p.outcome(case,callback_row=callbacks[0] if callbacks else None,result=s['Result'],code=int(s['ExecMainCode']),status=int(s['ExecMainStatus']),deadline=plan['deadline_boot_us'],expected=plan)
        if case=='collision':
            need(len([r for r in receipts if r['operation']=='duplicate'])==1,'collision refusal receipt')
            for collision_obs in (row.get('collision_before'),row.get('collision_after')):b.waiting(plan,collision_obs,domain)
            need(row['collision_before']['timer']==row['collision_after']['timer'] and row['collision_before']['service']==row['collision_after']['service'],'collision changed owned pair')
    need(cases['rearm-a']['final']['sample']['boot_us']>=cases['rearm-b']['final']['sample']['boot_us'],'canceled arm not observed through rearm closure')
    a=cases['rearm-a']['plan'];z=cases['rearm-b']['plan']
    need(a['name']!=z['name'] and a['generation']!=z['generation'] and z['deadline_boot_us']>a['deadline_boot_us']+2000000,'distinct ordered rearm')
    return {'status':'PASS_SYNTHETIC_ONLY' if synthetic else 'PASS_CONSISTENCY_ONLY',
            'authorization_granted':False,'authenticity_verified':False,'live_qualification':False}

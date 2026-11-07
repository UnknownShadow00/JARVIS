"""Read-only operator explanations and narrowly authenticated local recovery.

No retry, force-complete, delete, reset, import or real executor action exists.
Protected mutations require a short-lived command/payload/checkpoint-bound HMAC
permit from a separately trusted issuer. The public API exposes diagnostics only.
"""
from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import hmac
import json
import re
import uuid

from app.agent.authority import AuthorityError, canonical, identifier, instant, text
from app.agent.execution import phase_id, validate_spec
from app.agent.execution import SyntheticExecutor
from app.agent.ledger import MAX_BYTES, MAX_ROWS, encode, strict_json

TERMINAL = frozenset({'simulated_completed','simulated_failed','cancelled','denied','timed_out'})
STATUS_OUTBOX = {'pending':'held','executing_synthetic':'execution_claimed'}


def snapshot(authority):
    """Bounded consistent snapshot under the shared owner mutex; no mutation."""
    a=authority
    with a._mutex:
        a._fence()
        if a._conn.execute('PRAGMA quick_check').fetchone()[0]!='ok':
            raise AuthorityError('ledger_sqlite_corrupt')
        result={};size=rows=0
        for table in ('meta','ownership','control','records','receipts','events','outbox','simulation_effects'):
            values=[]
            for row in a._conn.execute(f'SELECT * FROM {table} ORDER BY rowid'):
                item=dict(row);size+=len(canonical(item));rows+=1
                if size>MAX_BYTES or rows>MAX_ROWS:raise AuthorityError('diagnostic_bound_exceeded')
                values.append(item)
            result[table]=values
        return result


def analyze(values, scope, *, now=None):
    now=now or datetime.now(UTC)
    issues=[];tasks={};occurrences={};schedules={};evidence={};receipts={};events={};origins={};transport_grants={};transport_reports={};transport_reservations={}
    def issue(code, ident=None):
        issues.append({'code':code,'identity':ident,'unsafe_to_dispatch':True})
    ownership=values.get('ownership',[])
    control=values.get('control',[])
    if values.get('meta')!=[{'version':1}]:issue('invalid_schema_metadata')
    if len(ownership)!=1 or ownership[0].get('id')!=1 or type(ownership[0].get('generation')) is not int or ownership[0]['generation']<1:
        issue('invalid_ownership')
    if len(control)!=1 or control[0].get('id')!=1 or control[0].get('enabled') not in (0,1) or type(control[0].get('epoch')) is not int or control[0]['epoch']<0:
        issue('invalid_scheduler_control')
    for row in values['records']:
        try:
            data=strict_json(row['data'])
            if type(data) is not dict:raise AuthorityError('invalid_record')
            if row['kind']=='task':
                identifier(row['id'])
                if type(data.get('metadata')) is not dict or data.get('status') not in {'pending','simulating','executing_synthetic','unknown','simulated_completed','simulated_failed','cancelled','denied','timed_out','failed','in_progress'} or type(data.get('cancel_requested')) is not bool or type(data.get('created_at')) is not str or data.get('execution') is not None and type(data['execution']) is not dict:
                    raise AuthorityError('invalid_task_record')
                text(data.get('goal'));text(data.get('scope'),128);instant(data['created_at'])
                execution=data.get('execution')
                if execution is not None:
                    validate_spec(**{k:execution[k] for k in ('capability','payload','expires_at','timeout_seconds')})
                    if execution.get('receipt_ids')!={phase:phase_id(row['id'],phase) for phase in ('claim','dispatch','record','publish','unknown')}:
                        issue('execution_receipt_identity_mismatch',row['id'])
                    auth=execution.get('authorization')
                    if type(auth) is not dict or type(auth.get('allowed')) is not bool or auth.get('scope')!=data['scope'] or auth.get('capability')!=execution['capability']:
                        issue('inconsistent_authorization',row['id'])
                if data.get('task_id')!=row['id'] or data.get('scope')!=row['scope']:issue('task_identity_mismatch',row['id'])
                tasks[row['id']]=data
            elif row['kind']=='occurrence':
                identifier(row['id'])
                if data.get('occurrence_id')!=row['id']:issue('occurrence_identity_mismatch',row['id'])
                instant(data.get('nominal'))
                occurrences[row['id']]=data
            elif row['kind']=='schedule':
                identifier(row['id'])
                if data.get('job_id')!=row['id'] or data.get('scope')!=row['scope']:issue('schedule_identity_mismatch',row['id'])
                schedules[row['id']]=data
            elif row['kind']=='execution_transport_grant':
                if data['binding']['operation_id']!=row['id'] or data['binding']['scope']!=row['scope']:
                    raise AuthorityError('invalid_transport_grant')
                transport_grants[row['id']]=data
            elif row['kind']=='execution_transport_report':transport_reports[row['id']]=data
            elif row['kind']=='execution_transport_reservation':transport_reservations[row['id']]=data
            elif row['kind']=='execution_evidence':
                identifier(row['id'])
                if type(data.get('response')) is not dict:raise AuthorityError('invalid_evidence')
                evidence[row['id']]=data
        except (AuthorityError,KeyError,TypeError):issue('invalid_record',row['id'])
    for row in values['receipts']:
        try:
            data=strict_json(row['data'])
            if type(data) is not dict or any(data.get(k)!=row[k] for k in ('request_id','scope','operation','payload_hash')) or data.get('state')!='committed' or type(data.get('result')) is not dict or not re.fullmatch('[0-9a-f]{64}',row['payload_hash']):
                raise AuthorityError('invalid_receipt')
            identifier(row['request_id'])
            receipts[row['request_id']]=data
            op=data['operation'];result=data['result']
            if op in {'submit','execution_submit','occurrence'} and result.get('task_id'):
                origins.setdefault(result['task_id'],[]).append(data)
                payload=None
                if op=='submit':payload={'goal':result['goal']}
                if op=='execution_submit':
                    payload={'goal':result['goal'],**{k:result['execution'][k] for k in ('capability','payload','expires_at','timeout_seconds')}}
                    if result['execution'].get('transport') is not None:
                        grant=transport_grants.get(result['task_id'])
                        if grant is None or hashlib.sha256(encode(grant)).hexdigest()!=result['execution']['transport']['grant_sha256']:
                            issue('transport_grant_missing_or_changed',result['task_id'])
                        else:payload['transport_permit']=grant['permit']
                if payload is not None and hashlib.sha256(canonical([row['scope'],op,payload]).encode()).hexdigest()!=row['payload_hash']:
                    issue('receipt_payload_binding_mismatch',row['request_id'])
            elif op=='import_legacy_snapshot':
                if type(result.get('task_ids')) is not dict:raise AuthorityError('invalid_receipt')
                for task_id in result.get('task_ids',{}).values():origins.setdefault(task_id,[]).append(data)
        except (AuthorityError,ValueError,TypeError,KeyError):issue('invalid_receipt',row['request_id'])
    previous=0;owner_generation=0;last_owner=None
    for row in values['events']:
        if row['seq']!=previous+1:issue('event_order_gap',row['request_id'])
        previous=row['seq']
        try:
            event=strict_json(row['data'])
            if type(event) is not dict:raise AuthorityError('invalid_event')
            if event.get('operation')=='owner_acquired':
                identifier(row['request_id'])
                base={'operation','generation','recovered_unknown_count','at'}
                if set(event) not in (base,base|{'enrollment'}) or type(event['generation']) is not int or event['generation']<1 or type(event['recovered_unknown_count']) is not int or event['recovered_unknown_count']<0:
                    raise AuthorityError('invalid_owner_event')
                if 'enrollment' in event:
                    admission=event['enrollment']
                    if type(admission) is not dict:raise AuthorityError('invalid_owner_event')
                    if admission.get('state')=='VERIFIED':
                        if set(admission)!={'state','verified','enrollment_id','genesis'} or admission['verified'] is not True:
                            raise AuthorityError('invalid_owner_event')
                        identifier(admission['enrollment_id'])
                        if type(admission['genesis']) is not dict or set(admission['genesis'])!={'sequence','sha256','checkpoint_hash'} or admission['genesis']['sequence']!=1:
                            raise AuthorityError('invalid_owner_event')
                    elif admission.get('state')=='LEGACY_APPROVED':
                        if set(admission)!={'state','verified','open_request_id','authorization_sha256','new_store_enrollment_proven'} or admission['verified'] is not False or admission['new_store_enrollment_proven'] is not False or not re.fullmatch('[0-9a-f]{64}',admission['authorization_sha256']):
                            raise AuthorityError('invalid_owner_event')
                        identifier(admission['open_request_id'])
                    else:raise AuthorityError('invalid_owner_event')
                instant(event['at'])
                if event['generation']<=owner_generation:issue('owner_generation_order',row['request_id'])
                owner_generation=event['generation'];last_owner=(event['generation'],row['request_id'])
                continue
            events.setdefault(row['request_id'],[]).append(event)
            if row['request_id'] not in receipts:issue('event_without_receipt',row['request_id'])
        except (AuthorityError,TypeError):issue('invalid_event',row['request_id'])
    for request_id,receipt in receipts.items():
        matches=events.get(request_id,[])
        if len(matches)!=1 or matches[0]!=receipt:issue('receipt_audit_mismatch',request_id)
    if len(ownership)==1 and last_owner!=(ownership[0].get('generation'),ownership[0].get('owner')):issue('ownership_audit_mismatch')
    outbox={row['task_id']:row for row in values['outbox']}
    markers={row['task_id']:row for row in values['simulation_effects']}
    for task_id,row in outbox.items():
        if task_id not in tasks:issue('outbox_without_task',task_id)
    for task_id,data in evidence.items():
        task=tasks.get(task_id)
        receipt=receipts.get(phase_id(task_id,'record'))
        if task is None or data.get('operation_id')!=task_id or receipt is None or receipt['result']!=data:
            issue('unbound_execution_evidence',task_id)
    from app.agent.execution_transport import ENDPOINTS, digest
    for task_id in set(transport_grants)|set(transport_reservations)|set(transport_reports):
        try:
            task=tasks.get(task_id)
            if task is None or not (task.get('execution') or {}).get('transport'):
                raise AuthorityError('orphan_transport_history')
            spec=task['execution'];grant=transport_grants[task_id];binding=grant['binding'];auth=grant['authorization']
            if (set(grant)!={'binding','permit','authorization'} or grant['permit']['body']!=auth
                or set(binding)!={'format','store_id','scope','operation_id','goal_sha256','endpoint_id','spec'}
                or binding['format']!='jarvis-synthetic-transport-grant-v1' or binding['operation_id']!=task_id
                or binding['scope']!=task['scope'] or binding['goal_sha256']!=digest(task['goal'])
                or binding['endpoint_id'] not in ENDPOINTS or spec['capability'] not in ENDPOINTS[binding['endpoint_id']]
                or binding['spec']!={k:spec[k] for k in ('capability','payload','expires_at','timeout_seconds')}
                or spec['transport']!={'endpoint_id':binding['endpoint_id'],'grant_sha256':digest(grant)}
                or (auth['request_id'],auth['scope'],auth['command'],auth['payload_hash'])!=(task_id,task['scope'],'dispatch_synthetic_transport',digest(binding))):
                raise AuthorityError('invalid_transport_grant')
            reserve=transport_reservations.get(task_id);report=transport_reports.get(task_id)
            reserve_receipt=receipts.get(phase_id(task_id,'transport_reserve'));report_receipt=receipts.get(phase_id(task_id,'transport_report'))
            if (reserve is not None)!=(reserve_receipt is not None) or (report is not None)!=(report_receipt is not None):
                raise AuthorityError('transport_receipt_missing')
            if reserve is not None:
                if (set(reserve)!={'request_sha256','generation','endpoint_id'} or type(reserve['generation']) is not int
                    or reserve['generation']<1 or reserve['endpoint_id']!=binding['endpoint_id']
                    or reserve_receipt['operation']!='transport_reserve' or reserve_receipt['scope']!=task['scope']
                    or reserve_receipt['result']!={'operation_id':task_id,'request_sha256':reserve['request_sha256'],'endpoint_id':binding['endpoint_id'],'state':'RESERVED_SYNTHETIC'}
                    or reserve_receipt['payload_hash']!=hashlib.sha256(canonical([task['scope'],'transport_reserve',{'request_sha256':reserve['request_sha256']}]).encode()).hexdigest()):
                    raise AuthorityError('invalid_transport_reservation')
            if report is not None:
                if reserve is None or set(report)!={'body','hmac_sha256'}:raise AuthorityError('invalid_transport_report')
                body=report['body'];wire=body['request'];out=outbox.get(task_id)
                if not re.fullmatch('[0-9a-f]{64}',report['hmac_sha256']) or not re.fullmatch('[0-9a-f]{64}',grant['permit']['hmac_sha256']):
                    raise AuthorityError('invalid_transport_signature_shape')
                expected=SyntheticExecutor().execute(task_id,spec)
                if (set(body)!={'format','request_sha256','request','response','reported_at'} or body['format']!='jarvis-synthetic-response-v1'
                    or set(wire)!={'format','operation_id','endpoint_id','store_id','scope','generation','nonce','deadline','grant_sha256','spec_sha256'}
                    or wire['format']!='jarvis-synthetic-request-v1' or wire['operation_id']!=task_id or wire['scope']!=task['scope']
                    or wire['store_id']!=binding['store_id'] or wire['endpoint_id']!=binding['endpoint_id']
                    or wire['generation']!=reserve['generation'] or out is None or out['generation']!=wire['generation']
                    or out['claim_id']!=task_id or wire['nonce']!=phase_id(task_id,'transport_nonce')
                    or wire['grant_sha256']!=digest(grant) or wire['spec_sha256']!=digest(binding['spec']) or wire['deadline']!=spec['deadline']
                    or body['request_sha256']!=reserve['request_sha256'] or body['response']!=expected
                    or report_receipt['operation']!='transport_report' or report_receipt['scope']!=task['scope']
                    or report_receipt['result']!={'operation_id':task_id,'endpoint_id':binding['endpoint_id'],'response_sha256':digest(report),'state':'REPORTED_SYNTHETIC_NOT_PUBLISHED'}
                    or report_receipt['payload_hash']!=hashlib.sha256(canonical([task['scope'],'transport_report',{'response_sha256':digest(report)}]).encode()).hexdigest()):
                    raise AuthorityError('invalid_transport_report')
                at=datetime.fromisoformat(instant(body['reported_at']))
                if not datetime.fromisoformat(instant(auth['issued_at']))<=at<min(datetime.fromisoformat(instant(auth['expires_at'])),datetime.fromisoformat(instant(spec['deadline']))):
                    raise AuthorityError('invalid_transport_report_time')
            if task_id in evidence and (report is None or evidence[task_id].get('transport_receipt')!=report):
                raise AuthorityError('transport_evidence_unbound')
        except (AuthorityError,KeyError,TypeError,ValueError):issue('invalid_transport_history',task_id)
    for task_id,task in tasks.items():
        if (task.get('execution') or {}).get('transport') and task_id not in transport_grants:issue('transport_grant_missing',task_id)
    diagnostics=[]
    for task_id,task in tasks.items():
        row=outbox.get(task_id)
        status=task.get('status')
        if row is None or row['state']!=STATUS_OUTBOX.get(status,status):issue('task_outbox_mismatch',task_id)
        origin=origins.get(task_id,[])
        if len(origin)!=1:issue('missing_or_ambiguous_admission_receipt',task_id)
        elif origin[0]['scope']!=task.get('scope') or origin[0]['operation']!='import_legacy_snapshot' and (origin[0]['result'].get('goal')!=task.get('goal') or origin[0]['result'].get('occurrence_id')!=task.get('occurrence_id')):
            issue('task_admission_binding_mismatch',task_id)
        occurrence_id=task.get('occurrence_id')
        if occurrence_id:
            occurrence=occurrences.get(occurrence_id)
            if occurrence is None or occurrence.get('task_id')!=task_id or occurrence.get('nominal')!=task.get('metadata',{}).get('nominal'):
                issue('occurrence_task_mismatch',task_id)
        execution=task.get('execution')
        has_evidence=task_id in evidence
        published=receipts.get(phase_id(task_id,'publish')) if execution else None
        if execution:
            if execution.get('operation_id')!=task_id:issue('execution_identity_mismatch',task_id)
            if status in {'simulated_completed','simulated_failed'} and (not has_evidence or published is None or published['result'].get('result')!=task.get('result') or evidence[task_id].get('response')!=task.get('result')):
                issue('completion_without_bound_evidence',task_id)
            if has_evidence and (row is None or row['claim_id']!=task_id or row['generation']!=evidence[task_id].get('generation')):
                issue('execution_claim_provenance_mismatch',task_id)
            if status in {'simulated_completed','simulated_failed'}:
                for phase in ('claim','dispatch','record','publish'):
                    receipt=receipts.get(phase_id(task_id,phase))
                    if receipt is None or receipt['operation']!='execution_'+phase or receipt['scope']!=task['scope']:
                        issue('execution_phase_receipt_missing',task_id)
        elif status in {'simulated_completed','simulated_failed'} and task_id not in markers:issue('simulation_completion_without_marker',task_id)
        if task.get('scope')!=scope:continue
        if status=='unknown':
            reason='result_recorded_publication_pending' if has_evidence else 'effect_outcome_unestablished'
            recommendation='authorize_publish_existing_synthetic_evidence' if has_evidence else 'preserve_unknown_investigate_original_receipts_never_retry'
        elif status=='executing_synthetic':
            reason='result_recorded_publication_pending' if has_evidence else 'claimed_outcome_not_yet_established'
            recommendation='inspect_worker_and_original_receipts_do_not_resubmit'
        elif status=='pending':reason='admitted_execution_held';recommendation='inspect_capability_policy_worker_and_expiry'
        elif status in {'simulated_failed','failed'}:reason=task.get('error') or 'execution_failed';recommendation='inspect_failure_evidence_no_automatic_retry'
        else:reason=status;recommendation='preserve_durable_receipts'
        if task.get('cancel_requested') and status=='unknown':reason='cancellation_requested_effect_outcome_unestablished'
        diagnostics.append(dict(task_id=task_id,original_request_id=origin[0]['request_id'] if len(origin)==1 else None,
            admission_receipt_id=origin[0]['request_id'] if len(origin)==1 else None,
            admission_operation=origin[0]['operation'] if len(origin)==1 else None,occurrence_id=occurrence_id,
            status=status,outbox_state=row['state'] if row else None,cancel_requested=task.get('cancel_requested'),
            admitted=bool(origin),execution_completed=status in {'simulated_completed','simulated_failed'},
            real_execution_completed=False,reason=reason,recommendation=recommendation,
            transport={'configured':bool(execution and execution.get('transport')),
                       'endpoint_id':execution.get('transport',{}).get('endpoint_id') if execution else None,
                       'reservation_present':task_id in transport_reservations,'report_present':task_id in transport_reports,
                       'report_is_completion':False,'real_execution_enabled':False},
            phase_receipt_ids=execution.get('receipt_ids',{}) if execution else {},
            recorded_evidence=has_evidence,published_receipt_id=published['request_id'] if published else None,
            created_at=task.get('created_at'),
            receipts=[{'receipt_id':receipt_id,'operation':receipts[receipt_id]['operation'] if receipt_id in receipts else expected,
                       'state':receipts[receipt_id]['state'] if receipt_id in receipts else 'missing',
                       'payload_hash':receipts[receipt_id]['payload_hash'] if receipt_id in receipts else None,
                       'audit_event_present':len(events.get(receipt_id,[]))==1}
                      for receipt_id,expected in ([(origin[0]['request_id'],origin[0]['operation'])] if len(origin)==1 else [])+
                          ([(phase_id(task_id,phase),'execution_'+phase) for phase in ('claim','dispatch','record','publish','unknown')] if execution else [])]))
    for occurrence_id,occurrence in occurrences.items():
        if occurrence.get('task_id') not in tasks:issue('occurrence_without_task',occurrence_id)
    schedule_diagnostics=[]
    for job_id,job in schedules.items():
        if job.get('scope')!=scope:continue
        overdue=False
        try:
            if job.get('enabled'):
                overdue=datetime.fromisoformat(instant(job['next_run_at']))<=now
            if job.get('last_run') and not any(t.get('metadata',{}).get('job_id')==job_id and t.get('metadata',{}).get('nominal')==job['last_run'] for t in tasks.values()):
                issue('schedule_last_run_without_occurrence',job_id)
        except (AuthorityError,KeyError,ValueError):issue('invalid_schedule',job_id)
        schedule_diagnostics.append(dict(job_id=job_id,enabled=job.get('enabled'),removed=job.get('removed'),
            last_run=job.get('last_run'),next_run_at=job.get('next_run_at'),overdue=overdue,
            recommendation='authorize_disable_without_catchup' if overdue else 'preserve_nominal_occurrence_identity'))
    # Never describe a structurally inconsistent operation as established completion.
    bad_ids={i['identity'] for i in issues}
    for task in diagnostics:
        if task['task_id'] in bad_ids or task['admission_receipt_id'] in bad_ids:
            task.update(execution_completed=False,reason='inconsistent_durable_state',recommendation='stop_dispatch_preserve_store_and_checkpoints_investigate')
    occurrence_summaries=[dict(occurrence_id=ident,task_id=value.get('task_id'),nominal=value.get('nominal'),
                              binding_ok=value.get('task_id') in tasks and tasks[value['task_id']].get('occurrence_id')==ident)
                          for ident,value in occurrences.items() if value.get('task_id') in tasks and tasks[value['task_id']].get('scope')==scope]
    exports=[]
    for receipt_id,receipt in receipts.items():
        if receipt['scope']==scope and receipt['operation']=='operator_export_admit':
            publication=receipts.get(phase_id(receipt_id,'export_complete'))
            exports.append({'export_id':receipt_id,'admission_receipt_id':receipt_id,'publication_receipt_id':phase_id(receipt_id,'export_complete'),
                            'state':'published' if publication else 'admitted_export_unpublished',
                            'recommendation':'preserve_verified_archive' if publication else 'verify_existing_manifest_then_reconcile_audit_never_regenerate'})
    return dict(consistent=not issues,issues=issues,tasks=diagnostics,schedules=schedule_diagnostics,
                occurrence_summaries=occurrence_summaries,exports=exports,unpublished_exports=sum(e['state']!='published' for e in exports),
                authority={'generation':ownership[0].get('generation') if len(ownership)==1 else None,
                           'scheduler_control':control[0] if len(control)==1 else None},
                receipts=len(receipts),events=len(values['events']),occurrences=len(occurrences),
                unresolved=sum(t['status'] not in TERMINAL for t in diagnostics),
                failed=sum(t['status'] in {'failed','simulated_failed'} for t in diagnostics),
                unknown=sum(t['status']=='unknown' for t in diagnostics),
                cancel_requested=sum(bool(t['cancel_requested']) for t in diagnostics),
                automatic_retry=False,history_deletion_supported=False)


class OperatorRecovery:
    def __init__(self, authority):self.authority=authority

    def diagnose(self, actor, *, task_id=None, limit=100, offset=0):
        a=self.authority;scope=a._scope(actor)
        if scope!='local-service':raise AuthorityError('operator_scope_required')
        if type(limit) is not int or not 1<=limit<=200 or type(offset) is not int or not 0<=offset<=1000000:
            raise AuthorityError('invalid_pagination')
        if task_id is not None:identifier(task_id)
        with a._mutex:
            values=snapshot(a)
            result=analyze(values,scope)
            integrity=a._ledger.verify(a._conn) if a._ledger is not None else {'verified':False,'reason':'external_checkpoint_not_configured'}
            tasks=[t for t in result['tasks'] if task_id is None or t['task_id']==task_id]
            if task_id is not None and not tasks:raise AuthorityError('not_found')
            total=len(tasks)
            transport_status={"configured":False,"history_verified":False,"real_execution_enabled":False}
            if any(t['transport']['configured'] for t in result['tasks']):
                verifier=getattr(a,'_transport_verifier',None)
                if verifier is None:
                    transport_status['reason']='transport_verifier_required'
                    for task in tasks:
                        if task['transport']['configured']:task.update(execution_completed=False,reason='transport_signature_verifier_unavailable')
                else:transport_status=verifier.ready(a)
            return {**result,'tasks':tasks[offset:offset+limit],'total_tasks':total,'offset':offset,
                    'occurrence_summaries':result['occurrence_summaries'][offset:offset+limit],
                    'schedules':result['schedules'][offset:offset+limit],'exports':result['exports'][offset:offset+limit],
                    'next_offset':offset+limit if offset+limit<total else None,'ledger_integrity':integrity,
                    'execution_transport':transport_status,'enrollment':a._enrollment_status,'recovery_decisions':a.recovery_decision_status(detailed=True),
                    'recovery_mutations_publicly_enabled':False,'disaster_recovery':a._ledger.disaster_status() if a._ledger is not None else {'enabled':False}}

    def retention_plan(self, actor, *, older_than, limit=100):
        with self.authority._mutex:
            return self._retention_plan(actor,older_than=older_than,limit=limit)

    def _retention_plan(self, actor, *, older_than, limit=100):
        cutoff=datetime.fromisoformat(instant(older_than))
        report=self.diagnose(actor,limit=200)
        if not report['consistent'] or not report['ledger_integrity']['verified']:
            raise AuthorityError('retention_integrity_required')
        if type(limit) is not int or not 1<=limit<=200:raise AuthorityError('invalid_pagination')
        eligible=[];protected=[]
        # Eligibility covers the entire bounded diagnostic snapshot, not just page 1.
        with self.authority._mutex:
            all_tasks=analyze(snapshot(self.authority),self.authority._scope(actor))['tasks']
            for task in all_tasks:
                old=datetime.fromisoformat(instant(task['created_at']))<cutoff
                reasons=[]
                if task['status'] not in TERMINAL:reasons.append('unresolved_or_held')
                if task['cancel_requested']:reasons.append('cancellation_evidence_preserved')
                if not old:reasons.append('newer_than_cutoff')
                if task['reason']=='inconsistent_durable_state':reasons.append('inconsistent_state')
                if not task['admission_receipt_id']:reasons.append('missing_admission_receipt')
                if reasons:protected.append({'task_id':task['task_id'],'reasons':reasons})
                else:eligible.append(task['task_id'])
        decision=hashlib.sha256()
        for item in eligible:decision.update(encode({'eligible':item}))
        for item in protected:decision.update(encode({'protected':item}))
        return {'eligible_for_archive':eligible[:limit],'eligible_total':len(eligible),'eligible_listing_complete':len(eligible)<=limit,
                'decision_sha256':decision.hexdigest(),'protected':protected[:limit],
                'protected_total':len(protected),'older_than':cutoff.isoformat(),'deletion_authorized':False,
                'policy':'archive-copy-only-v1','protected_history_deleted':False,
                'checkpoint':{k:report['ledger_integrity'][k] for k in ('sequence','sha256','checkpoint_hash')}}


class OperatorPermits:
    """HMAC issuer/verifier is trusted-local only; no issuance endpoint."""
    def __init__(self, key):
        if type(key) is not bytes or len(key)<32:raise AuthorityError('invalid_operator_key')
        self._key=key

    def issue(self, *, request_id, principal, scope, command, payload, checkpoint, expires_at, issued_at):
        identifier(request_id);text(principal,128);text(scope,128)
        body=dict(request_id=request_id,principal=principal,scope=scope,command=command,
                  payload_hash=hashlib.sha256(encode(payload)).hexdigest(),checkpoint=checkpoint,
                  expires_at=instant(expires_at),issued_at=instant(issued_at))
        return {'body':body,'hmac_sha256':hmac.new(self._key,encode(body),hashlib.sha256).hexdigest()}

    def authenticate(self, permit):
        """Verify historical HMAC evidence without granting current authorization."""
        if type(permit) is not dict or set(permit)!={'body','hmac_sha256'} or type(permit['body']) is not dict:
            raise AuthorityError('operator_authentication_required')
        body=permit['body']
        if set(body)!={'request_id','principal','scope','command','payload_hash','checkpoint','expires_at','issued_at'}:
            raise AuthorityError('operator_authentication_required')
        mac=permit['hmac_sha256']
        if type(mac) is not str or not re.fullmatch('[0-9a-f]{64}',mac) or not hmac.compare_digest(mac,hmac.new(self._key,encode(body),hashlib.sha256).hexdigest()):
            raise AuthorityError('operator_authentication_failed')
        text(body['principal'],128)
        return body

    def verify(self, permit, actor, request_id, command, payload):
        body=self.authenticate(permit)
        now=datetime.now(UTC);start=datetime.fromisoformat(instant(body['issued_at']));end=datetime.fromisoformat(instant(body['expires_at']))
        if not start<=now<end or not 0<(end-start).total_seconds()<=300:
            raise AuthorityError('operator_permit_expired')
        if (body['request_id'],body['scope'],body['command'],body['payload_hash'])!=(request_id,actor.scope,command,hashlib.sha256(encode(payload)).hexdigest()):
            raise AuthorityError('operator_permit_binding_mismatch')
        text(body['principal'],128)
        return body


class RecoveryActions:
    """Local, authenticated, audited, checkpoint-bound conservative operations."""
    def __init__(self, authority, permits):self.authority,self.permits=authority,permits

    def apply(self, actor, request_id, command, payload, permit):
        return self._apply(actor,request_id,command,payload,permit)

    def _apply(self, actor, request_id, command, payload, permit, *, verified_export=None):
        a=self.authority
        identifier(request_id)
        if uuid.UUID(request_id).version!=4:raise AuthorityError('invalid_public_request_identifier')
        if command not in {'publish_synthetic_evidence','reconcile_synthetic_transport_report','disable_overdue_schedule','prepare_archive'}:
            raise AuthorityError('unsafe_recovery_action')
        if a._ledger is None:raise AuthorityError('ledger_checkpoint_required')
        auth=self.permits.verify(permit,actor,request_id,command,payload)
        def authorized(result):
            return {**result,'operator_authorization':auth,'permit_fingerprint':hashlib.sha256(encode(permit)).hexdigest()}
        def effect(scope):
            if auth['checkpoint']!=a._ledger._head:raise AuthorityError('stale_operator_permit')
            report=analyze(snapshot(a),scope)
            if not report['consistent']:raise AuthorityError('recovery_inconsistent_state')
            if command=='reconcile_synthetic_transport_report':
                if type(payload) is not dict or set(payload)!={'task_id'}:raise AuthorityError('invalid_recovery_payload')
                task_id=identifier(payload['task_id']);task=a._get('task',task_id,scope)
                row=a._conn.execute('SELECT * FROM outbox WHERE task_id=?',(task_id,)).fetchone()
                if not a.allow_simulation or task['status']!='unknown' or row['state']!='unknown' or row['claim_id']!=task_id:
                    raise AuthorityError('unsafe_recovery_action')
                from app.agent.execution_transport import verify_transport_evidence,digest
                reply=a._get('execution_transport_report',task_id,scope)
                evidence={'response':reply['body']['response'],'generation':row['generation'],'operation_id':task_id,
                          'at':reply['body']['reported_at'],'source':'synthetic_authenticated_transport','transport_receipt':reply}
                if not task['execution'].get('transport'):raise AuthorityError('unsafe_recovery_action')
                verify_transport_evidence(a,actor,task,evidence)
                a._create('execution_evidence',task_id,scope,evidence)
                record_id=phase_id(task_id,'record')
                record_payload={'operation_id':task_id,'generation':row['generation'],'response':evidence['response'],
                                'transport_receipt_sha256':digest(reply)}
                record_hash=hashlib.sha256(canonical([scope,'execution_record',record_payload]).encode()).hexdigest()
                record={'request_id':record_id,'scope':scope,'operation':'execution_record','payload_hash':record_hash,
                        'state':'committed','result':evidence,'at':datetime.now(UTC).isoformat(),'owner_generation':a.generation}
                a._conn.execute('INSERT INTO receipts VALUES(?,?,?,?,?)',(record_id,scope,'execution_record',record_hash,canonical(record)))
                a._conn.execute('INSERT INTO events(request_id,data) VALUES(?,?)',(record_id,canonical(record)))
                return authorized({'task_id':task_id,'state':'EVIDENCE_RECORDED_NOT_PUBLISHED','execution_record_receipt_id':record_id,
                                   'executor_invoked':False,'publication_required':True})
            if command=='publish_synthetic_evidence':
                if type(payload) is not dict or set(payload)!={'task_id'}:raise AuthorityError('invalid_recovery_payload')
                task_id=identifier(payload['task_id']);task=a._get('task',task_id,scope)
                row=a._conn.execute('SELECT * FROM outbox WHERE task_id=?',(task_id,)).fetchone()
                evidence=a._get('execution_evidence',task_id,scope)
                if not a.allow_simulation or task['status']!='unknown' or row['state']!='unknown' or row['claim_id']!=task_id or row['generation']!=evidence['generation']:
                    raise AuthorityError('unsafe_recovery_action')
                # Use the existing publisher under this SAME SQL transaction so
                # recovered state and operator authorization receipt are atomic.
                from app.agent.execution_transport import verify_transport_evidence
                verify_transport_evidence(a,actor,task,evidence)
                result=evidence['response']
                expected=SyntheticExecutor().execute(task_id,task['execution'])
                if result.get('status') not in {'simulated_completed','simulated_failed'} or canonical(result)!=canonical(expected):
                    raise AuthorityError('untrusted_executor_response')
                task.update(status=result['status'],result=result,error=result['error'])
                a._put('task',task_id,scope,task)
                a._conn.execute('UPDATE outbox SET state=? WHERE task_id=?',(task['status'],task_id))
                publish_id=phase_id(task_id,'publish')
                digest=hashlib.sha256(canonical([scope,'execution_publish',{'operation_id':task_id}]).encode()).hexdigest()
                publication=dict(request_id=publish_id,scope=scope,operation='execution_publish',payload_hash=digest,state='committed',result=task,at=datetime.now(UTC).isoformat(),owner_generation=a.generation)
                a._conn.execute('INSERT INTO receipts VALUES(?,?,?,?,?)',(publish_id,scope,'execution_publish',digest,canonical(publication)))
                a._conn.execute('INSERT INTO events(request_id,data) VALUES(?,?)',(publish_id,canonical(publication)))
                return authorized({'task_id':task_id,'status':task['status'],'publication_receipt_id':publish_id,'executor_invoked':False})
            if command=='disable_overdue_schedule':
                if type(payload) is not dict or set(payload)!={'job_id'}:raise AuthorityError('invalid_recovery_payload')
                job_id=identifier(payload['job_id']);job=a._get('schedule',job_id,scope)
                if not job['enabled'] or datetime.fromisoformat(instant(job['next_run_at']))>datetime.now(UTC):raise AuthorityError('schedule_not_overdue')
                job.update(enabled=False,revision=job['revision']+1)
                a._put('schedule',job_id,scope,job)
                for task in a._list('task',actor):
                    if task['metadata'].get('job_id')==job_id and task['status'] not in TERMINAL:a._cancel(task)
                return authorized({'job_id':job_id,'enabled':False,'catchup':False})
            if type(payload) is not dict or set(payload)!={'export_id','manifest_sha256','older_than'}:raise AuthorityError('invalid_recovery_payload')
            identifier(payload['export_id'])
            # Export verification is supplied by a separate trusted-local method,
            # never a response or caller-provided self-asserted hash.
            verified=verified_export
            if verified is None or (verified['export_id'],verified['manifest_sha256'])!=(payload['export_id'],payload['manifest_sha256']):
                raise AuthorityError('verified_export_required')
            plan=OperatorRecovery(a).retention_plan(actor,older_than=payload['older_than'],limit=200)
            if not plan['eligible_listing_complete']:raise AuthorityError('retention_selection_too_large')
            for task_id in plan['eligible_for_archive']:
                current=hashlib.sha256(encode(a._get('task',task_id,scope))).hexdigest()
                if verified['task_bindings'].get(task_id)!=current:raise AuthorityError('export_does_not_cover_retention_candidate')
            a._create('archive_preparation',request_id,scope,{'export_id':payload['export_id'],'manifest_sha256':payload['manifest_sha256'],
                'plan':plan,'policy':'archive-copy-only-v1','history_deleted':False})
            return authorized({'archive_preparation_id':request_id,'plan':plan,'history_deleted':False})
        return a._mutate(actor,request_id,'operator_recovery',{'command':command,'payload':payload,'principal':auth['principal'],'authorization_scheme':'bounded-local-HMAC-v1'},effect)

    def prepare_archive(self, actor, request_id, directory, older_than, permit):
        if self.authority._ledger is None:raise AuthorityError('ledger_checkpoint_required')
        with self.authority._mutex:
            verified=self.verify_export(actor,directory)
            return self._apply(actor,request_id,'prepare_archive',dict(export_id=verified['export_id'],manifest_sha256=verified['manifest_sha256'],older_than=older_than),permit,verified_export=verified)

    def verify_export(self, actor, directory):
        a=self.authority
        with a._mutex:
            a._fence()
            if a._ledger is None:raise AuthorityError('ledger_checkpoint_required')
            verified=a._ledger.verify_export(directory)
            admission=a.receipt(actor,verified['export_id'])
            completion=a.receipt(actor,phase_id(verified['export_id'],'export_complete'))
            if admission is None or admission['operation']!='operator_export_admit' or completion is None or completion['operation']!='operator_export_complete' or completion['result'].get('manifest_sha256')!=verified['manifest_sha256']:
                raise AuthorityError('export_audit_publication_missing')
            attestation=a._ledger.verify_export_attestation(verified) if a._ledger.recovery_enabled else None
            return {**verified,'audit_publication_verified':True,'attestation':attestation}

    def export(self, actor, request_id, directory, permit, *, fault_hook=None):
        from pathlib import Path
        a=self.authority
        identifier(request_id)
        if uuid.UUID(request_id).version!=4:raise AuthorityError('invalid_public_request_identifier')
        if a._ledger is None:raise AuthorityError('ledger_checkpoint_required')
        payload={'export_id':request_id,'destination':str(Path(directory).absolute())}
        auth=self.permits.verify(permit,actor,request_id,'export_ledger',payload)
        def admit(scope):
            if scope!='local-service':raise AuthorityError('operator_scope_required')
            if auth['checkpoint']!=a._ledger._head:raise AuthorityError('stale_operator_permit')
            if not analyze(snapshot(a),scope)['consistent']:raise AuthorityError('recovery_inconsistent_state')
            return {'export_id':request_id,'destination':payload['destination'],'principal':auth['principal'],'operator_authorization':auth,'permit_fingerprint':hashlib.sha256(encode(permit)).hexdigest(),'history_deleted':False}
        with a._mutex:
            admitted=a._mutate(actor,request_id,'operator_export_admit',{'payload':payload,'principal':auth['principal'],'authorization_scheme':'bounded-local-HMAC-v1'},admit)
            dest=Path(directory)/request_id
            if admitted['replayed']:
                # Explicit same-ID reconciliation may publish an already complete
                # snapshot. Never regenerate a missing/partial export on replay.
                verified=a._ledger.verify_export(dest)
            else:
                verified=a._ledger.export(a,actor,request_id,directory,fault_hook=fault_hook)
            if fault_hook:fault_hook('export_before_audit_publication')
            publication=a._mutate(actor,phase_id(request_id,'export_complete'),'operator_export_complete',
                {'export_id':request_id,'manifest_sha256':verified['manifest_sha256']},
                lambda scope:{'export_id':request_id,'manifest_sha256':verified['manifest_sha256'],'history_deleted':False})
            attestation=a._ledger.attest_export(a,actor,verified) if a._ledger.recovery_enabled else None
            if attestation:self._record_attestation(actor,verified,attestation)
            return {'export':verified,'publication':publication,'attestation':attestation,'history_deleted':False}

    def reconcile_admitted_export(self, actor, request_id, directory):
        """Finish audit for an immutable export under its durable original grant.

        No fresh data copy or filesystem regeneration. The original signed permit
        was authenticated before admission; its stored decision authorizes this
        audit-only continuation after expiry/restart. No public route exposes it.
        """
        from pathlib import Path
        a=self.authority
        with a._mutex:
            a._fence()
            if a._ledger is None:raise AuthorityError('ledger_checkpoint_required')
            admission=a.receipt(actor,request_id)
            parent=Path(directory).absolute()
            if admission is None or admission['operation']!='operator_export_admit' or admission['result'].get('destination')!=str(parent):
                raise AuthorityError('export_admission_required')
            decision=admission['result'].get('operator_authorization')
            if type(decision) is not dict or decision.get('request_id')!=request_id or decision.get('command')!='export_ledger' or decision.get('scope')!=a._scope(actor):
                raise AuthorityError('export_admission_required')
            verified=a._ledger.verify_export(parent/request_id)
            publication=a._mutate(actor,phase_id(request_id,'export_complete'),'operator_export_complete',
                {'export_id':request_id,'manifest_sha256':verified['manifest_sha256']},
                lambda scope:{'export_id':request_id,'manifest_sha256':verified['manifest_sha256'],'history_deleted':False})
            if a._ledger.recovery_enabled:
                attestation=a._ledger.attest_export(a,actor,verified)
                self._record_attestation(actor,verified,attestation)
            return publication

    def _record_attestation(self,actor,verified,attestation):
        export_id=verified['export_id']
        payload={'export_id':export_id,'manifest_sha256':verified['manifest_sha256'],'attestation_sha256':attestation['attestation_sha256']}
        return self.authority._mutate(actor,phase_id(export_id,'export_attested'),'operator_export_attested',payload,
                                      lambda scope:{**payload,'execution_enabled':False})


def inspect_offline(database, actor, *, ledger=None, enrollment_context=None, **options):
    """Quiesced diagnostic only: SQLite mode=ro, no owner takeover or recovery.

    Refuses a running owner. Does not initialize directories, databases, locks,
    anchors or permits. A pending checkpoint is reported, never finalized here.
    """
    import fcntl
    import os
    from pathlib import Path
    import sqlite3
    import threading
    from types import SimpleNamespace
    from app.agent.authority import Authority
    from app.agent.ledger import private_directory
    path=Path(database).absolute()
    private_directory(path.parent)
    descriptor=lock=None;conn=None
    try:
        descriptor=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        Authority._check_file(descriptor)
        lock=os.open(path.with_suffix(path.suffix+'.writer.lock'),os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        Authority._check_file(lock)
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise AuthorityError('owner_busy') from exc
        if ledger is not None:ledger.acquire(path,readonly=True)
        conn=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,isolation_level=None)
        conn.row_factory=sqlite3.Row
        conn.execute('BEGIN')
        markers=conn.execute("SELECT id FROM records WHERE kind='ledger_config'").fetchall()
        if markers:
            if ledger is None:raise AuthorityError('ledger_checkpoint_required')
            if [r[0] for r in markers]!=[ledger.store_id]:raise AuthorityError('ledger_store_mismatch')
            ledger.verify(conn)
        elif ledger is not None:raise AuthorityError('ledger_enrollment_required')
        from app.agent.enrollment import verify_authority_enrollment
        enrollment_status=verify_authority_enrollment(conn,path,ledger,enrollment_context)
        shim=SimpleNamespace(_conn=conn,_mutex=threading.RLock(),_scope=Authority._scope,_ledger=ledger,_fence=lambda:None,_enrollment_status=enrollment_status,
                             recovery_decision_status=lambda **_: {'configured':False,'execution_enabled':False,'activation_authorized':False})
        return OperatorRecovery(shim).diagnose(actor,**options)
    except (OSError,sqlite3.Error) as exc:
        raise AuthorityError('offline_diagnostic_storage_unavailable') from exc
    finally:
        if conn is not None:conn.close()
        if ledger is not None:ledger.close()
        if lock is not None:os.close(lock)
        if descriptor is not None:os.close(descriptor)

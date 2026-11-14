"""Strict wire/readback, transition, invocation and artifact bindings. Pure checks."""
import re
import datetime as dt
from decimal import Decimal
from common import need, integer, digest, boot, sha, canonical, decode, utc
import packet as p
from launch_guard import condition_argv, guard_binding

TIMER_REQUIRED = {'Id','LoadState','ActiveState','SubState','Transient','Unit','Description','Result',
 'WakeSystem','AccuracyUSec','RandomizedDelayUSec','RemainAfterElapse','Persistent','TimersMonotonic',
 'NextElapseUSecMonotonic','LastTriggerUSecMonotonic','Job'}
SERVICE_REQUIRED = {'Id','LoadState','ActiveState','SubState','Transient','Description','Result','Type','User','Group',
 'ExecStart','ExecCondition','ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','Environment','EnvironmentFiles',
 'PassEnvironment','PAMName','LoadCredential','LoadCredentialEncrypted','ImportCredential','SetCredential',
 'OnFailure','OnSuccess','NoNewPrivileges','CapabilityBoundingSet','AmbientCapabilities','SupplementaryGroups',
 'Restart','RuntimeMaxUSec','TimeoutStartUSec','TimeoutStopUSec','MemoryMax','TasksMax','KillMode','SendSIGKILL',
 'StandardInput','StandardOutput','StandardError','UMask','PrivateNetwork','PrivateDevices','PrivateTmp','ProtectSystem',
 'ProtectHome','RestrictNamespaces','SetLoginEnvironment','CPUQuotaPerSecUSec','LimitNOFILE','LimitCORE','InaccessiblePaths',
 'RestrictSUIDSGID','UnsetEnvironment','MainPID','ControlPID','ControlGroup','Job','InvocationID','ExecMainCode','ExecMainStatus'}

def properties(raw, required):
    need(type(raw) is str and len(raw.encode()) <= 65536, 'raw show bound')
    result={}
    for line in raw.splitlines():
        need('=' in line, 'show field format')
        k,v=line.split('=',1)
        need(k not in result, 'duplicate show property')
        result[k]=v
    need(required <= set(result), 'incomplete systemctl show')
    return result


def usec(value):
    need(type(value) is str and 0<len(value)<=100,'time field')
    if value.isdecimal():return integer(int(value))
    units={'us':1,'ms':1000,'s':1000000,'min':60000000,'h':3600000000,'d':86400000000}
    total=Decimal(0);pos=0
    for m in re.finditer(r'(\d+(?:\.\d+)?)(us|ms|min|s|h|d)(?: |$)',value):
        need(m.start()==pos,'time serialization');total+=Decimal(m[1])*units[m[2]];pos=m.end()
    need(pos==len(value) and total==int(total),'time serialization')
    return integer(int(total))


def exec_check(raw, expected):
    # All R2 actual payload tokens are deliberately space-free. Unknown escapes fail.
    need(all(type(a) is str and a and not any(ch.isspace() for ch in a) and '\\' not in a for a in expected),'space-free argv protocol')
    prefix='{ path='+expected[0]+' ; argv[]='+' '.join(expected)+' ; ignore_errors=no ; '
    need(raw.startswith(prefix),'execution argv mismatch')
    need(re.fullmatch(r'start_time=\[[^\]]*\] ; stop_time=\[[^\]]*\] ; pid=\d+ ; code=[^;{}]* ; status=[^;{}]* \}',raw[len(prefix):]) is not None,'unknown exec serialization')


def verify_pair(plan, obs):
    p.check_plan(plan)
    need(type(obs) is dict and obs.get('name')==plan['name'],'current identity')
    need(boot(obs.get('boot_id'))==plan['boot_id'],'current epoch')
    need(obs.get('binding_sha256')==plan['binding_sha256'] and obs.get('generation')==plan['generation'],'current generation')
    need(obs.get('argv')==plan['argv'],'current argv binding')
    sample=obs.get('sample');p.window(plan['session'],sample,creation=False)
    observed=integer(obs.get('observed_boot_us'))
    need(0 <= sample['boot_us']-observed <= 3000000,'stale readback')
    captures=obs.get('capture_receipts')
    need(type(captures) is dict and set(captures)=={'timer','service','clock'},'raw capture receipts required')
    commands=p.observation_commands(plan['session']['nonce'],plan['case'],plan['boot_id'])
    for role,receipt in captures.items():
        need(receipt.get('argv')==commands[role],'capture argv identity')
        envelope=p.command_envelope(commands[role],'read' if role=='clock' else 'show',plan['session'],receipt.get('sample'))
        need(p.command_receipt(envelope,receipt)==0,'capture command failed')
        if role!='clock':need(receipt['raw_stdout']==obs.get('raw_'+role),'raw capture mismatch')
        else:
            cr=decode(receipt['raw_stdout'].encode(),65536)
            need(cr.get('boot_id')==plan['boot_id'] and cr.get('b2_us')==sample['boot_us'],'raw clock binding')
            need(type(cr.get('utc')) is str,'raw UTC missing')
            instant=dt.datetime.fromisoformat(cr['utc'])
            need(instant.utcoffset()==dt.timedelta(0) and 0 <= (instant-utc(sample['utc'])).total_seconds()<1,'raw UTC normalization')
            b1=integer(cr.get('b1_us'));b2=integer(cr.get('b2_us'));m=integer(cr.get('monotonic_us'))
            need(0<=b2-b1<=1000 and cr.get('offset_low_us')==b1-m==sample['offset_low_us'] and cr.get('offset_high_us')==b2-m==sample['offset_high_us'],'raw clock arithmetic')
    timer=properties(obs.get('raw_timer'),TIMER_REQUIRED)
    service=properties(obs.get('raw_service'),SERVICE_REQUIRED)
    need(obs.get('timer')==timer and obs.get('service')==service,'raw/decoded evidence mismatch')
    need(timer['Id']==plan['timer'] and service['Id']==plan['service'] and timer['Unit']==plan['service'],'wrong timer/service pair')
    for item in (timer,service):
        need(item['LoadState']=='loaded' and item['Transient']=='yes' and item['Description']==plan['description'],'unit custody')
        need(item['ActiveState'] in ('active','inactive','failed'),'unknown or transitional state')
        allowed={'active':{'waiting'} if item is timer else {'running'},'inactive':{'dead','elapsed'},'failed':{'failed'}}
        need(item['SubState'] in allowed[item['ActiveState']],'state/substate mismatch')
        need(item['Job']=='0','queued job not reconciled')
    need(timer['WakeSystem']=='yes' and timer['RemainAfterElapse']=='yes' and timer['Persistent']=='no','timer behavior')
    need(usec(timer['AccuracyUSec'])==1 and usec(timer['RandomizedDelayUSec'])==0,'timer accuracy')
    match=re.fullmatch(r'\{ OnBootUSec=([^;{}]+) ; next_elapse=([^;{}]+) \}',timer['TimersMonotonic'])
    need(match is not None and usec(match[1])==plan['deadline_boot_us'],'absolute timer deadline')
    need(usec(match[2])==usec(timer['NextElapseUSecMonotonic']),'next elapsed fields conflict')
    for k,v in {'Type':'exec','User':'65534','Group':'65534','Restart':'no','KillMode':'control-group',
       'SendSIGKILL':'yes','StandardInput':'null','StandardOutput':'journal','StandardError':'journal',
       'UMask':'0077','NoNewPrivileges':'yes','MemoryMax':'134217728','TasksMax':'16',
       'PrivateNetwork':'yes','PrivateDevices':'yes','PrivateTmp':'yes','ProtectSystem':'strict',
       'ProtectHome':'yes','RestrictSUIDSGID':'yes','RestrictNamespaces':'yes','SetLoginEnvironment':'no','LimitNOFILE':'64','LimitCORE':'0'}.items():
        need(service[k]==v,'service execution/security property')
    need(usec(service['RuntimeMaxUSec'])==(3000000 if plan['case']=='timeout' else 10000000),'runtime bound')
    need(usec(service['TimeoutStartUSec'])==5000000 and usec(service['TimeoutStopUSec'])==2000000 and
         usec(service['CPUQuotaPerSecUSec'])==100000,'service timeout/CPU bound')
    need(service['Environment']=='LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH=/usr/sbin:/usr/bin:/sbin:/bin','minimal environment readback')
    need(service['InaccessiblePaths']=='-/etc/pve -/var/lib/pve-cluster -/run -/root -/home','inaccessible path readback')
    need(service['UnsetEnvironment']=='LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME PYTHONSTARTUP','environment removal readback')
    for k in ('ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','EnvironmentFiles','PassEnvironment','PAMName',
              'LoadCredential','LoadCredentialEncrypted','ImportCredential','SetCredential','OnFailure','OnSuccess',
              'CapabilityBoundingSet','AmbientCapabilities','SupplementaryGroups'):
        need(service[k]=='','unexpected inherited setting')
    cmd=plan['argv'][plan['argv'].index('--')+1:]
    exec_check(service['ExecStart'],cmd);exec_check(service['ExecCondition'],condition_argv(plan))
    for k in ('MainPID','ControlPID','ExecMainCode','ExecMainStatus'):
        need(service[k].isdecimal(),'numeric service status')
    need(service['ControlGroup'] in ('','/system.slice/'+plan['service']),'cgroup ownership')
    return timer,service


def waiting(plan, obs, domain):
    t,s=verify_pair(plan,obs)
    need(t['ActiveState']=='active' and t['SubState']=='waiting' and t['Result']=='success' and usec(t['LastTriggerUSecMonotonic'])==0,'timer not waiting')
    need(s['ActiveState']=='inactive' and s['Result']=='success' and s['InvocationID']=='' and s['MainPID']=='0','service already invoked')
    sample=obs['sample'];need(sample['boot_us']<plan['deadline_boot_us'],'waiting sample late')
    need(domain in ('CLOCK_MONOTONIC','CLOCK_BOOTTIME'),'UNKNOWN clock domain')
    need(p.clock_domain(plan['deadline_boot_us'],usec(t['NextElapseUSecMonotonic']),sample['offset_low_us'],sample['offset_high_us'],domain)==domain,'clock convention')
    return True


def final_inactive(plan, obs):
    t,s=verify_pair(plan,obs)
    need(t['ActiveState'] in ('inactive','failed') and s['ActiveState'] in ('inactive','failed'),'unit remains active')
    need(s['MainPID']==s['ControlPID']=='0','remaining process')
    cg=obs.get('cgroup')
    need(type(cg) is dict and cg.get('path')=='/sys/fs/cgroup/system.slice/'+plan['service'],'cgroup evidence identity')
    need(cg.get('populated')==0 and type(cg.get('populated')) is int and cg.get('pids')==[] and
         cg.get('complete') is True,'cgroup not proved empty')
    need(cg.get('absent') in (True,False) and (cg['absent'] is False or cg.get('absence_corroborated') is True),'cgroup absence unproven')
    return True


def validate_events(plan, events, service):
    need(type(events) is list and len(events)<=32,'bounded journal selection')
    seen=set();guards=[];callbacks=[]
    for e in events:
        need(type(e) is dict and e.get('boot_id')==plan['boot_id'] and e.get('unit')==plan['service'],'journal host/unit')
        inv=e.get('invocation_id')
        need(type(inv) is str and re.fullmatch('[0-9a-f]{32}',inv) and inv==service['InvocationID'],'invocation binding')
        need(e.get('uid')==65534 and type(e['uid']) is int,'journal UID')
        cursor=e.get('cursor');need(type(cursor) is str and cursor and cursor not in seen,'duplicate journal record');seen.add(cursor)
        body=e.get('payload');need(type(body) is dict,'journal payload')
        if body.get('kind')=='STAGE2_GUARD_R2':
            need(body.get('binding')==guard_binding(plan) and body.get('invocation_id')==inv,'guard generation binding')
            need(all(type(body.get(k)) is int and body[k]==65534 for k in ('uid','euid','gid','egid')),'guard credentials')
            need(type(body.get('groups')) is list and set(body['groups'])<={65534},'guard groups')
            need(plan['deadline_boot_us']<=integer(body.get('boottime_us'))<=plan['deadline_boot_us']+5000000,'guard timing')
            guards.append(body)
        elif body.get('status')=='NON_ROOT_NON_VM_CLOCK_CANARY':callbacks.append(body)
        elif body.get('kind')=='STAGE2_TIMEOUT_PROBE':
            need(all(type(body.get(k)) is int and body[k]==65534 for k in ('uid','euid','gid','egid')) and
                 type(body.get('groups')) is list and set(body['groups'])<={65534},'timeout credentials')
        elif body.get('kind') in ('IMPORT_FAILURE','EXEC_FAILURE'):
            need(body.get('error')==('ModuleNotFoundError' if plan['case']=='missingdep' else 'EXEC'),'unexpected diagnostic')
        else:need(False,'unknown callback or unreviewed message')
    return guards,callbacks


def cancellation(plan, row, final):
    need(plan['case'] in ('cancel','inactive','rearm-a'),'not cancellation case')
    final_inactive(plan,final)
    need(row.get('events')==[],'canceled generation executed, including late firing')
    need(final['service']['InvocationID']=='' and final['service']['ExecMainCode']=='0' and
         usec(final['timer']['LastTriggerUSecMonotonic'])==0,'canceled generation has invocation')
    cancel=integer(row.get('cancel_boot_us'))
    need(cancel<=plan['deadline_boot_us']-5000000 and cancel>=plan['session']['start_boot_us'],'late cancellation')
    interval=row.get('journal_interval')
    need(type(interval) is dict and interval.get('complete') is True and interval.get('boot_id')==plan['boot_id'] and
         interval.get('unit')==plan['service'],'incomplete cancellation journal')
    need(integer(interval.get('from_boot_us'))<=plan['deadline_boot_us']-30000000 and integer(interval.get('through_boot_us'))>=plan['deadline_boot_us']+2000000,'insufficient no-execution observation')
    need(final['sample']['boot_us']>=interval['through_boot_us'],'future journal evidence')
    return 'EXPECTED_NEGATIVE'


def journal_events(plan, raw):
    """Decode captured JSON-lines journal bytes, never trust a selected event summary."""
    need(type(raw) is str and len(raw.encode())<=8388608,'journal byte bound')
    lines=raw.splitlines();need(len(lines)<=512,'journal row bound')
    events=[];seen=set()
    for line in lines:
        row=decode(line.encode(),65536)
        need(type(row) is dict and row.get('_BOOT_ID')==plan['boot_id'].replace('-',''),'raw journal epoch')
        cursor=row.get('__CURSOR');need(type(cursor) is str and cursor and cursor not in seen,'journal cursor');seen.add(cursor)
        message=row.get('MESSAGE');need(type(message) is str,'journal message encoding')
        if message.startswith('{'):
            body=decode(message.encode(),65536)
            need(row.get('_SYSTEMD_UNIT')==plan['service'] and row.get('_UID')=='65534','raw journal unit/UID')
            stamp=integer(int(row.get('__MONOTONIC_TIMESTAMP','-1')))
            event={'boot_id':plan['boot_id'],'unit':row['_SYSTEMD_UNIT'],'invocation_id':row.get('_SYSTEMD_INVOCATION_ID'),
                   'uid':65534,'cursor':cursor,'payload':body}
            events.append(event)
        else:
            # Keep all plain manager/traceback rows in raw evidence. They cannot
            # substitute for guard/canary JSON. Foreign rows fail closed.
            need(row.get('_SYSTEMD_UNIT') in (plan['timer'],plan['service']) or row.get('UNIT') in (plan['timer'],plan['service']),'foreign journal row')
    return events

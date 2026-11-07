"""Conservative systemctl-show codec; exact257 serialization needs Stage2 proof."""
from decimal import Decimal,InvalidOperation
import re
from model import need,names,worker_argv
UNITS={'us':Decimal(1),'ms':Decimal(1000),'s':Decimal(1000000),
       'min':Decimal(60_000_000),'h':Decimal(3_600_000_000),'d':Decimal(86_400_000_000),
       'w':Decimal(604_800_000_000)}
def usec(s):
    need(type(s) is str and 0<len(s)<=150,'timespan_schema')
    if s.isdecimal():return int(s)
    pos=0;total=Decimal(0)
    for m in re.finditer(r'(\d+(?:\.\d+)?)(us|ms|min|s|h|d|w)(?: |$)',s):
        need(m.start()==pos,'timespan_format');total+=Decimal(m[1])*UNITS[m[2]];pos=m.end()
    need(pos==len(s) and total==int(total) and 0<=total<=10**15,'timespan_range')
    return int(total)
def properties(raw):
    need(type(raw) is bytes and len(raw)<=65536,'show_output_bound')
    d={}
    for line in raw.decode('utf-8').splitlines():
        need('=' in line,'show_property_format');k,v=line.split('=',1)
        need(k not in d,'duplicate_show_property');d[k]=v
    return d

def argv_property(s):
    # Only this deliberately space-free fixed executable/path/nonce protocol.
    # Any escaping, second command, unknown field layout or variant fails closed.
    need(type(s) is str and s.count('argv[]=')==1 and s.count('path=')==1,'execstart_count')
    m=re.fullmatch(r'\{ path=(/usr/bin/python3) ; argv\[\]=([^;{}\\]+) ; ignore_errors=no ; start_time=\[[^\]]+\] ; stop_time=\[[^\]]+\] ; pid=\d+ ; code=[^;{}]+ ; status=[^;{}]+ \}',s)
    need(m is not None,'unsupported_execstart_serialization')
    argv=m[2].strip().split(' ');need(all(argv) and argv[0]==m[1],'execstart_path_mismatch')
    return argv

TIMER_PROPS=('Id','LoadState','ActiveState','SubState','Transient','Result','Unit',
             'WakeSystem','AccuracyUSec','RandomizedDelayUSec','LastTriggerUSecMonotonic',
             'NextElapseUSecMonotonic','TimersMonotonic','RemainAfterElapse')
SERVICE_PROPS=('Id','LoadState','ActiveState','SubState','Transient','Result','Type','User','Group',
               'Restart','KillMode','RuntimeMaxUSec','TimeoutStopUSec','ExecStart','ExecStartPre',
               'ExecStartPost','ExecCondition','InvocationID','Environment','EnvironmentFiles',
               'UMask','MemoryMax','TasksMax','SendSIGKILL','StandardInput','StandardOutput','StandardError',
               'TimeoutStartUSec')
def timer(raw):
    d=properties(raw);need(set(TIMER_PROPS)<=d.keys(),'timer_properties_missing')
    m=re.fullmatch(r'\{ OnBootUSec=([^;{}]+) ; next_elapse=([^;{}]+) \}',d['TimersMonotonic'])
    need(m is not None,'unsupported_timer_serialization')
    return {'id':d['Id'],'load':d['LoadState'],'active':d['ActiveState'],'sub':d['SubState'],
            'transient':d['Transient']=='yes','result':d['Result'],'trigger':d['Unit'],
            'wake':d['WakeSystem']=='yes','accuracy_us':usec(d['AccuracyUSec']),
            'random_us':usec(d['RandomizedDelayUSec']),'last_trigger_us':usec(d['LastTriggerUSecMonotonic']),
            'next_us':usec(d['NextElapseUSecMonotonic']),'on_boot_us':usec(m[1]),
            'remain':d['RemainAfterElapse']=='yes'}
def normalize_deadline(t,domain,offset_low,offset_high):
    need(domain in ('CLOCK_MONOTONIC','CLOCK_BOOTTIME'),'qualified_readback_clock_required')
    need(type(offset_low) is int and type(offset_high) is int and -1000<=offset_low<=offset_high
         and offset_high-offset_low<=1000,'clock_sample_skew_or_suspend')
    d=dict(t);raw=d['next_us']
    low,high=(0,0) if domain=='CLOCK_BOOTTIME' else (offset_low,offset_high)
    lo=max(0,raw+low);hi=max(0,raw+high)
    d.update(next_boot_min_us=lo,next_boot_max_us=hi,readback_clock=domain,
             readback_offset_low_us=low,readback_offset_high_us=high)
    return d
def service(raw):
    d=properties(raw);need(set(SERVICE_PROPS)<=d.keys(),'service_properties_missing')
    return {'id':d['Id'],'load':d['LoadState'],'active':d['ActiveState'],'sub':d['SubState'],
            'transient':d['Transient']=='yes','result':d['Result'],'type':d['Type'],
            'argv':argv_property(d['ExecStart']),'user':d['User'],'group':d['Group'],
            'restart':d['Restart'],'kill_mode':d['KillMode'],'runtime_us':usec(d['RuntimeMaxUSec']),
            'stop_timeout_us':usec(d['TimeoutStopUSec']),'invocation_id':d['InvocationID'],
            'umask':d['UMask'],'memory_max':d['MemoryMax'],'tasks_max':d['TasksMax'],
            'send_sigkill':d['SendSIGKILL']=='yes','stdin':d['StandardInput'],
            'stdout':d['StandardOutput'],'stderr':d['StandardError'],'start_timeout_us':usec(d['TimeoutStartUSec']),
            'extra_commands':any(d[k] for k in ('ExecStartPre','ExecStartPost','ExecCondition','Environment','EnvironmentFiles'))}

def timer_command(plan,phase):
    need(phase in ('grace','deadline'),'phase');names(plan['session'])
    deadline=plan[phase+'_us'];need(type(deadline) is int and deadline>0,'deadline')
    n=plan['names'][phase]
    runtime='45s' if phase=='grace' else '30s'
    return ['/usr/bin/systemd-run','--unit='+n,'--on-boot='+str(deadline//1_000_000)+'.'+str(deadline%1_000_000).zfill(6)+'s',
            '--timer-property=WakeSystem=yes','--timer-property=AccuracySec=1us',
            '--timer-property=RandomizedDelaySec=0','--timer-property=RemainAfterElapse=yes',
            '--property=Type=exec','--property=User=root','--property=Group=root',
            '--property=Restart=no','--property=RuntimeMaxSec='+runtime,'--property=TimeoutStopSec=5s',
            '--property=TimeoutStartSec=10s',
            '--property=KillMode=control-group','--property=SendSIGKILL=yes','--property=UMask=0077',
            '--property=MemoryMax=128M','--property=TasksMax=16',
            '--property=StandardInput=null','--property=StandardOutput=journal','--property=StandardError=journal',
            *worker_argv(plan['session'],phase)]

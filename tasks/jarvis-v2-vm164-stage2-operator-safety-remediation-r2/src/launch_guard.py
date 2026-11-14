"""Pure renderer for a future non-root ExecCondition. Never executes it here."""
import json

GUARD = r'''import datetime,json,os,re,sys,time
from pathlib import Path
try:
 p=json.loads(bytes.fromhex(sys.argv[1]))
 if not (os.getuid()==os.geteuid()==os.getgid()==os.getegid()==65534 and set(os.getgroups()) <= {65534}):raise ValueError()
 env=dict(os.environ)
 safe={'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PATH':'/usr/sbin:/usr/bin:/sbin:/bin'}
 if not (set(safe)<=set(env)<=set(safe)|{'INVOCATION_ID','JOURNAL_STREAM','SYSTEMD_EXEC_PID'} and all(env[k]==v for k,v in safe.items())):raise ValueError()
 inv=env.get('INVOCATION_ID','')
 if not re.fullmatch('[0-9a-f]{32}',inv):raise ValueError()
 b=time.clock_gettime_ns(time.CLOCK_BOOTTIME)//1000
 now=datetime.datetime.now(datetime.timezone.utc)
 start=datetime.datetime.strptime(p['starts_utc'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
 end=datetime.datetime.strptime(p['expires_utc'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
 if not (start<=now<end and (end-now).total_seconds()>=17 and p['start_boot_us']<=b and b+17000000<=p['end_boot_us']):raise ValueError()
 if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=p['boot_id']:raise ValueError()
 print(json.dumps({'kind':'STAGE2_GUARD_R2','binding':p,'uid':os.getuid(),'euid':os.geteuid(),'gid':os.getgid(),'egid':os.getegid(),'groups':os.getgroups(),'invocation_id':inv,'boottime_us':b}),flush=True)
except (ValueError,OSError,KeyError,TypeError):
 print('{"kind":"STAGE2_GUARD_REFUSED"}',flush=True)
 raise SystemExit(255)
'''

def guard_binding(plan):
    from common import utc
    s=plan['session']
    return {'boot_id':s['boot_id'],'nonce':s['nonce'],'generation':plan['generation'],'service':plan['service'],
            'stage2_sha256':plan['stage2_sha256'],'callback_pin':plan['callback_pin'],
            'starts_utc':s['starts_utc'],'expires_utc':s['expires_utc'],'start_boot_us':s['start_boot_us'],
            'end_boot_us':s['start_boot_us']+int((utc(s['expires_utc'])-utc(s['starts_utc'])).total_seconds()*1000000)}

def condition_argv(plan):
    return ['/usr/bin/python3','-I','-B','-S','-c',"exec(bytes.fromhex('"+GUARD.encode().hex()+"'))",
            json.dumps(guard_binding(plan),sort_keys=True,separators=(',',':')).encode().hex()]

def condition_property(plan):
    a=condition_argv(plan)
    # Double-quote the single code token to preserve its inner single quotes.
    return '--property=ExecCondition='+' '.join(a[:5])+ ' "'+a[5]+'" '+a[6]

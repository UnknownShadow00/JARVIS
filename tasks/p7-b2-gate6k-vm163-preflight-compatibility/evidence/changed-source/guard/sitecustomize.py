import atexit,json,os,socket,sys
from pathlib import Path
sys.dont_write_bytecode=True
stage=Path(os.environ['P7_OFFLINE_STAGE']).resolve()
production=Path('/home/jarvis/JARVIS')
network=[]
counts={'blocked_inet':0,'blocked_production_access':0,'blocked_credential_access':0,'blocked_external_write':0,'blocked_execution':0,'approved_offline_children':0}
def under(path,root):return path==root or root in path.parents
def hook(event,args):
    if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
        p=Path(os.fsdecode(args[0])).absolute()
        if under(p,Path('/home/jarvis/.config/jarvis')):
            counts['blocked_credential_access']+=1;raise AssertionError('PRODUCTION_CREDENTIAL_ACCESS_FORBIDDEN')
        if under(p,production) and not under(p,production/'.venv'):
            counts['blocked_production_access']+=1;raise AssertionError('CANONICAL_RUNTIME_ACCESS_FORBIDDEN')
        flags=args[2] or 0
        if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
            if not under(p,stage) and p!=Path('/dev/null'):
                counts['blocked_external_write']+=1;raise AssertionError('EXTERNAL_WRITE_FORBIDDEN')
    if event in ('socket.connect','socket.sendto') and getattr(args[0],'family',None) in (socket.AF_INET,socket.AF_INET6):
        network.append({'event':event,'destination':args[1]});counts['blocked_inet']+=1;raise ConnectionRefusedError('OFFLINE_INET_BLOCKED_BEFORE_SEND')
    if event=='socket.connect' and getattr(args[0],'family',None)==socket.AF_UNIX:
        address=args[1]
        if not isinstance(address,(str,bytes)) or not os.fsdecode(address).startswith(str(stage)+'/'):raise PermissionError('OFFLINE_UNIX_OUTSIDE_STAGE')
    if event=='socket.getaddrinfo':
        network.append({'event':event,'host':args[0],'port':args[1]});counts['blocked_inet']+=1;raise socket.gaierror('OFFLINE_DNS_BLOCKED')
    if event=='subprocess.Popen':
        executable,argv,cwd,env=args
        allowed=(isinstance(argv,(list,tuple)) and len(argv)>1 and
            (str(argv[0])==sys.executable and
             (argv[1]=='-c' or str(argv[1])==str(stage/'repo/scripts/switch_models.py'))
             or argv[0]=='bash' and str(argv[1])==str(stage/'repo/scripts/backup_restic.sh')))
        if not allowed:
            counts['blocked_execution']+=1;raise AssertionError('NON_FIXTURE_EXECUTION_FORBIDDEN')
        counts['approved_offline_children']+=1
    if event=='os.system':
        counts['blocked_execution']+=1;raise AssertionError('SHELL_EXECUTION_FORBIDDEN')
sys.addaudithook(hook)
def finish():
    (stage/('audit-'+str(os.getpid())+'.json')).write_text(json.dumps({'counts':counts,'network':network},sort_keys=True))
atexit.register(finish)

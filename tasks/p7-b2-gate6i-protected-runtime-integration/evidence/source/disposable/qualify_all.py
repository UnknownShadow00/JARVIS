#!/usr/bin/env python3
"""One future human invocation; privilege-separated checks then crash/transport suite.
Never run this on any production or development host.
"""
from qualify_multi_uid import main,BASE,RELEASE
import os,pwd,subprocess,sys,json
if __name__=='__main__':
    main()  # Refuses before writes unless explicit disposable VM marker and no NIC.
    account=pwd.getpwnam('g6i-service')
    temp=BASE/'suite';temp.mkdir(mode=0o700);os.chown(temp,account.pw_uid,account.pw_gid)
    # Inherited kernel AF_UNIX-only/no_new_privs policy; no inherited secrets/env.
    command=[sys.executable,'-B','-m','pytest','-p','no:cacheprovider','--basetemp',str(temp/'pytest'),
             'tests/execution/v3_protected_runtime_test.py','tests/execution/v3_protected_authority_test.py','-q']
    env={'PATH':'/usr/bin:/bin','HOME':str(temp),'TMPDIR':str(temp),'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(RELEASE/'repo'),'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','P7_OFFLINE_STAGE':str(temp)}
    # Explicit plugin matches the known suite; no project auto-loading or live evals.
    command[4:4]=['-p','pytest_asyncio.plugin']
    result=subprocess.run(command,cwd=RELEASE/'repo',env=env,user=account.pw_uid,group=account.pw_gid,extra_groups=[],capture_output=True,timeout=180)
    (BASE/'suite-stdout.txt').write_bytes(result.stdout+result.stderr)
    report=json.loads((BASE/'report.json').read_text());report['process_crash_transport_suite_exit']=result.returncode
    report['result']='PASS' if result.returncode==0 else 'FAIL'
    (BASE/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report));sys.exit(result.returncode)

#!/usr/bin/env python3
"""Future operator-controlled throwaway VM only; never invoked by current tests."""
from qualify_multi_uid import main,BASE,RELEASE
import os,pwd,subprocess,sys,json,hashlib

SUITE_SECONDS=900

def suite_command(interpreter,temp):
    return [interpreter,'-B','-m','pytest','-p','pytest_asyncio.plugin','-p','no:cacheprovider',
            '--basetemp',str(temp/'pytest'),'--junitxml',str(temp/'cases.xml'),'tests/execution/v3_redteam_test.py',
            'tests/execution/v3_protected_runtime_test.py','tests/execution/v3_protected_authority_test.py','-q']

def run_suite(command,*,cwd,env,account,output,summary,report):
    # Stream to a bounded-duration retained log; preserve evidence even on timeout.
    result=dict(report,result='FAIL',process_crash_transport_suite_exit=None)
    with output.open('wb') as log:
        try:
            run=subprocess.run(command,cwd=cwd,env=env,user=account.pw_uid,group=account.pw_gid,
                extra_groups=[],stdout=log,stderr=subprocess.STDOUT,timeout=SUITE_SECONDS)
            result['process_crash_transport_suite_exit']=run.returncode
            result['result']='PASS' if run.returncode==0 else 'FAIL'
        except subprocess.TimeoutExpired:result['failure']='SUITE_TIMEOUT'
        except Exception as error:result['failure']=type(error).__name__
    summary.write_text(json.dumps(result,indent=2)+'\n')
    return result

def seal_reports(base):
    names=('report.json','qualification.json','suite-stdout.txt','suite/cases.xml')
    lines=[]
    for name in names:
        path=base/name
        if path.is_symlink():raise RuntimeError('REPORT_SYMLINK')
        if path.is_file():lines.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+name)
    target=base/'EVIDENCE-SHA256SUMS'
    with target.open('x') as output:output.write('\n'.join(lines)+'\n')
    for line in target.read_text().splitlines():
        sha,name=line.split('  ',1)
        if hashlib.sha256((base/name).read_bytes()).hexdigest()!=sha:raise RuntimeError('REPORT_SEAL_VERIFY')
    return hashlib.sha256(target.read_bytes()).hexdigest()

if __name__=='__main__':
    main()  # Refuses before writes unless explicit disposable VM marker and no NIC.
    account=pwd.getpwnam('g6j-service')
    temp=BASE/'suite';temp.mkdir(mode=0o700);os.chown(temp,account.pw_uid,account.pw_gid)
    env={'PATH':'/usr/bin:/bin','HOME':str(temp),'TMPDIR':str(temp),'PYTHONDONTWRITEBYTECODE':'1',
         'PYTHONPATH':str(RELEASE/'repo'),'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','P7_OFFLINE_STAGE':str(temp)}
    report=run_suite(suite_command(sys.executable,temp),cwd=RELEASE/'repo',env=env,account=account,
        output=BASE/'suite-stdout.txt',summary=BASE/'qualification.json',report=json.loads((BASE/'report.json').read_text()))
    print(json.dumps({'report':report,'evidence_seal':seal_reports(BASE)}));sys.exit(0 if report['result']=='PASS' else 1)

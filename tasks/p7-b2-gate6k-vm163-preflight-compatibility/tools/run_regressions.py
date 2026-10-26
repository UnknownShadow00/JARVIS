"""Nexus offline regression launcher, with explicit harmless external canary.

Never reads an existing unrecognized canary. No SSH, qualification or provisioning.
"""
import json,os,stat,subprocess,sys
from pathlib import Path
BASE=Path('/home/nexus/.local/share/jarvis-gate6k-preflight-fix');STAGE=BASE/'release-r1'
PYTHON='/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/bin/python'
CANARY=Path('/tmp/jarvis-gate6c-denied-dummy.txt');RECORD=BASE/'canary-creation.json'
if os.geteuid()==0 or os.uname().nodename!='nexus-services':raise RuntimeError('NEXUS_UNPRIVILEGED_ONLY')
if not RECORD.exists():
    fd=os.open(CANARY,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        os.write(fd,b'SYNTHETIC OFFLINE SANDBOX CANARY; NO CREDENTIALS\n');os.fsync(fd);st=os.fstat(fd)
        with RECORD.open('x') as f:json.dump({'inode':st.st_ino,'device':st.st_dev,'uid':st.st_uid,'path':str(CANARY),'retained':True},f)
    finally:os.close(fd)
else:
    known=json.loads(RECORD.read_text());st=CANARY.lstat()
    if (st.st_ino,st.st_dev,st.st_uid)!=(known['inode'],known['device'],os.getuid()) or not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode)!=0o600 or st.st_nlink!=1:raise RuntimeError('CANARY_IDENTITY_CHANGED')
label=sys.argv[1]
if not label.replace('-','').isalnum():raise ValueError('LABEL')
for suffix in ('.txt','-result.json','-stdout.txt'):
    if (STAGE/(label+suffix)).exists():raise FileExistsError('NEW_RUN_LABEL_REQUIRED')
env={'PATH':'/usr/bin:/bin','HOME':str(STAGE),'TMPDIR':str(STAGE),'P7_OFFLINE_STAGE':str(STAGE),'PYTHONDONTWRITEBYTECODE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1'}
with (STAGE/(label+'-stdout.txt')).open('x') as output:
    r=subprocess.run([PYTHON,'-B',str(STAGE/'supervise_tests.py'),*sys.argv[1:]],env=env,stdout=output,stderr=subprocess.STDOUT)
print(json.dumps({'label':label,'exit':r.returncode,'result':str(STAGE/(label+'-result.json'))}));sys.exit(r.returncode)

"""Unprivileged, offline fixture installation. Not privileged VM qualification."""
import json,os,pathlib,platform,shutil,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from verify_bundle import verify
from offline_exec import deny_network
def main():
    base=pathlib.Path(__file__).resolve().parents[1]
    if len(sys.argv)!=2:raise ValueError('EXPECTED_MANIFEST_DIGEST_REQUIRED')
    if os.geteuid()==0:raise ValueError('ROOT_INSTALL_FORBIDDEN')
    if platform.machine()!='x86_64' or sys.version_info[:3]!=(3,14,4):raise ValueError('BOOTSTRAP_ARCH_OR_PYTHON')
    if shutil.which('dpkg-deb') is None:raise ValueError('DPKG_DEB_REQUIRED')
    if shutil.disk_usage(base).free<20*1024**3:raise ValueError('LESS_THAN_20_GIB_FREE')
    verify(base,sys.argv[1])
    work=base/'work'
    if work.exists():raise ValueError('PREEXISTING_WORK_REFUSED')
    work.mkdir(mode=0o700);(work/'tmp').mkdir(mode=0o700);(work/'home').mkdir(mode=0o700)
    deny_network()
    env={'PATH':'/usr/bin:/bin','HOME':str(work/'home'),'TMPDIR':str(work/'tmp'),'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'}
    steps=[]
    def run(label,cmd):
        with (work/(label+'.log')).open('x') as f:
            p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
        steps.append({'step':label,'returncode':p.returncode})
        (work/'INSTALL-RESULT.json').write_text(json.dumps({'steps':steps,'status':'IN_PROGRESS' if p.returncode==0 else 'FAIL'},indent=2)+'\n')
        if p.returncode:raise RuntimeError('STOP_PRESERVE_FAILURE '+label)
    run('materialize-runtime',[sys.executable,'-B',str(base/'tools/materialize_runtime.py')])
    runtime=work/'downloaded-runtime';py=runtime/'usr/bin/python3.14'
    env['LD_LIBRARY_PATH']=str(runtime/'usr/lib/x86_64-linux-gnu')
    run('prepare-python-payloads',[str(py),'-B',str(base/'tools/prepare_mixed_fixture.py')])
    vpy=work/'mixed-env-r2/bin/python'
    pip=[str(vpy),'-I','-B',str(base/'tools/offline_exec.py'),'pip']
    run('install-wheels',pip+['install','--no-index','--find-links',str(base/'artifacts/wheels'),'--find-links',str(base/'artifacts/built-wheels'),'--only-binary=:all:','--require-hashes','-r',str(base/'locks/mixed-wheels-hashed.txt'),'-r',str(base/'locks/built-wheel-hashed.txt')])
    run('pip-check',pip+['check'])
    run('exact-runtime-check',[str(py),'-S','-B',str(base/'tools/runtime_check.py')])
    (work/'INSTALL-RESULT.json').write_text(json.dumps({'status':'PASS','steps':steps,'scope':'unprivileged offline fixture; not VM qualification'},indent=2)+'\n')
    print('PASS: 127 exact distributions; preserve work/ evidence')
if __name__=='__main__':main()

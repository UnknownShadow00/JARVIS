"""Quarantine the full disposable fixture after smoke, checking every byte survives."""
from pathlib import Path
import datetime,json,subprocess,os,resource
P=Path(__file__).resolve().parents[1]
def main():
 install=json.loads((P/'INSTALLATION-TEST-RESULTS.json').read_text());work=P/install['run']/'work'
 require=work/'installed';assert require.is_dir()
 child=work/'rollback-child.py';child.write_text('''from pathlib import Path
import sys,json,os
sys.path.insert(0,'/input/tools')
import lab_package as lab
b=json.loads(Path('/input/BUNDLE.json').read_text());m,files=lab.load_bundle(Path('/input')/b['bundle'],b['bundle_sha256'])
expected={n:lab.digest(raw) for n,raw in files.items()}
path=lab.quarantine('/work','installed',expected,owner=os.getuid(),tag='20261106T000000Z')
lab.validate_installed(Path('/work')/path,expected,owner=os.getuid())
result={'status':'PASS_FULL_RELEASE_QUARANTINE','preserved_files':len(expected),'preserved_relative_path':path,'all_hashes_verified':True,'deletion_or_existing_service_change':False,'privileged_or_cross_uid_qualification':False}
Path('/work/FULL-ROLLBACK-RESULT.json').write_text(json.dumps(result,indent=2)+'\\n')
print(json.dumps(result,indent=2))
''')
 argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv','--setenv','PATH','/usr/bin:/bin','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--ro-bind',str(P),'/input','--bind',str(work),'/work','--proc','/proc','--dev','/dev','--symlink','/work','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3.14','-I','-B','-S','/work/rollback-child.py']
 def limits():
  resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 r=subprocess.run(argv,capture_output=True,text=True,stdin=subprocess.DEVNULL,timeout=60,preexec_fn=limits,env={'PATH':'/usr/bin:/bin'})
 (P/'evidence/full-rollback-stdout.txt').write_text(r.stdout);(P/'evidence/full-rollback-stderr.txt').write_text(r.stderr)
 if r.returncode:raise SystemExit(r.returncode)
 data=json.loads((work/'FULL-ROLLBACK-RESULT.json').read_text());data['original_install_run']=install['run'];(P/'FULL-ROLLBACK-RESULT.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
if __name__=='__main__':main()

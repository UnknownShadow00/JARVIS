from pathlib import Path
import sys,json,os
sys.path.insert(0,'/input/tools')
import lab_package as lab
b=json.loads(Path('/input/BUNDLE.json').read_text());m,files=lab.load_bundle(Path('/input')/b['bundle'],b['bundle_sha256'])
expected={n:lab.digest(raw) for n,raw in files.items()}
path=lab.quarantine('/work','installed',expected,owner=os.getuid(),tag='20261106T000000Z')
lab.validate_installed(Path('/work')/path,expected,owner=os.getuid())
result={'status':'PASS_FULL_RELEASE_QUARANTINE','preserved_files':len(expected),'preserved_relative_path':path,'all_hashes_verified':True,'deletion_or_existing_service_change':False,'privileged_or_cross_uid_qualification':False}
Path('/work/FULL-ROLLBACK-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

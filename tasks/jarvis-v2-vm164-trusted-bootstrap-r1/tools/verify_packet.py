"""Verify sealed local preparation, final media and predecessors; no VM/network calls."""
import hashlib,importlib.util,json,os,stat,subprocess,sys
from pathlib import Path
TASK=Path(__file__).resolve().parents[1];PROJECT=TASK.parents[1]
EXCLUDED={'MANIFEST.json','SEAL.json'}
def sha(b):return hashlib.sha256(b).hexdigest()
def inventory():
 files={};links={}
 for p in sorted(TASK.rglob('*')):
  n=str(p.relative_to(TASK))
  if n in EXCLUDED:continue
  st=p.lstat()
  if stat.S_ISLNK(st.st_mode):links[n]=os.readlink(p)
  elif stat.S_ISREG(st.st_mode):files[n]={'sha256':sha(p.read_bytes()),'bytes':st.st_size}
  elif not stat.S_ISDIR(st.st_mode):raise ValueError('SPECIAL_FILE:'+n)
 return {'format':'vm164-trusted-bootstrap-manifest-v1','files':files,'symlinks':links}
def verify():
 seal=json.loads((TASK/'SEAL.json').read_text());raw=(TASK/'MANIFEST.json').read_bytes();assert sha(raw)==seal['manifest_sha256'],'MANIFEST_SEAL'
 m=json.loads(raw);assert inventory()==m,'PACKET_INVENTORY_CHANGED'
 entry=json.loads((TASK/'evidence/entry.json').read_text());log=(PROJECT/'tasks/loop-log.md').read_bytes();assert sha(log[:entry['log_prefix_bytes']])==entry['log_prefix_sha256'],'ORIGINAL_LOG_PREFIX_CHANGED'
 pins=json.loads((TASK/'EXTERNAL-PINS.json').read_text())
 for name,pin in pins.items():assert sha(Path(name).read_bytes())==pin,'EXTERNAL_PIN:'+name
 spec=importlib.util.spec_from_file_location('media',TASK/'tools/check_media.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 delivery=json.loads((TASK/'delivery-r4/DELIVERY.json').read_text());image=TASK/'delivery-r4/vm164-trusted-bootstrap-fd91b8b07243565e.iso';media=mod.check(image,delivery)
 assert sha((TASK/'payload/BOOT.PY').read_bytes())==delivery['files']['BOOT.PY'],'HELPER_MEDIA_SOURCE'
 assert (TASK/'media-build-9/probe-data.iso').read_bytes()==image.read_bytes()==(TASK/'media-build-10/probe-data.iso').read_bytes(),'REPRODUCIBILITY'
 r=subprocess.run([sys.executable,'-I','-B','-S',str(PROJECT/'tasks/jarvis-v2-vm164-lab-readiness-r1/tools/verify_preparation.py')],capture_output=True,text=True,timeout=120)
 assert r.returncode==0,'PREDECESSOR_VERIFICATION_FAILED';prior=json.loads(r.stdout)
 assert prior['status']=='PASS_PREPARATION_ENGINEERING_ONLY','PREDECESSOR_STATUS'
 return {'status':'PASS_LOCAL_PREPARATION_ONLY','manifest_sha256':seal['manifest_sha256'],'regular_files':len(m['files']),'symlinks':len(m['symlinks']),'final_iso_sha256':media['iso_sha256'],'predecessor_status':prior['status'],'original_log_prefix_preserved':True,'VM_operation_performed':False,'bootstrap_or_installation_qualified':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))

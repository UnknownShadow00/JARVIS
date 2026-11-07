"""Build exclusive, deterministic nonboot probe media locally; no VM operations."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
PROJECT=TASK.parents[1]
PROBE=PROJECT/'tasks/jarvis-v2-vm164-lab-readiness-r1/tools/lab_package.py'
PIN='08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a'
TOOLROOT=Path('/home/nexus/.local/share/jarvis-g6k-vm164-build-r1/iso-tool/root')
TOOLPIN='48ef9572c33328fdce1ca9380dc52798d5e16456c2145dc46858ab7cfcdadd8b'
def sha(b):return hashlib.sha256(b).hexdigest()
def build(out):
 probe=PROBE.read_bytes();assert sha(probe)==PIN,'PREDECESSOR_PROBE_PIN'
 assert sha((TOOLROOT/'usr/bin/xorriso').read_bytes())==TOOLPIN,'BUILDER_PIN'
 out.mkdir(mode=0o700);payload=out/'input';payload.mkdir(mode=0o700)
 files={'BOOT.PY':(TASK/'payload/BOOT.PY').read_bytes(),'LABPKG.PY':probe}
 files['SHA256.SUM']=''.join(sha(b)+'  '+n+'\n' for n,b in sorted(files.items())).encode()
 for n,b in files.items():
  with (payload/n).open('xb') as f:f.write(b)
  os.chmod(payload/n,0o444)
 cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--ro-bind',str(TOOLROOT),'/tool','--ro-bind',str(payload),'/input','--bind',str(out),'/output','--proc','/proc','--dev','/dev','--dir','/tmp','--chdir','/output','--setenv','LD_LIBRARY_PATH','/tool/usr/lib/x86_64-linux-gnu','/tool/usr/bin/xorriso','-no_rc','-outdev','/output/probe-data.iso','-volid','J164BOOT','-uid','0','-gid','0','-volume_date','uuid','2026110600000000','-volume_date','all_file_dates','2026110600000000','-padding','0','-map','/input','/','-commit','-end']
 r=subprocess.run(cmd,capture_output=True,timeout=45,env={'PATH':'/usr/bin:/bin','LANG':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'1793923200'})
 with (out/'build.log').open('xb') as f:f.write(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('BUILD_REFUSED_PRESERVE_OUTPUT')
 image=(out/'probe-data.iso').read_bytes()
 d={'format':'vm164-trusted-bootstrap-data-v1','iso_sha256':sha(image),'iso_bytes':len(image),'volume_label':'J164BOOT','nonboot_data_only':True,'files':{n:sha(b) for n,b in sorted(files.items())},'builder_sha256':TOOLPIN,'build_epoch':'2026-11-06T00:00:00Z','vm_operation_performed':False}
 with (out/'DELIVERY.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps(d,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);build(p.parse_args().out.resolve())

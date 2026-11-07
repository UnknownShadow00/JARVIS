"""Run only new local Python consistency CLIs; no payload/host/guest execution."""
import argparse,json,subprocess,sys
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
def run(out):
 out.mkdir(mode=0o700);rows=[]
 cases=[('valid-policy-only',0),('guest-owned',1),('worker-unqualified',1),('no-hardstop-authority',1),('timer-inactive',1)]
 for name,want in cases:
  p=subprocess.run([sys.executable,'-I','-B','-S',str(TASK/'tools/lease_policy.py'),'--fixture',str(TASK/'fixtures-final'/(name+'.json'))],capture_output=True,text=True,timeout=5)
  r=json.loads(p.stdout);assert p.returncode==want and r['root_boot_go'] is False,(name,p.stderr)
  with (out/(name+'.json')).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
  rows.append({'fixture':name,'expected_exit':want,'actual_exit':p.returncode,'root_boot_go':False})
 name='diagnostic-stop-detach-chain';p=subprocess.run([sys.executable,'-I','-B','-S',str(TASK/'tools/state_gate.py'),'--bundle',str(TASK/'fixtures-final'/(name+'.json')),'--as-of','2026-11-06T18:01:00Z'],capture_output=True,text=True,timeout=5)
 r=json.loads(p.stdout);assert p.returncode==0 and r['root_boot_go'] is False,p.stderr
 with (out/(name+'.json')).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
 rows.append({'fixture':name,'expected_exit':0,'actual_exit':p.returncode,'root_boot_go':False})
 result={'status':'PASS_SIX_OFFLINE_CLI_FIXTURES','cases':rows,'root_boot_go':False,'VM_actions':False}
 with (out/'RESULTS.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);run(p.parse_args().out.resolve())

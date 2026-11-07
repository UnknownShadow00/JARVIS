"""Offline snapshot negatives and pure CLI dry-run/scenario checks only.
Never passes the native execution flag or starts a timer/service/VM.
"""
import argparse,json,subprocess,sys
from pathlib import Path
TASK=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TASK/'src'))
import model as M

def run(out):
 out.mkdir(mode=0o700);index=M.parse((TASK/'fixtures/INDEX.json').read_bytes());rows=[]
 for case in index['cases']:
  if case['category']!='snapshot':continue
  raw=(TASK/'fixtures'/case['file']).read_bytes();ok=False
  try:M.validate_snapshot(M.parse(raw),index['clock_us'],index['host_boot_id'],digest=index['expected_digest']);ok=True
  except (M.Refusal,KeyError,TypeError,ValueError):pass
  assert ok==case['expected_consistent'],case['name']
  rows.append({'case':case['name'],'consistent':ok,'matched_expected':True,'root_boot_go':False})
 cli=TASK/'src/cli.py';cases=[('default',[],0,'DRY_RUN_NO_ACTION'),
  ('prepare-dry',['prepare','--dry-run'],0,'DRY_RUN_NO_ACTION'),
  ('worker-dry',['worker','--session','1'*32,'--phase','deadline'],0,'DRY_RUN_NO_ACTION'),
  ('missing-prerequisites',['prerequisites','--fixture',str(TASK/'templates/stage2-prerequisites.example.json')],1,'NO_GO_MISSING_PREREQUISITES')]
 for name in ('scenario-A-stops','scenario-A-refuses','scenario-B-refuses'):
  cases.append((name,['simulate','--fixture',str(TASK/'fixtures'/(name+'.json'))],0,'PASS_SYNTHETIC_SCENARIO_ONLY'))
 cli_rows=[]
 for name,args,code,status in cases:
  assert '--execute-reviewed-host' not in args
  r=subprocess.run([sys.executable,'-I','-B','-S',str(cli),*args],capture_output=True,text=True,timeout=5)
  d=json.loads(r.stdout);assert r.returncode==code and d['status']==status,(name,r.stderr,d)
  assert d['root_boot_go'] is False
  if name=='scenario-A-refuses':assert d['termination_state']=='running' and d['expiration_result']=='POLICY_A_NO_EXPIRATION_GUARANTEE'
  if name=='scenario-B-refuses':assert d['simulated'] and d['forced_stop_runtime_enabled'] is False
  with (out/(name+'.json')).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
  cli_rows.append({'case':name,'expected_exit':code,'actual_exit':r.returncode,'status':status,'root_boot_go':False})
 result={'status':'PASS_OFFLINE_FIXTURE_REPLAY_ONLY','snapshot_cases':rows,'snapshot_count':len(rows),
         'cli_cases':cli_rows,'cli_count':len(cli_rows),'expected_snapshot_refusals':sum(not x['consistent'] for x in rows),
         'actual_host_timers_or_VM_actions':False,'root_boot_go':False}
 with (out/'RESULTS.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'status':result['status'],'snapshot_count':len(rows),'cli_count':len(cli_rows),'root_boot_go':False},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);run(p.parse_args().out.resolve())

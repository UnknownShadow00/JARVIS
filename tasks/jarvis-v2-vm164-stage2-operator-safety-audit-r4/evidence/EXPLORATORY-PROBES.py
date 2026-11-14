from pathlib import Path
import json,sys,copy,re,runpy
s=json.loads(Path('/tmp/r4audit-state.json').read_text());P=Path(s['candidate']);A=Path(s['audit'])
sys.path[:0]=[str(P/'src'),str(P/'tests')]
import fixtures as f,packet as p,results,retention,binding as b
from common import canonical,sha
base=json.loads((P/'evidence/SYNTHETIC-12-CASE.json').read_bytes())
def validate(r):
 r,a=f.seal(r);return results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256='e'*64)
def sync(o):f.sync(o)
def both(r,field,change):
 for k in ('completion','final'):
  o=r['cases']['rearm-b'][k];o['service'][field]=change(o['service'][field]);sync(o)
def earlyguard(r):both(r,'ExecCondition',lambda v:re.sub(r'start_time=\[[^\]]*\]',lambda _: 'start_time=['+f.stamp(r['cases']['rearm-b']['plan']['deadline_boot_us']-60000000)+']',v))
def plainwrong(r):
 row=r['cases']['rearm-b'];lines=[json.loads(x) for x in row['raw_journal'].splitlines()];last=copy.deepcopy(lines[-1]);bt=int(row['completion']['service']['ExecMainExitTimestampMonotonic']);last.update(MESSAGE='Main process exited, code=exited, status=0',_SYSTEMD_INVOCATION_ID='WRONG',__CURSOR='independent-exit',__MONOTONIC_TIMESTAMP=str(bt),__REALTIME_TIMESTAMP=str(int(last['__REALTIME_TIMESTAMP'])+bt-int(last['__MONOTONIC_TIMESTAMP'])));lines.append(last);raw=''.join(json.dumps(x)+'\n' for x in lines);row['raw_journal']=raw
 for k in ('journal_receipt','completion_journal_receipt'):row[k]['raw_stdout']=raw
for name,mut in [('earlyguard',earlyguard),('plainwrong',plainwrong)]:
 r=copy.deepcopy(base);mut(r)
 try:print(name,validate(r))
 except Exception as e:print(name,type(e).__name__,str(e))

"""Render data only. No host connection, installation, subprocess or activation."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import packet
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--input',type=Path,required=True)
p.add_argument('--case',choices=packet.CASES,required=True)
a=p.parse_args()
def unique(rows):
 d={}
 for k,v in rows:
  if k in d:raise ValueError('duplicate key')
  d[k]=v
 return d
raw=a.input.read_bytes()
if len(raw)>131072:raise ValueError('input too large')
d=json.loads(raw,object_pairs_hook=unique)
r=packet.plan(d['session'],d['sample'],a.case,d['identity'],d['occupied_units'],d['consumed_names'])
packet.freshness(d['session'],d['sample'],r)
r['observe']=packet.observation_commands(d['session']['nonce'],a.case,d['session']['boot_id'])
print(json.dumps(r,indent=2))

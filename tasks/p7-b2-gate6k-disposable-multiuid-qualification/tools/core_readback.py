"""Stdout-only production inspection. No application imports or credentials."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
def guard(event, args):
    if event in ('socket.connect', 'socket.bind', 'socket.getaddrinfo'):
        raise RuntimeError('NETWORK_FORBIDDEN')
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        p = Path(os.fsdecode(args[0])).absolute()
        if Path('/home/jarvis/.config') in p.parents:
            raise RuntimeError('CREDENTIAL_OPEN_FORBIDDEN')
        if (args[2] or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise RuntimeError('WRITE_FORBIDDEN')
sys.addaudithook(guard)
R = Path('/home/jarvis/JARVIS')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(*argv): return subprocess.check_output(argv, text=True).strip()
db = sqlite3.connect((R/'data/p7-b2-pilot-controller-v1/controller.sqlite3').as_uri()+'?mode=ro', uri=True)
db.execute('PRAGMA query_only=ON'); db.execute('BEGIN')
tables = [x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
counts = {n: db.execute('SELECT count(*) FROM "'+n.replace('"','""')+'"').fetchone()[0] for n in tables}
r = {'utc': datetime.now(timezone.utc).isoformat(), 'host': os.uname().nodename,
     'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
     'source_head': cmd('git','-C',str(R),'rev-parse','HEAD'),
     'worktree': cmd('git','--no-optional-locks','-C',str(R),'status','--short'),
     'config_sha256': sha(R/'config.yaml'),
     'app_inventory': {str(p.relative_to(R)):sha(p) for p in sorted((R/'app').rglob('*.py'))},
     'service': dict(x.split('=',1) for x in cmd('systemctl','--user','show','jarvis.service',
           '-p','ActiveState','-p','SubState','-p','UnitFileState','-p','MainPID','-p','InvocationID','-p','Restart').splitlines()),
     'D06':json.loads((R/'data/model-ownership-v1/state.json').read_bytes()),
     'D09': {'counts':counts, 'quick_check':db.execute('PRAGMA quick_check').fetchall(),
             'epochs':db.execute('SELECT id,status,input_complete FROM epochs').fetchall(),
             'pilot_events':db.execute('SELECT code FROM pilot_events').fetchall()},
     'controller_sha256':sha(R/'data/p7-b2-pilot-controller-v1/controller.sqlite3'),
     'D04_namespace_exists':(R/'data/p7-shadow-evidence-v1').exists(),
     'http_ws_probes':0, 'provider_requests':0, 'writes':0}
db.close()
# Report only the two approved feature booleans; no environment inspection.
import yaml
c = yaml.safe_load((R/'config.yaml').read_bytes())
def flags(v):
    out = {}
    if isinstance(v,dict):
        for k,x in v.items():
            if k in ('hermes_enabled','hermes_brain'): out[k] = x
            if isinstance(x,dict): out.update(flags(x))
    return out
r['hermes_flags'] = flags(c)
inventory = Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate4-v2-supervised-startup/installed-source-sha256.json')
if sha(inventory) != 'c2be606074bed90a0e22fa198cf64d704bb51b78e7f486e6c82bdb246752e6c7':
    raise RuntimeError('HISTORICAL_SOURCE_INVENTORY_IDENTITY')
expected = json.loads(inventory.read_bytes())
if any(not n.startswith('app/') or '..' in Path(n).parts for n in expected):
    raise RuntimeError('HISTORICAL_SOURCE_INVENTORY_PATH')
r['installed_source_baseline_mismatches'] = [n for n,h in expected.items() if sha(R/n) != h]
r['production_data_directories'] = sorted(p.name for p in (R/'data').iterdir() if p.is_dir() and not p.is_symlink())
r['proposed_v3_roots_present'] = {n:Path(n).exists() for n in ('/opt/jarvis-v3','/var/lib/jarvis-v3','/var/lib/jarvis-authority')}
r['system_v3_unit'] = dict(x.split('=',1) for x in subprocess.run(
    ['systemctl','show','jarvis-v3.service','-p','LoadState','-p','ActiveState','-p','MainPID'],
    capture_output=True,text=True).stdout.splitlines() if '=' in x)
r['user_jarvis_unit_files'] = cmd('systemctl','--user','list-unit-files','jarvis*','--no-legend','--no-pager')
r['relevant_user_units'] = [x.split()[:4] for x in cmd('systemctl','--user','list-units','--all','--plain','--no-legend','--no-pager').splitlines()
                            if x.split() and any(k in x.split()[0].lower() for k in ('jarvis','hermes'))]
print(json.dumps(r,indent=2))

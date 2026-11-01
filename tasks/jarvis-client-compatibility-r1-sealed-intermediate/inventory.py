"""Bounded first-party source discovery; never read real configs/runtime stores."""
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
PACKET=Path(__file__).resolve().parent
ROOTS=['app','frontend','scripts','evals','docs','.github']
TOP=['README.md','CLAUDE.md','HANDOFF.md','CONTRIBUTING.md','SESSION_STARTER.md','PHASE_0_TASKS.md','PHASE_1_TASKS.md','jarvis.py','jarvis.cmd']
ACTIVE_TASKS=['tasks/readiness_report.py','tasks/tool_readiness_smoke.py','tasks/pre_server_readiness.py','tasks/manual_voice_smoke.py']
SUFFIXES={'.py','.js','.ts','.tsx','.jsx','.html','.sh','.ps1','.md','.yml','.yaml','.cmd','.toml'}
EXCLUDED={'node_modules','dist','build','vendor','__pycache__','snapshots','coverage','baselines'}
PATTERNS={
 'changed_api':r'/tasks\b|/schedule/jobs\b|/requests/|agent_tasks|scheduled_jobs',
 'facade_or_authority':r'\btask_queue\b|\b(?:add_task|delete_task|update_status|add_job|remove_job|submit|set_schedule|admit_occurrence)\s*\(',
 'transport':r'\b(?:fetch|urlopen|WebSocket|XMLHttpRequest)\s*\(|\b(?:httpx|requests|axios)\b|\b_(?:get|post)\s*\(|\.(?:get|post|put|patch|delete|send)\s*\(',
 'lifecycle_or_backlog':r'scheduler\.(?:start|stop)|pending_task_count|pending_count|tasks/state|TaskQueue|Scheduler\(',
}


def scan():
    command=['rg','--files',*ROOTS]
    paths=set(subprocess.check_output(command,cwd=ROOT,text=True).splitlines())
    paths.update(name for name in [*TOP,*ACTIVE_TASKS] if (ROOT/name).is_file())
    rows=[];skipped=[];total=0
    for name in sorted(paths):
        path=Path(name)
        if path.suffix not in SUFFIXES or set(path.parts)&EXCLUDED or name.endswith(('.min.js','.map')):
            skipped.append(name);continue
        full=ROOT/path
        if full.is_symlink():raise RuntimeError('scoped source symlink refused')
        raw=full.read_bytes();total+=len(raw)
        if len(raw)>1024**2 or total>16*1024**2:raise RuntimeError('source discovery bound exceeded')
        content=raw.decode('utf-8')
        hits=[]
        for number,line in enumerate(content.splitlines(),1):
            kinds=[kind for kind,expression in PATTERNS.items() if re.search(expression,line)]
            if kinds:hits.append({'line':number,'kinds':kinds,'source':line.strip()[:500]})
        rows.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'hits':hits})
    return {'at_utc':datetime.now(UTC).isoformat(),'status':'SCOPED_FIRST_PARTY_SOURCE_SCAN','command':command,'explicit_top_level_files':TOP,'active_top_level_task_scripts':ACTIVE_TASKS,'suffixes':sorted(SUFFIXES),'excluded_path_components':sorted(EXCLUDED),'excluded_scopes':['all sealed/historical tasks directories, run copies and snapshots','dependency/generated bundles and binary assets','tests (test callers are fixtures, not deployed clients)','real config.yaml, environment files, credentials, runtime state','historical top-level task13 benchmark scripts and historical reports'],'patterns':PATTERNS,'source_bytes':total,'files':rows,'excluded_inventory_paths':skipped,'limits':{'per_source_bytes':1024**2,'total_bytes':16*1024**2}}


if __name__=='__main__':
    result=scan()
    with (PACKET/'INVENTORY.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'files':len(result['files']),'bytes':result['source_bytes'],'hit_files':sum(bool(r['hits']) for r in result['files'])}))

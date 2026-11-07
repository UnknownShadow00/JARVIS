from pathlib import Path
import json,hashlib,collections
P=Path(__file__).resolve().parent;W=P.parents[2]/'JARVIS-unified-rc1'
rows=json.loads((P/'INTEGRATION-MATRIX.json').read_text())
notes={
'app/agent/api.py':'Codex2 async exact Bearer comparison and strip() blank-token refusal. Codex1 already required authentication for every authority route; this strengthens that implementation.',
'app/server.py':'Codex1 bounded sends/closes and handler-owned registration retained; Codex2 cleanup behavior preserved. Independent review aligned transport startup blank-token checks with HTTP auth.',
'app/agent/storage_paths.py':'Codex1 retained-ancestor post-create verification plus Codex2 race-refusing descriptor-relative mkdir; no-follow/owner/mode checks retained.',
'app/comms/ue5_bridge.py':'Retain Codex1 cap accounting and send/close bounds, which are stronger than Codex2 removal-on-failed-broadcast implementation.',
'.dockerignore':'Union Codex2 COPY-input allowlist with Codex1 nested config/credential/private/cache exclusions.',
'app/config.py':'Keep Codex1 disabled resource-control class defaults; Codex2 snapshot still enabled them.',
'config.yaml.example':'Keep Codex1 safe dry-run/boot/dictation/resource/tracing defaults, clarify blank-token /ready contract.',
'app/cli.py':'Existing credentialed task/recovery helpers retained; add credentialed fail-closed ready command without startup/retry fallback.',
'docs/task_api.md':'Codex2 explicit mandatory auth wording plus reference to Codex1 stronger offline candidate contract.',
'docs/resource_management.md':'Replace ambiguous readiness instruction with protected credentialed CLI workflow.',
'tests/test_authority_http_security.py':'Codex2 superset adds whitespace configuration denial; previous cases retained.',
'tests/test_ue5_security.py':'Codex2 cancellation, capacity, UTF-8 and close-failure tests merged with Codex1 protocol close codes and bounded manager ownership.',
'tests/test_release_security.py':'Codex1 stronger full suite retained; three new actual transport-lifespan blank-token startup rejection cases.',
'README.md':'Preserve both predecessor scopes and point current release to unified packet.',
'PROJECT_STATUS.md':'Preserve historical claims and name unified packet as current offline candidate.',
'docs/release_candidate.md':'Unified packet identity, nonblank token contract and credentialed readiness command.',
'docs/security_baseline.md':'Codex2 guide retained, updated for Codex1 binary code and unified credentialed readiness CLI.',
}
for r in rows:
 n=r['path'];f=W/n
 if n.startswith('tasks/') and '/' in n[6:]:
  r['decision']='external predecessor artifact; not part of application release';r['rationale']='Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation.';r['merged_sha256']=None;continue
 r['merged_sha256']=hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
 if n in notes:r['rationale']=notes[n]
 elif n.startswith('tests/') and r['decision']=='release retained':r['rationale']='Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained.'
 elif r['decision']=='release retained':r['rationale']='Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs.'
for n in ['app/cli.py','docs/resource_management.md','tests/test_ready_client.py']:
 if not any(r['path']==n for r in rows):rows.append({'path':n,'codex1_sha256':None,'codex2_sha256':None,'merged_sha256':hashlib.sha256((W/n).read_bytes()).hexdigest(),'decision':'new integration fix/tests','rationale':notes.get(n,'Twelve fail-closed credentialed CLI readiness tests; no service startup, state mutation or retries.')})
rows.sort(key=lambda r:r['path'])
(P/'INTEGRATION-MATRIX.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
(P/'INTEGRATION-MATRIX.md').write_text('# File-by-file integration matrix\n\nBoth predecessors derive from Git base f4cac30259a7bf4610add2063679ae49138ee637 but contain uncommitted work. Codex1 source manifest is ab2d17fb7c522ef9 (full hash in predecessor BUILD.json); Codex2 source revision is e5774287b42dd9ad227ec2fe281dd5e48d07ba23fff9366d79d7cc7739024069. Initial and final per-file hashes are retained in the JSON companion. No shared or predecessor source was overwritten.\n\nAll four headline security fixes already existed in Codex1 in some form. Remaining differences were nonblank async authentication, race-refusing mkdir, allowlist context, expanded tests/docs and stronger Codex1 WebSocket/default behavior. Integration resolves these semantically, rather than copying newer timestamps.\n\n| File | Decision | Rationale |\n|---|---|---|\n'+''.join('| `'+r['path']+'` | '+r['decision']+' | '+r['rationale']+' |\n' for r in rows))
print('Matrix rows',len(rows))

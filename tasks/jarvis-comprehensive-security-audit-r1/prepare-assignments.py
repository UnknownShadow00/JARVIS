from pathlib import Path
import re,json,urllib.parse
O=Path(__file__).resolve().parent;S=Path('/home/nexus/.claude/skills/security-audit')
groups={
'http':('app/server.py#HTTP-and-WebSocket','app/server.py#api_token_middleware','app/server.py',['app/server.py','app/config.py','app/agent/api.py','frontend','tests/test_server_auth.py'],[
('Access control','WEB-PROTOCOL-AND-AUTH.md','API-key scope and resource binding'),
('Access control','WEB-PROTOCOL-AND-AUTH.md','Host and forwarded-header trust'),
('Access control','CLIENT-SIDE.md','Cross-site WebSocket request use'),
('Injection','CLIENT-SIDE.md','DOM-based XSS'),
('Resource and file handling','CLIENT-SIDE.md','Service-worker cache and identity confusion'),
('Access control','DESKTOP-MOBILE-AND-LOCAL-IPC.md','Navigation-origin to bridge confusion')]),
'authority':('app/agent/api.py#tasks-schedules-execution','app/agent/authority.py#transaction-and-scope','app/agent',['app/agent/authority.py','app/agent/execution.py','app/agent/simulation.py','app/agent/scheduler.py','app/agent/task_queue.py','app/agent/reporter.py','app/agent/admission.py'],[
('Access control','PROTOCOLS-RPC-AND-MESSAGING.md','Envelope and payload identity mismatch'),
('Business logic',None,None),
('Chained vulnerabilities and trust boundaries','AI-AND-LLM.md','Excessive agency and confused-deputy authority'),
('Business logic','RESOURCE-EXHAUSTION-AND-AVAILABILITY.md','Detached work after cancellation'),
('Resource and file handling','RESOURCE-EXHAUSTION-AND-AVAILABILITY.md','Quota-accounting scope and reset gaps')]),
'ledger':('app/agent/ledger.py#checkpoint-and-export','app/agent/ledger.py#LedgerGuard','app/agent/ledger',['app/agent/ledger.py','app/agent/checkpoint_epochs.py','app/agent/audit_attestations.py','app/agent/ledger_schema.py','app/agent/authority.py'],[
('Cryptography and secrets',None,None),
('Resource and file handling','DESKTOP-MOBILE-AND-LOCAL-IPC.md','Local file ownership and TOCTOU'),
('Business logic','DATA-ISOLATION-AND-LIFECYCLE.md','Backup and replication boundary drift'),
('Resource and file handling','RESOURCE-EXHAUSTION-AND-AVAILABILITY.md','Unsafe recovery and capacity rollback')]),
'recovery':('app/agent/operator_cli.py#offline-operator','app/agent/recovery.py#OperatorPermits','app/agent/recovery',['app/agent/recovery.py','app/agent/recovery_decisions.py','app/agent/enrollment.py','app/agent/branch_verification.py','app/agent/archive_restore.py','app/agent/operator_cli.py','app/agent/migration.py'],[
('Access control','DATA-ISOLATION-AND-LIFECYCLE.md','Import and restore authority expansion'),
('Business logic','DATA-ISOLATION-AND-LIFECYCLE.md','Restore reintroduces invalid state'),
('Cryptography and secrets',None,None),
('Business logic',None,None),
('Resource and file handling','DESKTOP-MOBILE-AND-LOCAL-IPC.md','Local file ownership and TOCTOU')]),
'legacy':('app/server.py#chat-and-confirm','app/tools/registry.py#call','app/brain-and-tools',['app/brain','app/tools','app/memory','app/computer','app/voice','app/boot.py','app/resource_manager.py','app/comms','app/logs','app/observability','app/agent/sensor_store.py'],[
('Injection','AI-AND-LLM.md','Tool-argument injection into a downstream sink'),
('Access control','AI-AND-LLM.md','Action-confirmation and approval binding'),
('Chained vulnerabilities and trust boundaries','AI-AND-LLM.md','Persistent memory poisoning'),
('Resource and file handling','RESOURCE-EXHAUSTION-AND-AVAILABILITY.md','Unbounded buffering and cardinality'),
('Feature abuse and data leakage','AI-AND-LLM.md','Sensitive context extraction')]),
'infra':('tasks/proxmox-automation-phase3/src/entry.py#broker-worker','tasks/proxmox-automation-phase3/src/g6k_serial/runtime.py#peer_identity','tasks/proxmox-automation-phase3',['tasks/proxmox-automation-phase3','tasks/proxmox-automation-phase2'],[
('Access control','DESKTOP-MOBILE-AND-LOCAL-IPC.md','Claimed principal versus channel identity'),
('Resource and file handling','DESKTOP-MOBILE-AND-LOCAL-IPC.md','Local file ownership and TOCTOU'),
('Business logic','PROTOCOLS-RPC-AND-MESSAGING.md','Message boundary and canonicalization disagreement'),
('Chained vulnerabilities and trust boundaries','CLOUD-AND-DEPLOYMENT.md','Workload identity overreach'),
('Resource and file handling','RESOURCE-EXHAUSTION-AND-AVAILABILITY.md','Poison-record and head-of-line blocking')]),
'deploy':('Dockerfile#build-and-runtime','app/config.py#load_settings','deployment-and-operations',['Dockerfile','docker-compose.yml','requirements-core.txt','requirements-desktop.txt','requirements.txt','.github','scripts','config','config.yaml.example','.env.example','.gitignore','app/cli.py','evals','tasks/*.py'],[
('Obvious things','SUPPLY-CHAIN-AND-RELEASE.md','Mutable and unbound build inputs'),
('Cryptography and secrets','CLOUD-AND-DEPLOYMENT.md','Secret exposure across workload boundaries'),
('Access control','CLOUD-AND-DEPLOYMENT.md','Unexpected service or management-plane reachability'),
('Business logic','CLOUD-AND-DEPLOYMENT.md','Security-control precedence drift'),
('Resource and file handling','SUPPLY-CHAIN-AND-RELEASE.md','Build-context inclusion')])}
def blocks(file):
 t=(S/file).read_text();starts=list(re.finditer(r'(?m)^(?:\*\*([^\n]+?)\*\*|## ([^\n]+))',t));b={}
 for i,m in enumerate(starts):
  name=(m.group(1) or m.group(2)).split(' (')[0];b[name]=t[m.start():starts[i+1].start() if i+1<len(starts) else len(t)]
 return b
ordinary=blocks('ATTACK-CLASSES.md');ledger=[]
for group,(surface,boundary,subsystem,paths,classes) in groups.items():
 for ordinaryname,comp,klass in classes:
  attack=comp+'#'+klass if comp else 'ATTACK-CLASSES.md#'+ordinaryname
  refs=dict(surface=surface,boundary=boundary,subsystem=subsystem,attack_class=attack)
  cid='::'.join(urllib.parse.quote(v,safe='-._~') for v in refs.values())
  selected=[] if not comp else [comp+'#'+x for x in ('Core discipline',klass,'Universal moves','Validation rules')]
  if comp and klass not in blocks(comp):raise SystemExit('Missing class '+attack)
  ledger.append(dict(coverage_id=cid,canonical_refs=refs,surface=surface,boundary=boundary,subsystem=subsystem,attack_class=klass or ordinaryname,starting_paths=paths,ordinary_attack_class_block='ATTACK-CLASSES.md#'+ordinaryname,selected_companion_blocks=selected,excluded_blocks=[{'block':'MEMORY-SAFETY-AND-BINARY.md','reason':'No maintained native binary implementation in assigned source; vendored binaries not executed.'}],prior_status='none',attempts=[],wave=1,status='planned',agent_id=None,reviewed_paths=[],local_checks=[],result_fingerprints=[],unresolved=[],assignment_group=group))
ledger.sort(key=lambda x:x['coverage_id']);(O/'coverage-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
hunting=(S/'HUNTING.md').read_text();method=hunting[hunting.index('#### Core hunting method'):hunting.index('## Local validation boundaries')];contract=hunting[hunting.index('## Structured hunter result'):hunting.index('## Parent consolidation')];schema=(S/'report-schema.json').read_text()
for group in groups:
 aid='hunt-'+group;a=O/'agents'/aid
 for d in ['scratch','artifacts']:(a/d).mkdir(parents=True,exist_ok=True)
 units=[u for u in ledger if u['assignment_group']==group]
 bnames=set(u['ordinary_attack_class_block'] for u in units)|set(b for u in units for b in u['selected_companion_blocks'])
 exact='\n'.join(blocks(f)[name] for f,name in (x.split('#',1) for x in sorted(bnames)))
 excluded=[{'block':'ATTACK-CLASSES.md#'+n,'reason':'No unit assigned for this ordinary class; related boundaries assigned to other hunters or selected companions.'} for n in ordinary if n not in [u['ordinary_attack_class_block'].split('#')[1] for u in units]]
 text='Find source-grounded security invariant failures in your assigned units. Return exactly one JSON object matching the structured hunter result below.\n\n'+(O/'architecture.md').read_text()+'\nASSIGNED UNITS\n'+json.dumps(units,indent=2)+'\nEXACT SELECTED BLOCKS\n'+exact+'\nEXCLUDED ORDINARY BLOCKS\n'+json.dumps(excluded,indent=2)+'\n'+method+'\nNo carried confirmed exclusions: no compatible prior audit ledgers. Do not duplicate peer-owned groups: '+', '.join(g for g in groups if g!=group)+'. Return different-boundary discoveries under uncovered.\n'+'Read source ONLY at '+str(O/'snapshot')+'. You are not alone in this codebase: do not change or revert others edits. You own only '+str(a/'scratch')+'. No direct target execution. Prepare minimal harness there if useful and message parent for sequential OS-sandbox execution. Parent alone runs sandbox-runner.py and promotes output. Planned output allowlist: each explicitly approved harness stem plus .txt, max262144 bytes/file and invocation. Artifact path: agents/'+aid+'/artifacts/<stem>.txt; no local check until parent returns promotion. No network, live files, credentials, production, Proxmox changes or heavy tests. '+('Specifically trace hypothesis A, including mandatory authority admission/startup and browser vs local-process distinctions.' if group=='http' else 'Specifically evaluate hypothesis B with real other-UID ownership prerequisites; same-UID trusted races are not privilege escalation.' if group=='ledger' else '')+'\n'+contract+'\nSCHEMA VERBATIM\n'+schema
 (a/'assignment.txt').write_text(text)
print(json.dumps({'units':len(ledger),'groups':list(groups),'prompt_bytes':sum((O/'agents'/('hunt-'+g)/'assignment.txt').stat().st_size for g in groups)}))

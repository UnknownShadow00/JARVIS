from pathlib import Path
import json,re
O=Path(__file__).resolve().parent;S=Path('/home/nexus/.claude/skills/security-audit')
ledger=json.loads((O/'coverage-ledger.json').read_text())
for group in ['latest-transport','latest-safety']:
 aid='hunt-'+group;r=json.loads((O/'agents'/aid/'scratch/result.json').read_text())
 (O/(aid+'-result.json')).write_text(json.dumps(r,indent=2)+'\n')
 for x in r['units']:
  u=next(u for u in ledger if u['coverage_id']==x['coverage_id'])
  u.update(status=x['disposition'],agent_id=aid,reviewed_paths=x['reviewed_paths'],local_checks=[dict(c,source_snapshot='snapshot-latest') for c in x['checks']],result_fingerprints=x['candidate_fingerprints'],unresolved=x['unresolved'],hardening=r.get('hardening',[]))
  artifact='transport-selected-tests.txt' if group=='latest-transport' else 'latest_safety.txt'
  u['local_checks'].append(dict(agent_id=aid,reviewed_paths=x['reviewed_paths'],invariant='Latest captured transport and retired effect boundaries retain the reviewed refusals.',method='local',result='10 selected existing synthetic transport tests passed in 1.05 seconds.' if group=='latest-transport' else 'Six dummy-only groups passed: 24 configuration/confirmation dispatch refusals, five getter refusals, three streaming fallbacks denied, inactive denial, removed confirmation route and dictation without effects/raw transcript.',artifact=f'agents/{aid}/artifacts/{artifact}',source_snapshot='snapshot-latest'))
(O/'coverage-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
v=(S/'VALIDATION-AND-REPORTING.md').read_text()
prompt=re.search(r'#### Candidate-verifier prompt\s*\n\s*```text\n(.*?)\n```',v,re.S).group(1)
promotion=re.search(r'Copy this promotion procedure verbatim.*?```text\n(.*?)\n```',v,re.S).group(1)
records=json.loads((O/'findings-before-latest.json').read_text())
for suffix,fp,comp in [('auth','app/server.py:anonymous-loopback-authority','WEB-PROTOCOL-AND-AUTH.md'),('screenshot','app/computer/screenshot.py:shared-temp-output','DESKTOP-MOBILE-AND-LOCAL-IPC.md')]:
 aid='verify-latest-'+suffix;root=O/'agents'/aid
 for d in ['scratch','artifacts']:(root/d).mkdir(parents=True,exist_ok=True)
 candidate=next(r for r in records if r['fingerprint']==fp)
 companion=(S/comp).read_text();companion=companion[companion.index('## Validation rules'):]
 text=prompt+'\nCANDIDATE FROM EARLIER SNAPSHOT (not current truth)\n'+json.dumps(candidate,indent=2)+'\nCURRENT SOURCE '+str(O/'snapshot-latest')+'\n'+(O/'architecture.md').read_text()+'\nLINKED UNITS\n'+json.dumps([u for u in ledger if fp in u['result_fingerprints']],indent=2)+'\nCOMPANION VALIDATION\n'+companion+'\n'+promotion+'\nSCHEMA VERBATIM\n'+(S/'report-schema.json').read_text()
 text+='\nOwn only '+str(root/'scratch')+'. Do not execute target yourself; parent can run a tiny synthetic harness sequentially through existing sandbox-runner.py. NO network/live state/production/credentials/PVE/VM/privileged actions. You are not alone; never modify source/shared files. Re-read EVERY cited current line. Prior source traces must be corrected or rejected. Latest registry/server/dictation unconditionally deny real effects; screenshot ordinary native/chat reachability is now blocked. Decide whether current specific application claim should be rejected versus a legitimate independently active helper boundary; do not preserve an unsupported lead merely because it existed. Authentication route reads/cancel remain separate from the newly credentialed transport permit path. Stock runtime admission must be respected. Write exactly decision+record JSON to scratch/result.json. Optional source checks list to scratch/checks.json. Parent owns project completion log.'
 (root/'assignment.txt').write_text(text)
aid='critic-wave5';root=O/'agents'/aid
for d in ['scratch','artifacts']:(root/d).mkdir(parents=True,exist_ok=True)
crit='Fresh post-wave5 Cloudflare coverage critic, independent of all hunters. Source ONLY '+str(O/'snapshot-latest')+'. Parent reviewed full active source across prior waves plus new 15-path delta; source-latest manifest has 388 files. Inspect coverage-ledger.json, source-manifest-latest.json, source-delta-latest.json and latest hunter results. Independently inspect actual source, particularly any missing current authoritative paths/entrypoints/lifecycle/control crossings. Prior units are retained point-in-time checks; do not call legacy effects current. Latest tools/confirm/dictation dispatch deny; transport is fixed synthetic same-process unnamed socketpair, not privilege separation.\n'+(O/'architecture.md').read_text()
crit+='\nRead ledger and hunter result files from '+str(O)+'. No target execution, external network, credentials, real DBs, providers, hardware/PVE/VM or privileged actions. Write only '+str(root/'scratch')+'. Do not modify shared reports or source. Return exact structured critic JSON {"missing_units":[],"reassign_ids":[],"resolved_prior_leads":[],"stop":true}; if gaps add concrete missing-unit objects as in prior critic-wave4-result.json with surface/boundary/subsystem/attack_class/starting_paths/selected_companion_blocks/excluded_blocks/reason, or reassign IDs. stop true only if no accepted work remains; explicit external blocks are limitations, not excuses for hidden source omissions. Save scratch/result.json. Parent logs completion.'
(root/'assignment.txt').write_text(crit)
print({'units':len(ledger),'prepared':['verify-latest-auth','verify-latest-screenshot','critic-wave5']})

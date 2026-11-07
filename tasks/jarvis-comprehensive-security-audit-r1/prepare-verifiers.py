from pathlib import Path
import json,re
O=Path(__file__).resolve().parent;S=Path('/home/nexus/.claude/skills/security-audit');L=json.loads((O/'coverage-ledger.json').read_text())
records=[]
for group,name,comps in [('http','auth',['WEB-PROTOCOL-AND-AUTH.md','CLIENT-SIDE.md']),('screenshot','screenshot',['DESKTOP-MOBILE-AND-LOCAL-IPC.md'])]:
 r=json.loads((O/('hunt-'+group+'-result.json')).read_text())['candidates'][0]
 r['verdict']=r.pop('proposed_verdict');records.append(r)
 root=O/'agents'/('verify-'+name)
 for n in ['scratch','artifacts']:(root/n).mkdir(parents=True,exist_ok=True)
 text=(S/'VALIDATION-AND-REPORTING.md').read_text();z=re.search(r'#### Candidate-verifier prompt\s*\n\s*```text\n(.*?)\n```',text,re.S).group(1);promotion=re.search(r'Copy this promotion procedure verbatim.*?```text\n(.*?)\n```',text,re.S).group(1)
 validations=''
 for f in comps:
  t=(S/f).read_text();start=t.index('## Validation rules');validations+=t[start:]+'\n'
 linked=[u for u in L if r['fingerprint'] in u['result_fingerprints']]
 prompt=z+'\n\nCANDIDATE\n'+json.dumps(r,indent=2)+'\nLINKED COVERAGE UNITS/CHECKS\n'+json.dumps(linked,indent=2)+'\nARCHITECTURE\n'+(O/'architecture.md').read_text()+'\nEXACT COMPANION VALIDATION\n'+validations+'\n'+promotion+'\nSCHEMA VERBATIM\n'+(S/'report-schema.json').read_text()+'\nNo compatible external prior finding record. You did not hunt this candidate; independently challenge it. Final source ONLY '+str(O/'snapshot-expanded')+'. Prior source/check capture is tagged explicitly and all relevant changed paths must be reread. Root-generated source-stability metadata is not deployment evidence. Agent_id verify-'+name+'. Own scratch only '+str(root/'scratch')+'. Parent owns artifacts; predeclared output allowlist approved harness stem .txt max262144bytes/file/invocation. NO targetexecution yourself; if minimal native fixture useful prepare harness and ask parent for sequential snapshot-final sandbox run. No production/credentials/provider/hardware/registry requests. Unknown OS/browser/deployed facts do not become confirmation.\nWrite exact wrapper decision+schema record to scratch/result.json, no extra fields. If making new local/source check, put optional separate checks.json list with agent_id,reviewed_paths,invariant,method,result,artifact; local artifact only after parentpromotion. Final response brief; parent performs project loop-log completion protocol.\n'
 (root/'assignment.txt').write_text(prompt)
(O/'candidate-inputs.json').write_text(json.dumps(records,indent=2)+'\n')
print({'candidate_fingerprints':[r['fingerprint'] for r in records]})

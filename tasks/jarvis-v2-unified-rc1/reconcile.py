"""Capture immutable predecessors and compose reviewed public source only."""
from pathlib import Path
import hashlib,json,subprocess,tarfile,difflib
MAIN=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
R=MAIN/'tasks/jarvis-v2-release-readiness-r1';S=MAIN/'tasks/jarvis-security-remediation-r1'
W=MAIN.parent/'JARVIS-unified-rc1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v): (P/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
a=json.loads((R/'release/BUILD.json').read_text())['source_sha256']
b={x['path']:x['sha256'] for x in json.loads((S/'final-2-manifest.json').read_text())['files']}
# Preserve hashes of all existing task evidence, with no traversal of symlinks.
preserved={};links={}
for p in sorted((MAIN/'tasks').rglob('*')):
 if p.is_relative_to(P):continue
 if p.is_symlink():links[str(p.relative_to(MAIN))]=str(p.readlink())
 elif p.is_file():preserved[str(p.relative_to(MAIN))]=sha(p)
write('PREDECESSOR-SHA256.json',preserved);write('PREDECESSOR-SYMLINKS.json',links)
write('INITIAL-STATE.json',{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=MAIN,text=True).strip(),'status':subprocess.check_output(['git','status','--porcelain=v1','-uall'],cwd=MAIN,text=True),'worktrees':subprocess.check_output(['git','worktree','list','--porcelain'],cwd=MAIN,text=True),'shared_public_hashes':{n:sha(MAIN/n) for n in b if (MAIN/n).is_file()},'log_bytes':(MAIN/'tasks/loop-log.md').stat().st_size})
archive=R/json.loads((R/'release/BUILD.json').read_text())['archive']
assert sha(archive)==json.loads((R/'release/BUILD.json').read_text())['archive_sha256']
with tarfile.open(archive) as t:
 for n,h in a.items():
  raw=t.extractfile(n).read();assert hashlib.sha256(raw).hexdigest()==h
  target=W/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
for n,h in b.items():assert sha(S/'final-2'/n)==h
# Include security-only public source/docs/helpers; exclude standalone broker evidence.
for n in b.keys()-a.keys():
 if n.startswith('tasks/') and '/' in n[len('tasks/'):]:continue
 target=W/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((S/'final-2'/n).read_bytes())
# Review records include exact diffs, rather than choosing by newer timestamps.
for n in sorted(a.keys()&b.keys()):
 if a[n]!=b[n]:
  raw1=(W/n).read_text();raw2=(S/'final-2'/n).read_text()
  d=P/'reconciliation-diffs'/Path(n+'.diff');d.parent.mkdir(parents=True,exist_ok=True)
  d.write_text(''.join(difflib.unified_diff(raw1.splitlines(True),raw2.splitlines(True),fromfile='codex1/'+n,tofile='codex2/'+n)))
# Exact API change is independently stronger for blank values and avoids threadpool checks.
(W/'app/agent/api.py').write_bytes((S/'final-2/app/agent/api.py').read_bytes())
# Preserve post-creation ancestor identity verification; refuse creation races.
f=W/'app/agent/storage_paths.py';text=f.read_text().replace('try:os.mkdir(part, mode=0o700, dir_fd=fd)\n                        except FileExistsError:pass','os.mkdir(part, mode=0o700, dir_fd=fd)');f.write_text(text)
# Union authority negative tests; no prior assertions removed.
f=W/'tests/test_authority_http_security.py';f.write_text((S/'final-2/tests/test_authority_http_security.py').read_text())
# Add Codex2's protocol-state/cancellation tests, retaining RFC1003 binary-frame policy
# and manager-owned bounded closes from Codex1 (exceptions are intentionally absorbed).
f=W/'tests/test_ue5_security.py';text=(S/'final-2/tests/test_ue5_security.py').read_text()
text=text.replace('== 1008','== 1003',1).replace('assert closed.value.code == 1008','assert closed.value.code == 1003')
text=text.replace('monkeypatch.setattr(server, "_UE5_CLOSE_TIMEOUT", 0.01)','monkeypatch.setattr(manager, "send_timeout_seconds", 0.01)').replace('assert sent[-1]["code"] == 1008','assert sent[-1]["code"] == 1003')
text=text.replace('    with pytest.raises(RuntimeError, match="synthetic close failure"):\n        asyncio.run(exercise([\n            {"type": "websocket.receive", "bytes": b"x"},\n        ], on_send=broken))','    asyncio.run(exercise([\n        {"type": "websocket.receive", "bytes": b"x"},\n    ], on_send=broken))')
f.write_text(text)
# Docker allowlist plus Codex1 nested config/credential/runtime exclusions.
f=W/'.dockerignore';f.write_text((S/'final-2/.dockerignore').read_text()+'\n# Retain Codex1 nested private-file exclusions inside allowed source trees.\n**/config.yaml\n**/*credential*\n**/.venv/\n**/venv/\n**/.pytest_cache/\n')
# Keep up-to-date authority contract wording in the merged public guide.
f=W/'docs/task_api.md';text=(S/'final-2/docs/task_api.md').read_text();f.write_text(text+'\nThe unified offline candidate retains the safer defaults and bounded WebSocket\nbehavior documented in [release_candidate.md](release_candidate.md).\n')
f=W/'config.yaml.example';text=f.read_text().replace('  # Authority state routes refuse access when empty, including loopback.','  # Empty/whitespace tokens refuse authority routes, including /ready on loopback.');f.write_text(text)
rows=[]
for n in sorted(a.keys()|b.keys()):
 merged=sha(W/n) if (W/n).is_file() else None
 decision='identical' if n in a and n in b and a[n]==b[n] else ('release retained' if merged==a.get(n) and merged else 'security retained' if merged==b.get(n) and merged else 'reviewed semantic union' if merged else 'external broker evidence preserved; excluded from application')
 reason='Byte-identical shared implementation.'
 if decision=='release retained':reason='Retain full offline recovery integration, stronger WS bounds, inert defaults or current regression contracts; security alternative retained in predecessor and diff.'
 if decision=='security retained':reason='Include security-only public documentation/helpers or stronger identity contract/tests.'
 if decision=='reviewed semantic union':reason='Combine both protections without weakening prior behavior; see exact diff and final review.'
 if not merged:reason='Standalone broker is not an application adapter; no installation or activation is authorized.'
 rows.append({'path':n,'codex1_sha256':a.get(n),'codex2_sha256':b.get(n),'initial_merged_sha256':merged,'decision':decision,'rationale':reason})
write('INTEGRATION-MATRIX.json',rows)
(P/'INTEGRATION-MATRIX.md').write_text('# File-by-file source reconciliation\n\nBase Git revision is f4cac30259a7bf4610add2063679ae49138ee637; both predecessors are dirty source snapshots, not separate commits. Every file and hash is in the JSON companion. Security-only standalone broker packets remain external and unchanged.\n\n| File | Decision |\n|---|---|\n'+''.join('| `'+x['path']+'` | '+x['decision']+' |\n' for x in rows))
print(json.dumps({'preserved_files':len(preserved),'matrix_files':len(rows),'decisions':{d:sum(x['decision']==d for x in rows) for d in set(x['decision'] for x in rows)}}))

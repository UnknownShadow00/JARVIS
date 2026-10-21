"""Read-only candidate identities and sealed Gate 6F preservation on Core."""
from pathlib import Path
import hashlib,json

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
g6f=Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate6f-v3-release-qualification')
g6g=Path('/home/jarvis/.hermes-poc/gate6g-candidates/release-r1')
old=Path('/home/jarvis/.hermes-poc/gate6f-candidates/release-r1')
# New manifest bytes arrive as literals through stdin only; nothing is written.
expected=json.loads(__import__('sys').argv[1])
r={}
for label,base,text in [('gate6f_full',old,(g6f/'candidate/FULL-SOURCE-SHA256SUMS').read_text()),('gate6f_source',old,(g6f/'candidate/CANDIDATE-SOURCE-SHA256SUMS').read_text()),('gate6g_full',g6g,expected['full'])]:
 bad=[]
 for line in text.splitlines():
  want,n=line.split('  ',1)
  if label=='gate6f_source':n=n.replace('qualification/','',1) if n.startswith('qualification/') else 'repo/'+n
  p=base/n
  if not p.is_file() or p.is_symlink() or sha(p)!=want:bad.append(n)
 r[label]={'members':len(text.splitlines()),'manifest_sha256':hashlib.sha256(text.encode()).hexdigest(),'mismatches':bad}
bad=[]
for line in (g6f/'SHA256SUMS').read_text().splitlines():
 want,n=line.split('  ',1)
 if sha(g6f/n)!=want:bad.append(n)
r['gate6f_seal']={'digest':sha(g6f/'SHA256SUMS'),'mismatches':bad,'members':len((g6f/'SHA256SUMS').read_text().splitlines())}
r['new_candidate_symlinks']=[str(p) for p in g6g.rglob('*') if p.is_symlink()]
print(json.dumps(r,indent=2))

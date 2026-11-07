"""Assemble unsealed release evidence without modifying prior sealed packets."""
import ast,difflib,hashlib,json,subprocess
from datetime import UTC,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
MAIN=P.parents[1]
ROOT=MAIN.parent/'JARVIS-release-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
    baseline=json.loads((P/'BASELINE.json').read_text())
    drift=[n for n,h in baseline['prior_files'].items() if sha(MAIN/n)!=h];assert not drift,drift
    log=(MAIN/'tasks/loop-log.md').read_bytes();assert hashlib.sha256(log[:baseline['log_bytes']]).hexdigest()==baseline['log_sha256']
    write('EVIDENCE-VERIFICATION.json',{'at':datetime.now(UTC).isoformat(),'prior_files_verified':len(baseline['prior_files']),'prior_changed_files':drift,'canonical_log_prefix_preserved':True,'initial_sealed_packets_modified':False})
    changes=[];patch=[]
    files=[]
    for folder in ['app','tests','docs']:
        files.extend(f for f in (ROOT/folder).rglob('*') if f.is_file() and not f.is_symlink() and '__pycache__' not in f.parts)
    files.extend(ROOT/n for n in ['README.md','PROJECT_STATUS.md','config.yaml.example','.dockerignore'])
    for f in sorted(files):
        name=str(f.relative_to(ROOT));before=P/'before'/name
        old=before.read_bytes() if before.exists() else b'';new=f.read_bytes()
        if old!=new:
            changes.append(name);target=P/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(new)
            patch.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='before/'+name,tofile='source/'+name))
    write('CHANGES.json',changes);(P/'SOURCE.patch').write_text(''.join(patch))
    current={str(f.relative_to(ROOT)):sha(f) for f in sorted((ROOT/'app').rglob('*.py'))}
    current.update({name:sha(ROOT/name) for name in changes})
    helpers={str(f.relative_to(MAIN)):sha(f) for f in P.glob('*.py')};write('SOURCE-SHA256.json',{'candidate_source_root':str(ROOT),'source':current,'evidence_helpers':helpers})
    parsed=[]
    for f in [*sorted((ROOT/'app').rglob('*.py')),*[ROOT/n for n in changes if n.endswith('.py') and n.startswith('tests/')],*P.glob('*.py')]:
        ast.parse(f.read_bytes(),filename=str(f));parsed.append(str(f))
    review=json.loads((P/'INDEPENDENT-REVIEW.json').read_text());assert all(sha(ROOT/n)==h for n,h in review['source_sha256'].items())
    check=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True);assert check.returncode==0,check.stdout+check.stderr
    build=json.loads((P/'release/BUILD.json').read_text());assert all(sha(ROOT/n)==h for n,h in build['source_sha256'].items())
    write('STATIC-CHECKS.json',{'at':datetime.now(UTC).isoformat(),'AST_files_parsed':len(parsed),'git_diff_check':check.returncode,'independent_source_pins_match':True,'candidate_archive_public_sources_match_worktree':True,'application_imported_on_host':False,'production_config_read':False,'dependency_environment_modified':False,'fresh_advisory_audit_claimed':False})
    # Preserve overlapping shared edits for review, without writing them back.
    base=json.loads((P/'ISOLATION-BASE.json').read_text())['source_sha256'];overlap=[];shared_patch=[]
    for n,h in base.items():
        live=MAIN/n;candidate=ROOT/n
        if live.exists() and candidate.exists() and sha(live)!=h and live.read_bytes()!=candidate.read_bytes():
            overlap.append(n);saved=P/'concurrent-shared'/n;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(live.read_bytes())
            shared_patch.extend(difflib.unified_diff(live.read_text().splitlines(True),candidate.read_text().splitlines(True),fromfile='shared/'+n,tofile='candidate/'+n))
    (P/'CONCURRENT-CHANGES.patch').write_text(''.join(shared_patch))
    write('SHARED-WORKSPACE.json',{'observed_at':datetime.now(UTC).isoformat(),'candidate_source_root':str(ROOT),'shared_source_root':str(MAIN),'release_source_promoted_over_concurrent_writers':False,'overlapping_paths_preserved_for_review':overlap,'authority':'sealed source archive and matching detached worktree only; no mixed-shared-checkout qualification claim','initial_pre_isolation_source_edits':'initial authority/ancestry/WebSocket scaffolding remains in shared source, followed by independent concurrent edits; final candidate hardening is isolated'})
    write('SYMLINKS.json',{str(f.relative_to(P)):str(f.readlink()) for f in sorted(P.rglob('*')) if f.is_symlink()})
    manifest=[]
    for f in sorted(P.rglob('*')):
        if f.is_file() and not f.is_symlink() and f!=P/'SHA256SUMS':manifest.append(sha(f)+'  '+str(f.relative_to(P))+'\n')
    (P/'SHA256SUMS').write_text(''.join(manifest))
    print(json.dumps({'changes':len(changes),'initial_prior_files_verified':len(baseline['prior_files']),'source_files':len(current),'seal':sha(P/'SHA256SUMS')},indent=2))
if __name__=='__main__':main()

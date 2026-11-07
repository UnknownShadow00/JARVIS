"""Local bytes-only verification. No subprocess, network, service or guest call."""
import hashlib,importlib.util,json,os,stat
from pathlib import Path
TASK=Path(__file__).resolve().parents[1];ROOT=TASK.parents[1]
OMIT={'MANIFEST.json','SEAL.json'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def inventory():
    files={};links={}
    for p in sorted(TASK.rglob('*')):
        n=str(p.relative_to(TASK));s=p.lstat()
        if n in OMIT:continue
        if stat.S_ISLNK(s.st_mode):links[n]=os.readlink(p)
        elif stat.S_ISREG(s.st_mode):files[n]={'sha256':sha(p.read_bytes()),'bytes':s.st_size}
        elif not stat.S_ISDIR(s.st_mode):raise ValueError('special_file:'+n)
    return {'format':'jarvis-vm164-bootstrap-remediation-r2-local-manifest','files':files,'symlinks':links}
def predecessors():
    e=json.loads((TASK/'evidence/ENTRY.json').read_bytes())
    for n,h in e['predecessor_files'].items():
        p=ROOT/n
        if p.is_symlink() or sha(p.read_bytes())!=h:raise ValueError('predecessor_changed:'+n)
    for n,target in e['predecessor_symlinks'].items():
        if not (ROOT/n).is_symlink() or os.readlink(ROOT/n)!=target:raise ValueError('predecessor_link_changed')
    log=(ROOT/'tasks/loop-log.md').read_bytes()
    if sha(log[:e['log_prefix_bytes']])!=e['log_prefix_sha256']:raise ValueError('log_prefix_changed')
    old=TASK.parent/'jarvis-v2-vm164-trusted-bootstrap-r1'
    m=json.loads((old/'MANIFEST.json').read_bytes());seal=json.loads((old/'SEAL.json').read_bytes())
    if sha((old/'MANIFEST.json').read_bytes())!=seal['manifest_sha256']:raise ValueError('original_seal')
    for n,info in m['files'].items():
        if sha((old/n).read_bytes())!=info['sha256'] or (old/n).stat().st_size!=info['bytes']:raise ValueError('original_manifest')
    for n,target in m['symlinks'].items():
        if os.readlink(old/n)!=target:raise ValueError('original_links')
    audit=TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1';audited=0
    for line in (audit/'SHA256SUMS').read_text().splitlines():
        h,n=line.split('  ',1);p=Path(n)
        if p.is_absolute() or '..' in p.parts or sha((audit/p).read_bytes())!=h:raise ValueError('audit_seal')
        audited+=1
    return {'predecessor_files_preserved':len(e['predecessor_files']),
            'predecessor_symlinks_preserved':len(e['predecessor_symlinks']),
            'r1_manifest_files_verified':len(m['files']),'audit_manifest_files_verified':audited,
            'original_log_prefix_preserved':True}
def candidate():
    s=importlib.util.spec_from_file_location('candidate_readonly_check',TASK/'tools/check_candidate.py')
    c=importlib.util.module_from_spec(s);s.loader.exec_module(c);r=c.check()
    raw=(TASK/'candidate/vm164-trusted-bootstrap-r2-09185f1f69108ab1.iso').read_bytes()
    if sha(raw)!=r['iso_sha256'] or raw!=(TASK/'media-build-5/probe-data.iso').read_bytes():raise ValueError('candidate_copy')
    return r

def verify():
    seal=json.loads((TASK/'SEAL.json').read_bytes());raw=(TASK/'MANIFEST.json').read_bytes()
    if sha(raw)!=seal['manifest_sha256'] or inventory()!=json.loads(raw):raise ValueError('packet_inventory_or_seal')
    p=predecessors();c=candidate();tests=json.loads((TASK/'evidence/regression-release/RESULTS.json').read_bytes())
    if tests['status']!='PASS_OFFLINE_ONLY' or tests['unique_test_methods']!=171:raise ValueError('test_record')
    return {'status':'PASS_OFFLINE_REMEDIATION_PACKET_ONLY','manifest_sha256':seal['manifest_sha256'],
            'regular_files':len(inventory()['files']),'candidate_iso_sha256':c['iso_sha256'],
            'tests':171,'new_tests':87,'failures':tests['failures'],'errors':tests['errors'],'skips':tests['skips'],
            **p,'network_or_VM_operations':False,'runtime_host_fence_backend_implemented':False,
            'root_boot_go':False,'installation_qualified':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))

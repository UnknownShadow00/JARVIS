"""Verify independently reviewed offline artifact inventory; never install anything."""
import argparse,hashlib,json,os,re,stat
from pathlib import Path
from safe_extract import bounded_file,valid_name,safe_parent


def strict_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('DUPLICATE_JSON_KEY')
        result[key]=value
    return result


def required_artifacts(release):
    pins=json.loads((Path(release)/'disposable/dependency-versions.json').read_text())
    return {'distribution:'+n:v for n,v in pins['packages'].items()}|{
        'interpreter:cpython':'3.14.4','library:sqlite':'3.46.1','library:libseccomp':'OPERATOR_REVIEWED_OS_BUILD','image:linux-x86_64':'OPERATOR_REVIEWED_OS_BUILD'}


def verify_artifacts(release,root,expected):
    root=Path(root)
    fd=safe_parent(root);os.close(fd)
    raw=bounded_file(root/'ARTIFACTS.json',512*1024)
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('ARTIFACT_RECORD_IDENTITY')
    value=json.loads(raw,object_pairs_hook=strict_object)
    required=required_artifacts(release)
    if type(value) is not dict or set(value)!=set(required):raise ValueError('ARTIFACT_INVENTORY')
    filenames=set()
    for identity,version in required.items():
        row=value[identity]
        if type(row) is not dict or set(row)!={'version','filename','sha256','provenance_record'} or row['version']!=version:raise ValueError('ARTIFACT_VERSION_OR_SCHEMA')
        name=valid_name(row['filename'])
        if '/' in name or name in filenames or name=='ARTIFACTS.json':raise ValueError('ARTIFACT_FILENAME')
        filenames.add(name)
        if not re.fullmatch('[0-9a-f]{64}',row['sha256']) or type(row['provenance_record']) is not str or not 1<=len(row['provenance_record'])<=512:raise ValueError('ARTIFACT_PROVENANCE_RECORD')
        # A provenance reference is a human review record, not automatic authenticity.
        fd=os.open(root/name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            before=os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_mode&0o022 or before.st_uid not in (0,os.geteuid()) or before.st_size>4*1024**3:raise ValueError('ARTIFACT_FILE')
            digest=hashlib.sha256();count=0
            while chunk:=os.read(fd,1024*1024):
                count+=len(chunk)
                if count>before.st_size:raise ValueError('ARTIFACT_CHANGED')
                digest.update(chunk)
            after=os.fstat(fd)
            if count!=before.st_size or (before.st_mtime_ns,before.st_ctime_ns)!=(after.st_mtime_ns,after.st_ctime_ns) or digest.hexdigest()!=row['sha256']:raise ValueError('ARTIFACT_DIGEST')
        finally:os.close(fd)
    return {'result':'PASS','artifact_count':len(required),'independent_provenance':'human record required; not inferred from hashes'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('release');p.add_argument('--root');p.add_argument('--expected');a=p.parse_args()
    if a.root and a.expected:print(json.dumps(verify_artifacts(a.release,a.root,a.expected)))
    else:print(json.dumps({'result':'BLOCKED','required_artifacts':required_artifacts(a.release)},indent=2))

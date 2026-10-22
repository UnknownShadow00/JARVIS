"""Fail-closed disposable VM checks. No provisioning and no environment-value reads."""
import hashlib,json,os,stat,re,shutil
from safe_extract import bounded_file
from offline_artifacts import strict_object
from pathlib import Path

VIRTUAL_FILESYSTEMS={'proc','sysfs','tmpfs','devtmpfs','devpts','cgroup2','mqueue','securityfs','debugfs','tracefs','configfs','hugetlbfs','ramfs','bpf','efivarfs','pstore','fusectl','binfmt_misc','autofs'}
FORBIDDEN_NAMES={'jarvis','jarvis-core','nexus-services','nexus','pve','proxmox','ai','ai-server','ollama'}
CREDENTIAL_PATHS=('/root/.ssh','/root/.aws','/root/.azure','/root/.config/gcloud','/root/.kube','/home/jarvis','/home/nexus','/run/credentials','/run/host','/mnt/host','/var/lib/cloud/instance')

def validate_environment(*,hostname,interfaces,mountinfo,credential_paths):
    if hostname.lower().split('.')[0] in FORBIDDEN_NAMES or set(interfaces)!={'lo'}:raise RuntimeError('NOT_ISOLATED_VM')
    if credential_paths:raise RuntimeError('CREDENTIAL_OR_HOST_PATH_PRESENT')
    root=False
    for line in mountinfo.splitlines():
        left,right=line.split(' - ',1);fields=left.split();fs,source,*_=right.split()
        if any(x.startswith(('shared:','master:','propagate_from:')) for x in fields[6:]):raise RuntimeError('SHARED_MOUNT_PROPAGATION')
        if fields[4]=='/':
            if root or fields[3]!='/' or fs!='ext4' or not source.startswith('/dev/'):raise RuntimeError('PRIVATE_EXT4_ROOT_REQUIRED')
            root=True
        else:
            mount=Path(fields[4].replace('\\040',' ').replace('\\011','\t').replace('\\012','\n').replace('\\134','\\'))
            protected=('/opt','/var/lib','/etc','/usr','/lib','/lib64','/bin','/sbin')
            if any(mount==Path(path) or mount in Path(path).parents or Path(path) in mount.parents for path in protected):raise RuntimeError('PROTECTED_PATH_MOUNT_OVERRIDE')
            if fs=='autofs' or fs not in VIRTUAL_FILESYSTEMS:raise RuntimeError('ADDITIONAL_OR_SHARED_MOUNT')
    if not root:raise RuntimeError('PRIVATE_EXT4_ROOT_REQUIRED')

def validate_approval(value,machine):
    fixed={'machine_id':machine,'scope':'GATE6K_DISPOSABLE_ONLY','network':'NO_NIC','release':'/opt/g6j-release','credentials':'NONE','mounts':'PRIVATE_ROOT_ONLY','test_scope':'SYNTHETIC_MULTI_UID_NO_POWERCUT'}
    hashes={'source_manifest','archive_sha256','artifacts_sha256'}
    identity={'vmid','vm_uuid','hypervisor_node','disk_identity','operator_console','snapshot_preservation_policy'}
    if type(value) is not dict or set(value)!=set(fixed)|hashes|identity or any(value[k]!=v for k,v in fixed.items()):raise RuntimeError('APPROVAL_SCOPE')
    if not re.fullmatch('[0-9a-f]{32}',machine):raise RuntimeError('APPROVAL_MACHINE_ID')
    for name in hashes:
        if type(value[name]) is not str or not re.fullmatch('[0-9a-f]{64}',value[name]):raise RuntimeError('APPROVAL_DIGEST')
    if type(value['vmid']) is not int or value['vmid']<=0 or value['vmid'] in (101,162,200,50):raise RuntimeError('APPROVAL_VMID')
    if type(value['vm_uuid']) is not str or not re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',value['vm_uuid']):raise RuntimeError('APPROVAL_VM_UUID')
    for name in identity-{'vmid','vm_uuid'}:
        text=value[name]
        if type(text) is not str or not 1<=len(text)<=256 or not text.isascii() or any(ord(c)<32 for c in text) or any(x in text.upper() for x in ('PLACEHOLDER','REPLACE_ME','ACTUAL_','PENDING')):raise RuntimeError('APPROVAL_IDENTITY')


def read_approval(path,*,owner_uid=0):
    st=Path(path).lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid!=owner_uid or stat.S_IMODE(st.st_mode)!=0o600 or st.st_nlink!=1:raise RuntimeError('APPROVAL_MARKER')
    raw=bounded_file(path,8192)
    return json.loads(raw,object_pairs_hook=strict_object)


def validate_capacity(path,*,minimum=20*1024**3):
    if shutil.disk_usage(path).free<minimum:raise RuntimeError('TWENTY_GIB_FREE_REQUIRED')


def verify_manifest(root,expected,*,owner_uid=0):
    root=Path(root);manifest=root/'SOURCE-SHA256SUMS'
    paths=[root,*root.parents,*root.rglob('*')]
    for path in paths:
        st=path.lstat()
        if (path.is_symlink() or st.st_uid!=owner_uid and st.st_uid!=0 or st.st_mode&0o022
            or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode))
            or stat.S_ISREG(st.st_mode) and st.st_nlink!=1):raise RuntimeError('IMMUTABLE_RELEASE_REQUIRED')
    raw=bounded_file(manifest,1024*1024)
    if len(raw)>1024*1024 or hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('RELEASE_MANIFEST_IDENTITY')
    inventory={}
    for row in raw.decode('ascii').splitlines():
        sha,name=row.split('  ',1)
        if name in inventory or Path(name).is_absolute() or '..' in Path(name).parts or name=='SOURCE-SHA256SUMS':raise RuntimeError('RELEASE_MANIFEST_PATH')
        if len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):raise RuntimeError('RELEASE_MANIFEST_DIGEST')
        inventory[name]=sha
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p!=manifest}
    if actual!=set(inventory):raise RuntimeError('RELEASE_MANIFEST_INVENTORY')
    for name,sha in inventory.items():
        p=root/name
        if p.stat().st_size>64*1024*1024 or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:raise RuntimeError('RELEASE_FILE_IDENTITY')
    return len(inventory)

def validate_dependencies(root):
    import sys,sqlite3,importlib.metadata as metadata
    import cryptography
    pins=json.loads((Path(root)/'disposable/dependency-versions.json').read_text())
    if list(sys.version_info[:3])!=pins['python'] or sqlite3.sqlite_version!=pins['sqlite'] or cryptography.__version__!=pins['cryptography']:raise RuntimeError('INTERPRETER_OR_CRYPTO_PIN')
    for name,version in pins['packages'].items():
        if metadata.version(name)!=version:raise RuntimeError('DEPENDENCY_VERSION_PIN')

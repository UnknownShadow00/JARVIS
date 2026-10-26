"""Metadata-only disposable environment inspection. Never open credential files.

Empty OS containers are not credentials. Opaque cloud-init data is NOT certified
secret-free: acceptance additionally requires a specific, snapshot-bound human
fresh-image provenance review in the VM approval. Active systemd payloads refuse.
"""
import hashlib,json,os,re,stat
from pathlib import Path

STRICT_PATHS=('/root/.ssh','/root/.aws','/root/.azure','/root/.config/gcloud','/root/.kube',
 '/root/.netrc','/root/.git-credentials','/home/nexus','/run/host','/mnt/host',
 '/home/jarvis/JARVIS','/home/jarvis/.hermes-poc')
HOME_MARKERS=('.ssh','.aws','.azure','.kube','.gnupg','.netrc','.git-credentials',
 '.pypirc','.npmrc','.boto','.env','.docker/config.json','.config/gcloud',
 '.config/gh/hosts.yml','.config/jarvis','.local/share/keyrings')
CREDENTIAL_STORES=('/run/credentials','/etc/credstore','/etc/credstore.encrypted',
 '/run/credstore','/run/credstore.encrypted','/usr/lib/credstore','/usr/lib/credstore.encrypted')
KEY_NAMES={'id_rsa','id_ed25519','id_ecdsa','id_dsa','credentials','credentials.json',
 'signing.key','private.key','application_default_credentials.json','.netrc','.git-credentials'}
PUBLIC_CACHE_NAMES={'boot-finished','datasource','instance-id','previous-instance-id',
 'result.json','status.json','set-hostname','previous-datasource'}

class Metadata:
    def __init__(self,root=Path('/'),*,root_uid=0,preparation_uid=None):
        self.root=Path(root);self.root_uid=root_uid;self.allowed_uids={root_uid,preparation_uid}
    def _parent(self,path):
        parts=Path(path).parts
        if not str(path).startswith('/') or '..' in parts:raise RuntimeError('METADATA_PATH')
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            base=os.fstat(fd)
            if base.st_uid!=self.root_uid or base.st_mode&0o022:raise RuntimeError('UNPROTECTED_INSPECTION_ROOT')
            for index,part in enumerate(parts[1:-1],1):
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                os.close(fd);fd=child
                st=os.fstat(fd)
                allowed=self.allowed_uids if parts[1:3]==('home','jarvis') and index>=2 else {self.root_uid}
                if st.st_uid not in allowed or st.st_mode&0o022:raise RuntimeError('UNPROTECTED_PATH_ANCESTOR')
            return fd,parts[-1]
        except BaseException:os.close(fd);raise
    def info(self,path):
        try:fd,name=self._parent(path)
        except FileNotFoundError:return None
        except OSError:raise RuntimeError('METADATA_UNSAFE_ANCESTOR') from None
        try:
            try:return os.stat(name,dir_fd=fd,follow_symlinks=False)
            except FileNotFoundError:return None
        finally:os.close(fd)
    def link(self,path):
        fd,name=self._parent(path)
        try:return os.readlink(name,dir_fd=fd)
        finally:os.close(fd)
    def tree(self,path,*,directories_only=False):
        parent,name=self._parent(path)
        try:fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
        finally:os.close(parent)
        rows=[];budget=[0]
        def walk(current,relative,depth):
            if depth>16:raise RuntimeError('METADATA_TREE_BUDGET')
            before=os.fstat(current)
            if before.st_uid!=self.root_uid or before.st_mode&0o022:raise RuntimeError('UNPROTECTED_OS_CONTAINER')
            for name in sorted(os.listdir(current)):
                budget[0]+=1
                if budget[0]>4096:raise RuntimeError('METADATA_TREE_BUDGET')
                st=os.stat(name,dir_fd=current,follow_symlinks=False)
                rel=relative+'/'+name if relative else name
                if st.st_uid!=self.root_uid or st.st_mode&0o022:raise RuntimeError('UNPROTECTED_OS_CONTAINER')
                if stat.S_ISLNK(st.st_mode) or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
                    raise RuntimeError('OS_CONTAINER_LINK_OR_SPECIAL')
                if name in KEY_NAMES or name.startswith('.ssh') or name.endswith(('.key','.pem')):
                    raise RuntimeError('CREDENTIAL_INDICATOR_PRESENT')
                rows.append((rel,stat.S_IFMT(st.st_mode),stat.S_IMODE(st.st_mode),st.st_uid,st.st_gid,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_ino,st.st_dev))
                if stat.S_ISDIR(st.st_mode):
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=current)
                    try:
                        opened=os.fstat(child)
                        if (opened.st_dev,opened.st_ino)!=(st.st_dev,st.st_ino):raise RuntimeError('METADATA_CHANGED')
                        walk(child,rel,depth+1)
                    finally:os.close(child)
                else:
                    if st.st_nlink!=1:raise RuntimeError('OS_CONTAINER_HARDLINK')
                    if directories_only:raise RuntimeError('SYSTEMD_CREDENTIAL_PAYLOAD_PRESENT')
                    if st.st_size and (name not in PUBLIC_CACHE_NAMES or 'scripts' in Path(rel).parts) and st.st_mode&0o077:
                        raise RuntimeError('EXPOSED_CLOUD_INIT_PAYLOAD')
            after=os.fstat(current)
            if (before.st_mtime_ns,before.st_ctime_ns)!=(after.st_mtime_ns,after.st_ctime_ns):raise RuntimeError('METADATA_CHANGED')
        try:walk(fd,'',0)
        finally:os.close(fd)
        return rows

def inspect_environment_paths(*,root=Path('/'),preparation_uid=None,root_uid=0):
    """Return minimized nonsecret findings; contents/secret hashes never collected.

    Known credential indicators are not a proof that arbitrary files are secret-
    free. The independently reviewed VM provenance/credentials approval remains
    mandatory. This function cannot grant qualification authorization.
    """
    m=Metadata(root,root_uid=root_uid,preparation_uid=preparation_uid);findings=[];cache_digest=None;cache_files=0
    try:
        for path in STRICT_PATHS:
            if m.info(path) is not None:findings.append('CREDENTIAL_OR_HOST_PATH_PRESENT')
        home=m.info('/home/jarvis')
        if home is not None:
            if (not stat.S_ISDIR(home.st_mode) or preparation_uid is None or preparation_uid==0
                or home.st_uid!=preparation_uid or home.st_mode&0o022):
                findings.append('UNVERIFIED_PREPARATION_HOME')
            else:
                for marker in HOME_MARKERS:
                    if m.info('/home/jarvis/'+marker) is not None:findings.append('PREPARATION_HOME_CREDENTIAL_INDICATOR')
        for path in CREDENTIAL_STORES:
            try:
                st=m.info(path)
                if st is not None:
                    if not stat.S_ISDIR(st.st_mode):raise RuntimeError('CREDENTIAL_STORE_TYPE')
                    m.tree(path,directories_only=True)
            except (OSError,RuntimeError) as e:
                findings.append(str(e) if isinstance(e,RuntimeError) else 'METADATA_INSPECTION_UNAVAILABLE')
        # Scan the complete cloud cache, including seeds/previous instances. Only
        # the canonical "instance" alias is allowed; never deserialize obj.pkl.
        cloud=m.info('/var/lib/cloud')
        if cloud is not None:
            if not stat.S_ISDIR(cloud.st_mode):raise RuntimeError('CLOUD_CACHE_TYPE')
            instance=m.info('/var/lib/cloud/instance');target=None
            if instance is not None and stat.S_ISLNK(instance.st_mode):
                if instance.st_uid!=root_uid:raise RuntimeError('CLOUD_INSTANCE_LINK_OWNER')
                link=m.link('/var/lib/cloud/instance')
                relative=link.removeprefix('/var/lib/cloud/')
                if not re.fullmatch(r'instances/[A-Za-z0-9_-][A-Za-z0-9_.-]*',relative):raise RuntimeError('CLOUD_INSTANCE_LINK_TARGET')
                target='/var/lib/cloud/'+relative
                if m.info(target) is None or not stat.S_ISDIR(m.info(target).st_mode):raise RuntimeError('CLOUD_INSTANCE_LINK_TARGET')
            # Temporarily removing/hiding aliases is forbidden. Inventory each
            # direct child separately, recording the sole canonical link itself.
            parent,name=m._parent('/var/lib/cloud')
            try:fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            finally:os.close(parent)
            rows=[]
            try:
                before=os.fstat(fd)
                if before.st_uid!=root_uid or before.st_mode&0o022:raise RuntimeError('UNPROTECTED_OS_CONTAINER')
                names=sorted(os.listdir(fd))
                if len(names)>128:raise RuntimeError('METADATA_TREE_BUDGET')
                for name in names:
                    path='/var/lib/cloud/'+name;st=m.info(path)
                    if st is None:raise RuntimeError('METADATA_CHANGED')
                    if name=='instance' and target:
                        rows.append(('instance-link',target,st.st_uid,st.st_mtime_ns));continue
                    if stat.S_ISDIR(st.st_mode):
                        child=m.tree(path);rows.extend((name+'/'+r[0],*r[1:]) for r in child)
                        rows.append((name,'directory',st.st_uid,stat.S_IMODE(st.st_mode),st.st_mtime_ns))
                    elif stat.S_ISREG(st.st_mode) and st.st_uid==root_uid and not st.st_mode&0o022 and st.st_nlink==1:
                        if name in KEY_NAMES or name.endswith(('.key','.pem')):raise RuntimeError('CREDENTIAL_INDICATOR_PRESENT')
                        if st.st_size and name not in PUBLIC_CACHE_NAMES and st.st_mode&0o077:raise RuntimeError('EXPOSED_CLOUD_INIT_PAYLOAD')
                        rows.append((name,stat.S_IFREG,stat.S_IMODE(st.st_mode),st.st_uid,st.st_gid,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_ino,st.st_dev))
                    else:raise RuntimeError('OS_CONTAINER_LINK_OR_SPECIAL')
                    if len(rows)>8192:raise RuntimeError('METADATA_TREE_BUDGET')
                after=os.fstat(fd)
                if (before.st_mtime_ns,before.st_ctime_ns)!=(after.st_mtime_ns,after.st_ctime_ns):raise RuntimeError('METADATA_CHANGED')
            finally:os.close(fd)
            if len(rows)>8192:raise RuntimeError('METADATA_TREE_BUDGET')
            cache_files=sum(len(r)>1 and r[1]==stat.S_IFREG for r in rows)
            if cache_files:cache_digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
    except (OSError,RuntimeError) as e:
        findings.append(str(e) if isinstance(e,RuntimeError) else 'METADATA_INSPECTION_UNAVAILABLE')
    return {'findings':sorted(set(findings)),'cloud_cache_files':cache_files,'cloud_cache_metadata_sha256':cache_digest}

def require_paths(report,approval):
    if report['findings']:raise RuntimeError(report['findings'][0])
    if report['cloud_cache_metadata_sha256'] is not None:
        expected={'provenance':'FRESH_DISPOSABLE_IMAGE_NO_IMPORTED_CREDENTIALS',
                  'metadata_sha256':report['cloud_cache_metadata_sha256']}
        if approval.get('cloud_cache_review')!=expected:raise RuntimeError('CLOUD_CACHE_REVIEW_REQUIRED')

"""Proposed human-only metadata report. No regular file contents opened.

Never treats a partial scan as empty or as credential-free. No qualification,
cleanup, chmod, cloud-init commands, network, or approval-marker creation.
"""
import json,os,re,stat
from pathlib import Path
PUBLIC={'boot-finished','datasource','instance-id','previous-instance-id','result.json','status.json','set-hostname','previous-datasource'}

def open_directory(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('PATH')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=child
        return fd
    except BaseException:os.close(fd);raise

def inventory(path,*,max_entries=8192,max_depth=16):
    result={'complete':True,'entries':0,'regular_files':0,'directories':0,'symlinks':0,'special_files':0,
      'nonempty_regular_files':0,'potential_exposure_rule_matches':0,'key_or_auth_name_indicators':0,
      'hardlinked_regular_files':0,'group_other_writable':0,'nonroot_owned':0,'directory_acl_or_capability_metadata':0,
      'mount_device_changes':0,'canonical_instance_alias_syntax':0,'errors':[],'root':None}
    def error(code):
        result['complete']=False
        if code not in result['errors']:result['errors'].append(code)
    try:fd=open_directory(path)
    except FileNotFoundError:
        result['status']='ABSENT';return result
    except OSError:
        result['status']='UNKNOWN_UNSAFE_OR_UNREADABLE';error('DIRECTORY_OPEN_REFUSED');return result
    try:
        top=os.fstat(fd);result['root']={'uid':top.st_uid,'gid':top.st_gid,'mode':oct(stat.S_IMODE(top.st_mode))}
        def walk(directory,relative,depth):
            if depth>max_depth:error('DEPTH_LIMIT');return
            before=os.fstat(directory)
            try:
                attrs=os.listxattr(directory)
                if any(x.startswith('system.posix_acl_') or x=='security.capability' for x in attrs):result['directory_acl_or_capability_metadata']+=1
                # scandir(fd) is metadata-only and stops without materializing an unbounded list.
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if result['entries']>=max_entries:error('ENTRY_LIMIT');return
                        result['entries']+=1
                        try:st=os.stat(entry.name,dir_fd=directory,follow_symlinks=False)
                        except OSError:error('ENTRY_STAT_UNAVAILABLE');continue
                        rel=relative+'/'+entry.name if relative else entry.name
                        if st.st_uid!=0:result['nonroot_owned']+=1
                        if st.st_mode&0o022 and not stat.S_ISLNK(st.st_mode):result['group_other_writable']+=1
                        if st.st_dev!=before.st_dev:result['mount_device_changes']+=1
                        if entry.name.startswith(('id_rsa','id_ed25519','id_ecdsa','id_dsa')) or entry.name.endswith(('.key','.pem')) or entry.name in ('authorized_keys','authorized_keys2','config','known_hosts','environment','rc'):
                            result['key_or_auth_name_indicators']+=1
                        if stat.S_ISREG(st.st_mode):
                            result['regular_files']+=1
                            result['nonempty_regular_files']+=bool(st.st_size)
                            result['hardlinked_regular_files']+=st.st_nlink!=1
                            result['potential_exposure_rule_matches']+=bool(st.st_size and (entry.name not in PUBLIC or 'scripts' in Path(rel).parts) and st.st_mode&0o077)
                        elif stat.S_ISLNK(st.st_mode):
                            result['symlinks']+=1
                            if rel=='instance':
                                link=os.readlink(entry.name,dir_fd=directory).removeprefix('/var/lib/cloud/')
                                if re.fullmatch(r'instances/[A-Za-z0-9_-][A-Za-z0-9_.-]*',link):result['canonical_instance_alias_syntax']+=1
                        elif stat.S_ISDIR(st.st_mode):
                            result['directories']+=1
                            try:child=os.open(entry.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
                            except OSError:error('CHILD_DIRECTORY_UNAVAILABLE');continue
                            try:
                                seen=os.fstat(child)
                                if (seen.st_dev,seen.st_ino)!=(st.st_dev,st.st_ino):error('DIRECTORY_CHANGED')
                                else:walk(child,rel,depth+1)
                            finally:os.close(child)
                        else:result['special_files']+=1
            except OSError:error('DIRECTORY_METADATA_UNAVAILABLE')
            after=os.fstat(directory)
            if (before.st_mtime_ns,before.st_ctime_ns)!=(after.st_mtime_ns,after.st_ctime_ns):error('DIRECTORY_CHANGED')
        walk(fd,'',0)
    finally:os.close(fd)
    result['status']='COMPLETE_METADATA_ONLY' if result['complete'] else 'PARTIAL_UNKNOWN'
    result['empty_directory']=result['complete'] and result['entries']==0
    result['credential_free']='NOT_ESTABLISHED_BY_METADATA'
    return result

def report():
    return {label:inventory(path) for label,path in (
      ('root_ssh','/root/.ssh'),('preparation_ssh','/home/jarvis/.ssh'),('cloud_cache','/var/lib/cloud'),
      ('systemd_credentials','/run/credentials'),('etc_credstore','/etc/credstore'),
      ('etc_credstore_encrypted','/etc/credstore.encrypted'),('run_credstore','/run/credstore'),
      ('run_credstore_encrypted','/run/credstore.encrypted'),('usr_credstore','/usr/lib/credstore'),
      ('usr_credstore_encrypted','/usr/lib/credstore.encrypted'))}

if __name__=='__main__':
    if os.geteuid()!=0 or os.uname().nodename!='jarvis-security':raise SystemExit('HUMAN_VM163_METADATA_REVIEW_ONLY')
    print(json.dumps({'qualification':'NOT_RUN','inventory':report()},sort_keys=True,indent=2))

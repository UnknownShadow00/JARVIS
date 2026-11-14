"""Inert source renderer. Never executes the returned argv."""
from pathlib import Path
import ast
import packet as p
from common import need

def library():
    root=Path(__file__).parent
    common=(root/'common.py').read_text()
    bounded=(root/'bounded.py').read_text()
    bounded='\n'.join(x for x in bounded.splitlines() if not x.startswith('from common import '))
    return common+'\n'+bounded+'\n'

LIMITS='''import resource
resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
resource.setrlimit(resource.RLIMIT_CPU,(3,3))
resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
'''

def protected_read(path, limit, expected_sha, compressed=False):
    need(type(path) is str and path.startswith('/'),'mandatory approved path')
    body=LIMITS+library()+'''\nimport sys,json
end=time.monotonic()+8
raw=read_protected(sys.argv[1],int(sys.argv[2]),end,sys.argv[3])
'''
    body+=('raw=gunzip_bounded(raw,8388608,end)\n' if compressed else '')
    body+="sys.stdout.buffer.write(raw)\n"
    return ['/usr/bin/python3','-I','-B','-S','-c',body,path,str(limit),expected_sha]

# Exclusivity/custody code is retained from R1 after independent review; executed only
# by a future separately authorized operator through the bounded command recorder.
INSTALL_CODE = "import hashlib,json,os,stat,sys\nPIN='a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa'\ndef check(fd,directory):\n s=os.fstat(fd)\n if s.st_uid!=0 or s.st_gid!=0 or s.st_mode&0o022:raise ValueError('root custody')\n if directory and not stat.S_ISDIR(s.st_mode):raise ValueError('directory required')\n if directory and 'system.posix_acl_default' in os.listxattr(fd):raise ValueError('default ACL blocks')\n return s\ndef descend(parts):\n fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)\n check(fd,True)\n try:\n  for part in parts:\n   new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)\n   os.close(fd);fd=new;check(fd,True)\n  return fd\n except BaseException:os.close(fd);raise\nif os.getuid()!=0 or os.geteuid()!=0 or os.getegid()!=0:raise ValueError('existing authorized administrator required')\nsource=sys.argv[1]\nif not source.startswith('/') or any(p in ('','.', '..') for p in source.split('/')[1:]):raise ValueError('absolute canonical staged path required')\nparts=source.split('/')[1:];parent=descend(parts[:-1])\ntry:\n fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)\n try:\n  s=check(fd,False)\n  if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>16384:raise ValueError('source type/size/link')\n  raw=os.read(fd,16385);after=os.fstat(fd)\n  if (s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('source race')\n  if len(raw)!=s.st_size or hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('source hash')\n finally:os.close(fd)\nfinally:os.close(parent)\nopt=descend(['opt'])\ntry:\n # Exclusive mkdir refuses any existing file, directory or symlink. Never adopt or repair it.\n os.mkdir('jarvis-vm164-r3-stage2',0o755,dir_fd=opt)\n d=os.open('jarvis-vm164-r3-stage2',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=opt)\n try:\n  check(d,True);os.fchmod(d,0o755)\n  f=os.open('canary.py',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400,dir_fd=d)\n  try:\n   view=memoryview(raw)\n   while view:\n    n=os.write(f,view)\n    if n<=0:raise OSError('short write')\n    view=view[n:]\n   os.fchmod(f,0o444);os.fsync(f);s=os.fstat(f)\n   if s.st_uid!=0 or s.st_gid!=0 or s.st_nlink!=1:raise ValueError('created custody')\n  finally:os.close(f)\n  os.fsync(d)\n finally:os.close(d)\n os.fsync(opt)\nfinally:os.close(opt)\nprint(json.dumps({'created':'/opt/jarvis-vm164-r3-stage2/canary.py','sha256':PIN,'bytes':len(raw)}))\n# Any failure leaves partial artifacts intact for evidence and blocks all activation.\n"

def install(source, session, sample):
    p.window(session,sample)
    need(type(source) is str and source.startswith('/'),'approved staged callback source')
    need(INSTALL_CODE is not None,'installer source missing')
    # The mandatory recorder enforces both clocks before starting this command.
    return ['/usr/bin/python3','-I','-B','-S','-c',LIMITS+INSTALL_CODE,source]

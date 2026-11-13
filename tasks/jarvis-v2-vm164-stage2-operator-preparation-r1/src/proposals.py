"""Literal future Python command bodies; importing this file performs no host work."""
INSPECT_CODE = r'''import hashlib,json,os,stat,sys,time,platform
from pathlib import Path
paths=json.loads(sys.argv[1])
rows=[]
for name in paths:
 p=Path(name)
 row={'path':name}
 try:
  q=p.resolve(strict=True)
  chain=[]
  # Retain the original symlink plus resolved ancestors, including each lexical ancestor.
  for x in dict.fromkeys([Path('/'),*reversed(p.parents[:-1]),p,*reversed(q.parents[:-1]),q]):
   s=x.lstat()
   chain.append({'path':str(x),'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),
    'symlink':os.readlink(x) if stat.S_ISLNK(s.st_mode) else None,'dev':s.st_dev,'ino':s.st_ino})
  row.update(resolved=str(q),chain=chain)
  s=q.stat()
  if not stat.S_ISREG(s.st_mode) or s.st_size>33554432: raise ValueError('not bounded regular binary')
  fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   a=os.fstat(fd);data=b''
   while len(data)<=33554432:
    chunk=os.read(fd,65536)
    if not chunk:break
    data+=chunk
   z=os.fstat(fd)
   if (a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('changed while hashing')
   if len(data)!=a.st_size:raise ValueError('size')
   row['sha256']=hashlib.sha256(data).hexdigest()
   row['file_capability_hex']=os.getxattr(q,'security.capability').hex() if 'security.capability' in os.listxattr(q) else None
  finally:os.close(fd)
 except (OSError,ValueError) as e:row['error']=type(e).__name__+':'+str(e)
 rows.append(row)
print(json.dumps({'node':Path('/etc/hostname').read_text().strip(),'uname':list(os.uname()),
 'python':platform.python_version(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'binaries':rows}))
'''
METADATA_CODE = r'''import json,os,stat,sys
from pathlib import Path
rows=[]
for name in json.loads(sys.argv[1]):
 p=Path(name);row={'path':name}
 try:
  s=p.lstat();row.update(uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),
   dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,size=s.st_size,symlink=stat.S_ISLNK(s.st_mode))
 except OSError as e:row['error']=type(e).__name__
 rows.append(row)
print(json.dumps(rows))
'''
PROCESS_CODE = r'''import json
from pathlib import Path
rows=[];errors=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  fields=dict(line.split(':',1) for line in (p/'status').read_text().splitlines() if ':' in line)
  if '65534' in fields.get('Uid','').split():
   rows.append({'pid':int(p.name),**{k:fields.get(k) for k in ('Name','Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs')}})
 except FileNotFoundError:pass
 except OSError as e:errors.append({'pid':int(p.name),'error':type(e).__name__})
print(json.dumps({'nobody_processes':rows,'errors':errors}))
'''
INSTALL_CODE = r'''import hashlib,json,os,stat,sys
PIN='a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa'
def check(fd,directory):
 s=os.fstat(fd)
 if s.st_uid!=0 or s.st_gid!=0 or s.st_mode&0o022:raise ValueError('root custody')
 if directory and not stat.S_ISDIR(s.st_mode):raise ValueError('directory required')
 if directory and 'system.posix_acl_default' in os.listxattr(fd):raise ValueError('default ACL blocks')
 return s
def descend(parts):
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 check(fd,True)
 try:
  for part in parts:
   new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
   os.close(fd);fd=new;check(fd,True)
  return fd
 except BaseException:os.close(fd);raise
if os.getuid()!=0 or os.geteuid()!=0 or os.getegid()!=0:raise ValueError('existing authorized administrator required')
source=sys.argv[1]
if not source.startswith('/') or any(p in ('','.', '..') for p in source.split('/')[1:]):raise ValueError('absolute canonical staged path required')
parts=source.split('/')[1:];parent=descend(parts[:-1])
try:
 fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
 try:
  s=check(fd,False)
  if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>16384:raise ValueError('source type/size/link')
  raw=os.read(fd,16385);after=os.fstat(fd)
  if (s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('source race')
  if len(raw)!=s.st_size or hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('source hash')
 finally:os.close(fd)
finally:os.close(parent)
opt=descend(['opt'])
try:
 # Exclusive mkdir refuses any existing file, directory or symlink. Never adopt or repair it.
 os.mkdir('jarvis-vm164-r3-stage2',0o755,dir_fd=opt)
 d=os.open('jarvis-vm164-r3-stage2',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=opt)
 try:
  check(d,True);os.fchmod(d,0o755)
  f=os.open('canary.py',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400,dir_fd=d)
  try:
   view=memoryview(raw)
   while view:
    n=os.write(f,view)
    if n<=0:raise OSError('short write')
    view=view[n:]
   os.fchmod(f,0o444);os.fsync(f);s=os.fstat(f)
   if s.st_uid!=0 or s.st_gid!=0 or s.st_nlink!=1:raise ValueError('created custody')
  finally:os.close(f)
  os.fsync(d)
 finally:os.close(d)
 os.fsync(opt)
finally:os.close(opt)
print(json.dumps({'created':'/opt/jarvis-vm164-r3-stage2/canary.py','sha256':PIN,'bytes':len(raw)}))
# Any failure leaves partial artifacts intact for evidence and blocks all activation.
'''
VERIFY_PUBLIC_CODE = r'''import hashlib,json,os,stat
from pathlib import Path
p=Path('/opt/jarvis-vm164-r3-stage2/canary.py');rows=[]
for q in (Path('/'),Path('/opt'),p.parent,p):
 s=q.lstat()
 if stat.S_ISLNK(s.st_mode) or s.st_uid!=0 or s.st_gid!=0 or s.st_mode&0o022:raise ValueError('custody')
 rows.append({'path':str(q),'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'dev':s.st_dev,'ino':s.st_ino})
s=p.stat()
if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>16384 or stat.S_IMODE(s.st_mode)!=0o444:raise ValueError('leaf')
if stat.S_IMODE(p.parent.stat().st_mode)!=0o755:raise ValueError('directory mode')
h=hashlib.sha256(p.read_bytes()).hexdigest()
if h!='a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa':raise ValueError('pin')
print(json.dumps({'paths':rows,'sha256':h,'bytes':s.st_size}))
'''
CGROUP_CODE = r'''import json,re,sys
from pathlib import Path
name=sys.argv[1]
if not re.fullmatch(r'jarvis-vm164-r3-stage2-[0-9a-f]{32}-(success|exit7|missingexec|missingdep|timeout|late|inactive|failedtimer|collision|cancel|rearm-a|rearm-b)',name):raise ValueError('exact owned namespace required')
p=Path('/sys/fs/cgroup/system.slice')/(name+'.service')
row={'path':str(p),'name':name}
try:
 row['events']=(p/'cgroup.events').read_text()
 row['procs']=(p/'cgroup.procs').read_text()
except FileNotFoundError:row['absent_or_partial']=True
print(json.dumps(row))
'''

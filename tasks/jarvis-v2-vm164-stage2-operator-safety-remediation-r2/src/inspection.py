"""Future read-only command bodies. No host reads occur on import."""
import json
from common import need
from proposals import library,LIMITS

def command(body,*args):return ['/usr/bin/python3','-I','-B','-S','-c',LIMITS+library()+'\n'+body,*args]

HASH_BODY='''import json,sys
path=sys.argv[1]
fd=open_protected(path)
try:
 raw=read_fd(fd,33554432,time.monotonic()+8)
 s=os.fstat(fd)
 print(json.dumps(dict(path=path,sha256=sha(raw),bytes=len(raw),uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink)))
finally:os.close(fd)
'''
METADATA_BODY='''import json,sys
path=sys.argv[1]
need(path.startswith('/') and all(x not in ('','.','..') for x in path.split('/')[1:]),'canonical path')
# Local-mounted path prerequisite, no arbitrary credential content read.
parts=path.split('/')[1:];fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
 for part in parts[:-1]:
  s=os.fstat(fd);need(s.st_uid==s.st_gid==0 and not s.st_mode&0o022,'ancestor custody')
  new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=new
 try:
  s=os.stat(parts[-1],dir_fd=fd,follow_symlinks=False)
  print(json.dumps(dict(path=path,absent=False,uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),type=stat.S_IFMT(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,size=s.st_size,symlink=os.readlink(parts[-1],dir_fd=fd) if stat.S_ISLNK(s.st_mode) else None)))
 except FileNotFoundError:print(json.dumps(dict(path=path,absent=True,errno='ENOENT')))
finally:os.close(fd)
'''
PROCESS_BODY='''import json
end=time.monotonic()+8;rows=[];count=0
with os.scandir('/proc') as entries:
 for entry in entries:
  tick(end)
  if not entry.name.isdecimal():continue
  count+=1;need(count<=8192,'process scan limit')
  try:
   fd=os.open('/proc/'+entry.name+'/status',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
   with os.fdopen(fd,'rb') as stream:raw=read_stream(stream,65536,end)
  except FileNotFoundError:continue
  fields={}
  for line in raw.decode('utf-8').splitlines():
   if ':' in line:
    k,v=line.split(':',1);need(k not in fields,'duplicate proc field');fields[k]=v.strip()
  need(all(k in fields for k in ('Uid','Gid','Groups','Name')),'incomplete proc fields')
  if '65534' in fields['Uid'].split():rows.append(dict(pid=int(entry.name),**{k:fields[k] for k in ('Name','Uid','Gid','Groups')}))
print(json.dumps(dict(nobody_processes=rows,complete=True)))
'''
CGROUP_BODY='''import json,re,sys
name=sys.argv[1]
need(re.fullmatch(r'jarvis-vm164-r3-stage2-[0-9a-f]{32}-(success|exit7|missingexec|missingdep|timeout|late|inactive|failedtimer|collision|cancel|rearm-a|rearm-b)',name),'namespace')
path='/sys/fs/cgroup/system.slice/'+name+'.service';end=time.monotonic()+3
try:
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
except FileNotFoundError:
 print(json.dumps(dict(path=path,absent=True,complete=False,requires_independent_absence_corroboration=True)))
else:
 try:
  values={}
  for leaf in ('cgroup.events','cgroup.procs'):
   f=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
   with os.fdopen(f,'rb') as stream:values[leaf]=read_stream(stream,65536,end).decode('ascii')
  print(json.dumps(dict(path=path,absent=False,raw=values,complete=True)))
 finally:os.close(fd)
'''

def hash_command(path):return command(HASH_BODY,path)
def metadata_command(path):return command(METADATA_BODY,path)
def process_command():return command(PROCESS_BODY)
def cgroup_command(name):return command(CGROUP_BODY,name)

IDENTITY_BODY="""import json,sys
raw=read_protected('/etc/hostname',4096,time.monotonic()+8)
print(json.dumps(dict(node=raw.decode('ascii').strip(),uname=list(os.uname()),python=sys.version,uid=os.getuid(),euid=os.geteuid())))
"""
def identity_command():return command(IDENTITY_BODY)

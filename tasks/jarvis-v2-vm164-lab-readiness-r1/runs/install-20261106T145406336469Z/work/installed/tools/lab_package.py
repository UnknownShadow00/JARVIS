#!/usr/bin/env python3
"""Bounded offline VM164 preparation; protected install requires independent root approval.

No networking, account/credential creation, service control, disk/mount commands,
provider calls, enrollment or runtime database operations exist in this tool.
"""
import argparse,base64,csv,ctypes,datetime,hashlib,io,json,os,platform,re,sqlite3,ssl,stat,sys,tarfile,zipfile
from pathlib import Path
REVISION='e9b4734740070b9e7c990735e43801e592c114c6'
VM_UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL='g6k164-12821f6b54a2'
DESTINATION=Path('/opt/jarvis-v2-lab/releases/rc1-345626bddd36028e')
MAX_ARCHIVE=128*1024**2;MAX_TOTAL=384*1024**2;MAX_FILE=64*1024**2;MAX_FILES=16000
class Refusal(Exception):pass
def require(ok,code):
 if not ok:raise Refusal(code)
def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
def pairs(rows):
 d={}
 for k,v in rows:require(k not in d,'duplicate_json_key');d[k]=v
 return d
def decode(raw):return json.loads(raw,object_pairs_hook=pairs)
def safe_name(n):
 require(type(n) is str and 0<len(n)<=240 and '\\' not in n and '\x00' not in n,'unsafe_member_name')
 require(not n.startswith('/') and all(x not in ('','..','.') for x in n.split('/')),'unsafe_member_name')
 return n
def regular(path,limit=MAX_ARCHIVE):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
 try:
  a=os.fstat(fd);require(stat.S_ISREG(a.st_mode) and a.st_nlink==1 and a.st_size<=limit,'unsafe_input_file')
  chunks=[];total=0
  while True:
   b=os.read(fd,min(1024**2,limit+1-total))
   if not b:break
   total+=len(b);require(total<=limit,'input_bound');chunks.append(b)
  z=os.fstat(fd);require((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'input_changed')
  return b''.join(chunks)
 finally:os.close(fd)
def verify_tar(raw):
 require(len(raw)<=MAX_ARCHIVE,'archive_size_bound');files={};total=0
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
  for m in t:
   safe_name(m.name);require(m.isfile() and not m.pax_headers and m.name not in files,'unsafe_archive_type_or_duplicate')
   require(0<=m.size<=MAX_FILE and m.uid==m.gid==m.mtime==0 and m.mode==0o644,'unsafe_archive_metadata')
   total+=m.size;require(total<=MAX_TOTAL and len(files)<MAX_FILES,'archive_expansion_bound')
   b=t.extractfile(m).read(MAX_FILE+1);require(len(b)==m.size,'archive_size_mismatch');files[m.name]=b
 return files
def wheel_payload(raw,expected_name,expected_version):
 result={};total=0
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  records=[n for n in z.namelist() if n.endswith('.dist-info/RECORD')]
  require(len(records)==1,'wheel_record_count');rec=records[0];rows={}
  for row in csv.reader(io.StringIO(z.read(rec).decode())):
   require(len(row)==3 and row[0] not in rows,'wheel_record_duplicate');rows[row[0]]=row[1:]
  names=set()
  for m in z.infolist():
   if m.is_dir():continue
   n=safe_name(m.filename);require(n not in names and n in rows,'wheel_unrecorded_or_duplicate');names.add(n)
   mode=m.external_attr>>16;require(not stat.S_ISLNK(mode) and not mode&0o6000,'wheel_unsafe_mode')
   require('.data' not in n.split('/')[0] and not n.endswith(('.pth','.pyc')),'wheel_active_or_relocated_content')
   total+=m.file_size;require(m.file_size<=MAX_FILE and total<=128*1024**2,'wheel_expansion_bound')
   b=z.read(m);h,size=rows[n]
   if n==rec:require(h==size=='','wheel_record_self')
   else:
    require(h.startswith('sha256=') and size==str(len(b)),'wheel_record_algorithm_or_size')
    require(base64.urlsafe_b64encode(hashlib.sha256(b).digest()).rstrip(b'=').decode()==h[7:],'wheel_record_hash')
   result[n]=b
  require(names==set(rows),'wheel_missing_record_payload')
  from email.parser import BytesParser
  meta=BytesParser().parsebytes(result[rec.rsplit('/',1)[0]+'/METADATA'])
  canon=lambda n:re.sub('[-_.]+','-',n).lower()
  require(canon(meta['Name'])==canon(expected_name) and meta['Version']==expected_version,'wheel_identity')
 return result

def load_bundle(path,expected):
 require(re.fullmatch('[a-f0-9]{64}',expected or '') is not None,'expected_archive_pin_required')
 raw=regular(path);require(digest(raw)==expected,'bundle_hash_mismatch');files=verify_tar(raw)
 require('MANIFEST.json' in files,'bundle_manifest_missing');m=decode(files.pop('MANIFEST.json'))
 require(m['format']=='jarvis-vm164-offline-v1' and m['source_git_revision']==REVISION and m['real_execution_enabled'] is False,'wrong_release')
 require(set(files)==set(m['files']),'bundle_inventory_mismatch')
 for n,b in files.items():require(digest(b)==m['files'][n],'bundle_member_hash')
 source={n[7:]:b for n,b in files.items() if n.startswith('source/')}
 require({n:digest(b) for n,b in source.items()}==m['source_sha256'],'source_manifest_mismatch')
 require(len(source)==315 and len(m['dependencies'])==31,'release_inventory_count')
 installed={n:b for n,b in files.items() if n.startswith(('source/','tools/','serial-candidate/')) or n in ('SBOM.cdx.json','RUNTIME-PREREQUISITES.json')}
 for d in m['dependencies']:
  raw=files['wheels/'+d['filename']];require(digest(raw)==d['sha256'],'wheel_hash_mismatch')
  for n,b in wheel_payload(raw,d['name'],d['version']).items():
   key='python/'+n;require(key not in installed,'dependency_path_collision');installed[key]=b
 installed['INSTALL-MANIFEST.json']=encoded({'format':'jarvis-inert-install-v1','source_git_revision':REVISION,'versions':{d['name'].lower().replace('_','-'):d['version'] for d in m['dependencies']},'files':{n:digest(b) for n,b in sorted(installed.items())},'services_started':False,'runtime_state_created':False})
 require(sum(map(len,installed.values()))<=MAX_TOTAL and len(installed)<=MAX_FILES,'installed_size_bound')
 return m,installed

def protected_chain(path,*,owner=0,directory=False):
 path=Path(path);require(path.is_absolute() and '..' not in path.parts,'absolute_protected_path_required')
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  for i,part in enumerate(path.parts[1:]):
   final=i==len(path.parts[1:])-1
   flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK
   if not final or directory:flags|=os.O_DIRECTORY
   nxt=os.open(part,flags,dir_fd=fd);os.close(fd);fd=nxt
   st=os.fstat(fd)
   require(st.st_uid in (0,owner) and not st.st_mode&0o022 and not st.st_mode&0o6000,'unprotected_ancestry_or_owner')
   require(stat.S_ISDIR(st.st_mode) if not final or directory else stat.S_ISREG(st.st_mode) and st.st_nlink==1,'protected_path_type')
  return fd
 except BaseException:os.close(fd);raise

def publish(parent,name,files,*,owner,fail_after=None):
 """Retain validated parent descriptors throughout; exclusive writes, no cleanup."""
 safe_name(name);require('/' not in name,'single_destination_name')
 pfd=protected_chain(parent,owner=owner,directory=True)
 try:
  os.mkdir(name,0o755,dir_fd=pfd)
  rootfd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=pfd)
  try:
   count=0
   for n,b in sorted(files.items()):
    safe_name(n);parts=n.split('/');fd=os.dup(rootfd)
    try:
     for part in parts[:-1]:
      try:os.mkdir(part,0o755,dir_fd=fd)
      except FileExistsError:pass
      nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
      st=os.fstat(nxt);require(st.st_uid==owner and not st.st_mode&0o022,'unsafe_install_directory');os.close(fd);fd=nxt
     out=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644,dir_fd=fd)
     with os.fdopen(out,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
     os.fsync(fd);count+=1
     if fail_after is not None and count==fail_after:raise Refusal('injected_interruption_preserved')
    finally:os.close(fd)
   # Reopen every directory bottom-up to persist each directory entry.
   dirs={str(Path(n).parent) for n in files}
   dirs|={str(p) for n in files for p in Path(n).parents if str(p)!='.'}
   for d in sorted(dirs,key=lambda x:x.count('/'),reverse=True):
    if d=='.':continue
    fd=os.dup(rootfd)
    try:
     for part in d.split('/'):
      nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
     os.fsync(fd)
    finally:os.close(fd)
   os.fsync(rootfd);os.fsync(pfd)
  finally:os.close(rootfd)
 finally:os.close(pfd)

def validate_installed(root,expected_files,*,owner=0):
 fd=protected_chain(root,owner=owner,directory=True)
 try:
  # Stable top directory identity is rechecked after descriptor-relative file reads.
  before=os.fstat(fd);actual=set()
  for p in Path(root).rglob('*'):
   require(not p.is_symlink(),'installed_symlink')
   st=p.stat();require(st.st_uid==owner and not st.st_mode&0o022,'installed_owner_or_mode')
   if p.is_file():actual.add(str(p.relative_to(root)))
  require(actual==set(expected_files),'installed_inventory_mismatch')
  for n,h in expected_files.items():
   parts=n.split('/');current=os.dup(fd)
   try:
    for part in parts[:-1]:
     nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=current);os.close(current);current=nxt
    f=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=current)
    try:
     st=os.fstat(f);require(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size<=MAX_FILE,'installed_file_type')
     data=bytearray()
     while True:
      b=os.read(f,1024**2)
      if not b:break
      data.extend(b);require(len(data)<=MAX_FILE,'installed_file_bound')
     require(digest(data)==h,'installed_file_hash')
    finally:os.close(f)
   finally:os.close(current)
  again=protected_chain(root,owner=owner,directory=True)
  try:require((os.fstat(again).st_dev,os.fstat(again).st_ino)==(before.st_dev,before.st_ino),'installed_root_replaced')
  finally:os.close(again)
 finally:os.close(fd)

def quarantine(parent,name,expected,*,owner,tag):
 """No deletion/overwrite. For a never-activated release, preserve it beside itself."""
 require(re.fullmatch('[0-9]{8}T[0-9]{6}Z',tag) is not None,'quarantine_tag')
 validate_installed(Path(parent)/name,expected,owner=owner)
 fd=protected_chain(parent,owner=owner,directory=True)
 try:
  target=name+'.quarantine-'+tag
  # Reserve a new directory. Rename into its exclusive empty payload slot.
  os.mkdir(target,0o755,dir_fd=fd)
  qfd=os.open(target,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
  try:os.rename(name,'payload',src_dir_fd=fd,dst_dir_fd=qfd);os.fsync(qfd);os.fsync(fd)
  finally:os.close(qfd)
 finally:os.close(fd)
 return target+'/payload'

def probe():
 def small(n):return Path(n).read_text()[:1024].strip()
 osinfo={}
 for line in Path('/etc/os-release').read_text().splitlines():
  if '=' in line:
   k,v=line.split('=',1)
   if k in ('ID','VERSION_ID'):osinfo[k]=v.strip('"')
 lines=Path('/proc/self/mountinfo').read_text().splitlines();mounts=[x.split() for x in lines]
 root=next(x for x in mounts if x[4]=='/');sep=root.index('-');device=root[2]
 fsuuids=[]
 if Path('/dev/disk/by-uuid').is_dir():
  for x in Path('/dev/disk/by-uuid').iterdir():
   try:
    st=x.stat()
    if stat.S_ISBLK(st.st_mode) and f'{os.major(st.st_rdev)}:{os.minor(st.st_rdev)}'==device:fsuuids.append(x.name)
   except OSError:pass
 mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if k in ('MemTotal','MemAvailable')}
 disks=sorted(x.name for x in Path('/sys/block').iterdir() if re.fullmatch(r'(sd[a-z]+|vd[a-z]+|nvme\d+n\d+)',x.name))
 executable=Path(sys.executable).resolve();disk=Path('/sys/block/sda')
 runtime_paths={str(executable)}
 for line in Path('/proc/self/maps').read_text().splitlines():
  parts=line.split(maxsplit=5)
  if len(parts)==6 and parts[5].startswith(('/usr/lib/','/lib/')):
   require(not parts[5].endswith(' (deleted)'),'runtime_mapping_deleted')
   runtime_paths.add(str(Path(parts[5]).resolve()))
 native={}
 for name in sorted(runtime_paths):
  fd=protected_chain(name);os.close(fd);native[name]=digest(regular(name))
 return {'format':'vm164-readonly-probe-v1','observed_at_utc':datetime.datetime.now(datetime.UTC).isoformat(),'os':osinfo,'architecture':platform.machine(),'python_version':platform.python_version(),'python_sha256':digest(regular(executable)),'native_runtime_files':native,'bwrap_sha256':digest(regular('/usr/bin/bwrap')) if Path('/usr/bin/bwrap').is_file() else None,'sqlite_version':sqlite3.sqlite_version,'openssl_version':ssl.OPENSSL_VERSION,'vm_uuid':small('/sys/class/dmi/id/product_uuid').lower(),'machine_id':small('/etc/machine-id'),'boot_id':small('/proc/sys/kernel/random/boot_id'),'disk_serial':small(disk/'device/serial') if disk.exists() else None,'disk_bytes':int(small(disk/'size'))*512 if disk.exists() else None,'root_filesystem':root[sep+1],'root_device':device,'root_filesystem_uuids':sorted(fsuuids),'network_interfaces':sorted(x.name for x in Path('/sys/class/net').iterdir()),'block_disks':disks,'optical_media_present':any(x.name.startswith('sr') and (x/'size').exists() and int(small(x/'size'))>0 for x in Path('/sys/block').iterdir()),'shared_or_slave_mounts':sum(any(y.startswith(('shared:','master:','propagate_from:')) for y in x[6:x.index('-')]) for x in mounts),'external_filesystems':sum(x[x.index('-')+1] in ('nfs','nfs4','cifs','9p','virtiofs','fuse.virtiofs') for x in mounts),'cpu_count':os.cpu_count(),'memory':mem,'free_bytes':os.statvfs('/opt').f_bavail*os.statvfs('/opt').f_frsize,'uid':os.getuid(),'euid':os.geteuid(),'guest_report_is_independent_attestation':False}

def check_target(facts,binding):
 expected={'vm_uuid':VM_UUID,'disk_serial':SERIAL,'disk_bytes':64*1024**3,'architecture':'x86_64','python_version':'3.14.4','root_filesystem':'ext4','network_interfaces':['lo'],'block_disks':['sda'],'optical_media_present':False,'shared_or_slave_mounts':0,'external_filesystems':0,'sqlite_version':'3.46.1','openssl_version':'OpenSSL 3.5.5 27 Jan 2026'}
 for k,v in expected.items():require(facts.get(k)==v,'target_'+k)
 require(facts['os']=={'ID':'ubuntu','VERSION_ID':'26.04'},'target_os')
 for k in ('machine_id','boot_id','root_device','root_filesystem_uuids','python_sha256','native_runtime_files','bwrap_sha256'):
  require(binding.get(k) not in (None,'',[]) and binding[k]==facts.get(k),'unbound_or_changed_'+k)
 require(type(binding['native_runtime_files']) is dict and len(binding['native_runtime_files'])>=3 and all(re.fullmatch('[a-f0-9]{64}',v) for v in binding['native_runtime_files'].values()),'native_runtime_hash_bindings')
 require(re.fullmatch('[0-9a-f]{32}',binding['machine_id']) is not None,'machine_id_format')
 require(len(binding['root_filesystem_uuids'])==1,'root_filesystem_uuid_count')
 require(facts['cpu_count']>=4 and facts['memory']['MemTotal']>=5*1024**3 and facts['memory']['MemAvailable']>=3*1024**3 and facts['free_bytes']>=20*1024**3,'target_resource_headroom')

def approval(path,bundle_sha,facts):
 fd=protected_chain(path)
 try:require(stat.S_IMODE(os.fstat(fd).st_mode)==0o600,'approval_mode')
 finally:os.close(fd)
 return validate_approval(decode(regular(path,65536)),bundle_sha,facts)

def validate_approval(a,bundle_sha,facts):
 require(set(a)=={'format','purpose','operator_reference','expires_at_utc','bundle_sha256','source_git_revision','destination','target'},'approval_schema')
 require(a['format']=='vm164-lab-approval-v1' and a['purpose']=='DORMANT_OFFLINE_INSTALL_ONLY' and a['source_git_revision']==REVISION and a['bundle_sha256']==bundle_sha and a['destination']==str(DESTINATION),'approval_scope')
 require(type(a['operator_reference']) is str and 1<=len(a['operator_reference'])<=128,'operator_reference')
 expiry=datetime.datetime.fromisoformat(a['expires_at_utc']);now=datetime.datetime.now(datetime.UTC)
 require(expiry.tzinfo is not None and now<expiry<=now+datetime.timedelta(hours=1),'approval_expired_or_too_long')
 check_target(facts,a['target']);return a

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 v=sub.add_parser('verify');v.add_argument('bundle');v.add_argument('sha256')
 sub.add_parser('probe')
 for command in ('install','validate-installed','quarantine'):
  x=sub.add_parser(command);x.add_argument('bundle');x.add_argument('sha256');x.add_argument('approval')
 args=p.parse_args()
 if args.command=='probe':print(json.dumps(probe(),indent=2,sort_keys=True));return
 m,files=load_bundle(args.bundle,args.sha256)
 expected={n:digest(b) for n,b in files.items()}
 if args.command=='verify':print(json.dumps({'status':'VERIFIED_INERT_BUNDLE','files_to_install':len(files),'installed_bytes':sum(map(len,files.values())),'source_git_revision':REVISION,'dependencies':len(m['dependencies']),'protected_installation_performed':False},indent=2));return
 require(os.getuid()==os.geteuid()==0,'trusted_guest_root_required')
 # Bootstrap/tool/runtime must already be in root-protected custody. Never trust
 # an operator approval or code supplied through a preparation-user-writable path.
 for path in (Path(__file__).resolve(),Path(sys.executable).resolve()):
  fd=protected_chain(path);os.close(fd)
 facts=probe();a=approval(args.approval,args.sha256,facts)
 require(DESTINATION.parent.is_dir(),'approved_protected_parent_must_already_exist')
 if args.command=='install':
  require(os.statvfs(DESTINATION.parent).f_bavail*os.statvfs(DESTINATION.parent).f_frsize>=20*1024**3,'destination_free_space')
  # Verify target and expiry a second time immediately before the first write.
  approval(args.approval,args.sha256,probe())
  publish(DESTINATION.parent,DESTINATION.name,files,owner=0)
  validate_installed(DESTINATION,expected)
  status='DORMANT_INSTALL_VERIFIED_NO_ACTIVATION'
 elif args.command=='validate-installed':validate_installed(DESTINATION,expected);status='DORMANT_INSTALL_VERIFIED'
 else:
  status=quarantine(DESTINATION.parent,DESTINATION.name,expected,owner=0,tag=datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ'))
 print(json.dumps({'status':status,'source_git_revision':REVISION,'operator_reference':a['operator_reference'],'activation_performed':False,'runtime_state_created':False},indent=2))
if __name__=='__main__':
 try:main()
 except (Refusal,OSError,ValueError,KeyError,tarfile.TarError,zipfile.BadZipFile) as e:
  print(json.dumps({'status':'REFUSED_PRESERVE_ALL_OUTPUT','reason':str(e) if isinstance(e,Refusal) else type(e).__name__,'automatic_retry':False,'cleanup_performed':False}));raise SystemExit(1)

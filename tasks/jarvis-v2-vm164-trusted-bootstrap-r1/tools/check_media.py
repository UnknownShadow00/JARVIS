"""Independent bounded ISO9660 reader: no mounts, no xorriso for inspection."""
import argparse,hashlib,json
from pathlib import Path
ALLOWED={'BOOT.PY','LABPKG.PY','SHA256.SUM'}
def need(ok,s):
 if not ok:raise ValueError(s)
def check(path,delivery):
 need(delivery['iso_bytes']==196608 and path.stat().st_size==196608,'FIXED_MEDIA_SIZE_BOUND')
 raw=path.read_bytes();need(len(raw)==delivery['iso_bytes'] and hashlib.sha256(raw).hexdigest()==delivery['iso_sha256'],'IMAGE_PIN')
 need(raw[:32768]==bytes(32768),'NO_BOOT_SYSTEM_AREA')
 descriptors=[];pvd=None
 for i in range(16,48):
  sector=raw[i*2048:(i+1)*2048];need(len(sector)==2048 and sector[1:7]==b'CD001\x01','DESCRIPTOR')
  descriptors.append(sector[0]);need(sector[0]!=0,'BOOT_RECORD_FORBIDDEN')
  if sector[0]==1:pvd=sector
  if sector[0]==255:break
 need(pvd is not None and descriptors[-1]==255,'PRIMARY_AND_TERMINATOR')
 need(pvd[40:72].decode().strip()=='J164BOOT','LABEL')
 root=pvd[156:190];offset=int.from_bytes(root[2:6],'little')*2048;size=int.from_bytes(root[10:14],'little');need(size<65536,'DIRECTORY_BOUND');directory=raw[offset:offset+size];pos=0;found={}
 while pos<len(directory):
  length=directory[pos]
  if not length:pos=(pos//2048+1)*2048;continue
  rec=directory[pos:pos+length];pos+=length;need(len(rec)>=34,'RECORD')
  n=rec[32];name=rec[33:33+n].decode('ascii')
  if name in ('\x00','\x01'):continue
  name=name.split(';')[0];need(name in ALLOWED and name not in found and not rec[25]&2,'EXACT_FLAT_PAYLOAD')
  extent=int.from_bytes(rec[2:6],'little')*2048;size=int.from_bytes(rec[10:14],'little');need(0<size<=65536 and extent+size<=len(raw),'EXTENT_BOUND')
  data=raw[extent:extent+size];need(hashlib.sha256(data).hexdigest()==delivery['files'][name],'MEMBER_PIN');found[name]=data
 need(set(found)==ALLOWED,'INVENTORY')
 need(hashlib.sha256(found['LABPKG.PY']).hexdigest()=='08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a','UNCHANGED_PREDECESSOR_PROBE')
 need(found['SHA256.SUM']==''.join(hashlib.sha256(found[n]).hexdigest()+'  '+n+'\n' for n in ('BOOT.PY','LABPKG.PY')).encode(),'INTERNAL_MANIFEST')
 return {'status':'PASS_NONBOOT_DATA_ISO','iso_sha256':delivery['iso_sha256'],'bytes':len(raw),'descriptor_types':descriptors,'files':delivery['files'],'system_area_zero':True,'no_el_torito':True,'mounted_or_attached':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--iso',type=Path,required=True);p.add_argument('--delivery',type=Path,required=True);a=p.parse_args();print(json.dumps(check(a.iso,json.loads(a.delivery.read_text())),indent=2))

"""Validate trusted VM164-only PVE readbacks OFFLINE. No subprocess/network/mutation."""
import argparse,hashlib,json,re
from pathlib import Path
UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL='g6k164-12821f6b54a2'
VOLUME='downloads:164/vm-164-disk-0.raw'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def validate(c,s,p,*,phase,iso_volume,expect_status):
 need(type(c) is dict and type(s) is dict and type(p) is list,'READBACK_SCHEMA')
 need(s.get('vmid')==164 and s.get('status')==expect_status,'VMID_OR_STATE')
 need(c.get('smbios1')=='uuid='+UUID,'UUID')
 need(c.get('boot')=='order=scsi0' and str(c.get('onboot'))=='0','DISK_ONLY_MANUAL_BOOT')
 need(str(c.get('agent','0')) in ('0','enabled=0'),'NO_AGENT')
 need(c.get('vga','std')=='std' and c.get('serial0')=='socket','EXISTING_VGA_REQUIRED_SERIAL_UNUSED')
 need(not c.get('lock') and not c.get('template'),'NO_CONFIG_LOCK_OR_TEMPLATE')
 need(str(c.get('hotplug'))=='0' and str(c.get('protection'))=='1','PROTECTED_NO_HOTPLUG')
 need(re.fullmatch('[0-9a-f]{40}',c.get('digest','')) is not None,'CONFIG_DIGEST')
 disk=c.get('scsi0','').split(',');need(disk[0]==VOLUME and 'serial='+SERIAL in disk and 'size=64G' in disk,'ORIGINAL_DISK')
 need(not any('pending' in r or r.get('delete') or r.get('deleted') for r in p),'NO_PENDING_CONFIG')
 for k in c:
  need(not re.match(r'^(net|hostpci|usb|virtiofs|unused|parallel|mp)\d+$',k),'NO_EXTRA_CHANNEL:'+k)
  if re.fullmatch(r'(scsi|ide|sata|virtio|serial)\d+',k):need(k in ('scsi0','ide2','serial0'),'EXTRA_DEVICE:'+k)
  need(k not in ('args','hookscript','cicustom','ciuser','cipassword','sshkeys','ivshmem','smbios','affinity'),'UNREVIEWED_CHANNEL:'+k)
 need(re.fullmatch(r'local:iso/vm164-trusted-bootstrap-[0-9a-f]{16}\.iso',iso_volume) is not None,'PINNED_NEW_MEDIA_NAME')
 need(c.get('ide2')==('none,media=cdrom' if phase=='empty' else iso_volume+',media=cdrom'),'MEDIA_PHASE')
 need(int(c.get('cores',0))*int(c.get('sockets',1))>=4 and int(c.get('memory',0))>=6000 and str(c.get('balloon'))=='0','RESOURCE_BASELINE')
 return {'status':'PASS_HOST_READBACK_ONLY','node':'pve','vmid':164,'uuid':UUID,'disk_volume':VOLUME,'disk_serial':SERIAL,'digest':c['digest'],'phase':phase,'vm_status':s['status'],'not_a_live_check':True,'mutations_performed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--status',type=Path,required=True);p.add_argument('--pending',type=Path,required=True);p.add_argument('--phase',choices=['empty','attached'],required=True);p.add_argument('--expect-status',choices=['stopped','running'],required=True);p.add_argument('--iso-volume',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 names={'config':a.config,'status':a.status,'pending':a.pending};raw={k:v.read_bytes() for k,v in names.items()}
 d=validate(*(json.loads(raw[k]) for k in ('config','status','pending')),phase=a.phase,iso_volume=a.iso_volume,expect_status=a.expect_status)
 d['readback_sha256']={k:hashlib.sha256(v).hexdigest() for k,v in raw.items()}
 with a.out.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps(d,indent=2))

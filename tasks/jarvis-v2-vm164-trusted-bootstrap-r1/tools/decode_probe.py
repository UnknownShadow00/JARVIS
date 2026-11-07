"""Recover captured VGA rows without trusting transcription; never contacts VM."""
import argparse,base64,hashlib,json,re
from pathlib import Path
UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
def decode(text,pin):
 if not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('HASH_REQUIRED')
 pairs=re.findall(r'^R([0-9]{4}):([A-Za-z0-9+/=]{1,48})$',text,re.M)
 if not pairs or len(pairs)>9999:raise ValueError('ROWS_BOUND')
 if [int(n) for n,_ in pairs]!=list(range(len(pairs))):raise ValueError('MISSING_DUPLICATE_OR_UNORDERED_ROW')
 raw=base64.b64decode(''.join(s for _,s in pairs),validate=True)
 if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('TRANSCRIPTION_OR_HASH_MISMATCH')
 d=json.loads(raw)
 if d.get('vm_uuid')!=UUID or d.get('disk_serial')!='g6k164-12821f6b54a2' or d.get('disk_bytes')!=64*1024**3:raise ValueError('WRONG_TARGET')
 if d.get('format')!='vm164-readonly-probe-v1' or d.get('optical_media_present') is not False:raise ValueError('PROBE_FORMAT_OR_MEDIA')
 return raw
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--rows',type=Path,required=True);p.add_argument('--sha256',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=decode(a.rows.read_text(),a.sha256);a.out.mkdir(mode=0o700)
 with (a.out/'PROBE.JSON').open('xb') as f:f.write(raw)
 with (a.out/'CAPTURE.json').open('x') as f:json.dump({'sha256':a.sha256,'bytes':len(raw),'temporary_debug_boot':True,'independent_attestation':False,'installation_authorized':False},f,indent=2);f.write('\n')
 print('VERIFIED_TRANSCRIPTION; installation readiness requires separate host/guest review')

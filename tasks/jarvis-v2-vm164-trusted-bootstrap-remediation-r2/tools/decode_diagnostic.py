"""Local console transcription verifier; diagnostic-only, never install evidence."""
import argparse,base64,hashlib,json,re
from pathlib import Path
UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
BOOT_PATTERN=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
def decode(text,pin,expected_boot):
 if not re.fullmatch('[0-9a-f]{64}',pin) or not re.fullmatch(BOOT_PATTERN,expected_boot):raise ValueError('independent_hash_and_boot_binding_required')
 if len(text)>131072:raise ValueError('capture_bound')
 rows=re.findall(r'^R([0-9]{4}):([A-Za-z0-9+/=]{1,48})$',text,re.M)
 if not rows or [int(i) for i,_ in rows]!=list(range(len(rows))):raise ValueError('missing_duplicate_or_unordered_rows')
 raw=base64.b64decode(''.join(s for _,s in rows),validate=True)
 if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('record_hash_mismatch')
 d=json.loads(raw)
 if d.get('format')!='vm164-readonly-probe-v1' or d.get('vm_uuid')!=UUID or d.get('disk_serial')!='g6k164-12821f6b54a2' or d.get('boot_id')!=expected_boot or type(d.get('disk_bytes')) is not int or d['disk_bytes']!=64*1024**3 or d.get('optical_media_present') is not True:raise ValueError('wrong_diagnostic_binding_or_media')
 return raw
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rows',type=Path,required=True);p.add_argument('--sha256',required=True);p.add_argument('--expected-boot-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.rows.stat().st_size>131072:raise SystemExit('capture_too_large')
 raw=decode(a.rows.read_text(),a.sha256,a.expected_boot_id);a.out.mkdir(mode=0o700)
 with (a.out/'PROBE.JSON').open('xb') as f:f.write(raw)
 with (a.out/'DIAGNOSTIC.json').open('x') as f:json.dump({'raw_probe_sha256':a.sha256,'boot_id':a.expected_boot_id,'optical_media_present':True,'installation_qualified':False,'live_origin_authenticated':False},f,indent=2);f.write('\n')
 print('VERIFIED_TRANSCRIPTION_ONLY; MEDIA_ATTACHED; INSTALLATION_NO_GO')

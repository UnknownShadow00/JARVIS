"""Offline-only deterministic generation of argv templates, never executes them."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import packet as p
import proposals as q
root=Path(__file__).resolve().parents[1]
def python(code,*args):return ['/usr/bin/python3','-I','-B','-S','-c',code,*args]
read={
 'R01-clock':p.observation_commands('0'*32,'success','00000000-0000-0000-0000-000000000000')['clock'],
 'R02-host-binaries':python(q.INSPECT_CODE,json.dumps(p.BINARIES)),
 'R03-packages':['/usr/bin/dpkg-query','-W','--showformat=${Package}=${Version}\\n',*p.PACKAGES],
 'R04-systemd-version':['/usr/bin/systemd-run','--version'],
 'R05-python-version':['/usr/bin/python3','-I','-B','-S','--version'],
 'R06-account':['/usr/bin/getent','passwd','nobody'],
 'R07-numeric-account':['/usr/bin/getent','passwd','65534'],
 'R08-group':['/usr/bin/getent','group','65534'],
 'R09-memberships':['/usr/bin/id','nobody'],
 'R10-processes':python(q.PROCESS_CODE),
 'R11-loaded-units':['/usr/bin/systemctl','--system','--no-pager','--all','list-units','jarvis-vm164-r3-stage2-*'],
 'R12-unit-files':['/usr/bin/systemctl','--system','--no-pager','list-unit-files','jarvis-vm164-r3-stage2-*'],
 'R13-path-metadata':python(q.METADATA_CODE,json.dumps(['/','/opt','/opt/jarvis-vm164-r3-stage2',p.PUBLIC])),
 'R14-access-acl':['/usr/bin/getfacl','--absolute-names','--numeric','--','<ONE_REVIEWED_PATH_FROM_COMPLETE_INVENTORY>'],
 'R15-sudo-policy':['/usr/bin/sudo','-n','-l','-U','nobody'],
 'R16-manager':['/usr/bin/systemctl','--system','--no-pager','show','--property=Version,Virtualization,SystemState'],
 'R17-unit-search-paths':['/usr/bin/systemctl','--system','--no-pager','show','--property=UnitPath'],
 'R18-public-verification':python(q.VERIFY_PUBLIC_CODE),
 'R19-policy-or-manual-read':python("import sys; from pathlib import Path; p=Path(sys.argv[1]); b=p.read_bytes(); assert len(b)<=1048576; sys.stdout.buffer.write(b)",'<EXACT_APPROVED_NONSECRET_POLICY_OR_MANUAL_PATH>'),
 'R20-manual-gzip-read':python("import gzip,sys; from pathlib import Path; b=gzip.decompress(Path(sys.argv[1]).read_bytes()); assert len(b)<=8388608; sys.stdout.buffer.write(b)",'<EXACT_APPROVED_INSTALLED_MANUAL_GZ_PATH>'),
 'R22-cgroup':python(q.CGROUP_CODE,'<EXACT_OWNED_BASE>'),
 'R21-inventory-metadata':python(q.METADATA_CODE,'<JSON_ARRAY_OF_REVIEWED_PATHS_AND_ANCESTORS>'),
}
create={}
observe={}
for case in p.CASES:
 argv=p.timer_argv('0'*32,case,1)
 create[case]=[a.replace('0'*32,'<SESSION_NONCE>').replace('--on-boot=0.000001s','--on-boot=<ABSOLUTE_BOOT_SECONDS.SIX_DIGITS>s') for a in argv]
 cmds=p.observation_commands('0'*32,case,'00000000-0000-0000-0000-000000000000')
 observe[case]={k:[a.replace('0'*32,'<SESSION_NONCE>').replace('00000000-0000-0000-0000-000000000000','<HOST_BOOT_ID>') for a in argv] for k,argv in cmds.items()}
sealed=root.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src'
sys.path.insert(0,str(sealed))
import systemd_codec
parser_readback={name:['/usr/bin/systemctl','--system','--no-pager','show','--property='+','.join(props),'<EXACT_BASE>.'+name] for name,props in (('timer',systemd_codec.TIMER_PROPS),('service',systemd_codec.SERVICE_PROPS))}
collision_readback=['/usr/bin/systemctl','--system','--no-pager','show','--property=Id,LoadState,ActiveState,SubState,Names,FragmentPath,SourcePath,Transient,Job,Description','<EXACT_PROPOSED_UNIT_WITH_SUFFIX>']
cat={'collision_readback':collision_readback,'parser_readback':parser_readback,'kind':'INERT_ARGV_TEMPLATES_NOT_HOST_EVIDENCE_NOT_AUTHORIZATION','read':read,
 'install':python(q.INSTALL_CODE,'<ROOT_CONTROLLED_STAGED_CALLBACK_SOURCE>'), 'create':create,'observe':observe,
 'cleanup':{'timer':['/usr/bin/systemctl','--system','--no-ask-password','stop','<EXACT_OWNED_BASE>.timer'],
            'service':['/usr/bin/systemctl','--system','--no-ask-password','stop','<EXACT_OWNED_BASE>.service']}}
(root/'COMMAND-CATALOG.json').write_text(json.dumps(cat,indent=2)+'\n')
session={'nonce':None,'boot_id':None,'starts_utc':None,'expires_utc':None,'start_boot_us':None,
 'start_offset_low_us':None,'start_offset_high_us':None}
identity={'node':'pve','packages':p.PACKAGES,'uid':65534,'gid':65534,'groups':None,'nobody_processes':None,
 'source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,
 **{k:None for k in ('vm_authority_absent_review','credential_access_denied_review','binary_custody_review',
 'acl_review','source_custody_review','exclusive_operator_review')}}
(root/'templates/PREFLIGHT-INPUT.json').write_text(json.dumps({'kind':'UNFILLED_NOT_HOST_EVIDENCE','session':session,
 'sample':{'utc':None,'boot_id':None,'boot_us':None,'offset_low_us':None,'offset_high_us':None},
 'identity':identity,'occupied_units':None,'consumed_names':None},indent=2)+'\n')
result={'kind':'UNFILLED_STAGE2_RESULT_NOT_AUTHORIZATION','source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,
 'packet_manifest_sha256':None,'authorization_reference':None,'operator':None,'independent_reviewer':None,
 'session':session,'fresh_host_evidence':None,'clock_domain':'UNKNOWN','clock_domain_basis':None,
 'cases':{c:{'status':'NOT_RUN','argv_sha256':None,'deadline_boot_us':None,'unit_names':None,
             'evidence':[],'observations':None,'failure_reason':None} for c in p.CASES},
 'cleanup':{'status':'NOT_RUN','owned_units':[],'inactive_evidence':[],'callback_retained':None},
 'unqualified':['manager_reexec','host_reboot','physical_suspend_wake','VM_termination','root_bootstrap'],
 'stage2_authorized':False,'live_qualification':False,'expiration_guaranteed':False,'result':'NOT_RUN'}
(root/'templates/LIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')

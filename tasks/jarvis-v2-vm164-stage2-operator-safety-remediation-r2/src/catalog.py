"""Pure catalogue generation with explicit mandatory placeholders, no execution."""
import packet as p
import proposals as q
import inspection as i
from common import need

def build():
 read={
 'R01-clock':['/usr/bin/python3','-I','-B','-S','-c',p.CLOCK_CODE],
 'R02-host-identity':i.identity_command(),
 'R02-hash-resolved-file':i.hash_command('/MANDATORY/REVIEWED/RESOLVED/REGULAR/FILE'),
 'R03-packages':['/usr/bin/dpkg-query','--show','--showformat=${Package}\t${Version}\n',*p.PACKAGES],
 'R04-systemd-version':['/usr/bin/systemd-run','--version'],
 'R05-python-version':['/usr/bin/python3','-I','-B','-S','--version'],
 'R10-nobody-processes':i.process_command(),
 'R11-loaded-units':['/usr/bin/systemctl','--system','--no-pager','--plain','--no-legend','list-units','--all','jarvis-vm164-r3-stage2-*'],
 'R12-unit-files':['/usr/bin/systemctl','--system','--no-pager','--no-legend','list-unit-files','jarvis-vm164-r3-stage2-*'],
 'R14-numeric-acl':['/usr/bin/getfacl','--numeric','--absolute-names','--all-effective','--','/MANDATORY/APPROVED/METADATA/PATH'],
 'R16-manager':['/usr/bin/systemctl','--system','--no-pager','show','--all','--property=Version,Architecture,Virtualization,SystemState'],
 'R17-unit-paths':['/usr/bin/systemctl','--system','--no-pager','show','--all','--property=UnitPath'],
 'R19-policy-or-manual-read':q.protected_read('/MANDATORY/APPROVED/NONSECRET/REGULAR/FILE',1048576,'MANDATORY_SOURCE_SHA256'),
 'R20-manual-gzip-read':q.protected_read('/MANDATORY/APPROVED/REGULAR/MANUAL.gz',1048576,'MANDATORY_SOURCE_SHA256',True),
 'R21-no-follow-metadata':i.metadata_command('/MANDATORY/APPROVED/METADATA/PATH'),
 'R22-owned-cgroup':i.cgroup_command('MANDATORY_EXACT_OWNED_BASE')}
 return {'kind':'INERT_CATALOG_NOT_AUTHORIZATION','read':read,
 'retired':['R06-account','R07-numeric-account','R08-group','R09-memberships','R15-sudo-policy'],
 'install':['/usr/bin/python3','-I','-B','-S','-c',q.LIMITS+q.INSTALL_CODE,'/MANDATORY/ROOT_CONTROLLED/STAGED_CALLBACK'],
 'collision_readback':['/usr/bin/systemctl','--system','--no-pager','show','--all','--property=Id,Names,LoadState,ActiveState,SubState,Job,FragmentPath,SourcePath,Transient','MANDATORY_EXACT_NAME'],
 'service_properties':list(p.SERVICE_PROPERTIES),'timer_properties':list(p.TIMER_PROPERTIES),
 'operation_caps':{op:{'timeout_s':cap,'stdout_limit':limit,'stderr_limit':65536,'kill_reap_reserve_s':2} for op,(cap,limit) in p.CAPS.items()},
 'namespace':'jarvis-vm164-r3-stage2-<32_LOWER_HEX_NONCE>-<EXACT_CASE>',
 'case_renderer':'src/packet.py:plan','host_execution_implemented':False}

"""Independent prerequisite assessment; only supplied records, no commands."""
import re
from model import BASE,need,sha,canonical
BINARIES=('/usr/bin/python3','/usr/bin/systemd-run','/usr/bin/systemctl','/usr/sbin/qm',
          '/usr/bin/pvesh','/usr/sbin/pvesm','/usr/bin/dpkg-query')
PACKAGES=('pve-manager','qemu-server','pve-qemu-kvm','systemd')
PACKAGE_COMMAND=['/usr/bin/dpkg-query','-W','--showformat=${Package}=${Version}\\n',*PACKAGES]
EXPECTED={'node':'pve','proxmox':'pve-manager/9.2.5','kernel':'7.0.14-6-pve',
          'systemd':'257 (257.13-1~deb13u1)'}
def runtime_packages(raw,expected):
    need(type(raw) is bytes and len(raw)<=4096,'runtime_package_output_bound')
    packages={}
    for line in raw.decode().splitlines():
        need(line.count('=')==1,'runtime_package_schema');key,value=line.split('=')
        need(key in PACKAGES and key not in packages,'runtime_package_schema');packages[key]=value
    need(packages==expected,'host_package_versions_changed')
    return packages

def assess(record,source_hash):
    need(type(record) is dict,'prerequisite_schema');missing=[]
    if record.get('host')!=EXPECTED:missing.append('exact_reported_host_identity_and_versions')
    if record.get('source_sha256')!=source_hash:missing.append('source_tree_pin')
    for path in BINARIES:
        d=record.get('binaries',{}).get(path,{})
        if not (d.get('root_owned_chain') is True and d.get('regular_resolved_binary') is True
                and d.get('not_group_or_other_writable') is True
                and type(d.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}',d['sha256'])):
            missing.append('binary_custody:'+path)
    for key in ('python_supported','qemu_server_version_captured','qemu_version_captured',
                'pve_command_help_reviewed','systemd_show_codec_qualified',
                'boottime_deadline_readback_qualified','wake_system_qualified',
                'exec_failure_observed','manager_reexec_behavior_qualified',
                'reboot_invalidation_qualified','journal_retention_qualified',
                'no_other_controller_autostarts_vm164','private_install_and_state_custody',
                'stage2_callbacks_unprivileged_verified'):
        if record.get(key) is not True:missing.append(key)
    if record.get('timer_readback_clock_domain') not in ('CLOCK_MONOTONIC','CLOCK_BOOTTIME'):
        missing.append('timer_readback_clock_domain')
    if record.get('paired_clock_conversion_qualified') is not True:missing.append('paired_clock_conversion_qualified')
    if type(record.get('stage2_callback_uid')) is not int or record['stage2_callback_uid']<=0:
        missing.append('stage2_callback_must_be_verified_nonroot_uid')
    packages=record.get('package_versions',{})
    if not (type(packages) is dict and set(packages)==set(PACKAGES)
            and packages.get('pve-manager')=='9.2.5' and packages.get('systemd')=='257.13-1~deb13u1'
            and all(type(v) is str and re.fullmatch('[A-Za-z0-9.+:~_-]{1,100}',v) for v in packages.values())):
        missing.append('exact_runtime_package_versions')
    return {'status':'PASS_SUPPLIED_PREREQUISITE_CONSISTENCY_ONLY' if not missing else 'NO_GO_MISSING_PREREQUISITES',
            'missing':missing,'record_sha256':sha(canonical(record)),
            'live_origin_verified':False,'root_boot_go':False,'forced_stop_authorized':False,
            'host_checks_executed':False}

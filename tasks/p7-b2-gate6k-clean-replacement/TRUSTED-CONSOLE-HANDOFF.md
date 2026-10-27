# Trusted PVE console handoff

Immediate blocker: neither available public-key identity authenticated to PVE. No capacity/VMID can truthfully be reported. Use your existing trusted Proxmox **node** shell, verify node `pve` and management address `.50`, and paste this read-only block. It collects allowlisted inventory and a free-ID candidate only; it never queries a guest agent or changes a VM. Output contains no auth material. The fuller equivalent is `tools/pve_inventory.py` after trusted transfer and source/hash review.

```bash
python3 -I -B - <<'PY'
import datetime,json,os,socket,subprocess
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='pve'
def run(argv):
    return subprocess.run(argv,check=True,capture_output=True,text=True,timeout=30).stdout
links=json.loads(run(['ip','-j','-4','address','show']))
assert any(a.get('local')=='192.168.0.50' for l in links for a in l.get('addr_info',[]))
def get(path,*args):
    return json.loads(run(['pvesh','get',path,*args,'--output-format','json']))
def keep(row,keys):
    return {k:row[k] for k in keys if k in row}
vms=get('/cluster/resources','--type','vm')
used={int(v['vmid']) for v in vms if 'vmid' in v}|{50,101,162,163,200}
candidate=next(i for i in range(164,1000000) if i not in used)
assert int(get('/cluster/nextid','--vmid',str(candidate)))==candidate
status=get('/nodes/pve/status')
storage=get('/nodes/pve/storage')
mem={}
for line in Path('/proc/meminfo').read_text().splitlines():
    k,v=line.split(':',1)
    if k in ('MemTotal','MemAvailable','SwapTotal','SwapFree'):mem[k+'_bytes']=int(v.split()[0])*1024
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'node':'pve','scope':'GET_ONLY_NO_GUEST_ACCESS_NO_MUTATIONS',
 'vms':[keep(v,('vmid','node','type','status','maxmem','maxcpu','maxdisk')) for v in vms],
 'candidate_vmid_available_at_observation_only':candidate,
 'memory':keep(status.get('memory',{}),('total','used','free')),
 'cpu':keep(status.get('cpuinfo',{}),('cpus','cores','sockets')),'meminfo':mem,
 'storage':[keep(s,('storage','type','active','enabled','shared','content','total','used','avail')) for s in storage],
 'creation':'NOT_RUN','qualification':'NOT_RUN'},indent=2))
PY
```

Independently retain the JSON and its UTC observation. The candidate is **not reserved**. The existing VM163 may appear only as an inventory row; do not change it. If the node identity, address, command or permission fails, preserve that result and stop. No package installation or SSH enrollment is needed for this block.

## Next stage after inventory is available

1. Verify CPU capacity and fixed6000MiB memory plus host/service reserve using physical memory, `MemAvailable` and configured limits of running workloads. If insufficient, report the deficit. Existing VM shutdown, memory reduction or migration is not authorized.
2. Select active local nonshared image storage from actual inventory. Inspect that specific backend's real data/metadata capacity read-only (for LVM thin, selected pool `lvs` data/metadata percentages; for ZFS, selected pool free space/health; for directory storage, actual filesystem free bytes). Verify ISO storage capacity separately. Storage IDs, physical disk paths and volume IDs are still unknown; no allocation command using guessed `local-lvm` or a guessed pool is supplied.
3. Resolve/test the installation-time empty-SSH/source-construction procedure and console bootstrap described in the design. Original signed media alone does not meet unchanged r1 path policy.
4. Revalidate the selected ID through the cluster inventory and `/cluster/nextid` immediately before normal `qm create`. Set four cores,6000MiB fixed memory, no network devices or passthrough/shares, autostart off, dedicated new disk, fresh UUID/serial and trusted console. Record the resulting actual config. Disk-size64GiB is conditional on physical capacity/reserve, not a reservation. No clone/import-from-existing-volume operation is appropriate. Use the installed PVE's `qm help create`/`qm help set` to bind version-specific options; [upstream command reference](https://github.com/proxmox/pve-docs/blob/master/generated/qm.1-synopsis.adoc) is planning guidance.
5. Build/install from independently compared public hashes; record before-first-boot source/target metadata and every installation input. Keep failures and partial new allocations for review; no automatic destroy/retry. Create new identity and protected artifact/runtime records. The GO already authorizes these actions when access, identity, capacity and a reviewed executable design actually pass.

There is intentionally no guessed VMID, disk volume, ISO storage ID or executable unattended `qm create` block. Exact creation arguments depend on the unobserved infrastructure and unresolved installation implementation. This access failure cannot be solved by pretending those inputs are known.

## Replacement-only metadata/preflight sequence, not yet runnable

After a real guest boot, from its trusted root console, record UTC, hostname, machine-id, DMI product UUID, boot ID, `/proc/self/ns/mnt` and `/proc/1/ns/mnt`; read-only `lsblk` UUID/PARTUUID/serial/parent metadata; `findmnt` target/source/type/propagation; `ip -brief link`, IPv4/IPv6 routes; and `statvfs` available bytes for `/opt` and `/var/lib`. Compare against the new PVE volume/config/console record externally. Do not use a live installer/chroot or Nexus as the replacement guest.

Verify all runtime/source/artifact paths are root-protected, including every interpreter/venv symlink target and native loader/import path. Run unchanged `verify_manifest`, `validate_dependencies`, `verify_artifacts`, `inspect_environment_paths`, `validate_environment` and `validate_capacity` from the protected runtime, with **actual** boot-source policy. Retain all failures. `preflight_report.py` is informational and contains a historical `/dev/sda2` mount assumption; it cannot attest the new disk. A separate metadata wrapper may supply the actual verified `boot_source` to the unchanged function; it must not alter or suppress its decisions. Independently inspect actual UID/GID membership/locked-shell/admin grants. Require at least21,474,836,480 available bytes after all setup, then recheck immediately before any later qualification.

Shared-mount refusal before scope approval is expected and remains NO-GO. Do not make propagation private merely to make the diagnostic pass. A populated cache needs independently established installer provenance plus its current accepted metadata digest. No credential content, cloud cache content, environment, private-key digest or raw log bundle is requested.

Only after real evidence supports every prerequisite may a separately authorized human review/create the root-owned0600 approval marker bound to the new identity and chosen namespace scope. Privileged qualification remains another separate explicit authorization. No qualification launch command or automated marker creator is provided.

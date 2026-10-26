# VM163 consolidated preflight remediation plan

**Decision: NO-GO for qualification. GO only for separately authorized human evidence collection next.** This packet authorizes no VM command. All commands below are proposals for the independently identified VM163 console, require the stated new human authorization, and must stop on any failure. Do not paste the whole document into a shell.

Nexus work completed: source review, public documentation research, unprivileged synthetic fixtures and this plan. No VM163, PVE, Core or AI-host connection; no remediation, qualification, approval-marker creation, model generation or V3 startup. Existing uncommitted workspace changes were preserved. Task profile: `workspace-write` for local plan/tools/tests.

The operator reports VM163 `jarvis-security-lab`, guest `jarvis-security`, UUID `1d279e9b-12cb-4a02-8815-a682cb9457a9`, pve; Ubuntu26.04, private ext4, loopback only, approximately23GiB free;618 source files and127 pins verified; fixture and approval marker absent. These are operator observations, not fresh remote observations by this task.

## Go/no-go matrix

| Finding | Current decision | Required evidence / permitted later disposition |
|---|---|---|
| `/root/.ssh`, `/home/jarvis/.ssh` | NO-GO under installed r1, even if empty | Complete no-follow metadata scan. Empty ordinary directories are not keys; optional **empty-only** cleanup requires specific approval and preserved metadata. Any file, link, nested entry or unknown scan stops cleanup. Preserving them instead requires a new reviewed release policy; r1 has no empty-SSH exception. |
|38 cloud files,23 permission-rule matches,1 symlink | NO-GO; credential content/provenance unknown | Complete inventory and trusted installation/input provenance. Neither chmod nor deleting/quarantining cache proves safety. If provenance cannot be established without accessing secrets, preserve VM163 and authorize a clean replacement VM. |
|28 non-private mounts | NO-GO under current mount gate | Independently exclude host/network shares first. Prefer an explicitly reviewed, temporary **mount-only namespace** for the qualification process tree if policy review accepts that scope; otherwise separately authorize guest-wide recursive privacy. Never simply suppress flags. |
|5 systemd credential mounts | UNKNOWN, not cleared by propagation change | Metadata inventory of all payloads; r1 refuses any regular credential payload, even empty/root-only. Do not unmount stores or stop services to hide findings. |
| `/opt/g6k-offline` absent | NO-GO |131 pinned artifacts plus manifest, exact hashes, no links/extras, writer quiescence, same-filesystem rename into protected storage, at least20GiB free afterward. No second3GB copy. |
| Offline media mounted; marker absent | Intentional NO-GO | Finish reviewed transfer/evidence first; separately approve normal unmount and hypervisor media detachment, then scope-bound approval. Never infer approval from a marker or from this plan. |
| Source/runtime verification | PASS as operator-reported; local source reverified | Preserve all3 installed releases/runtime paths. Reverify source, dependencies, protected interpreter ownership and artifacts before any future execution. |

**Recommended sequence:** H1 metadata/provenance review → choose retain/remediate versus rebuild → approve only the necessary H2/H3 changes → H4 media removal → H5 isolation context → H6 final read-only gates → a separate approval-marker decision → a separate qualification authorization. Do not provision artifacts or change propagation merely while the cloud decision remains unresolvable.

## 1. H1 — authorize metadata collection and establish identity

New authorization must name VMID163, UUID above, pve, exact private disk, trusted console/session and a retention location. No passwords, private keys, console tickets, process environments, cloud-init user-data or log bundles may be read or shared. Keep metadata evidence locally protected; share only minimized counts/codes/digests. Record UTC time and boot ID so observations cannot silently span reboots.

Human read-only console commands, **after H1 approval**:

```bash
id -u
hostname -s
cat /etc/machine-id
cat /sys/class/dmi/id/product_uuid
cat /proc/sys/kernel/random/boot_id
readlink /proc/self/ns/mnt
readlink /proc/1/ns/mnt
findmnt --kernel --list --noheadings --output TARGET,SOURCE,FSTYPE,PROPAGATION
lsblk --output NAME,TYPE,SIZE,FSTYPE,UUID,PARTUUID,PKNAME,MODEL,SERIAL,WWN,MOUNTPOINTS
ip -brief link
ip route show table all
ip -6 route show table all
df -B1 --output=avail,target /var/lib /opt /home/jarvis
```

Match the guest disk's parent device/UUID/PARTUUID/serial against the exact Proxmox volume and VM hardware identity through the **human's trusted management console**. A block-device name, hostname, UUID string inside the guest or approval JSON alone cannot prove isolation. This task issues no PVE commands. Confirm no NIC, host filesystem passthrough, shared folders, cloud/config-drive with unreviewed inputs, production routes, agent forwarding or production credentials. Read-only findmnt metadata omits arbitrary mount-option strings; do not publish raw infrastructure/config/environment dumps.

Two proposed helper files are supplied in `tools/`; neither is an installed authority component or a new release. Before a human executes them as root, inspect their source and compare these independently retained hashes:

| Helper | SHA256 |
|---|---|
| `metadata_only.py` | `cd1f1843e697eebc8c2c997ea6fdcf467387d750143b82ff83be2c152a8c37de` |
| `artifact_transfer.py` | `8c78295c163cade78d9d77cf4441b1ed8fb6e3489a24bea1e22a23d814e86805` |

If H1 explicitly authorizes copying these small reviewed helpers and retaining nonsecret reports, use read-only reviewed offline media at `/mnt/g6k-update` and a **new** protected directory. If that media path differs, stop and record the approved exact path first. Existing `/opt/g6k-update-r1` and releases are not modified.

```bash
set -euC
umask 077
test "$(id -u)" = 0
test "$(hostname -s)" = jarvis-security
test ! -e /root/vm163-remediation-r1
test ! -L /root/vm163-remediation-r1
mkdir -m 0700 /root/vm163-remediation-r1
install -o root -g root -m 0600 /mnt/g6k-update/metadata_only.py /root/vm163-remediation-r1/metadata_only.py
install -o root -g root -m 0600 /mnt/g6k-update/artifact_transfer.py /root/vm163-remediation-r1/artifact_transfer.py
printf '%s  %s\n' 'cd1f1843e697eebc8c2c997ea6fdcf467387d750143b82ff83be2c152a8c37de' /root/vm163-remediation-r1/metadata_only.py | sha256sum -c -
printf '%s  %s\n' '8c78295c163cade78d9d77cf4441b1ed8fb6e3489a24bea1e22a23d814e86805' /root/vm163-remediation-r1/artifact_transfer.py | sha256sum -c -
/opt/g6j-venv/bin/python -I -B /root/vm163-remediation-r1/metadata_only.py > /root/vm163-remediation-r1/metadata-before.json
cat /root/vm163-remediation-r1/metadata-before.json
sha256sum /root/vm163-remediation-r1/metadata-before.json
```

The helper opens **directories only**, counts every visible entry without aborting on a permission finding, does not follow symlinks, never opens/hashes regular credential/cache files, and bounds traversal. A permission error, race or traversal limit reports `complete=false`, never “empty”. Counts include link/special/hardlink indicators and candidate authentication filenames; filenames alone cannot establish that an actual key exists. Only aggregate metadata is output. The one cloud alias is counted as canonical-*syntax* only; r1 must separately validate its owner and target. Directory ACL metadata is flagged, but the helper is not a complete per-file ACL/effective-access proof or a universal credential detector.

Validate that the cloud count now reconciles with the reported38 files and23 potential-exposure matches; investigate differences without reading contents. A nonempty `.ssh/authorized_keys`, a private-key-like name, configuration or an unknown entry is **not eligible for empty-directory cleanup**. Even an empty `authorized_keys` file is an entry. Never cat, hash, copy, archive or deserialize those files. Systemd credential payloads remain an independent blocker even if their mounts later become private.

## 2. H2 — SSH and cloud disposition; choose before mutation

### SSH: preserve evidence, then distinguish empty directories

If each SSH path is a real empty directory, fully inventoried with expected owner, safe ancestors and permissions, capture its UID/GID/mode and scan result first. Absence of entries establishes only that no key is stored **there at that observation**, not that the VM has no credentials elsewhere. Fresh-image/import provenance is still required.

The installed r1 source unconditionally refuses either path's existence. There are two explicit choices:

1. Preserve both empty directories and request a future, separately versioned, regression-tested empty-directory policy correction. This plan does not change or approve any release; r1 remains NO-GO.
2. Only after a **new approval specifically authorizing removal of the two proven-empty directory objects**, use the following narrow operation. This is configuration cleanup supported by an empty inventory, not deletion of credential evidence. It is not authorized now. If the operator's preservation policy requires the directory objects themselves, choose option1.

```bash
# H2-SSH ONLY: recheck complete empty inventories and preserve metadata first.
# Execute from the already approved root console, with preparation writers quiescent.
rmdir -- /root/.ssh
rmdir -- /home/jarvis/.ssh
```

`rmdir` refuses nonempty directories and symlinks. Stop on the first failure; preserve any partial outcome. Never use `rm`, recursive removal, rename/quarantine or a bind mount to hide these paths. If any authentication material exists or history indicates imported credentials, stop; do not delete it to make preflight pass. After any approved empty-only removal, re-run the metadata report and r1 diagnostic. Returning these directory objects later would require a new approved, exclusive recreation using recorded ownership/modes, and would restore the r1 refusal; no automatic rollback is supplied.

### Cloud: current evidence does not justify an in-place “fix”

The reporting defect is confirmed: r1 computes its final cloud count only after a successful scan. Its first permission exception leaves `cloud_cache_files: 0`; `findings` still makes authorization refuse. This is misleading inventory, **not an authority bypass**. The independent diagnostic above supplies a complete/partial distinction without modifying the sealed release.

The23 matches are the scanner's conservative mode-based rule, not proof that23 secrets exist or that23 files were actually readable through every ancestor/ACL. Conversely, root ownership or restricting modes today cannot prove prior non-exposure. Cloud-init caches may contain original datasource inputs; `cloud-init clean` removes state and can trigger first-boot behavior again. Do not invoke it or run cloud-init query/status/debug/collect commands that may disclose cached data or logs. [Cloud-init cache documentation](https://docs.cloud-init.io/en/latest/development/internal_files.html), [clean command semantics](https://docs.cloud-init.io/en/latest/reference/cli.html).

**In-place continuation is defensible only if all of these are independently established:** reviewed installer/image and seed provenance; no imported production/external credentials; no unreviewed user-data/scripts executed; every flagged file's generator/classification and safe handling are accounted for from trusted records; no unresolved credential compromise; all lifecycle actors that may regenerate the files are understood. Preserve the pre-change metadata and every unknown cache file in place. A later permission operation would need an exact reviewed file list, expected inode/type/owner/mode, generator justification and post-change checks. A blanket `chmod -R`, cache deletion, moving it outside the scanner or adding an exception by filename is unacceptable. **No executable cloud chmod/cleanup command is offered for23 unidentified files.** Providing one now would invent security evidence.

If the matches turn out to be legitimate public OS bookkeeping, a source-backed scanner correction may be appropriate; it requires separate engineering approval, a new source digest and new VM release approval. Do not silently change r1. Any populated accepted cache still requires its current metadata digest and the exact approved provenance statement; the current failed/zero report cannot supply that digest.

**If provenance remains uncertain, a clean replacement VM is safer.** Preserve VM163 and its disk/evidence in place; do not overwrite, clone its unknown cache, wipe it, export unknown secrets or reuse its identity. Separately authorize a new VMID/UUID/disk and a reviewed offline installation using only the pinned public artifacts. Do not import the old home/cloud cache or secrets. Fresh OS provenance still must explain any installer-created cloud files, SSH directories and systemd credential mounts: a rebuild alone does not guarantee r1 acceptance. Approve preservation/snapshot handling explicitly; no new snapshot, power change, VM creation or disk operation is performed by this plan.

## 3. H3 — protected artifacts without a second3GB copy

Proceed only after the VM disposition is settled. Historical public export manifest SHA256:

`9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837`

Proposed source `/home/jarvis/gate6k-artifacts`; protected destination `/opt/g6k-offline`; failure staging path `/opt/.g6k-offline-stage-r1`. Require exactly131 public artifact records plus `ARTIFACTS.json`, matching the protected release's required versions; no extra files, links, nested directories, unsafe types/modes or unreviewed xattrs. No credentials are valid input to this operation. Hashes verify integrity, not independent publisher authenticity; retain the existing supply-chain provenance/risk review.

**Writer quiescence is a hard prerequisite.** End the preparation account's writing sessions/processes through separately approved human session handling. The root console must not be that account's remaining process. Inspect process identity metadata only, e.g. `ps -u jarvis -o pid=,comm=` and `ps -eo pid=,uid=,comm=` locally; never command arguments or environments. Account for root/other writers as well. An empty process listing is a point-in-time observation, not proof that no root service can write later. Existing writable descriptors or mappings survive rename/chown/chmod; the negative-control test demonstrates this. If writer exclusion cannot be established, **do not promote this user-owned export**. Rebuild or separately procure a clean protected copy with sufficient disk space instead; do not declare it immutable merely after chown.

The proposed helper performs `renameat2(RENAME_NOREPLACE)` on the same filesystem, never a copy fallback, then restricts ownership/modes on **only the exact verified inventory**. It checks all hashes before transfer, after ownership conversion and after final publication. File inodes and allocated blocks must remain identical; cross-filesystem `EXDEV`, existing stage/destination, hash errors or free-space failure stop and preserve state. It requires20GiB plus64MiB metadata headroom before starting, and at least20GiB after. Measure exact available bytes (`f_bavail`), not rounded “23GiB”. Recheck free space again immediately before qualification. The no-replace operation and surviving-descriptor limitation follow [Linux rename semantics](https://man7.org/linux/man-pages/man2/rename.2.html).

Do not use general `mv` with copy fallback, hardlinks (the verifier requires link count1), symlinks, bind mounts, broad recursive ownership repair or an unreviewed duplicate tree. The helper creates no approval and invokes no package installer.

**H3-only proposed command**, after all above conditions and separate exact transfer approval. It has not been run against any real artifact export:

```bash
set -euC
umask 077
/opt/g6j-venv/bin/python -I -B - <<'PY' > /root/vm163-remediation-r1/artifact-transfer.json
import json,os,pwd,sys
from pathlib import Path
assert os.geteuid()==0 and os.uname().nodename=='jarvis-security'
assert {p.name for p in Path('/sys/class/net').iterdir()}=={'lo'}
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()=='1d279e9b-12cb-4a02-8815-a682cb9457a9'
sys.path.insert(0,'/opt/g6k-preflight-r1/disposable')
from safety_preflight import verify_manifest
from offline_artifacts import required_artifacts,verify_artifacts
verify_manifest('/opt/g6k-preflight-r1','b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc')
sys.path.insert(0,'/root/vm163-remediation-r1')
from artifact_transfer import promote
expected='9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837'
result=promote('/home/jarvis/gate6k-artifacts','/opt/g6k-offline',expected,
    required_artifacts('/opt/g6k-preflight-r1'),source_uid=pwd.getpwnam('jarvis').pw_uid,owner_uid=0,owner_gid=0)
result['installed_verifier']=verify_artifacts('/opt/g6k-preflight-r1','/opt/g6k-offline',expected)
print(json.dumps(result,sort_keys=True))
PY
cat /root/vm163-remediation-r1/artifact-transfer.json
```

Success requires131 verified records, unchanged file inodes, no data copy, and free space≥21,474,836,480 bytes. The source export pathname intentionally ceases to exist, while its exact artifact bytes remain at the protected destination; retain the before/after record. This is not permission to move any other preparation/evidence files. On interruption, preserve whichever source/stage/final path exists; never rerun blindly, delete staging or move it back automatically. A reverse rename would not restore prior ownership, descriptor state or evidence history and requires a new review. Reboot does not constitute rollback proof.

## 4. H4 and H5 — media and mount propagation

After all reviewed helper/artifact transfer and evidence retention, explicitly authorize **normal unmount of the exact observed offline media** and human console detachment of that ISO from VM163. Do this before cloning a private mount namespace, which can otherwise retain its own copy of the mount. In the guest, list only metadata:

```bash
findmnt --kernel --list --noheadings --types iso9660,udf --output TARGET,SOURCE
```

If `/mnt/g6l-cd` is the approved currently mounted target, the H4 command is `umount -- /mnt/g6l-cd`. If `/mnt/g6k-update` is also mounted and separately listed/approved, its command is `umount -- /mnt/g6k-update`. Do not blindly run either against an unconfirmed target. Stop if busy; do not use lazy/forced unmount or kill services. The human then selects **Do not use any media** for the exact VM163 CD/DVD device in the trusted management console, only under separate hardware authorization. Recheck guest mounts; do not remove files or restart the VM automatically.

### Interpretation and recommended temporary scope

Shared propagation can be normal within a Linux guest. Systemd's upstream startup code makes the root mount recursively shared in typical non-container boots; that is not evidence of a Proxmox host filesystem passthrough. It does mean this runner's explicit gate refuses. [Systemd mount setup](https://github.com/systemd/systemd/blob/main/src/shared/mount-setup.c).

Private mounts neither receive nor forward propagation; changing only `/` non-recursively leaves existing nested mounts unchanged. Recursive handling must include `/boot`, all credential mounts and every other existing mount. Changing flags does not remove a host share, credential payload, media mount, bind subtree or unsafe permissions. [Linux shared-subtree semantics](https://docs.kernel.org/filesystems/sharedsubtree.html).

**Preferred least-mutation option H5-N:** after a specific policy approval for a private *qualification process-tree mount namespace*, create a mount-only namespace from the trusted root console with no user/PID/network namespace remapping:

```bash
# H5-N ONLY; enters a shell, never launches qualification automatically.
unshare --mount --propagation private -- /usr/bin/env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/root /bin/bash --noprofile --norc
```

Inside that shell, record `readlink /proc/self/ns/mnt` and `/proc/1/ns/mnt` and run the read-only H6 gate. The helper and all future qualification children must remain in that same namespace. The unchanged gate must see every relevant mount private and still inspect the real unchanged directories. **The guest PID1 namespace remains shared.** Do not report this as guest-wide remediation. If the original policy requires PID1/all guest namespaces private, H5-N is ineligible unless that scope is explicitly reviewed; use H5-G instead, not an unacknowledged workaround. External disk/network/no-credential attestation remains mandatory in either scope.

The namespace is temporary and lasts while processes/references retain it; closing only the parent shell does not necessarily destroy it if descendants survive. It is recreated and rechecked for each newly authorized run, not made persistent with a namespace bind mount. There is no persistent service, fstab edit or boot modification. No filesystem, account or evidence changes made *inside* it are undone by exit. Mount-only isolation does not hide shared underlying file contents or constrain a hostile root outside it. [util-linux unshare](https://man7.org/linux/man-pages/man1/unshare.1.html).

**Alternative H5-G, broader and not preferred:** only if guest-wide policy requires it and the console's mount namespace equals PID1's, separately approve this one-time guest operation:

```bash
# H5-G ONLY; NOT an additional step after H5-N.
test "$(readlink /proc/self/ns/mnt)" = "$(readlink /proc/1/ns/mnt)"
mount --make-rprivate /
```

It affects existing mounts recursively in that namespace, including the nested credential mounts, and can change how guest services see mount events. It does not convert other preexisting namespaces or prove hypervisor isolation. Revalidate all mounts and relevant service behavior; do not restart model/production services. `mount --make-rshared /` is **not** an exact rollback of original peer/master relationships. Preserve before/after metadata and stop if behavior differs. Neither option is independently kernel-qualified by this task.

**Reboot/persistence:** global runtime flags are not a reliable persistent configuration; a later boot or mount lifecycle can restore shared mounts. No persistence unit is proposed. Any reboot requires separate approval and invalidates prior boot/namespace/cloud metadata observations; do not reboot merely to try to clear findings. Systemd `PrivateMounts=yes` alone is not this gate's “all private” guarantee; its slave/incoming propagation may still violate the gate. Unit-specific private namespaces also have removable-media lifecycle implications. [systemd namespace controls](https://www.freedesktop.org/software/systemd/man/258/systemd.exec.html). Persistent systemd policy would be a new design/provisioning approval with real boot/service tests, not an automatic next step here.

## 5. H6 — final read-only gates and exact approval binding

Only after the disposition and authorized preparations, from the exact approved namespace/console, run this **read-only** gate. It cannot create the fixture, an epoch or the approval marker; it deliberately stops on any remaining finding.

```bash
/opt/g6j-venv/bin/python -I -B - <<'PY'
import grp,json,os,pwd,sys
from pathlib import Path
r=Path('/opt/g6k-preflight-r1')
sys.path.insert(0,str(r/'disposable'))
from safety_preflight import validate_environment,verify_manifest,validate_dependencies,validate_capacity
from environment_probe import inspect_environment_paths
from offline_artifacts import verify_artifacts
assert os.geteuid()==0 and os.uname().nodename=='jarvis-security' and os.uname().machine=='x86_64'
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()=='1d279e9b-12cb-4a02-8815-a682cb9457a9'
validate_environment(hostname=os.uname().nodename,interfaces=[p.name for p in Path('/sys/class/net').iterdir()],
    mountinfo=Path('/proc/self/mountinfo').read_text(),credential_paths=[],boot_source='/dev/sda2')
assert not (Path('/var/lib/g6j-disposable').exists() or Path('/var/lib/g6j-disposable').is_symlink())
count=verify_manifest(r,'b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc')
validate_dependencies(r);validate_capacity('/var/lib');validate_capacity('/opt')
a=verify_artifacts(r,'/opt/g6k-offline','9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837')
prep=pwd.getpwnam('jarvis');assert prep.pw_dir=='/home/jarvis' and prep.pw_uid!=0
roles=[pwd.getpwnam(n) for n in ('g6j-operator','g6j-service','g6j-agent')]
assert [e.pw_uid for e in roles]==[999,995,994]
assert len({0,*(e.pw_gid for e in roles)})==4
for e in roles:
    assert e.pw_shell in ('/usr/sbin/nologin','/sbin/nologin','/bin/false')
    assert set(os.getgrouplist(e.pw_name,e.pw_gid))=={e.pw_gid}
report=inspect_environment_paths(preparation_uid=prep.pw_uid)
print(json.dumps({'source_files':count,'artifact_count':a['artifact_count'],'paths':report,
    'mount_namespace':os.readlink('/proc/self/ns/mnt'),'qualification':'NOT_RUN'},sort_keys=True))
assert not report['findings'],'REMAINING_PATH_FINDINGS'
# A populated accepted cache still requires separately established human provenance.
PY
```

Expected618 source files,131 artifacts,127 pins, no path findings, actual reported UIDs, private distinct primary GIDs, non-login shells, no supplemental/admin memberships,≥20GiB free, no fixture. This is not a kernel cross-UID test. Human review must also establish no per-user sudo/polkit/admin grants (without dumping secret configuration), protected interpreter/venv ownership including resolved symlinks and writable paths, no leaked descriptors, and no unaccounted lifecycle actors. No real credentials are requested.

Preserved identities:

| Object | Exact identity |
|---|---|
| `/opt/g6j-release` | Historical Gate6K manifest `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03`; untouched |
| `/opt/g6j-venv` | Protected Python3.14.4,SQLite3.46.1,cryptography46.0.5,127 required distributions; untouched |
| `/opt/g6k-preflight-r1` | Manifest `b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc`; untouched |
| Replacement archive | `15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55` |
| Artifact record | `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837` |

### Approval-marker decision — separate human action, no creation command here

Require the independently retained signed/reviewed authorization to name VMID163, UUID above, pve, actual guest machine-id, exact Proxmox volume plus guest disk identifiers, approved console/session, new observation boot ID, chosen namespace policy/context, source/archive/artifact identities, actual cloud provenance, test scope and preservation policy. Do not insert unknown values, make up a disk/console identity, or convert “NO-GO” to approval. A rebuilt VM requires its own new identity and approval.

The existing parser accepts exactly these fields; namespace/boot review belongs in the external approval record referenced by the console/preservation record, not invented extra JSON keys:

- `machine_id`: actual32-hex guest value; `vmid`:163; `vm_uuid`:the confirmed UUID; `hypervisor_node`:pve; `disk_identity`, `operator_console`, `snapshot_preservation_policy`:real reviewed values, never placeholders or credentials.
- `scope=GATE6K_DISPOSABLE_ONLY`, `network=NO_NIC`, `release=/opt/g6k-preflight-r1`, `credentials=NONE`, `mounts=PRIVATE_ROOT_ONLY`, `test_scope=SYNTHETIC_MULTI_UID_NO_POWERCUT`.
- `source_manifest`, `archive_sha256`, `artifacts_sha256`:the exact hashes above. `boot_source=/dev/sda2` only after its private ext4 identity is reconfirmed.
- When the successful cache scan is populated, `cloud_cache_review` must contain **both** `provenance=FRESH_DISPOSABLE_IMAGE_NO_IMPORTED_CREDENTIALS` established from trusted history and the current accepted scan's `metadata_sha256`. Do not derive it from the failed zero report or invent it after chmod. If provenance is not supportable, do not create the marker.

Only a later explicitly authorized human may exclusively create `/etc/g6k-disposable-approved.json` as root:root0600, regular, single link. This task does not create it or supply an unattended creator. After such a separately approved creation, these are the exact **read-only** binding checks:

```bash
/opt/g6j-venv/bin/python -I -B - <<'PY'
import os,pwd,sys
from pathlib import Path
sys.path.insert(0,'/opt/g6k-preflight-r1/disposable')
from safety_preflight import read_approval,validate_approval
from environment_probe import inspect_environment_paths,require_paths
a=read_approval('/etc/g6k-disposable-approved.json')
assert Path('/etc/g6k-disposable-approved.json').lstat().st_gid==0
validate_approval(a,Path('/etc/machine-id').read_text().strip(),release='/opt/g6k-preflight-r1')
assert a['vmid']==163 and a['vm_uuid']=='1d279e9b-12cb-4a02-8815-a682cb9457a9' and a['hypervisor_node']=='pve'
assert a['source_manifest']=='b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc'
assert a['archive_sha256']=='15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55'
assert a['artifacts_sha256']=='9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837'
assert a.get('boot_source')=='/dev/sda2'
require_paths(inspect_environment_paths(preparation_uid=pwd.getpwnam('jarvis').pw_uid),a)
print('LOCAL_BINDINGS_MATCH; EXTERNAL_IDENTITY_REVIEW_REQUIRED; QUALIFICATION_NOT_RUN')
PY
```

Compare disk, console, boot/namespace and preservation values against the trusted external record separately; parser success cannot attest them. Keep the marker absent until every prerequisite supports its claims. A separate final authorization must name the exact future qualification command and namespace, four principals, synthetic-only scope and preservation rules. **No qualification launch command is included in this plan's executable blocks.** There is no permission for V2 retirement, V3 startup/succession/deployment, pilot admission, model operations or measurement.

## 6. Offline evidence and limits

The original618 source entries reverify locally. Proposed helper tests: **39 passed /0 failed**, under unprivileged Nexus LandlockABI8/seccomp with non-AF_UNIX networking denied. Tests cover the38/23 cloud shape, incomplete scans, empty/nonempty/link SSH cases, same-filesystem atomic no-replace moves, hash failures, hardlinks/FIFOs/symlinks, low-space refusal, EXDEV without copy, interruption preservation, and the open-writer negative control. Synthetic28-mount projections show all-shared and root-only-private refuse, all-private can pass topology, and private flags do not hide ISO/host shares/unsafe credential mounts. Projection is **not** a real mount operation.

No actual root chown, real `.ssh` removal, cloud permission change, artifact export move, mount/unshare, media detach, reboot, marker creation, VM setup or multi-UID qualification occurred. Fixture transfers use tiny synthetic public bytes and the same unprivileged UID; they do not prove root ownership exclusion,3GB transfer performance or VM free-space behavior. The public-source research supports mechanisms, not VM-state attestation. Helper source is a **proposal**, not an approved privileged package.

The historical7741/11/0 application regression remains preserved; no application/runtime/release files changed, so that suite was not rerun for this plan. Existing uncommitted documentation and loop log were retained. `evidence/proposal-tests-final.txt` contains actual test results; `SHA256SUMS` covers the plan, helper source and evidence. Independently retain its seal before any future human approval. No commit or push.

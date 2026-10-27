# Offline installation and fresh identity checkpoints

**Future console procedure. No PVE creation, upload, media attachment, guest installation or boot has been executed by this agent. Boot is currently NO-GO for memory.** All commands below are for the new identity bound in `VM164-PLAN.json`; they give no authority over VM163,162 or the AI server. No qualification launch or final approval-marker creator is supplied.

## 1. Provision stopped and retain actual identity

Use the live pressure/inspection/stopped-creation blocks in `VM164-PROVISIONING-PLAN.md`. Preserve PVE `/root/g6k-vm164-create-r1/` before proceeding. Check actual VM UUID `faeb1db8-0df9-482d-b3e4-f6ccc1602193`, disk serial `g6k164-12821f6b54a2`, the newly allocated downloads volume/path/inode and stopped/no-NIC hardware. These are planned identities until that console evidence exists. Do not substitute a VMID or attach an existing disk.

Upload the two ISO files from `MEDIA-PROVENANCE.md` to unused filenames in local ISO storage through the existing trusted Proxmox UI. They total9,272,885,248 bytes. Stop on a filename collision or hash difference. On PVE the exact read-only verification is:

```bash
python3 -I -B - <<'PY'
import hashlib,json,os,socket,stat,subprocess
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='pve'
items={
 'local:iso/ubuntu-26.04.1-g6k-vm164-r3.iso':'4161509164bcaff08506ad2ffcd52a6782eb34eb4b08d47f1bb8754016a07346',
 'local:iso/g6k-public-inputs-r1.iso':'8464ac2f1bb77ce9e29042b2fe6ae797992b420b7601fd0cfba8b13d42f10190'}
for volume,expected in items.items():
 p=Path(subprocess.check_output(['pvesm','path',volume],text=True).strip())
 st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==0 and st.st_nlink==1 and not st.st_mode&0o022
 with p.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
 assert actual==expected,'MEDIA_HASH_MISMATCH'
 print(json.dumps({'volume':volume,'bytes':st.st_size,'sha256':actual,'result':'VERIFIED_PUBLIC_BYTES_ONLY'}))
PY
```

Use `ATTACH-INSTALLER-CONSOLE.sh` only after stopped creation and successful upload checks. It binds UUID/serial/actual new disk inode, refuses an initialized disk, independently rehashes the protected installer ISO and uses the PVE config digest for the update. It attaches only ide2 and sets install-media-first boot order; it does not start or format anything.

## 2. Boot admission and installer

Do not start with the currently reported memory conditions. Obtain representative normal-load memory/PSI/swap evidence, inspect configured maxima/other commitments, and retain the stated physical reserve plus overhead. Rerun the current checks immediately before any eventual start. Existing GO covers safe new-VM installation after those conditions support it; passing a short quiet screen alone does not establish this. No automated start command is supplied in this packet.

Once safely admitted, select the trusted VM164 console and boot the reviewed r3 installer. It loads direct media autoinstall data, validates the planned DMI UUID and one virgin64GiB disk with exact serial, and refuses other hardware/signature states before formatting. A confirmation prompt may still require the human's console response; no kernel autoinstall override was added. Expect a BIOS/direct ext4 installation using only original public package inputs. Online access cannot succeed because there is no NIC.

The target source omits the authenticated empty SSH directory and already disables cloud-init. The late target guard refuses regenerated root or preparation SSH paths; it does not remove them. It also checks actual target ext4/disk parentage, creates the three distinct locked/non-login test roles and records machine-id/actual role IDs in root-owned0600 `/var/log/g6k-install-origin.json`. The normal successful installer powers off only the new guest. A failure must remain preserved; never format again, delete a regenerated directory, clean cloud-init or retry unattended. r3's virgin-signature guard blocks a second installation over an initialized disk.

After successful installation, through the independently identified stopped164 config, change ide2 to the public-data ISO and boot order to disk. This is an exact identity-checked **future** block, not a step to run now:

```bash
python3 -I -B - <<'PY'
import json,os,socket,subprocess
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='pve'
def get(path):return json.loads(subprocess.check_output(['pvesh','get',path,'--output-format','json']))
c=get('/nodes/pve/qemu/164/config')
assert c['smbios1']=='uuid=faeb1db8-0df9-482d-b3e4-f6ccc1602193'
assert 'serial=g6k164-12821f6b54a2' in c['scsi0'].split(',')
assert c['ide2']=='local:iso/ubuntu-26.04.1-g6k-vm164-r3.iso,media=cdrom'
assert get('/nodes/pve/qemu/164/status/current')['status']=='stopped' and int(c.get('onboot',1))==0
subprocess.run(['qm','set','164','--digest',c['digest'],'--ide2','local:iso/g6k-public-inputs-r1.iso,media=cdrom','--boot','order=scsi0'],check=True)
print('NEW_VM_ONLY_MEDIA_UPDATED; NOT_STARTED')
PY
```

Use this only after the public ISO hash was independently checked and the installer actually completed. Preserve any installation failure instead of swapping media to conceal it.

## 3. Actual guest console and identity

Installed root and preparation/test passwords are locked; no shared password, imported key or persistent autologin is introduced. A documented credential-free bootstrap option is a **one-boot** GRUB edit adding `systemd.debug_shell=1`, followed by tty9 in the trusted VGA console. It exposes an unauthenticated root shell on that guest tty for that boot, within the existing trusted-Proxmox-console boundary. Record this choice and actual boot arguments; it is not enabled by the supplied ISO/console blocks, must not be made persistent, and does not itself approve a qualification context. Actual boot/console behavior remains untested. See [systemd debug generator](https://www.freedesktop.org/software/systemd/man/latest/systemd-debug-generator.html). Do not import credentials merely to work around a console issue.

From the actual booted replacement's trusted root console, collect these read-only metadata values (never from a live installer/chroot or Nexus):

```bash
id -u
hostname -s
date -u +%FT%TZ
cat /etc/machine-id
cat /sys/class/dmi/id/product_uuid
cat /proc/sys/kernel/random/boot_id
readlink /proc/self/ns/mnt
readlink /proc/1/ns/mnt
lsblk --output NAME,TYPE,SIZE,FSTYPE,UUID,PARTUUID,PKNAME,MODEL,SERIAL,MOUNTPOINTS
findmnt --kernel --list --noheadings --output TARGET,SOURCE,FSTYPE,PROPAGATION
ip -brief link
ip route show table all
ip -6 route show table all
df -B1 --output=avail,target /opt /var/lib /home/jarvis
stat --printf='%u %g %a %s %h\n' /etc/cloud/cloud-init.disabled
cat /var/log/g6k-install-origin.json
```

These cats read public identity/build records, not cloud cache or credentials. Match DMI UUID, actual disk serial/parent/volume/filesystem and console session against PVE externally. Expect hostname `jarvis-g6k-164`, newly generated32-hex machine-id,64GiB new disk, private ext4 root and only lo/no default routes. Do not invent `/dev/sda2` as a boot source; the direct layout may have no separate `/boot` mount. Record actual root and any boot filesystem UUIDs. Record actual role UIDs/private GIDs, non-login shells, locked status and no supplemental/admin grants using metadata only.

Any `.ssh` path, unexpected cloud data, credential payload, imported home, wrong identity or extra mount is a preserved finding and stops readiness. Do not fix it by deleting/restricting unexplained contents. The installer source has no cloud cache, but Subiquity can generate target seeds: retain the known public input/generator provenance and run unchanged r1's metadata inspection later. Shared mount propagation is expected under normal systemd boot and remains a separate NO-GO until its explicit scope approval; do not change it during these checks.

## 4. Offline preparation from public media

Confirm the only optical device is the externally verified public ISO. If not already mounted, prepare a fresh mountpoint and mount that exact optical device read-only,nosuid,nodev,noexec. For the expected one optical device `/dev/sr0`, after that identity check:

```bash
test "$(id -u)" = 0
test ! -e /mnt/g6k-public
mkdir -m 0755 /mnt/g6k-public
mount -t iso9660 -o ro,nosuid,nodev,noexec /dev/sr0 /mnt/g6k-public
```

Media transfer is not a ready preflight state. Independently compare the transport manifest SHA256 `922b82cec3076e01577e410ac68c2d74f92d7d74f1886e215b1f83ed75ae1341`, then verify all139 input checksums from that mount and reject extras/links using the preserved exact inventory. Optical POSIX ownership may show Nexus's UID; confirm preparation-user read access. If read access differs, do not broadly change guest permissions or remount arbitrary paths; a fresh protected copy of only the verified public bootstrap inputs can be explicitly made readable for the preparation user. The media itself remains read-only.

The pinned bundle extractor and offline installer both **refuse root**. For the already created `jarvis` preparation account, only after checking actual ownership/non-writable ancestors of its fresh home and the signed OS Python3.14.4, the documented unprivileged fixture procedure is:

```bash
# Root console invokes only the exact unprivileged preparation identity.
# First verify extract_bundle.py SHA256 = 13792921e64036de94af62a95fddd343fbf37063b9dfd9c150764413edb2feeb
# and gate6l-bundle-r1.tar SHA256 = 228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00.
runuser -u jarvis -- /usr/bin/python3 -I -B /mnt/g6k-public/extract_bundle.py /mnt/g6k-public/gate6l-bundle-r1.tar /home/jarvis/gate6l-bundle 228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00
runuser -u jarvis -- /usr/bin/python3 -I -B /home/jarvis/gate6l-bundle/tools/verify_bundle.py /home/jarvis/gate6l-bundle 1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390
runuser -u jarvis -- /usr/bin/python3 -I -B /home/jarvis/gate6l-bundle/tools/install_offline.py 1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390
```

Stop/preserve on any nonzero result, wrong interpreter, inadequate space, source mismatch or preexisting destination/work. These are a fresh unprivileged fixture build, **not** protected `/opt/g6j-venv` provisioning and not multi-UID qualification. Never run root from a preparation-writable runtime, edit the sealed helpers to remove refusals, globally install all debs or copy VM163's environment. Protected runtime materialization/relocation still needs its separately reviewed exact implementation, writer exclusion and import/native-library path validation; that remains pending and is not replaced with blanket chown.

For the corrected source, use only the pinned archive `15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55` and pinned safe extractor `31f77b42d6ee41f73abef56f8a59d5191a8695686cc2e79ced28236b623639d8`. Root must stage those exclusively under a new protected directory and verify before execution; original [safe extraction procedure](../p7-b2-gate6k-vm163-preflight-compatibility/OFFLINE-VM-UPDATE-PROCEDURE.md) supplies the reviewed extractor semantics, but its old hostname/UUID/disk assertions must never be reused for164. Require manifest `b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc` and all618 source entries in `/opt/g6k-preflight-r1`.

The read-only public ISO also contains the complete flat131 artifacts and their exact manifest `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837`. A new root-owned `/opt/g6k-offline` may be constructed exclusively by copying those pinned public media files and independently verifying the full inventory/hash/ownership afterward. This avoids promoting VM163 or a user-writable export; preserve partial failures and never overwrite a destination. All ancestors and interpreter/native backing paths must be protected, including resolved symlinks. Keep at least21,474,836,480 available bytes after complete setup and immediately before any later qualification; measure exact available bytes, not rounded df output.

## 5. Stop at metadata-only readiness

Run unchanged source/artifact/dependency/path/environment/capacity checks from the protected replacement runtime only after it exists. Keep the final approval marker absent. Supply actual boot-source policy to unchanged `validate_environment`; the informational `preflight_report.py` has a historical VM163 `/dev/sda2` assumption and cannot attest this new disk. Preserve findings and a complete metadata inventory without reading credential/cache contents.

Normally unmount only the exact observed public-media target after all transfer/verification, stop if busy, then detach only VM164's optical media through its identity-checked PVE configuration. Record the guest and hypervisor observations. Do not force/lazy-unmount, stop services or hide credential mounts. Approval of temporary qualification-process mount scope versus guest-wide propagation policy is still explicitly outstanding. No private namespace or propagation mutation is included here.

Guest preflight, protected runtime/artifacts, identity/console/supplier review and scope approval must all precede any later separately authorized final marker. Privileged qualification remains another explicit authorization. Preserve VM163 running and unchanged; this packet supplies no lifecycle command for it.

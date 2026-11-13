# Host facts and mandatory refreshes

Source: user-supplied verified facts for pve. They are accepted as reported;
Codex did not connect to pve or independently remeasure them. They describe a
prior inspection and cannot satisfy a later session's freshness requirement.

| Reported fact | Value | Required future refresh |
|---|---|---|
| Node | pve | Console identity, /etc/hostname, uname, manager virtualization/context |
| pve-manager | 9.2.5 | Exact dpkg metadata and approved binary/library custody |
| qemu-server | 9.2.1 | Exact dpkg metadata; qm/pvesh file custody only, no VM tool execution |
| pve-qemu-kvm | 11.0.2-2 | Exact dpkg metadata |
| systemd | 257.13-1~deb13u1 | Package and systemd-run version, exact matching installed interfaces |
| Python | 3.13 | Exact patch version, executable path/resolved chain/hash |
| Available root-owned programs | systemd-run, systemctl, python3, pvesh, pvesm, qm | Actual paths, all symlinks/ancestors, mode/ACL, file capabilities and SHA256; prior report does not supply hashes |
| Clocks | MONOTONIC and BOOTTIME readable | Paired samples, uncertainty, boot ID, actual output convention |
| nobody | UID/GID65534 | Name/numeric mapping, NSS sources, all groups, process census and authority denial review |
| nobody activity | No observed active processes | Fresh census; errors or unknown UID sharing block |
| /opt | root:root0755 | Ancestry/ACL/default-ACL and inode custody |
| /opt/jarvis-vm164-r3-stage2 | Absent at last inspection | Fresh absence including dangling symlinks, checked exclusively at creation |
| Stage2 loaded units | None found at last inspection | Loaded units, all search-path files/masks/aliases, exact pair and pending job collisions |
| VM164 | Reported STOPPED | Keep unchanged/no NIC. No VM status query or operation belongs to this packet. Operator maintenance freeze attests preservation; no new measured VM status is claimed. |

Stable content pins independently reverified offline on Nexus:

- R3 source tree: `43ea91000e251b9cf34fadf0466cb5135042a3232686c155de1b4ab5ee1ad3d1`.
- Public callback source: `a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa`, 2441 bytes.
- R3 packet manifest: `dd03f4fc5c3b7bf0cd7a5a5beebbabdad5e06ffd4397ab114af280d6fcfc15ea`.
- Approved future callback location: `/opt/jarvis-vm164-r3-stage2/canary.py`.

Mandatory unknowns: live boot UUID, current kernel, exact Python patch, all binary
hashes/resolved paths/ACLs, installed matching manual/source hashes, actual clock
convention, WakeSystem support, callback privilege denial, sudo/polkit/PVE policy,
complete private credential metadata inventory, new session nonce, exact UTC
start/expiration, BOOTTIME anchor, evidence destination/recorder custody, operator
and independent reviewer identities, root-controlled staged source path, all
unit namespace/search path collisions and post-trial results.

R3 historically pins kernel `7.0.14-6-pve`; this is not a new verified host fact.
Capture the actual kernel, compare to that candidate pin and block R3 applicability
if different. Do not “refresh” the sealed R3 EXPECTED constant. Missing auxiliary
getfacl/sudo/journalctl/dpkg-query paths or docs block the relevant step; this
packet does not authorize installation to satisfy them.

No synthetic fixture date/boot ID/hash/uptime/account assertion is actual host
evidence. Templates retain null for unknowns. The offline tests deliberately use
synthetic future timestamps and a historical suspend offset; they are labeled and
never copied into the command catalogue or live-results template as observations.

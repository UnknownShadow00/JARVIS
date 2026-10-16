# VM identity verification

Addendum to Gate 6F (report `tasks/p7-b2-gate6f-v3-release-qualification/FINAL-REPORT.md`, seal `df3090b9…`). Read-only. Captured 2026-10-15 ~19:12–19:20Z.

## What was established from the guests

| Property | Nexus | JARVIS Core |
|---|---|---|
| IP (ens18) | 192.168.0.101 | 192.168.0.162 |
| Hostname | `nexus-services` | `jarvis` |
| NIC MAC (ens18) | `bc:24:11:61:2e:56` | `bc:24:11:7b:01:3d` |
| Platform | QEMU i440FX, KVM | QEMU i440FX |
| machine-id | different (in `evidence/*-identity.txt`) | different |
| Current boot | 2026-10-15T17:27:43Z | 2026-10-15T03:42:45Z |
| vCPU / RAM, previous boot | 4 / 8,388,064 KiB | 4 / 8,388,064 KiB |
| vCPU / RAM, current boot | **6 / 12,517,856 KiB** | 4 / 8,388,064 KiB (unchanged) |
| qemu-guest-agent | installed, active | **not running** (`inactive`) |

Both MACs carry the `BC:24:11` prefix Proxmox uses for generated NICs. That supports "Proxmox VM", not a VMID.

The two guests are different machines: different hostnames, machine-ids, MACs, boot histories and resources. The Core power event is recorded in Core's own journal (`_HOSTNAME=jarvis`, boot `3a86fab9…`). It is not a Nexus record.

## What was NOT established: VMID, node, VM name

Proxmox access from this environment is not available. Exactly one BatchMode, publickey-only probe each was made to `192.168.0.50` as the default user and as `root`, with strict host-key checking. Both returned `Permission denied (publickey,password)`. No password was tried, no key enrolled, no known_hosts changed, and the Proxmox API (8006) was not contacted.

The guest SMBIOS UUID (`/sys/class/dmi/id/product_uuid`) is root-only on both guests and was not read. The VMID, node and Proxmox VM name of each guest are therefore **UNVERIFIED**. The historical "AI server VM 200" label was not applied to either VM.

## Human-only, read-only commands for the operator's trusted `.50` console

Map each VM by MAC (two independent identifiers: MAC and the guest's own hostname/IP):

```
qm list
for id in $(qm list | awk 'NR>1{print $1}'); do echo "== $id"; qm config $id | grep -E '^(name|cores|sockets|memory|balloon|net0|agent|onboot):'; done
pvesh get /cluster/resources --type vm --output-format json-pretty | grep -E '"(vmid|name|node|status|uptime)"'
```

Expected: one VM with `net0` MAC `BC:24:11:61:2E:56` (Nexus; should now show 6 cores / ~12 GiB) and one with `BC:24:11:7B:01:3D` (Core; 4 cores / 8 GiB; no `agent: 1` or agent not running in the guest).

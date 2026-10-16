# Nexus (192.168.0.101) maintenance timeline

Source: Nexus's own systemd journal, read locally (this task runs on Nexus). Excerpts are in `evidence/nexus-maintenance-excerpt.log` and `evidence/nexus-identity.txt`. All times are UTC. The host's local zone is CDT (UTC−5).

| UTC | Event | Source |
|---|---|---|
| 2026-10-10T22:30:50Z | Previous boot begins: 4 vCPU, 8,388,064 KiB | kernel `smp:` and `Memory:` lines, boot `d2738c5c…` |
| 2026-10-13/14/15 ~02:04Z | `guest-fsfreeze` then `guest-fsthaw` daily. Pattern of a scheduled hypervisor backup with the guest agent; not a power operation | qemu-ga |
| **2026-10-15T03:30–03:50Z** | **No power, shutdown or guest-agent shutdown entry on Nexus** (count 0). Nexus stayed up through the Core event | journal |
| 2026-10-15T17:03:13.142Z | `qemu-ga: guest-shutdown called` (preceded by `guest-ping` at 17:03:13.042Z) | qemu-ga |
| 2026-10-15T17:03:13.147Z | `The system will power off now!` | systemd-logind |
| 2026-10-15T17:03:16Z | Journal stopped (clean shutdown) | journald |
| 2026-10-15T17:27:43Z | New boot `bff2e037…`: **6 vCPU, 12,517,856 KiB** | kernel |

## Interpretation

- Nexus was shut down through the QEMU guest agent. That is the mechanism Proxmox uses for a "Shutdown" when the VM's agent option is on: the hypervisor called it, not anything in the guest.
- The VM stayed off for about 24.5 minutes, and came back with +2 vCPU and +4 GiB RAM. That is consistent with the operator's stated RAM/CPU upgrade. Resource changes of this kind usually need a full power-off.
- This is about **13 h 21 m after** the Core event. The Nexus maintenance did not coincide with, and did not cause, the Core power-off.
- Who issued the guest-agent shutdown is not visible from the guest. It is consistent with the operator's statement, and the Proxmox task log would confirm it.

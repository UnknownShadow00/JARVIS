# JARVIS Core (192.168.0.162) power-event timeline

Source: Core's own journal, read over the existing `jarvis` key-based SSH with strict host-key checking. Filtered excerpts are in `evidence/core-power-event-excerpt.log` and `evidence/core-interactive-logins-2026-10.log`. Source ports, session numbers and key fingerprints are redacted. All times are UTC, and Core's journal is in UTC.

Previous boot `3a86fab97ae74fc88cd1bb2f8b450294` ran from 2026-09-07T23:23:16Z to 2026-10-15T03:42:19Z, on kernel 7.0.0-31. Kernel 7.0.0-38 had been installed by apt on 2026-10-08, so a reboot had been pending for about 7 days.
Current boot `2486e474da434cdc94c883b2cc52a763` started 2026-10-15T03:42:45Z on kernel 7.0.0-38. No boot since.

| UTC | Event |
|---|---|
| 02:01:30Z | Interactive **password** SSH login as `jarvis` **from 192.168.0.50** (the Proxmox management node) |
| 03:31:05Z | Key-based login from 192.168.0.101 (Nexus automation; 0.3 s session, one of 4,304 such logins since Oct 1) |
| 03:32:59Z | The 02:01:30Z session from .50 disconnects ("disconnected by user") |
| 03:39:55Z | New **password** SSH login as `jarvis` from **192.168.0.50** |
| — | No `sudo`, no polkit authentication, no other privileged action recorded in the previous boot since 2026-10-14 (count 0) |
| **03:42:17.027Z** | `systemd-logind: Power key pressed short.` → `Powering off...` |
| 03:42:17.258Z | `System is powering down.` |
| 03:42:17.267Z | The .50 SSH session is terminated by SIGTERM as part of shutdown |
| 03:42:17.447Z | `Stopping user@1000.service` |
| 03:42:17.456Z | `Stopping jarvis.service - JARVIS Core backend` (user manager, SIGTERM) |
| 03:42:17.597Z | V2 audit `server_stop` |
| 03:42:17.656Z | D09 `controller.sqlite3` last modified (epoch close + `OPERATOR_STOP`) |
| 03:42:17.732Z | V2 terminal backup bundle `62f417a2…` created (CLOSED_COMPLETE, 0 attempts) |
| 03:42:17.767Z | `Finished server process [594042]` |
| 03:42:17.814Z | `Stopped jarvis.service` (clean; Result=success) |
| 03:42:19.108Z | `systemd: Shutting down.` → filesystems synced → journal stopped 03:42:19.182Z |
| **03:42:45.870Z** | Kernel starts (new boot). Gap of about 26.5 s from the last record and about 28.8 s from the power key |
| 03:42:51Z | User manager for `jarvis` starts (linger=yes). `jarvis.service` is **not** started (disabled, Restart=no) |
| 03:43:07.989Z | sshd listening |
| **03:43:10.760Z** | **Password** SSH login as `jarvis` from **192.168.0.50**, **2.8 s after sshd came up** |
| 03:43:22.683Z | That session disconnects ("disconnected by user"). No sudo, no unit start |

## Findings

1. **The event belongs to Core.** It is recorded under Core's hostname and boot ID. Nexus has no power entries in that window.
2. **Mechanism: ACPI power button.** On a VM, "Power key pressed short" is an input event from the virtual ACPI power button. Only the hypervisor (QEMU) can inject it. An in-guest `systemctl poweroff` does not log a power-key press, and no sudo or polkit action was recorded. Core runs **no** qemu-guest-agent, so a Proxmox "Shutdown" or "Reboot" falls back to exactly this ACPI request. Nexus, which has the agent, logged `guest-shutdown` instead.
3. **The guest powered off rather than rebooting:** logind ran "Powering off". The VM was therefore started again from outside about 26 s later. That matches either a Proxmox "Reboot" (which on a non-agent VM is ACPI shutdown followed by an automatic start) or a "Shutdown" followed by a manual "Start". The guest cannot tell these apart.
4. **The guest shutdown was clean.** Services were stopped in order, filesystems synced, and the journal closed.
5. **JARVIS V2 stopped only as part of the guest shutdown.** It received SIGTERM from the user manager, its lifespan hook ran, and the process exited normally. There was no crash, no restart before the event and no restart after it. Its run (5 d 6 h) began 2026-10-09T21:25:32Z.
6. **Human-activity correlation:** an interactive password session from the Proxmox node was open on Core when the power key fired. A new password session from the same node arrived 2.8 s after Core's sshd returned. That pattern fits a person at the Proxmox node rebooting Core and immediately checking it, and the same node had a pattern of interactive password sessions on Oct 8, 9, 10, 13 and 15. It is **corroborating, not proof**: it identifies the source host (.50) and the guest account (`jarvis`), not the person, and not the Proxmox account that issued the VM operation.

The 26-second gap is the VM's power-off/power-on time. It says nothing about why the VM was shut down, and nothing about how long V2 would take to start (V2 was never started).

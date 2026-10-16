# Proxmox audit correlation

## Status: NOT PERFORMED, because no trusted access exists from this environment

No Proxmox task log, `pveproxy` access log or node journal was read. The Proxmox side of every event below is **unverified**. No Proxmox events are invented here.

| Event | VMID | Node | UTC | Operation | UPID | Initiator | Outcome | Evidence |
|---|---|---|---|---|---|---|---|---|
| Core ACPI power-off | unverified | unverified | 2026-10-15T03:42:17Z | ACPI powerdown, from the guest's view | none | unknown | guest off at 03:42:19Z | Core journal only |
| Core power-on | unverified | unverified | ≤03:42:45Z | start (or the second half of a reboot) | none | unknown | booted | Core journal only |
| Nexus guest-agent shutdown | unverified | unverified | 2026-10-15T17:03:13Z | agent shutdown | none | unknown | guest off at 17:03:16Z | Nexus journal only |
| Nexus resource change | unverified | unverified | between 17:03:16Z and 17:27:43Z | cores 4→6, memory 8→~12 GiB | none | unknown | visible in guest | Nexus kernel |
| Nexus power-on | unverified | unverified | ≤17:27:43Z | start | none | unknown | booted | Nexus journal only |

## Human-only, read-only commands (operator's existing `.50` console)

First, identify the VMIDs with the commands in `VM-IDENTITY-VERIFICATION.md`. Then, with `<CORE>` and `<NEXUS>` as the VMIDs:

```
# Cluster task index around both events (UPID, type, user, status)
pvenode task list --since $(date -d '2026-10-15 03:30Z' +%s) --until $(date -d '2026-10-15 03:50Z' +%s) --output-format text
pvenode task list --vmid <CORE>  --since $(date -d '2026-10-14 00:00Z' +%s) --output-format text
pvenode task list --vmid <NEXUS> --since $(date -d '2026-10-15 16:30Z' +%s) --output-format text

# Detail of each UPID found (operation type and initiating account are inside the UPID)
pvenode task log <UPID>
pvenode task status <UPID>

# Config history: did Core's resources change? (Nexus's should.)
journalctl -u pvedaemon -u pveproxy --since '2026-10-15 03:30:00 UTC' --until '2026-10-15 03:50:00 UTC' --no-pager | grep -E 'qmreboot|qmshutdown|qmstart|qmstop|update VM'
journalctl -u pvedaemon -u pveproxy --since '2026-10-15 16:50:00 UTC' --until '2026-10-15 17:30:00 UTC' --no-pager | grep -E 'qmreboot|qmshutdown|qmstart|update VM'

# Rule out HA, node restart and automation
ha-manager status
journalctl --list-boots --no-pager | tail -3
grep -rE 'qm (shutdown|reboot|stop|start)|pvesh .*status/(shutdown|reboot)' /etc/cron* /etc/pve/jobs.cfg 2>/dev/null
```

Interpretation, to be filled in by the operator:

- A `qmreboot` UPID for `<CORE>` near 03:42:17Z means "Reboot" was used. A `qmshutdown` followed by `qmstart` means two separate actions.
- The `user@realm` field in the UPID is the authenticated account. It proves which **account** acted, not which person.
- No task at all for `<CORE>` would point to a CLI `qm`/`kvm monitor` path, or to log rotation. That should be recorded as a limitation, not filled in.
- Do not paste API tokens, tickets or session cookies into the addendum. UPIDs and account names are enough.

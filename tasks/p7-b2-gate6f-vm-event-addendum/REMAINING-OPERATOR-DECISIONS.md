# Remaining operator decisions, in order

**0a. (NEXT) Attribute the Core event from the Proxmox side.** Run the read-only commands in `VM-IDENTITY-VERIFICATION.md` and `PROXMOX-AUDIT-CORRELATION.md` on the `.50` console. Record:
- each VMID, node and name, matched by MAC;
- the UPID(s) for Core around 2026-10-15T03:42:17Z, giving `qmreboot` versus `qmshutdown`+`qmstart`, the account, and the outcome;
- the UPID(s) for the Nexus shutdown, config update and start around 17:03Z–17:27Z;
- whether any HA, cron or job entry targets Core.

Then state whether *you* issued the Core reboot. With a matching UPID under your account, the classification becomes "CONSISTENT WITH OPERATOR MAINTENANCE — ATTRIBUTION SUPPORTED".

**0b. Decide V2's disposition.** Choose one:
- (i) **Retire** epoch `606a991a…` under the limited "unattributed-shutdown zero-use retirement" exception in `V3-SUCCESSOR-IMPLICATIONS.md`. The exception is not approved by this addendum.
- (ii) **Keep V2 stopped** with no successor for now. This is the current state and needs no action.

Restarting the existing V2 in pilot mode is **not** a way to get a fresh pilot: its controller refuses `PILOT_EPOCH_ALREADY_EXISTS`, and any restart is outside this addendum.

**0c. Operational hygiene, optional, operator's call.** Core has no qemu-guest-agent. Every Proxmox Shutdown/Reboot therefore arrives as an anonymous ACPI power key. Installing the agent, or tagging Core in Proxmox as "pilot host: no reboot without checklist", would make future events attributable. This addendum changes nothing.

Then the Gate 6F sequence continues unchanged:

1. Experiment contract X1–X11 (including the normal-responder `num_ctx` 8192 proposal G6F-LP-2).
2. Independent AI-host (192.168.0.200) and legacy endpoint/model identity attestation. Still PENDING.
3. OS-identity / privilege and protected-root (antirollback) design, plus a disposable-VM qualification.
4. Retirement and successor authorization, using the signed verb from H-1–H-3.
5. V3 install and a new Gate 5.
6. Pilot permits.

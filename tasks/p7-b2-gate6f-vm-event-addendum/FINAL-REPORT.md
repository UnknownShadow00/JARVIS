# Gate 6F addendum — VM shutdown investigation, final report

Addendum to the Gate 6F report `tasks/p7-b2-gate6f-v3-release-qualification/FINAL-REPORT.md` and evidence seal `df3090b9e459b192dc7c23a6bd8113ce4d5d9814c7e370dcad27bbcf554bda06`. Both are unchanged; the seal was re-verified (all members OK) on 2026-10-15 ~19:13Z.

This was read-only infrastructure investigation, run by Claude on Nexus. There was no restart, no reload, no production/Proxmox/SSH-trust change, no credential read, no model request and no push.

**JARVIS P7 GATE 6F ADDENDUM — VM EVENT CONFIRMED, OPERATOR ATTRIBUTION UNRESOLVED**

Classification: **2. EXPLAINED VM OPERATION — HUMAN ATTRIBUTION UNCONFIRMED.**

## Answers

1. **Nexus VMID/node:** **unverified.** There is no Proxmox access from this environment. The guest is identified by hostname `nexus-services`, IP .101 and MAC `bc:24:11:61:2e:56`.
2. **Core VMID/node:** **unverified**, for the same reason. The guest is identified by hostname `jarvis`, IP .162 and MAC `bc:24:11:7b:01:3d`. Exact `.50` commands to resolve both are in `VM-IDENTITY-VERIFICATION.md`.
3. **Nexus restart for the RAM/CPU change:** confirmed from the guest. A qemu-guest-agent `guest-shutdown` ran at 2026-10-15T17:03:13Z, the guest was off about 24.5 min, and it booted at 17:27:43Z with **4→6 vCPU and 8→~12 GiB**. Nexus had **no** power event at 03:42Z; it had been up continuously since 2026-10-10.
4. **Core timeline:** password SSH login from .50 at 03:39:55Z → **ACPI "Power key pressed short" at 03:42:17.027Z** → clean power-off (V2 SIGTERM-stopped 03:42:17.456–.814Z; journal closed 03:42:19.18Z) → kernel boot 03:42:45.87Z → sshd up 03:43:07.99Z → password SSH login from .50 at 03:43:10.76Z (12 s, no sudo). Core's resources are unchanged at 4 vCPU / 8 GiB. The kernel moved 7.0.0-31 → 7.0.0-38, which had been pending since the 2026-10-08 apt install. Details are in `JARVIS-CORE-POWER-EVENT-TIMELINE.md`.
5. **Did Proxmox initiate an operation against Core?** Almost certainly the hypervisor: on a VM, only QEMU can raise the ACPI power button, and the VM was powered on again from outside. **Which Proxmox operation it was (Reboot, or Shutdown+Start), whether it came from GUI, API or CLI, and the UPID: not verified.**
6. **Initiating account/mechanism:** the mechanism is a hypervisor ACPI powerdown plus an external start. Core has no guest agent, which is why this is not a `guest-shutdown` like Nexus's. The Proxmox account is **unknown**. Correlating, but not attributing: an interactive password session as guest user `jarvis` **from the Proxmox node 192.168.0.50** was open at the moment of the power key, and another arrived from .50 2.8 s after Core's sshd returned.
7. **Operator attribution:** **plausible, not proven.** The evidence fits a person at the Proxmox node rebooting Core and checking it, possibly to apply the pending kernel. It identifies a source host and a guest account, not a person. It is not a security incident on this evidence.
8. **V2 now:** `jarvis.service` inactive/dead, MainPID 0, NRestarts 0, Restart=no, disabled, not started in the current boot. HEAD `bd53dbc7…`, config `00d7b460…`, 0 source mismatches. Epoch `606a991a…` CLOSED_COMPLETE. 0 attempts, 0 submissions, 0 D04 receipts. D06 current/last None, no remote unknown. Backups valid, including the **terminal backup `62f417a2…`** (created during shutdown; Gate 6F listed but did not verify it), which is logically identical to the live D09. See `V2-CURRENT-STATE.md`.
9. **Historical V2 `OPERATOR_STOP`:** attributable to a mechanism (lifespan default reason on SIGTERM during the guest power-off), **not** to an operator decision. The label overstates intent; the CLOSED_COMPLETE state is truthful. Nothing was rewritten. See `OPERATOR-STOP-SEMANTICS.md`.
10. **V3 successor design:** handles the scenario correctly. The attribution is fixed to `UNATTRIBUTED_V2_SHUTDOWN_HOOK`, retirement exists only in a new operator-signed payload, there is one successor, and the 4-attempt ordinal table is durable. A limited "unattributed-shutdown zero-use retirement" exception is specified but **not** approved. See `V3-SUCCESSOR-IMPLICATIONS.md`.
11. **New engineering defect:** **none.** There is no isolated fix, and candidate `ff2444df…` is unchanged and re-verified (29/29 members; full 596/596). Four transition hardening items (H-1 live-vs-archive proof, H-2 config/archive digests in the signed payload, H-3 a signed succession verb, H-4 mechanism-specific stop codes in V3) are recorded for the next engineering step.
12. **Updated Gate 6 prerequisites:** 0a Proxmox-side attribution (new), 0b V2 disposition, then X1–X11, AI-host/legacy attestation, OS identity/protected root, signed retirement/successor (now including H-1–H-3), V3 install and new Gate 5, pilot permits. The Gate 6F technical results stand as reported: focused 303 passed, full 7,469 passed / 11 deselected / 0 failed, 0 real provider transmissions. They were not rerun because nothing changed.
13. **Evidence:** `tasks/p7-b2-gate6f-vm-event-addendum/` (workspace, Nexus), mirrored to Core `/home/jarvis/.hermes-poc/evidence/p7-b2-gate6f-vm-event-addendum/`. The seal is the SHA-256 of `SHA256SUMS`, reported separately in `EVIDENCE-MANIFEST.md`'s companion seal line and in the session's final response.
14. **Next operator decision:** **0a.** Run the read-only Proxmox commands on `.50`, record the UPID/account for Core's 03:42Z operation and the Nexus 17:03Z–17:27Z operations, and state whether you issued the Core reboot. Then make decision 0b (retire under the limited exception, or keep V2 stopped).

## Corrections to the original Gate 6F report

These are recorded here; the original report is not edited.

- C1: "ACPI power button **from the hypervisor**" was an inference. It is now supported by mechanism (no guest agent, no in-guest privileged action, external power-on), but the Proxmox task is still unverified.
- C2: "booted again approximately 26 seconds later". The interval is about 26.5 s from the last shutdown record (03:42:19.18Z) and about 28.8 s from the power key, to kernel start.
- C3: Gate 6F validated two backups. A third, **terminal** bundle `62f417a2…` was created at 03:42:17.732Z by the shutdown. It is now verified valid.
- C4: F01's sentence "Production now has exactly that shape" should read: "the production *history* now has exactly that shape (an OPERATOR_STOP produced by an unattributed shutdown)". No production change occurred.
- No identity or attribution error was found in Gate 6F's facts.

## Limitations

- No Proxmox data, so VMIDs, nodes, UPIDs and accounts are all unverified.
- Guest journals show source IPs and the guest account only. Password logins from .50 could come from any user or process on the Proxmox node that knows the `jarvis` password.
- This workspace packet is swept nightly by `/opt/apps/nightly-snapshot.sh` to `origin/snapshot`. The documents are filtered for that reason: no key fingerprints, source ports or session numbers.

GATE 5: COMPLETE HISTORICALLY FOR V2

PRODUCTION SHADOW: NOT ACTIVE — V2 `jarvis.service` inactive/dead since the guest power-off at 2026-10-15T03:42:17Z; not restarted

V2 EPOCH: 606a991a06b74fd79ed72b308417cc3f — CLOSED_COMPLETE (truthful zero-use; stop unattributed)

PILOT ADMISSIONS: CLOSED

REAL PILOT ATTEMPTS: 0

V3 CANDIDATE: ISOLATED ONLY (ff2444df…, unchanged)

V3 DEPLOYMENT AUTHORIZED: NO

GATE 6 PILOT AUTHORIZED: NO

AI-HOST TRUST: PENDING

MEASUREMENT STARTED: NO

FORMAL P7 EXIT: NOT COMPLETE

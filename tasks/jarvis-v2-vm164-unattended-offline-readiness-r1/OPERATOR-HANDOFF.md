# Return checklist — no live action completed by this sprint

Last **operator-reported**, not freshly observed: VM164 stopped; verified r4 data
ISO attached; `hotplug: 0`; no NIC/guest agent; boot `order=scsi0;ide2`.
The disk-only correction is approved but **not reported executed**. Do not infer
anything more recent from the synthetic fixtures or offline PASS receipts.

1. **Establish the current supervised session.** Match the operator's approval
   reference, expiry, trusted console, target and permitted actions. Historical
   approval is not unattended authority. Target is node pve / VM164,
   UUID `faeb1db8-0df9-482d-b3e4-f6ccc1602193`,
   `downloads:164/vm-164-disk-0.raw`, serial `g6k164-12821f6b54a2`, 64GiB.
   VM162/163/200 and the AI server are outside this task.
2. **Restore disk-only boot in person using the already-approved prepared
   command.** Independently confirm the selected VM is stopped and matches the
   approved target before using that command. Intended result is exactly
   `order=scsi0`. This handoff supplies no replacement management command and
   executes none. If state/scope differs, stop for operator review.
3. **Capture fresh private readbacks after the correction.** Keep config,
   status/current and pending JSON in a new exclusive per-step evidence folder,
   with node/VM identity, UTC capture times and original-byte hashes. Establish
   explicit effective/current config selection (the reviewed broker uses
   `current=1`); verify installed host syntax and view semantics. Missing fields,
   pending-only values, mixed-time samples or an ambiguous view are a stop.
4. **Run the unchanged official guard locally** against those fresh files,
   selecting `attached`, `stopped`, and the exact volume below. Retain its receipt.
   Independently compare host-side media content/size, not just the volume name.
   The new validator is a supplemental consistency check with stricter input
   requirements; neither tool establishes live origin/freshness on its own.

   ```sh
   python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/host_guard.py \
     --config /NEW-STEP/config.json --status /NEW-STEP/status.json \
     --pending /NEW-STEP/pending.json --phase attached --expect-status stopped \
     --iso-volume local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso \
     --out /NEW-STEP/guard.json
   ```

   Only r4: `local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso`,
   **196608 bytes**, SHA256
   `fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154`.
   Do not reattach/reupload merely because the historical procedure starts empty.
5. **Hold before starting VM164 until stop conditions and open hazards are
   dispositioned.** No start with an unexpected boot entry/media, identity/disk
   mismatch, NIC/agent/extra device, pending change, stale/missing evidence, guard
   refusal, expired scope or absent trusted console. Review H1–H4 in FINDINGS:
   live ejection is unproved with hotplug 0; root precedes timer arming; cleanup
   has pre-`try` and service-budget gaps. This audit does not close those issues
   or authorize a revised helper. If the existing plan cannot safely cover them,
   retain stopped state and prepare a separately authorized design.
6. **Perform any later approved boot/console/media/cleanup actions in person.**
   Follow the pinned procedure only within current explicit scope. One unsaved
   GRUB interception; identity before guest actions; successful watchdog; whole-CD
   and helper verification before execution; same-boot RAM staging; proven actual
   ejection/no pending; unchanged probe; external hash-verified capture; verified
   closure and stopped state; normal clean-entry/login observation and final
   stopped/empty/no-pending readback. Failure means preserve and close under the
   approved failure procedure. No extra boot attempt, timer extension, pending
   repair, force reset, credentials, packages, networking or alternate boot mode.
7. **Keep the gates separate.** Preflight establishes measured host/guest facts
   only. Dormant installation requires its own finite approval, protected custody,
   exact RC1/bundle/native hashes, private rootfs, existing restricted principal
   and a fresh current-boot binding. Live Gate 6K needs separate privileged
   multi-UID/mount/network qualification. Production promotion is another explicit
   decision. This sprint completed none of those live gates.

The exact ejection/watchdog uncertainties, detection criteria and operator-required
recovery are in [FAILURE-ANALYSIS.md](FAILURE-ANALYSIS.md). No interactive approval
was requested while the operator was away.

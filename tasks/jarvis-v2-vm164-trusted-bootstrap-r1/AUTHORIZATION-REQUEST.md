# Exact next privileged operation — approval pending

Approve **one supervised, at-most60-minute, VM164-only trusted-console preflight
window** on node pve, bound to UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193 and the
existing64GiB `downloads:164/vm-164-disk-0.raw`, serial g6k164-12821f6b54a2:

- Fresh trusted config/status/pending readbacks; graceful ACPI shutdown first if
  running; verify no NIC, agent, additional channel or pending configuration.
- Upload a new, exclusive **nonboot** 196608-byte data ISO to
  `local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso`, verify SHA256
  `fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154`,
  and attach/eject media only through the already-empty ide2 drive. Retain the
  uploaded object, detached, afterward; never overwrite/delete existing media.
- One installed-disk boot with a supervised, unsaved VGA GRUB edit appending only
  `systemd.debug_shell=tty1 systemd.mask=getty@tty1.service`. No password changes.
- On identity-checked tty1: arm a20-minute runtime shutdown watchdog, verify/read-
  only mount this CD, stage its verified helper/probe exclusively on tmpfs /run,
  unmount/eject CD, run the unchanged pinned **lab_package.py probe**, capture
  hash-verified public JSON, then runtime-mask/stop/verify the temporary root shell
  and gracefully power off. No persistent configuration/account/permission edits.
- One subsequent normal disk boot to observe unchanged GRUB arguments and locked
  login without unauthenticated root; graceful ACPI shutdown to finish stopped,
  with the original empty CD/disk-only/no-network configuration and preserved disk.

This is the minimum complete operation for the chosen reliable delivery/closure
path; the probe alone cannot run while every installed administrator login is
locked and no approved transport exists. Whole procedure and failure conditions:
**OPERATOR-PROCEDURE.md**. Any guard refusal, inaccessible GRUB editor, missing
Python, media/live-ejection failure, failed capture or failed closure means stop,
preserve evidence and close by graceful shutdown. Forced stop/reset, persistent
credentials, new users/grants/SSH/guest-agent/NIC, alternate boot media or disk
repair require a different explicit decision. No automated retry/expansion.

Approval does **not** authorize JARVIS installation/startup, serial broker/real
executor activation, provider/network use, migrations, Gate6K, VM162/163 or V3.
Normal Ubuntu boot/shutdown journal/accounting writes are inherent and allowed
within this proposed window; identity/disk preservation does not mean zero writes.
No operation in this request has been performed during preparation.

A single sufficient human response is:

> Approve the VM164-only supervised trusted-console preflight window exactly as
> scoped in jarvis-v2-vm164-trusted-bootstrap-r1/AUTHORIZATION-REQUEST.md, with the
> pinned fd91b8b07243565e data ISO and OPERATOR-PROCEDURE.md; no installation or
> Gate6K authorization.

After execution, review truthful fresh host/guest facts. A later protected-install
approval must bind actual runtime/rootfs/native hashes and the **then-current**
boot-id; this temporary boot-id expires at shutdown and cannot authorize a later
boot. Restricted worker identities, protected parent custody/ownership, dormant
installation destination, exact RC1/package pins and UTC expiry remain separate
requirements under the preserved lab-readiness packet. Gate6K remains separately
blocked pending explicit privileged multi-UID/no-network/mount qualification scope.

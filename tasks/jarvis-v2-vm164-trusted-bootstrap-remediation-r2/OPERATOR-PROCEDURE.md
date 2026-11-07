# Revised single operator procedure — r2, NOT executed

**Current first action: KEEP VM164 STOPPED. Root boot is NO-GO.** This procedure
is ready for review but its root section is blocked until the host fence backend
exists, is reviewed and passes real non-root qualification. Offline PASS receipts
cannot open that gate. No operation below was performed in this engineering task.

Reported current state: VM164 stopped; order=scsi0 successfully corrected; verified
old r4 192KiB ISO remains attached to ide2. This is operator-reported, not a fresh
readback. Do not repeat the boot correction, assume the CD was ejected, reupload
r4, or follow the old root/timer procedure to discover whether it works.

## 1. Verify preparation locally; establish the gated scope

From the JARVIS project root, only this is presently executable without new live
scope:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tools/verify_packet.py
```

Read GO-NO-GO.md, RISK-REGISTER.md and AUTHORIZATION-REQUEST.md. New candidate:

```text
candidate/vm164-trusted-bootstrap-r2-09185f1f69108ab1.iso
196608 bytes
ISO SHA256 09185f1f69108ab18fbdf2b589c5eba9bb8b8e90c85dd92a797926b8972aa2ee
BOOT.PY SHA256 39ff990b630a7ec361fba543526bcdf72a545301400b758c0319ac977ef86182
LABPKG.PY SHA256 08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a
future PVE volume local:iso/vm164-trusted-bootstrap-r2-09185f1f69108ab1.iso
```

This is NEW/unapproved/unattached. The original r4 ISO remains pinned at SHA256
fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154.
Preserve it and every predecessor. Never identify the two images by their equal
192KiB size or common J164BOOT label. Superseded media-build1–4, delivery/ and
fixtures/ in this new folder are engineering history, not transfer artifacts.

## 2. Before root: reviewed host enforcement and non-root qualification

Only under a new finite approval, collect trusted current/status/pending/version
facts and implement/review the fixed-target host backend using those actual
interfaces. HOST-FENCE-CONTRACT.json is a requirements document; lease_policy.py
is an executable OFFLINE model, not an enforcement daemon. There is no ready
host-worker command hidden in this packet. Do not improvise one or substitute an
active guest timer. No credential/token/grant change is needed or authorized.

Q/R gates require actual observations of both independent host workers, exact
execution paths/target/custody and suspend-inclusive deadline semantics **while
VM164 is stopped**. Nominal schedule from arm: grace at540s, hard-stop escalation
at600s, real stopped proof by630s. Command acknowledgment alone never means
termination. Host worker/clock/process identity failure behavior, no auto-restart,
console/launcher loss and VM164-only emergency termination must be qualified on
separately approved normal boots WITHOUT any root/debug/rescue argument first.
Each named trial needs preservation/failure scope; do not create trial permission
from this procedure. Forced termination may damage in-flight Ubuntu state; its
acceptance and preservation plan are mandatory. Missing backend or proof is STOP.

## 3. Fresh target/media preparation while stopped

After successful qualification and a NEW explicit root-session authorization:

- Trusted node pve/VM164 only; UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193,
  original downloads:164/vm-164-disk-0.raw,64GiB,serial g6k164-12821f6b54a2.
- Fresh effective/current config, status/current and pending observations, supported
  query semantics, no NIC/agent/new device/shared or passthrough channel, no pending
  change, protection1/hotplug0/onboot0, fixed >=4vCPU/>=6000MiB RAM, disk-only boot.
  Keep original raw bytes/timestamps/source and private readback hashes in a new
  execution folder. No other VM is a target. Guard refusal is not repair authority.
- Only while actually stopped, upload the new image under its exclusive name if
  absent and perform the specifically approved existing-ide2 media-only swap.
  Retain the old object/disk; no overwrite/deletion, boot-order edit, raw disk
  mount, hotplug change, QMP workaround, NIC/agent or privilege grant. Re-read and
  verify actual content/size, current disk-only config and no pending change.
- Use r2 tools/state_gate.py for supplied-envelope consistency, with the read-only
  contract inherited from the prior VALIDATOR.md. It binds the NEW exact image.
  Old host_guard.py's media contract has not been weakened or repinned. Neither
  validator establishes origin, live freshness or authority from saved JSON.

## 4. Arm BEFORE start; one unsaved console boot

The qualified host implementation must arm and inspect a NEW fixed lease while
VM164 is stopped, binding the current host boot/session/target/config digest and
one allowed boot generation. Both workers/deadlines must be independently observed
before start; <=15s from arm to start or NO START. No renewal/extension/cancellation
while running. The host mechanism stays active if every guest helper, timer or
console vanishes. Preserve the pre-start evidence. This is an actual R-gate check,
not a JSON field an operator can set to true. Missing evidence means no root.

On the already approved trusted VGA/noVNC console, one installed-disk GRUB editor
attempt only; retain the original linux/initrd/root arguments. Append only:

```text
systemd.debug_shell=tty1 systemd.mask=getty@tty1.service
```

Use the unsaved editor, Ctrl-X to boot. No serial experiment, init=/bin/bash,
rescue, saved GRUB changes, password/key/account or persistent debug modification.
A missed/editor-locked/ambiguous boot ends the attempt; no key-spam or second root
boot. Keep the trusted console supervised. The root shell is trusted cooperative
access, not confinement against hostile root. Its expiry protection was already
armed OUTSIDE the guest, not typed after this prompt appears.

## 5. Verify CD, run attached-media diagnostic; never live-eject

Only on the identity-checked VM164 tty1 within the admitted session, using the new
candidate's pre-approved hashes, first read:

```sh
cat /sys/class/dmi/id/product_uuid
cat /sys/block/sda/device/serial
cat /sys/block/sda/size
cat /proc/sys/kernel/random/boot_id
blockdev --getsize64 /dev/sr0
sha256sum /dev/sr0
```

Require exact UUID/serial above,134217728 sectors,196608 CD bytes and new ISO hash
from step1. Record boot-id separately with the trusted session/timeline. A wrong,
missing or inaccessible value means abort under the admitted host fence, not a
guest device guess or unverified poweroff target. Then, one command chain:

```sh
mkdir -m 0700 /run/vm164-bootstrap-media-r2 &&
mount -t iso9660 -o ro,nosuid,nodev,noexec /dev/sr0 /run/vm164-bootstrap-media-r2 &&
sha256sum /run/vm164-bootstrap-media-r2/BOOT.PY
```

Stop and compare the helper hash against step1 BEFORE executing it. Do not paste
helper execution into the same unchecked checksum chain. Only after exact match:

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-media-r2/BOOT.PY probe --execute-supervised-guest
```

The candidate verifies narrow identity, tty1, tmpfs /run, restrictive read-only
ISO mount and unchanged probe hash; creates exclusive0700 /run/vm164-bootstrap-r2;
records a0600 session; invokes only LABPKG.PY probe with -I -B -S. Raw stdout is
preserved. Expected diagnostic has optical_media_present=true and never grants
installation qualification. No live CD eject/unmount-to-fake-absence or data edit.
Unexpected false/pending/unknown media is INCOMPLETE, never a media-free PASS.
Missing Python or native-probe error is abort, not package installation permission.

## 6. Capture early, close early; never extend for evidence

Immediately display/capture all zero-based pages before closure:

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-media-r2/BOOT.PY page 0 --execute-supervised-guest
```

Repeat page1 through N-1 as printed. Retain all48-character indexed base64 rows,
full raw-record SHA256 (console wrapping does not remove characters), and the
separately observed boot-id. Capture only public minimized data; no credential or
raw secret-bearing logs. Finish capture early; begin close with >=120s remaining
before the hard-stop escalation, preferably much earlier. Do not wait for
transcription/hash reconstruction while privileged access is open. A missed page
or failed later decode stays incomplete; it never renews this boot/lease.

Always submit abort/success cleanup from the same verified media, even if the
probe failed or its session/output is missing:

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-media-r2/BOOT.PY close --execute-supervised-guest
```

Submission is not closure. It launches a separate runtime unit with a60-second
work budget,90-second startup limit,5-second stop limit, control-group killing and
no restart. After narrow target verification, any state-validation failure still
attempts runtime mask, stop, kill-all, cgroup/state inspection and poweroff. Wrong/
unknown identity deliberately permits no guest mutation; the qualified host fence
remains responsible for its admitted target. No STATE/PROBE/console prerequisite
can skip post-identity termination attempts. No cleanup delay/sleep is present.

Capture the console observation if available. It is printed **before** the final
poweroff request, so poweroff_requested is not yet true in that preliminary record.
It is only a guest closure observation. Final process result/journal, if retained,
still cannot prove that the VM stopped. SIGKILL/manager/kernel death can bypass
Python finally entirely. Do not type exit or disarm host enforcement based on a
disappeared prompt, successful systemd-run, guest JSON or an acknowledgment.

## 7. Obtain true stopped proof; detach only stopped; verify clean return

The trusted host operator must confirm actual stopped state, target identity and
current/pending configuration. Keep host enforcement armed until independently
confirmed stopped and its retirement is allowed by the reviewed backend contract.
Never mark a missing/failed stop as PASS. No stop proof by arm+630s is FENCE FAILURE;
use only the pre-authorized VM164 emergency action and record failure, never host
power/reset or another VM. If no such qualified action exists, this boot should
never have been admitted.

Only after stopped proof may the approved operator detach the data medium from
existing ide2. Re-read stopped/empty/no-pending and unchanged disk-only config.
Keep both ISO objects and all evidence. No running eject or surprise pending-change
clearance. Lost RAM data/boot-id cannot be resumed after shutdown.

An explicitly approved clean-verification boot is a separate allowed generation:
retire the old lease against stopped proof, prearm a NEW fixed lease while stopped,
verify new bindings, then normal disk boot with empty CD and NO added arguments.
This is not an extension of an active root lease. Observe unchanged normal GRUB
entry and ordinary locked login with no unauthenticated root. Do not attempt
passwords or claim authenticated clean-boot service inspection. Finish stopped/
empty/no-pending under the admitted fence. Unexpected root/debug state or missing
final observation means NO-GO and preservation, not credential/boot-file repair.

After shutdown, reconstruct captured rows locally in an exclusive new directory:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tools/decode_diagnostic.py \
  --rows /NEW-EXECUTION/rows.txt --sha256 CAPTURED_FULL_SHA256 \
  --expected-boot-id SEPARATELY_CAPTURED_BOOT_ID --out /NEW-EXECUTION/decoded
```

This checks transcription and session equality, not cryptographic guest origin.
Retain raw readbacks/approval/version/hash/deadline/console/stop/failure evidence
privately in that new packet. State remains diagnostic-only; original installer
rejects attached media. No JARVIS, broker, executor, model, real database, Gate6K,
VM162/163/200, AI-server or V3 action is part of this operator path.

# VM164 trusted bootstrap — prepared, not executed

The single operator procedure is **OPERATOR-PROCEDURE.md**; the exact minimal next
approval is **AUTHORIZATION-REQUEST.md**. Preparation is complete for a supervised
one-time installed-disk root console and read-only preflight. No Proxmox/VM164
query or modification, power action, guest console input, media attachment,
credential change, installation, JARVIS startup or Gate6K action was performed.
Public upstream documentation was consulted; every engineering test ran locally,
without VM access. The existing observer credential was not used or changed.

Use an unsaved VGA GRUB edit appending:

```text
systemd.debug_shell=tty1 systemd.mask=getty@tty1.service
```

This keeps normal installed Ubuntu/systemd startup and places the temporary root
shell on the visible VGA terminal. It requires no password/key/NIC/guest agent or
persistent debug enablement. A single nonboot data CD supplies the pinned public
probe; stage it in tmpfs, unmount/eject, then run it with isolated Python flags.
Cleanup runs independently of the root shell, masks/stops/kills it, verifies its
state/cgroup, and powers off; a runtime20-minute shutdown watchdog bounds access.
A normal boot/login observation and final stopped/empty state complete the
operator's verification. Typing exit alone is insufficient (stock Restart=always).

## Exact deliverable

Only use `delivery-r4/vm164-trusted-bootstrap-fd91b8b07243565e.iso`:

| Item | Exact identity |
|---|---|
| Data ISO | SHA256 `fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154`,196608 bytes |
| Media contents | BOOT.PY, LABPKG.PY, SHA256.SUM; J164BOOT; no boot descriptor/system-area boot code |
| New staging/closure helper | SHA256 `ac90206dc70f8473fe3b0bfa2e3e9d1be7e3471af4090637cb715d96e0aaf6bb` |
| Unchanged lab_package.py probe | SHA256 `08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a` |
| Preserved Unified RC1 source | Git `e9b4734740070b9e7c990735e43801e592c114c6` |
| Preserved future install bundle | SHA256 `0c42464637a8ffd1f443f532a087acf0d9a7c48213f9803b4e228aeda5a898ba`,23548033 bytes; not on this CD |

Builds9 and10 are byte-identical to delivery-r4. Earlier builds1–8, delivery/, delivery-final/ and delivery-r3/
are preserved superseded engineering evidence, not approved transfer artifacts.
No predecessor candidate, application source or broker candidate was changed.
Main repository HEAD at entry was f4cac30259a7bf4610add2063679ae49138ee637, with
preexisting dirty work preserved; the RC1 identity above is the release being probed.

## Implemented tools and verification

- `payload/BOOT.PY`: identity/cmdline/unit/cgroup/watchdog/media checks; exclusive
  RAM staging; unchanged pinned probe invocation; paginated lossless evidence;
  distinct runtime cleanup/poweroff unit. It does nothing at import.
- `tools/host_guard.py`: offline checks for exact VMID/UUID/original disk/digest,
  expected status/media phase, no NIC/agent/extra channels/pending change, original
  protected disk-only configuration and CPU/RAM baseline. No network/subprocess.
- `tools/decode_probe.py`: strictly reconstruct indexed console rows, require exact
  SHA256/target identity and media absence, write exclusively to a new destination.
- `tools/build_media.py` and `check_media.py`: pinned retained unprivileged ISO
  builder in a no-network sandbox; separate bounded ISO9660 inspection without
  mounting. No package installation, autorun, El Torito image or kernel/initrd.
- `tools/test_bootstrap.py`: **43 test methods passed**, zero failures/errors/skips
  in the release run (`evidence/tests-release-r4.log`). Covers UUID/serial refusal
  before commands; boot/network/disk/watchdog/root/cgroup controls; host identity,
  pending/media/channel/state negatives; corrupt/symlink/hardlink/FIFO/oversize
  inputs; partial-stage/existing-output preservation; exact pinned probe handoff;
  console capture roundtrip and tamper/loss/duplication/order negatives; cleanup
  success/failure/residual children and shutdown fallback; media/reproducibility.
- `tools/test_generator.py`: **three native generator cases passed** in a separate
  unprivileged network-isolated namespace, no system manager or actual root shell:
  tty1/getty mask; clean/no-debug boot; default boolean tty9 behavior. Retained
  generated links/drop-in, binary hash and stock unit under evidence/generator-tests.
- Python AST checks passed for all29 Python files/copies in the preparation packet.
- `evidence/final-media-inspection-r4.json`: independent final-image/member hashes,
  zero boot system area, descriptor types1/255 only, exact inventory and probe pin.
- `evidence/predecessor-verification.json`: sealed lab-readiness/RC1 evidence
  reverified:315 source files,31 wheels,2444 installed files,18582 RC1 evidence files,
  177460 prior files. Historical test counts are not claimed as new bootstrap runs.
- `ENGINEERING-REVIEW.md`: separate source/negative-path review, resolved findings
  and explicit limits; no independent external-review or VM-qualification claim.

Initial uppercase-source test-loader failure is retained in tests-initial.log;
fixed in the harness. Subsequent release run passed all43. No hardware/live/Gate6K
or actual system-service tests were attempted or silently counted as passes.
All power/service calls in fixture tests were mocked; only the generator itself
ran natively in its sandbox. No new third-party Python dependencies were added.
Retained xorriso executable pin and prior signed-package provenance are recorded
in EXTERNAL-PINS.json and its referenced evidence. No fresh advisory scan was
needed for these stdlib-only additions; the predecessor's advisory findings remain.

## Reproduce locally without privilege

From the JARVIS project root:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/verify_packet.py
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/test_bootstrap.py
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/build_media.py --out /NEW-EXCLUSIVE-LOCAL-DIRECTORY
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/check_media.py --iso /NEW-EXCLUSIVE-LOCAL-DIRECTORY/probe-data.iso --delivery /NEW-EXCLUSIVE-LOCAL-DIRECTORY/DELIVERY.json
```

Use destinations outside this sealed packet for further test/build output. No
sudo, loop mount, networking or VM is needed. Generator test may likewise run
with `--out /NEW-EXCLUSIVE-LOCAL-DIRECTORY`. The retained builder and bwrap must
still be available at their pinned paths; missing tools cause a stop, not download.

MANIFEST.json inventories every regular file and symlink without following the
generator's absolute links; SEAL.json hashes that manifest. The verifier checks
exact inventory, external pins, final-helper/media agreement, reproducibility,
original canonical loop-log prefix, and reruns the sealed predecessor verifier.
These are local hashes, not a cryptographic signature or guest attestation. Retain
the manifest hash externally with the operator approval for custody.

## Remaining decision and truth limits

The latest installed-disk boot/hardware facts in evidence/entry.json are supplied
by the operator. No new live inspection was authorized. Fresh host readbacks,
reachable VGA editor, installed Python, actual debug-unit behavior, live media
ejection, hash-verified probe capture and true cleanup/clean-login evidence remain
pending execution. If any fail, follow the single preservation/shutdown procedure;
no persistent-password, serial, rescue, alternate-media or disk-repair fallback.

Request only the one supervised <=60-minute VM164 preflight window specified in
AUTHORIZATION-REQUEST.md: gracefully stop if necessary; attach the verified data
CD to empty ide2; one transient root boot, read-only probe and capture; eject;
verified runtime closure/shutdown; one clean normal verification boot and final
ACPI shutdown. Keep VM164 without NIC/agent and preserve the disk/evidence.

This can establish truthful public preflight facts; it cannot make an incompatible
runtime or missing isolation package pass. Review native hashes/versions, private
mount/rootfs, machine identity, bwrap, CPU/RAM/storage and independent host facts
before any protected install. Its temporary boot-id is invalid after shutdown.
A later install requires a fresh current-boot binding, exact RC1/bundle/tool pins,
root-protected custody/new destination, restricted worker identities/ownership,
operator reference and expiry, all under a separate approval. Gate6K still needs
separate authorized privileged multi-UID/network/mount qualification. Broker,
real executor, provider, real databases, VM162/163, AI server and V3 stay outside
this scope. No release/deployment readiness is newly declared here.

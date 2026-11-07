# One minimal next human action — trusted VM164 preflight only

**Requested decision:** authorize one supervised, at-most60-minute VM164 trusted-
console preflight window to acquire the exact public host/guest facts required by
the prepared installer. This is not an installation, repair, broker activation or
Gate6K qualification request. The final bundle/tool/installed-manifest pins are in
BUNDLE.json; Unified RC1 is e9b4734740070b9e7c990735e43801e592c114c6.

The unchanged read-only observer currently receives HTTP401. Do not broaden,
replace or issue a credential/grant to make this sprint pass. The trusted operator
can instead supply a fresh minimized VM164 host configuration readback from an
existing approved management console, bound to node pve / VM164 UUID
faeb1db8-0df9-482d-b3e4-f6ccc1602193, original64GiB volume and hardware serial
g6k164-12821f6b54a2. Confirm no NIC, agent, passthrough, shared host channels,
setup/transfer media or pending configuration, disk-only boot and onboot disabled.
Retain the readback's timestamp and hash. No other VM is an allowed target.

If an existing trusted installed-OS root console and an already approved means of
delivering the independently hash-verified public probe are available, run only:

```text
/usr/bin/python3.14 -I -B -S /already-approved-read-only-or-protected-path/lab_package.py probe
```

The exact standalone tool hash is BUNDLE.json bootstrap_tool_sha256. The tool now
refuses a different DMI UUID or hardware serial before broader guest inspection.
It reads public identity, rootfs, runtime/library, network/mount and capacity facts;
it opens no serial device, credential, real database, provider or management
connection and makes no install/ownership/account/service/power change. It emits
JSON to stdout. The operator retains only this minimized record through an already
approved evidence channel; no raw installer/cloud-init logs or secrets in chat.

**Stop condition:** if trusted installed root, approved probe delivery or completed
OS boot is not established, stop and preserve the current disk/state. Do not boot,
reboot, attach media, type into an unqualified console, reuse the r4 installer,
format, mount/repair a disk, enable guest-agent/SSH/NIC, unlock an account or invent
machine/boot IDs. Missing delivery/bootstrap scope requires a separate exact
preservation/bootstrap decision using the existing incident records.

Expected output is one trusted host readback plus one matching minimized guest
probe record, with machine-id, current boot-id, private root filesystem UUID/device,
root-protected Python/native mapped-file hashes, bwrap identity, lo-only interfaces,
private mounts and measured CPU/RAM/free-space. The guest JSON is unsigned, not a
substitute for independent trusted observations or installed privilege qualification.

After those facts pass review, a **later exact protected-install approval** can bind
the package/tool/source pins, truthful actual identities/runtime/rootfs, fixed new
destination, operator reference and at-most1-hour UTC expiry using the null-filled
approval.example.json. The prepared command then installs only dormant immutable
files. Existing restricted lab identities, media transfer/detachment, protected
bootstrap custody and parent-directory creation must be explicitly scoped then.
No enrollment, real executor, serial-source promotion, new token/ACL/user, systemd
activation, production startup or V3 is implied.

Controlled installed synthetic testing additionally requires verified no-network
cage/one-principal scope. Known certifi/Electron/undici findings are retained in
ADVISORY-ASSESSMENT.md. Networked/frontend use, broker activation, real adapter
integration and privileged Gate6K multi-UID qualification remain separate blocked
milestones with their own authorization and evidence. VM162, VM163 and the AI
server remain outside every step in this request.

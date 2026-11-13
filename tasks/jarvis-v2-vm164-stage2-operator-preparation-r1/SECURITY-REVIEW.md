# Security review — offline author review; independent live signoff pending

The reported nobody account is a candidate, not an established security boundary.
UID65534 may be shared by NFS mapping, containers, services or dynamic policy.
No active processes at a prior inspection does not establish permission denial.
**Current blocker: lack of complete fresh VM-authority and credential-access proof.**
No credentials were read, requested, tested, transferred or created in this work.

## Mandatory independent nobody review before callback placement

A named reviewer must create a finite inventory of all host VM-management and
private-credential routes. Retain a digest of the inventory, each supporting
policy/metadata record, its capture time and any exclusions. An inventory with
unknown scope is not sufficient. The hash of a review does not make it true.
`validate_identity()` only checks record consistency, not the truth of assertions.

| Surface | Required denial evidence; allowed inspection |
|---|---|
| UID/GID/NSS | Both name and numeric getent mapping, id groups exactly65534, local passwd/group policy plus resolved NSS source inventory; no duplicate/foreign UID mapping or uncontrolled external directory. Noninteractive locked login policy must be attested without reading shadow/password contents. |
| Existing processes | All real/effective/saved/filesystem UIDs in /proc/status checked for65534; no preexisting process or unexplained process during session. Do not inspect environ or other secret-bearing process files. |
| sudo and other elevation | Root-side noninteractive `sudo -n -l -U nobody`, full include-policy review, polkit rules and relevant local administrative/D-Bus policy. No allowed arbitrary command, systemd management or VM management privilege, even password-gated. Unknown dynamic policy blocks. Do not execute a privilege probe. |
| Proxmox roles/ACLs | Independently review installed nonsecret `/etc/pve/user.cfg` and relevant realm/group/role policy, inherited ACLs and nobody's mapped identities. Determine nobody has no VM-management authorization. Do not use pveum/API login or create/query a token. ACL identifiers are not credential bytes; retain policy records privately. |
| Local control paths | Inventory permissions/ACLs on system manager/PVE/QMP sockets, `/run` sockets, cluster database, VM configuration/storage paths, device nodes and any local helper service that accepts peer-UID65534. Determine nobody cannot write disk/config/device data or issue manager/control requests. Do not contact any socket or execute qm/pvesh/pvesm. |
| Elevation executables | Review installed relevant setuid/setgid/file-capability helpers and administrative wrappers against nobody, including sudo and custom scripts; account membership alone is insufficient. No exploitation or activation. Unknown custom helper blocks. |
| Private credentials | Operator supplies COMPLETE applicable inventory of secret directories/files, backups, key material, service credential stores, SSH agent sockets, token files and private runtime authorization/state. Inspect ONLY stat/ACL/ancestry and access policy; never contents or a can-open/read test. Include storage ACLs and symlink targets. Each secret must have a demonstrable deny along its access path for nobody and all its groups; world-readable secret, usable agent socket or incomplete inventory blocks. |
| Root/operator custody | No concurrent root writer replacing code, NSS, binaries, ACLs or units; no package/host maintenance during the trial. A hostile root is outside this model. The baseline and trust attestation must be explicit. |

`R19` is permitted only for reviewer-selected **nonsecret policy/manual** files.
A complete list and exact paths must be approved before using it; do not read a
whole policy directory indiscriminately. `R14` and `R21` provide exact metadata
and ACL argv for every inventory path and ancestor. Policy paths such as
`/etc/polkit-1/rules.d` and `/etc/sudoers.d` must have their actual included files
resolved by the reviewer; do not invent host contents. Any needed inspection
outside the reviewed catalogue requires amended review before use.

If existing local inventory/evidence cannot establish this negative authority
claim without credential or VM operations, report **BLOCKED_NO_UID_PROOF**.
Do not create a new UID, revoke rights, chmod someone else's files, change ACLs,
run a root callback, or silently rely on added sandboxing to waive the requirement.

## Source and command review

- R3 is sealed and unchanged. The 2441-byte canary has no subprocess, VM, network,
  manager, private-grant or write interface. It rejects UID/eUID0, wrong path,
  non-root-owned or writable ancestry, symlink, multiple-link/oversize/nonregular
  leaf and wrong SHA256. These checks do not prove global UID privilege absence.
- Stage 2 creation uses only fixed absolute Python/canary paths and fixed bounded
  diagnostic Python bodies. Timeout sleeps30s under RuntimeMax3s; late sleeps2s
  before the pinned callback. Neither has a VM or manager interface. Missingdep
  uses isolated Python and a nonce-bound absent module. Missingexec names a path
  required to be absent. No shell command is a service payload.
- Explicit User=65534/Group=65534 and no capabilities/new privileges protect the
  callbacks. Setup requires existing administrator permission but does not launch
  a root worker or obtain a root shell. SupplementaryGroups= alone is insufficient;
  the group audit and timeout credential record are mandatory.
- Exclusive directory creation cannot overwrite or adopt prior objects. Source
  and `/opt` ancestry are opened through O_NOFOLLOW directory descriptors; leaf
  O_EXCL, bounded hash, regular/nlink checks, stable metadata and fsync are required.
  No full runtime, private approval file or new secret is deployed.
- Namespace permits only twelve enumerated case bases under a random session nonce.
  Every attempted name is consumed even on lost acknowledgment. Foreign collisions
  are never stopped; the intentional collision repeats an owned identical command.
- Cancellation requires exact prior ownership and fresh properties. Timer is
  stopped before service; no killall/pkill, unit wildcard stop, reset-failed,
  collect, disable, daemon-reload, daemon-reexec or service-manager restart.
- UTC plus BOOTTIME limits, fixed expiry, admission cutoff and cleanup reserve
  reduce exposure. The canary itself contains **no authorization-expiry check**;
  suspension/manager failure may delay it beyond operator expiry. Supervision and
  runtime limits are not guaranteed revocation under host failure.

## Review findings and resolutions

1. A near-zero clock offset cannot establish convention. Packet fails UNKNOWN,
   requiring exact-version documented interface evidence or discriminating
   observations, without inducing suspend.
2. A systemd-run missing-executable refusal may happen before timer activation.
   It is not counted as 203/EXEC; qualification remains blocked if not observed.
3. Missing dependency may leave timer inactive rather than failed. Actual failed
   timer state remains unobserved if so; fixture coverage is labeled separately.
4. A stopped timer can still have a running service. Cleanup now resumes by
   stopping that exact service after ownership verification; a dedicated test
   covers the interrupted-cleanup state.
5. Empty SupplementaryGroups does not clear implicit groups. Mandatory NSS/group
   review and emitted timeout-probe groups cover the distinction.
6. Resource settings and sandboxing are stronger than the R3 worker contract.
   This packet explicitly limits findings to Stage 2 and never claims the root
   worker or private runtime is qualified.
7. R3 prerequisite assessment requires manager reexec, reboot invalidation,
   private installation custody and other facts outside this task. These stay
   unqualified; there is no boolean-only promotion to Stage 3.

## Independent review acceptance criteria

Before any future approval, a person other than the operator/author must review:
source/manifest pins; exact catalogue and rendered names/argv; current UID/ACL/
credential-denial inventory; binary/source custody; fixed UTC/boot window; all
property support; exact-version clock/interface evidence; failure classifications;
owned cleanup and recovery authority; evidence recorder custody/limits; and all
scope exclusions. Record identity, date, evidence hashes, finding disposition
and signoff. No independent reviewer was fabricated or impersonated here.

After a live trial, independent reviewer checks every raw evidence digest and
exit result, both waiting observations, source/boot/UID consistency, invocation
correlation, all expected negative cases and retained failures, absence of
unowned actions, terminal cgroups/jobs, unchanged consumed-name ledger, and the
unaltered expiry. UNKNOWN, missing, late or contradictory evidence cannot become
PASS. This packet's offline test results and self-review are not that live signoff.

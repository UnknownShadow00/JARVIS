# Clean replacement lab — readiness report

Status: **BLOCKED BEFORE VM CREATION. NO-GO for Gate 6K qualification.**

This task used the `network` profile. The user's GO authorizes new-VM provisioning after target, capacity and access checks; historical packets' narrower prohibitions do not revoke that GO. No new blanket permission to build is needed. Administrative access and installation design remain unresolved. This packet is not a qualification approval.

## Actual work and evidence

- Read the VM163 consolidated remediation, corrected-release update procedure, dependency handoff and supplier-risk register.
- Probed only Proxmox `192.168.0.50`, once each as `root` and `nexus`, using noninteractive public-key authentication, strict existing host-key verification, no agent/X11/port forwarding, no password attempts and no key enrollment. Both returned exit 255, `Permission denied (publickey,password)`. `sudo -n true` on Nexus returned exit 1, requiring interactive authentication. No authenticated PVE command ran. See `evidence/access-and-identity.json`.
- Rehashed the original ISO, full offline archive, corrected release archive, both bootstrap extractors, 618 source files, 657 dependency-bundle entries and all 131 artifact records. Independently fetched Ubuntu's current signed checksums and public key; verified the full published fingerprint and ISO digest. `evidence/input-verification.json` records actual results.
- Read ISO9660 and Squashfs metadata/public cloud-init code directly from the verified ISO without a mount, root operation, VM connection or guest boot. `evidence/iso-inspection.json` records **an empty `/root/.ssh` already in the signed base image**, before any installation. Cloud-init defaults also include SSH and user creation modules. See `INSTALLATION-AND-ISOLATION-DESIGN.md`.
- Refused the preexisting Nexus `gate6k-flat-r1` export because its manifest does not match the requested digest; retained it unchanged. Generated a separate fresh public export from the verified bundle. Its independent recheck and protected-copy limits are in `evidence/prepared-public-inputs.json`.
- Added read-only inventory and verification tools, a console handoff, and unprivileged guard tests. No application/security-release source was modified.

No VM was created, started, stopped, snapshotted, cloned, mounted or reconfigured. No VM163 guest access or VM163 lifecycle action occurred. No connection to Core `.162` or AI `.200`, production service launch, provider request, approval-marker creation, mount-namespace change or privileged qualification occurred. Existing VM163 evidence was not accessed or modified. Its current power state remains unobserved.

## Readiness matrix

| Requirement | Actual status |
|---|---|
| Signed Ubuntu 26.04.1 amd64 installation input | VERIFIED on Nexus; signature is origin/integrity evidence, not a malware-free guarantee |
| Corrected release archive and 618 source entries | VERIFIED on Nexus |
| Dependency bundle and 131 public input records | VERIFIED on Nexus; historical supplier limitations retained |
| Fresh public offline export | PREPARED on Nexus; user-owned staging is not a protected guest installation |
| PVE administrative access and capacity | BLOCKED; authentication denied; no capacity assertion |
| Unused VMID / new UUID / dedicated disk | NOT SELECTED / NOT CREATED |
| Guest machine-id, hostname, boot ID, console session | NOT OBSERVED |
| 4 vCPU / preferably 6000 MiB / private ext4 | DESIGNED; not provisioned |
| At least 20 GiB available after complete setup | UNMEASURED in guest |
| No NIC/routes/shares/credentials | REQUIRED; not attested in a nonexistent guest |
| Installer-origin SSH/cloud/credential-store issues | INVESTIGATED; reviewed installation implementation still needed |
| Protected Python 3.14.4 / SQLite 3.46.1 / cryptography 46.0.5 / 127 pins | VERIFIED INPUTS ONLY; no replacement runtime installed |
| Root plus three distinct test identities | NOT CREATED |
| Metadata-only replacement preflight | NOT RUN; cannot substitute Nexus diagnostics |
| Mount-propagation scope approval | OUTSTANDING; neither proposed option executed |
| Root-protected artifact installation | NOT DONE |
| Approval marker / privileged qualification | ABSENT / NOT RUN |

## Exact next step and authorization gates

Use the already trusted **PVE node root console**, confirm `pve` at `.50`, and run the read-only block in `TRUSTED-CONSOLE-HANDOFF.md`. Return only its minimized JSON. Do not send passwords, keys, API tokens or console tickets. This supplies the missing administrative observations without requiring credential disclosure or SSH changes.

After inventory, existing GO covers a new isolated VM if identity/capacity checks pass. Construction must use a newly checked free VMID and preserve VM163; stop if 6000 MiB plus host headroom cannot be supplied, rather than stopping another VM or quietly reducing RAM. The empty-SSH installation design must be implemented and validated before any claim of security readiness.

Later **separate human decisions**: (1) approve the exact mount-policy scope (temporary qualification process tree versus guest-wide policy); (2) review actual machine/disk/console/boot identities, supplier limitations and preservation record before separately authorizing the approval marker; (3) explicitly authorize the exact privileged qualification command. This task never creates a marker or launches `qualify_all.py`. A populated cloud cache requires its real accepted metadata digest and supported provenance statement; unknown or failed scans never qualify.

## VM163 retention recommendation

**Keep VM163 in its existing state now.** Replacement inputs are not a replacement guest. Recommend considering a separately authorized graceful power-off only after the replacement's identity, clean installation history, offline runtime/artifacts and preflight are independently reviewed; relevant original evidence and its hashes have a verified independent retention plan; and either qualification succeeds or the operator explicitly accepts that shutdown will end volatile comparison evidence before success. Record VM163 boot/mount/process metadata and retention requirements before that decision. Power-off loses volatile evidence and requires explicit lifecycle authorization. Retain its original disks/configuration and existing snapshots; do not auto-snapshot, delete, export unknown secrets or repurpose its VMID. No shutdown command is supplied.

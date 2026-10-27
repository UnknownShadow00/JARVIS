# Installation-time SSH resolution and prepared media

**The empty SSH directory issue is resolved and validated at source-image construction scope. No guest installation or boot has been tested.** Gate6K's checks/source were not changed. Nothing was removed from VM163, an installed guest, an unknown credential store or a live filesystem.

The original independently authenticated Ubuntu26.04.1 amd64 ISO remains unchanged:

`cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927`

The previous packet retains Ubuntu's detached signature, current-at-verification checksum, full image-signing fingerprint and original input verification. See [original verification](../p7-b2-gate6k-clean-replacement/BUILD-AND-PROVENANCE.md). This continuation rehashed original media and the selected public transport before construction. No VM163 bytes are inputs.

## Precisely bounded construction

The signed base filesystem had exactly one `root/.ssh` entry: an ordinary empty directory, uid/gid0, mode0700, timestamp1787719573, with no child or xattr entry. The helper refuses a populated directory, file, link, unexpected ownership/mode or extra metadata. It keeps the original public metadata/specification and omits **only that directory entry when constructing a new image**. It adds one empty root:root0644 `/etc/cloud/cloud-init.disabled` before the installed OS ever boots. No `rm`, `rmdir`, hiding mount or post-boot cleanup is involved.

Unprivileged `unsquashfs -pf` exports the full signed filesystem as metadata plus public file data. `mksquashfs` builds from the modified specification without extracting root-owned special nodes to the host filesystem. The [upstream pseudo-file format](https://github.com/plougher/squashfs-tools/blob/master/Documentation/4.7.5/USAGE-UNSQUASHFS.md) explicitly supports editable metadata and data offsets. The code rejects pseudo commands that could execute arbitrary generators. The initial helper refused the format's separator line before producing any derivative; its parser was corrected and a regression case retained.

The derivative was re-exported and canonicalized:79,987 records before/after;65,249 original regular-file records. All other data hashes, numeric ownership, modes, inode timestamps, symlink/hardlink targets, special nodes and xattrs compared equal. The original source's machine-id was an empty file, not an imported machine identity. gzip replaces xz compression; actual kernel installation/boot compatibility remains part of the pending guest test. See `evidence/clean-source-validation.json` and the retained external canonical inventories.

Derived source Squashfs SHA256:

`4dfc8a6cf8967eb9332bfce8421895195316233c061231c7a47d06452514a638`

## Reviewed final transport

Both files exist **on Nexus only**, under `/home/nexus/.local/share/jarvis-g6k-vm164-build-r1/`:

| File | Bytes | SHA256 |
|---|---:|---|
| `ubuntu-26.04.1-g6k-vm164-r3.iso` |3,042,836,480 | `4161509164bcaff08506ad2ffcd52a6782eb34eb4b08d47f1bb8754016a07346` |
| `g6k-public-inputs-r1.iso` |6,230,048,768 | `8464ac2f1bb77ce9e29042b2fe6ae797992b420b7601fd0cfba8b13d42f10190` |

These are locally built derivatives, **not Ubuntu-signed images**. Trust follows the original authenticated media/public artifacts plus recorded tooling, bounded transformations, file comparisons and independently retained new hashes. Intermediate r1/r2 installer drafts remain preserved and are **not the reviewed upload candidates**; r3 requires explicit empty disk-signature metadata and refuses missing/null signature results. No image has been uploaded, attached or booted by this agent.

The installer retains all833 unchanged original ISO file records, changes the base Squashfs and checksum file, and replays the original boot catalog/BIOS boot image metadata as needed for new block locations. It adds only direct `autoinstall.yaml` and a pre-first-boot target guard. BIOS/UEFI catalog entries are present; catalog inspection is not a firmware boot test. Original kernel/initrd/package payload files compare unchanged. The public-data ISO is nonbootable and its140 embedded files independently reverify against the previous external139-input manifest plus the manifest itself.

ISO tool xorriso and its three private libraries were obtained from Ubuntu HTTPS artifacts after validating the signed release→compressed index→deb hash chain, using the retained archive fingerprint `F6ECB3762474EDA9D21B7022871920D1991BC93C`. Only unprivileged package-data extraction occurred: no apt install, system library replacement or maintainer script. Existing Nexus squashfs tools and Python form part of the trusted build environment; their identity is recorded in final verification, not presented as a new independent publisher attestation. Original supplier limitations for67/127 integrity-only selected distributions, GPUtil and the dependency bootstrap remain unchanged.

## Installer guard and limits

The direct media configuration has no password secret: `!` is a public account-lock value. It imports no SSH key, seed/config drive, root home, provider configuration or old cloud cache. It selects the derived minimized OS, disables installer refresh/geoip/online fallback/SSH server/key import, and requests direct ext4 installation on the exact planned disk serial. No network adapter is present. The original source's cloud-init disabled sentinel is present before first target boot; cloud-init is not cleaned afterward.

Before probing/formatting, the installer guard requires the planned VM UUID, loopback-only interfaces, exactly one64GiB disk named sda with the planned serial, and an explicitly empty signature list from read-only `wipefs --json --no-act`. An initialized disk, NIC, wrong UUID/serial, missing signature report or malformed state stops. This prevents a repeat ISO boot from silently reinstalling a previously initialized lab disk. It is still an unattended disk-formatting configuration **only for that virgin new disk**; do not boot it on any other machine or substitute a serial/UUID merely to get past a refusal.

The late target guard rechecks VM/disk/ext4 parentage, refuses any regenerated root/preparation `.ssh`, requires the disabled sentinel, creates distinct locked non-login test roles only when absent, initializes/records a fresh machine-id and writes exclusive root-only installation evidence. It never deletes a finding or creates a qualification marker. Normal successful installation powers off the **new** VM; an installation failure is retained for review. Generated target cloud inputs must still receive metadata/provenance inspection; no permission repair or claim that all cache is empty is made.

The ISO-pinned Subiquity7403 snapshot supplied literal schemas for11 configuration sections, all checked without executing installer code on Nexus. YAML and early guard code are validated and exercised with synthetic negative controls. Apt/network/command-list/version shapes are reviewed separately; **full Subiquity/curtin execution and actual target boot remain untested**. This packet therefore does not certify a successful OS installation, an empty real credential store, or scanner PASS.

Reproduction sources: `tools/build_clean_source.py`, `acquire_iso_tool.py`, `remaster_iso.py`, `verify_derivative.py`, `build_public_payload_iso.py`. These use exclusive new outputs and preserve intermediates; do not rerun over existing output names. The source export command and all tool versions/hashes are retained in evidence. Original offline input digests and the new media digests must be retained outside the removable media before any root use.

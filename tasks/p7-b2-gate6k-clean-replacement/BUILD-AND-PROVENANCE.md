# Build and provenance record

No replacement VM exists as a result of this task. Null values in `NEW-VM-IDENTITY.json` are deliberately unresolved, not approved identities. Evidence was collected on Nexus (`nexus-services`, `192.168.0.101`) starting 2026-10-27 UTC / 2026-10-26 America/Chicago.

## Independently pinned inputs

| Input | SHA256 |
|---|---|
| Ubuntu 26.04.1 live server amd64 ISO | `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927` |
| Corrected Gate 6K archive | `15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55` |
| Corrected source manifest, 618 files | `b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc` |
| Corrected release safe extractor | `31f77b42d6ee41f73abef56f8a59d5191a8695686cc2e79ced28236b623639d8` |
| Gate 6L dependency archive | `228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00` |
| Dependency manifest, 657 entries | `1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390` |
| Bundle safe extractor | `13792921e64036de94af62a95fddd343fbf37063b9dfd9c150764413edb2feeb` |
| Artifact manifest, 131 records | `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837` |

Original inputs remain at `/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1` and `/home/nexus/.local/share/jarvis-gate6k-preflight-fix`. The new credential-free **public-file staging area**, not a VM/runtime image, is `/home/nexus/.local/share/jarvis-g6k-clean-replacement`. Only explicitly pinned public inputs are eligible for transfer. No VM163 files are inputs.

Ubuntu checksums, detached signature and public key were fetched anew from HTTPS Ubuntu release/keyserver endpoints into an isolated temporary verification home, then retained under `evidence/ubuntu-*`. `gpgv` returned success with signer fingerprint `843938DF228D22F7B3742BC0D94AA3F0EFE21092`, independently matched to the [Ubuntu verification guide](https://ubuntu.com/tutorials/how-to-verify-ubuntu). The ISO digest matches the [published checksum](https://releases.ubuntu.com/26.04.1/SHA256SUMS). Temporary verification files were ephemeral public metadata, not guest evidence. The script neither imports a key into a user's normal keyring nor modifies the original media.

All dependency-bundle bytes reverified against the retained manifest. This does **not** newly authenticate all Python publishers: the historical risk register records 60/127 selected distributions with stronger publisher/repository provenance and 67 with weaker integrity-only provenance, plus the unsigned GPUtil tag/reproducible build limitation. Retain [the original supplier register](../p7-b2-gate6l-offline-dependency-bundle/SUPPLY-CHAIN-RISK-REGISTER.md), signature/build records and separate human risk review. No dependency substitutions, new vulnerability audit, model execution or online package installation were performed.

## Reproduction on Nexus

Read the tools first. `verify_inputs.py` uses exclusive output creation and is intended for a fresh evidence directory; do not overwrite prior evidence for a repeat run. It verifies full inventories, hashes, no links and stable file metadata. `inspect_iso.py` requires the already installed `unsquashfs`; it extracts only public source/defaults into a new evidence directory, never a mounted root. Neither tool executes downloaded guest code or contacts private infrastructure.

```bash
python3 -I -B tasks/p7-b2-gate6k-clean-replacement/tools/verify_inputs.py
python3 -I -B tasks/p7-b2-gate6k-clean-replacement/tools/inspect_iso.py
python3 -I -B tasks/p7-b2-gate6k-clean-replacement/tools/test_guards.py
```

The actual fresh flat export used the already verified bundle helper:

```bash
# Actual command already executed; destination now exists. Never rerun in place.
python3 -I -B /home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/tools/export_gate6k_artifacts.py /home/nexus/.local/share/jarvis-g6k-clean-replacement/public-artifacts 1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390
```

The preexisting `gate6k-flat-r1/ARTIFACTS.json` failed its pinned hash. Its refusal record is retained; no files there were changed, repaired or copied. The new export uses the verified bundle inventory instead. Ownership on Nexus remains the preparation user's; protected guest provisioning must establish writer exclusion, copy into exclusive root-owned destinations and independently rehash. Do not label staging immutable.

The fresh export was then packaged by the supplied preparation tool (already executed; exclusive destinations now exist):

```bash
python3 -I -B tasks/p7-b2-gate6k-clean-replacement/tools/prepare_transport.py
```

Actual transport:139 public input files plus `PUBLIC-INPUTS-SHA256SUMS`,6,229,447,516 bytes total. The flat131 artifacts account for3,034,192,090 bytes. The transport also includes the complete original dependency archive, corrected release archive, pinned extractors and Ubuntu's public signature/checksum/key. The OS ISO is present in `public-artifacts/ubuntu-26.04.1-live-server-amd64.iso`; it was not modified or remastered. Retain this transport manifest digest independently before moving public inputs:

`922b82cec3076e01577e410ac68c2d74f92d7d74f1886e215b1f83ed75ae1341`

No ISO-writing tools or QEMU/libguestfs provisioning tools were available in this session. The transport is a directory of checked public bytes, **not a generated ISO, booted image or root-protected installation**. It has not been transferred to PVE. On a trusted offline recipient, compare the external manifest digest first, then run `sha256sum -c PUBLIC-INPUTS-SHA256SUMS` within that exact fresh directory. Independently reject unexpected files/links and confirm the installed guest's exact inventories afterward; checksum verification alone is not an isolation attestation.

## Capacity and hardware design, pending measurement

Use four vCPUs, fixed 6000 MiB RAM, ballooning disabled, no NIC (including disconnected NICs), no QEMU guest-agent channel for remote command execution, no shares/passthrough/cloud-init drive, no host credentials, autostart off, trusted management console only. A new dedicated virtual disk should use a unique serial and recorded Proxmox volume ID. Prefer BIOS boot with a private ext4 `/` and, if needed, a separate private ext4 `/boot` on the same dedicated disk; no EFI filesystem that the unchanged mount gate would reject. Record actual partition UUIDs/filesystem UUIDs and boot source; never assume `/dev/sda2` from VM163.

Disk proposal: 64 GiB only if measured local storage, thin-pool **data and metadata** headroom, host reserve and all other commitments support it. It is not a verified allocation. Budget for OS, source, runtime, artifact export (~3 GB including the ISO), temporary bundle/archive copies, test logs and at least 21,474,836,480 available bytes afterward. Avoid duplicate full bundles in the guest where possible. Sparse advertised virtual capacity is not physical free storage. Select a smaller adequate disk only from an explicit verified byte budget, or stop for capacity resolution; do not reclaim old VM space. RAM proposal similarly needs actual `MemAvailable`, running VM configured limits, other workloads and at least a documented host reserve; do not assume swap or ballooning makes 6000 MiB available.

Recheck capacity and VMID immediately before creation; a read-only candidate is not a reservation. Use the normal atomic Proxmox create operation and preserve a partial new VM on failure for review. Never destroy a partially created VM, free a volume or retry with an existing VMID automatically.

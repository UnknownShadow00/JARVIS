# Human offline VM installation handoff

**No VM is authorized. Do not execute privileged provisioning until the human records exact VM-specific approval.** The dependency bundle is complete; this handoff does not grant production or multi-UID execution authority.

## Independently retain these identities

| Object | Exact SHA256 |
|---|---|
| Gate 6K source manifest | `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03` |
| Gate 6K source archive | `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d` |
| Gate 6K evidence seal | `5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6` |
| Gate 6L dependency archive | `228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00` |
| Gate 6L SHA256SUMS digest | `1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390` |
| Gate 6L bootstrap extractor | `13792921e64036de94af62a95fddd343fbf37063b9dfd9c150764413edb2feeb` |
| Gate 6K-compatible ARTIFACTS.json | `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837` |
| Ubuntu 26.04.1 server ISO | `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927` |

Archive on Nexus: `/home/nexus/.local/share/jarvis-gate6l-offline/gate6l-bundle-r1.tar` (3,189,688,320 bytes).
Bootstrap source: `/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/tools/extract_bundle.py`.
The ISO is in `bundle-r1/artifacts/os/ubuntu-26.04.1-live-server-amd64.iso`; it can be transferred separately through approved offline media. Its signed checksum and public verification key are in metadata/ubuntu. Do not copy Nexus virtualenvs, work/ fixtures, credentials or databases. Deliver only the sealed archive, independently pinned extractor, ISO and human approval record.

## Exact approval needed

The human must name: new VMID and UUID; trusted hypervisor node; guest machine-id; exact private ext4 disk identifier; approved console/session; the source and dependency digests above; synthetic qualification scope; snapshot/preservation policy. The trusted management console must independently establish these facts. A guest JSON marker or hostname does not prove them.

Target OS: signed Ubuntu Server 26.04.1 amd64. Linux x86-64 kernel with seccomp and AF_UNIX credential support; private ext4. Resource estimate:4 vCPU, 8 GiB RAM, 40 GiB disk, no GPU. Require at least20 GiB free before installation and before qualification. No attached NIC, production routes, shared mounts, forwarded SSH agent or credentials. No online installer updates. OS installation and four-user/root ownership provisioning are separately approved human work under the preserved Gate 6K plan, not commands executed here.

## Unprivileged offline installation commands after approved OS provisioning

The artifact media path below is an example mountpoint to be established by the approved human. These commands do not mount media, provision users or alter system libraries.

```bash
printf '%s  %s\n' '13792921e64036de94af62a95fddd343fbf37063b9dfd9c150764413edb2feeb' /media/offline/extract_bundle.py | sha256sum -c -
printf '%s  %s\n' '228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00' /media/offline/gate6l-bundle-r1.tar | sha256sum -c -
python3 -I -B /media/offline/extract_bundle.py /media/offline/gate6l-bundle-r1.tar "$HOME/gate6l-bundle" 228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00
python3 -I -B "$HOME/gate6l-bundle/tools/verify_bundle.py" "$HOME/gate6l-bundle" 1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390
python3 -I -B "$HOME/gate6l-bundle/tools/install_offline.py" 1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390
cat "$HOME/gate6l-bundle/work/INSTALL-RESULT.json"
cat "$HOME/gate6l-bundle/work/exact-runtime-check.log"
python3 -I -B "$HOME/gate6l-bundle/tools/export_gate6k_artifacts.py" "$HOME/gate6k-artifacts" 1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390
```

Bootstrap Python must be3.14.4 from the signed OS. The installer refuses root, wrong interpreter/architecture, insufficient free space, modified/missing/extra artifacts and preexisting work. It uses downloaded Python and private libraries thereafter. It performs no apt/dpkg installation, global pip install, system Python replacement, account creation, operational command, network download or provider generation. Never run `dpkg -i artifacts/debs/*.deb`: most collected OS packages are review/closure inputs, not an approved host provisioning list.

Expected results: all five installation steps PASS;127 exact distributions; Python 3.14.4; Python-linked SQLite 3.46.1; cryptography 46.0.5; libseccomp 2.6.0; Ed25519 synthetic verification; private-library origin checks; no broken pip requirements. Every source/install package hash is already in the retained manifest. The unchanged Gate 6K artifact verifier accepted the 131-record export on Nexus. Its provenance fields explicitly retain human-review-pending status.

The fixture is under `work/downloaded-runtime` and `work/mixed-env-r2`. Do not run the privileged authority helper from a preparation-user-writable runtime. The later human-reviewed provisioning stage must place the approved runtime/source/configuration under protected ownership and bind its exact identity to the approved runner invocation. That operation requires the separate exact VM approval and ownership checks; it is not authorized by this package's PASS.

## Evidence and stopping

Keep `work/INSTALL-RESULT.json`, all work/*.log, package/source/manifest digests, and console identity evidence. Store only minimized nonsecret outcomes in synchronized task documents. No signing secret is written by the dependency tests. Synthetic Ed25519 material exists only in process memory.

Stop on any nonzero command or unexpected package/path/version/library. Preserve the complete failed directory. Never erase/reuse it automatically, switch on networking, substitute a newer version or repair broad permissions. Retry only in a reviewed fresh directory; real VM qualification failures require reviewed clean-state authorization. Cleanup requires separate human authorization. No power-cut test is authorized.

The bundle's67 integrity-only selected distributions require explicit supply-chain risk review. Publisher signatures establish origin, not absence of vulnerabilities. X1–X11, AI/legacy attestations, protected multi-UID qualification, V2 disposition and all release/pilot approvals remain pending.

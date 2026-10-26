# Gate6K VM163 preflight compatibility fix

**ISOLATED FIX COMPLETE — VM UPDATE AND QUALIFICATION AUTHORIZATION PENDING**

The confirmed path-existence blocker is repaired in a separately versioned candidate. Ordinary protected preparation directories no longer imply credential exposure. Active systemd credential payloads still refuse. Opaque cloud-init cache is never read or deserialized and requires a snapshot-bound human fresh-image provenance review when populated. Unknown or exposed credentials, unsafe mounts and prohibited identities remain fail-closed.

Two additional compatibility defects are repaired: isolated `-I` sibling import and explicit private `/boot` partition handling. The offline regression harness now binds to the Nexus interpreter instead of a Core path. All V3 application files, protected-authority implementation and dependency pins remain unchanged.

- Prior Gate6K manifest: `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03`; archive: `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d`; evidence seal: `5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6`. All historical source/evidence entries reverify.
- Replacement: `/home/nexus/.local/share/jarvis-gate6k-preflight-fix/gate6k-vm163-preflight-r1.tar` (5,416,960 bytes,619 members).
- Archive SHA256: `15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55`.
- Source manifest SHA256: `b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc`.
- Bootstrap SHA256: `31f77b42d6ee41f73abef56f8a59d5191a8695686cc2e79ced28236b623639d8`.
- Tests:133 standalone passes (84 existing +49 new), repeated successfully on extracted archive;5 additional mocked handoff-gate checks pass; full7741 passed /11 deselected /0 failed. The full suite initially exposed a missing synthetic canary prerequisite; it was corrected without changing the assertion and the full suite rerun. See TEST-RESULTS.md.

Nexus is actually Ubuntu26.04 LTS x86-64 with the required runtime versions; the supplied VM163 topology is covered by synthetic fixtures. This does not claim VM163 preflight PASS. Known continuing blockers: mounted offline ISO, absent `/opt/g6k-offline`, absent VM-specific approval marker. Actual systemd credential payloads, cloud provenance, mount propagation, role GIDs/shells, disk free space and protected runtime/artifact review still require human verification.

Exact side-by-side update instructions: OFFLINE-VM-UPDATE-PROCEDURE.md. Install only after explicit approval into `/opt/g6k-preflight-r1`; preserve `/opt/g6j-release`. The invalid approval template deliberately refuses until real identity/review fields are supplied. New release hashes require renewed explicit authorization; prior-digest approval is insufficient. No qualification launch is included in the update commands.

Next action: review this source/patch/evidence and explicitly approve the VM163 offline side-by-side update and read-only diagnostic scope, naming VMID163,UUID `1d279e9b-12cb-4a02-8815-a682cb9457a9`,pve,exact disk and console plus the replacement hashes. Resolve reported blockers under separately approved human preparation. Privileged qualification remains a distinct later authorization.

No VM163,Core,Proxmox or AI host was accessed. No privileged qualification, credentials, real provider operations, production changes, commits or pushes. Production state was not freshly inspected. Evidence seal is recorded separately alongside this packet and in the final handback, avoiding circular hashing.

PRODUCTION JARVIS: UNCHANGED BY THIS TASK; NOT READ BACK

V2 EPOCH: PRESERVED; NOT REVERIFIED

V3 CANDIDATE: ISOLATED ONLY

GENUINE MULTI-UID QUALIFICATION: NOT RUN

VM163 UPDATE / PRIVILEGED QUALIFICATION: SEPARATE AUTHORIZATION REQUIRED

X1–X11: OPERATOR APPROVAL PENDING

AI/LEGACY ATTESTATIONS: PENDING

V2 RETIREMENT / REAL V3 SUCCESSOR / DEPLOYMENT: NOT AUTHORIZED

MEASUREMENT: NOT STARTED

FORMAL P7 EXIT: NOT COMPLETE

# JARVIS P7 GATE 6L — OFFLINE DEPENDENCY BUNDLE COMPLETE

The exact 127-distribution environment is now reproducibly installable from local artifacts with network socket creation denied. A complete packaged-archive extraction and clean offline installation passed. This is Nexus-only preparation, not disposable-VM or multi-UID qualification.

## Entry and output identities

- Gate 6K candidate: `/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2`.
- Source manifest: `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03`;615 entries verified at entry.
- Source archive: `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d`.
- Previous evidence seal: `5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6`;124 entries verified at entry.
- Final historical hashes and both dependency lockfiles reverified unchanged.
- New artifact workspace: `/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1`.
- Deliverable archive: `/home/nexus/.local/share/jarvis-gate6l-offline/gate6l-bundle-r1.tar`.
- Archive SHA256: `228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00`.
- Artifact manifest SHA256: `1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390`;657 entries and658 outer archive members independently byte-verified.
- Gate 6K-compatible131-entry artifact record: `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837`.
- Documentation evidence seal is the SHA256 of this packet's SHA256SUMS, recorded separately in the sibling `.seal` file to avoid circularity.

## Actual artifact and compatibility results

All 127 pins have installable artifacts:108 exact public wheels,18 signed Ubuntu Python payloads and one locally built GPUtil wheel. No primary artifact is missing.345 artifacts totaling3,151,074,186 bytes were acquired/built, including109 public target wheels,7 sdists,193 signed debs,31 verification-tool wheels, the official CPython and SQLite sources, upstream GPUtil source, built GPUtil wheel and signed Ubuntu ISO. Large binaries are outside task documents.

60/127 selected distributions have verified publisher/repository signatures:42 selected PyPI wheels plus18 Ubuntu payloads.67 retain weaker HTTPS/hash/source-review provenance, explicitly flagged. Across downloaded inputs,43 PyPI attestations,193 deb signature chains, CPython Sigstore and the ISO checksum signature verified. No signature is inferred from a same-index checksum.

Ubuntu Server 26.04.1 amd64 is the artifact-verified target. Downloaded Python 3.14.4 runs with private downloaded SQLite 3.46.1, OpenSSL 3.5.5 and libseccomp 2.6.0. The Python module's actual library path and sqlite_source_id were inspected; the CLI sqlite version was not used as proof. cryptography 46.0.5 passes synthetic Ed25519 sign/verify with the signed native CFFI backend. The exact runtime checks all 127 versions, no extra/duplicate distributions, private library origins and core FastAPI/NumPy/Pydantic imports. Actual VM boot and other OS utilities remain untested.

## Testing and demonstrated corrections

48 new preparation tests pass, 0 failures. All delivered Python sources parse.103-wheel subset installation and pip check pass; this is reported separately from the full 127 mixed installation. Fresh-copy and packaged-archive clean-install rehearsals pass all five steps with kernel network denial. Gate 6K's unchanged verifier accepts131 actual exported artifacts. GPUtil rebuilds are byte-identical. No full V3 suite rerun was necessary because application/authority source is unchanged; historical 7741 passed /11 deselected /0 failed and Golden 12/20 remain historical.

Demonstrated corrections: resolved distro-only pins instead of treating the 127-version inventory as a pip lock; selected exact Ubuntu cryptography plus native CFFI backend after a real missing-module failure; rejected GPUtil's unsafe-mode PyPI tar and reviewed an upstream tagged archive whose code differs only in line endings; corrected the offline dependency closure for versioned virtual Debian providers; rejected host-library fallback and duplicate metadata; added bounded safe bundle extraction; fixed Gate 6K export incompatibility with `+`/`~` filenames using digest aliases. All initial failures remain recorded. No V3 experimental semantics or authority implementation changed.

## Remaining authorization and next action

Review the exact archive, manifest, source record and67 integrity-only provenance risks. Then separately authorize a specific new disposable VM by VMID+UUID, hypervisor, guest machine-id, exact private disk, console/session, approved digests, test scope and snapshot/preservation policy. Follow HUMAN-VM-INSTALLATION-HANDOFF.md. No VM has been created, identified as approved, provisioned or subjected to privileged tests.

Only Nexus was contacted for development and public distribution sources for acquisition. No production SSH, readback, source/config/state access or mutation occurred. “Unchanged by this task” is an action-scope claim, not fresh production-state verification. X1–X11 and independent AI/legacy endpoint/model/GPU/topology attestations remain pending.

PRODUCTION JARVIS: UNCHANGED BY THIS TASK

V2 EPOCH: PRESERVED

V3: ISOLATED ONLY

GENUINE MULTI-UID QUALIFICATION: NOT RUN

DISPOSABLE VM: NOT YET AUTHORIZED

X1–X11: OPERATOR APPROVAL PENDING

AI/LEGACY ATTESTATIONS: PENDING

V3 DEPLOYMENT: NOT AUTHORIZED

REAL PILOT ATTEMPTS: ZERO HISTORICALLY

MEASUREMENT: NOT STARTED

FORMAL P7 EXIT: NOT COMPLETE

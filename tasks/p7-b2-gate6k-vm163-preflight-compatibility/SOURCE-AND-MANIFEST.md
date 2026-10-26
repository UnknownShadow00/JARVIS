# Reviewed replacement identities

| Object | SHA256 |
|---|---|
| Preserved Gate6K source manifest | `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03` |
| Preserved Gate6K archive | `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d` |
| Preserved Gate6K evidence seal | `5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6` |
| Replacement source manifest | `b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc` |
| Replacement source archive | `15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55` |
| Replacement bootstrap extractor | `31f77b42d6ee41f73abef56f8a59d5191a8695686cc2e79ced28236b623639d8` |

Authoritative new candidate: `/home/nexus/.local/share/jarvis-gate6k-preflight-fix/candidate-r1`.

Replacement archive: `/home/nexus/.local/share/jarvis-gate6k-preflight-fix/gate6k-vm163-preflight-r1.tar` —5,416,960 bytes,619 regular-file members,618 source entries plus `SOURCE-SHA256SUMS`.

Bootstrap: `/home/nexus/.local/share/jarvis-gate6k-preflight-fix/safe_extract_vm163_r1.py`. Transport checksums: `REPLACEMENT-ARTIFACTS-SHA256SUMS` in the same private directory. Retain these expected values independently before transfer; a colocated checksum file alone is not operator authorization.

Working test copy: `release-r1` under the same private parent; its fixture trees and logs are deliberately excluded from the archive. Actual reviewed unprivileged extraction: `extraction-check-r1`. Packaging copies only the original615 source names plus3 explicit new modules, verifies application byte identity, parses Python syntax, creates a reproducible normalized USTAR archive, validates its complete structure, and performs an exclusive safe extraction. No arbitrary directory tree export or fixture/private signing-key export.

Changed files (10): `disposable/environment_probe.py`, `disposable/compatibility_tests.py`, `disposable/preflight_report.py`, `disposable/qualify_all.py`, `disposable/qualify_multi_uid.py`, `disposable/safe_extract.py`, `disposable/safety_preflight.py`, `guard/sitecustomize.py`, `run_tests.py`, `supervise_tests.py`. The latter3 are test harness portability only. All `repo/` files, both dependency pin files and protected-authority implementation are unchanged.

Reviewable patch: `evidence/gate6k-to-vm163-fix.patch`. Actual source manifest: `evidence/SOURCE-SHA256SUMS`. Changed executable source is also included under `evidence/changed-source/`; binaries stay outside synchronized documentation. Source identity and evidence identity are separate, noncircular manifests. The packet seal is retained outside this directory and reported in the final handback.

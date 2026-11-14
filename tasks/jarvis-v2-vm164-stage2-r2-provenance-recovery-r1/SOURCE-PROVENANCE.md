# Source provenance

The authority for expected R2 bytes is the independent rejection audit, not a regenerated R2 manifest. Trust chain:

1. Previously recorded audit manifest SHA256 `e721c7769c3644fe8d6f7ef74d66d7e1c2e99b1614f9a841c8aba2bcf0db0ddf` matches the retained MANIFEST.json.
2. That manifest hashes evidence/INPUT-INVENTORY.json and the audit reports/probes. Every audit payload hash was checked.
3. INPUT-INVENTORY.json gives independent per-file SHA256 and size for all 67 reviewed R2 files, including all 14 src modules, tests, catalogue, schemas, reports, manifests and retained evidence.
4. Every current R2 byte matches those independent values. SOURCE-MANIFEST.json also matches its independently reviewed hash, and its source-file hashes match the audit inventory.
5. Canonical and old isolated R2 copies have identical file sets, bytes and observed permission modes. The new index and committed blobs match those same independent expected hashes.

VERIFIED-FILE-INVENTORY.json gives expected, actual and committed SHA256, physical source, independent reference, current mode and committed Git mode for every added file. No missing/unexpected R2 file or symlink was accepted. No reviewed manifest was regenerated.

The two existing copies are canonical tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r2/ and the same relative path in ../JARVIS-vm164-stage2-safety-r2/. Both were untracked before recovery. All registered worktrees were inspected for an R2 packet; these were the only copies found there. This is not a claim that no unrelated copy exists anywhere on the filesystem.

All R2 files are regular and non-executable; their containing paths have no symlinks. Observed permission modes across the 94 added implementation/audit files are 0600 and 0664. The copy preserves those POSIX modes; all committed Git modes are 100644. Git does not preserve group write/read distinctions or ownership. The old audit recorded bytes/sizes, not historical POSIX modes; we do not claim independent historical mode attestation. These Python tools are invoked by an interpreter, and no reviewed source executable bit was introduced. This is local development custody, not future root-owned host placement proof.

The five absolute symlinks in the much older bootstrap evidence are already tracked in the verified parent and are outside the R2 source tree. Their literal targets and 120000 modes were checked without dereferencing them. See evidence/SYMLINK-REPRESENTATION.json. No new source symlink or escaping source dependency was introduced.

The source imports only its own fourteen modules and Python standard-library modules (evidence/IMPORTS.json). Packet verification additionally reads the tracked predecessor packets. The final replay rejects canonical-repository reads outside its report directory and records module origins. One legacy regression uses a fixed canonical path for the first-action JSON; the wrapper redirects only that read to the identical committed fixture. Legacy tests/run.py and tests/reproduce.py also contain canonical path references but were not used as runners. Their original bytes are retained. No test assertion was changed and no uncommitted application file supplied a dependency.

Limit: this establishes reproducible local provenance against previously recorded independent audit evidence. Neither local manifests nor this unsigned recovery commit establish remote attestation, protected historical custody, historical filesystem ownership or the truth of synthetic host observations.

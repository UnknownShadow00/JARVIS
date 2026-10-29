# Evidence manifest and provenance

This packet is sealed by `SHA256SUMS` (relative file paths, SHA256 for every packet member except that manifest) and the adjacent `p7-b2-gate6k-vm164-r4-investigation.seal` (manifest SHA256). The seal detects changes against a retained digest; it is not a signature, independent witness or proof that future mutable files cannot be altered. `tasks/loop-log.md` records completion and scope separately, outside the packet seal.

| Artifact | Origin and meaning |
|---|---|
| `evidence/operator-observation.json` | Conversation observations including automatic-failure clarification; no raw live evidence acquired |
| `evidence/local-input-verification.json` | Current Nexus r4 ISO digest, embedded file digests and verification of all prior sealed r4 members; does not verify live media |
| `evidence/local-input-run.txt` | Local input-verifier stdout; no media construction |
| `evidence/autoinstall.yaml`, `g6k-disk-guard-r4.py`, `boot-grub-grub.cfg` | Exact small files parsed from retained hash-verified r4 ISO |
| `evidence/source-record.json`, `pinned-source/*` | 22 exact files extracted from the hash-verified retained 7403 snap, with original paths and SHA256; installer code not imported as a live application |
| `evidence/tests-red.txt`, `tests-first.txt`, `tests-final.txt` | New suite development/final outputs; red is a missing-module error; final is 28 passing tests |
| `evidence/r4-baseline-tests.txt` | Unmodified r4 18-test regression/pinned matcher suite output |
| `evidence/verification.json` | Test counts/results, interpreter, syntax and source-record checks; no real disk tests |
| `evidence/public-references.json` | Official public documentation URLs consulted; contextual corroboration rather than runtime evidence |
| `tools/guard_proposal.py` | Pure final admission predicates; no live collector or installer integration |
| `tools/test_proposal.py` | Synthetic fixtures, exact pinned startup AST with inert collaborators, regular-file-only concurrency demonstration |
| `tools/capture_local_inputs.py` | Reproducible read-only local artifact verification/capture; cannot construct an ISO or access a VM |
| Reports | Root-cause assessment, revised design, exact proposed operator procedure and test/self-review record |

Key retained inputs:

- r4 ISO: `/home/nexus/.local/share/jarvis-g6k-vm164-installer-r4/ubuntu-26.04.1-g6k-vm164-r4.iso`, SHA256 `050875e2f3ffd5a7711bb2f520bce98404416d2117faedf2ba608831e2a416f3`.
- Subiquity snap: `/home/nexus/.local/share/jarvis-g6k-vm164-build-r1/subiquity_7403.snap`, SHA256 `ee9467fec724cf2a7f4fc61641a4a05d84f7730f06b8fefaceaf0b51a9a0331b`.
- Prior r4 manifest SHA256: `1915c8d8e1d75984d17a72bc33f6f933c2380670146534da906151de05ff9b87`.
- Embedded r4 early guard SHA256: `9f33c3630f60e9999a5b87983d1ec7c56304e458e61e86d5a469fb8215d92c82`.
- Embedded r4 autoinstall SHA256: `6cd4fcb481a9d18c41126deb05d3c4457627a309dff20b2364369b0fa85d4121`.

Not present: raw preboot Proxmox scan; live installer/journal/curtin/cloud-init logs; live effective configuration; running executable/revision/media attestation; backing-volume access timeline; raw GPT/ext4 headers; disk image; RAM image; independent acquisition or witness record. Their absence bounds attribution. The reported UUID/boot/GPT IDs are identifiers, not file hashes or provenance proofs.

Verify from the project root:

```bash
sha256sum -c tasks/p7-b2-gate6k-vm164-r4-investigation.seal
(
    cd tasks/p7-b2-gate6k-vm164-r4-investigation
    sha256sum -c SHA256SUMS
)
```

Preserve this packet and prior packets. A later evidence export must be stored separately, hashed at acquisition and receipt, and linked by acquisition provenance rather than silently replacing the conversation record.

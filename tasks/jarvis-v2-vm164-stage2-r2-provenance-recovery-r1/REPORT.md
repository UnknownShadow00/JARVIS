# R2 provenance recovery R1

**PASS_OFFLINE_R2_PROVENANCE_BASELINE_READY_FOR_R3**

The exact reviewed R2 implementation was recovered and committed unchanged in a new isolated worktree. This is a new provenance recovery commit, not a claim that R2 was committed at the time of its review. The independently rejected behavior is preserved: all sixteen Astra failures remain reproducible. R3 implementation has not started. Stage 2 remains NOT AUTHORIZED.

| Git identity | Value |
|---|---|
| Branch | `codex/jarvis-v2-stage2-r2-provenance-baseline-r1` |
| Worktree | `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-stage2-r2-provenance-baseline-r1` |
| Verified parent | `4c0f9ff666ac3bbce5f695a6b071e42320911652` |
| Recovery commit | `5088a240943f2d39b67ca7d528ea8e5f7e51d6f9` |
| Recovery tree | `089ec4e0364578548cceff4abadd65adfbac93dd` |

The commit adds exactly 94 audited files: all 67 R2 implementation packet files and all 27 second independent rejection audit files. The 29 original preparation, 15 first audit and 96 sealed Host Enforcement R3 files already exist unchanged in the verified parent. The exact 94 paths, source locations, expected independent hashes, committed hashes and Git modes appear in VERIFIED-FILE-INVENTORY.json and evidence/STAGED-INVENTORY.txt.

The separate recovery report and logs remain in canonical tasks/jarvis-v2-vm164-stage2-r2-provenance-recovery-r1/; they are intentionally outside the recovered implementation commit. No canonical merge, push or application modification occurred. The previous blocked R3 packet remains unchanged.

## Provenance established

The audit's previously recorded manifest SHA256 is `e721c7769c3644fe8d6f7ef74d66d7e1c2e99b1614f9a841c8aba2bcf0db0ddf`. Its sealed INPUT-INVENTORY independently names every reviewed R2 file and hash. Both existing R2 copies match every expected byte. All fourteen source modules match the independent inventory and the source-tree digest `3a95bf671008ff46e5e45287c3be58076491c6fed6764cd10c18b906f2bcabea`.

R2 was untracked in canonical and the previous R2 worktree. No existing R2 implementation commit was found in all refs/reflogs; a full local object check found no unreachable commits. The original engineering report identifies the same parent as its base; the independent audit records that HEAD. All 140 direct predecessor file blobs and modes match that parent. No uncommitted external implementation dependency was needed by the final replay.

## Verification outcome

- Original preparation: 71 passed.
- Previous audit against R2: 30 passed.
- R2 regression/design: 95 passed.
- Latest independent probes: 35 passed, exactly 16 expected failures.
- Extra historical controls: original audit 20 passed/10 failed; old design checks 3 expected failures.
- Final runs: 280 executions of 247 distinct methods; 251 passes, 29 expected historical failures, zero errors/skips or unexpected final failures.
- Existing synthetic twelve-case record and predecessor integrity verification pass. These do not establish live safety.

The first replay attempt encountered checkout/harness issues, retained under evidence/attempt-1/. It is not hidden from totals: 280 earlier executions, 249 passes, 31 failures (two harness-induced), zero unit errors/skips, plus two runner interruptions after suites. See TEST-RESULTS.md for remediation and combined counts. No reviewed assertion or implementation was changed.

All 274 canonical historical files across six packets and the 67-file previous R2 worktree copy retain their original bytes and modes. The baseline checkout is clean before and after verification. Local checksums are not external attestation or independent historical custody; historical permission modes were not captured by the audit. Current non-executable modes were verified between both copies and preserved as Git mode 100644.

**No remaining source-provenance blocker was found within this scope. R3 may begin later from the exact recovery commit.** Its sixteen safety defects, real systemd behavior, fresh privilege proof and separate review/authorization remain unresolved. The immediate next action is offline verification of this commit and the handoff; no host command is authorized.

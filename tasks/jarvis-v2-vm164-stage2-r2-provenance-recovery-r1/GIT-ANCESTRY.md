# Git ancestry and exact commit scope

Verified chain:

```text
5088a240943f2d39b67ca7d528ea8e5f7e51d6f9  Recover byte-identical reviewed Stage 2 R2 baseline
  parent 4c0f9ff666ac3bbce5f695a6b071e42320911652  Nightly snapshot 2026-11-12
    parent 9315be3f4829bdb561ef4d552e2547fa8feb3116  Nightly snapshot 2026-11-11
```

The original R2 REPORT.md states that its worktree was based on 4c0f9ff66. The independent audit PRESERVATION-AND-LIMITS.md records the full same HEAD, and the previous R3 blocker records matching canonical and R2 HEADs. We verified the parent relationship and the 140 direct predecessor blobs/modes against independent inventory evidence before creating the worktree. The parent was not selected merely because it was current HEAD.

Before recovery, `git log --all --reflog -- <R2 path>` was empty and no R2 path was tracked in either existing worktree. `git fsck --full --unreachable --no-reflogs` exited zero, reporting unreachable trees/blobs but no commits. No alternate implementation commit was found. No objects were removed or rewritten.

Branch: `codex/jarvis-v2-stage2-r2-provenance-baseline-r1`. Worktree: `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-stage2-r2-provenance-baseline-r1`. Tree: `089ec4e0364578548cceff4abadd65adfbac93dd`. The new commit has exactly one parent, `4c0f9ff666ac3bbce5f695a6b071e42320911652`. The parent remains canonical HEAD on docs/p7-d06-d07-passive-review; the old R2 branch also remains there.

Only the explicit 94-path audited inventory was passed to git add. No add -A, broad add, stash, reset, clean, merge or push was used. Before commit, staged bytes and 100644 modes were checked individually. After commit, diff-tree equals the same explicit inventory and all committed SHA256s equal independent expectations. No applicable Git attributes/filter transformation was present. Git hooks and signing were disabled only for the relevant commands; no shared Git configuration was changed.

Included additions: the complete 67-file reviewed R2 packet and 27-file second rejection audit, including the untouched independent probes and integrity evidence. Already inherited unchanged: preparation 29, first audit 15, sealed R3 96, plus their tracked predecessor chain.

Intentionally excluded from commit: this new recovery report/evidence/tools, the 40-file blocked R3 packet, canonical task-log changes, duplicate copies from the old R2 worktree, and all unrelated modified/untracked work. Every other parent path is unchanged. The recovery report is separate so it can identify the final commit/tree without a circular self-reference.

Checkout issue: inherited core.symlinks=false represented five historical tracked evidence links as text. Only those exact five new-worktree paths were restored from the index using a per-command core.symlinks=true override. No tree or historical artifact changed. Their literal absolute targets were not followed, and no service-manager path was touched. The checkout remained Git-clean. Future checkouts must preserve those links to run the full sealed predecessor verifier.

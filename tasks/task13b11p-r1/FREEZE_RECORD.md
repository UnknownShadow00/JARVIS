# RECORDED-TURN ADMISSION CONTRACT V1 — freeze record

Frozen 2026-10-02 in resolution of follow-up P-B01, raised by the blocked Task 13B11P.

## Baselines

| Item | Value |
|---|---|
| Production baseline (entry and exit) | `db54d615c3ee023d753e86143860c4efdc251230` |
| Production tracked files, digests identical at exit | 337 |
| `app/execution/pipeline.py` at the baseline | absent |
| Workspace parent at task start | `29c6acd9f36c7fc4c7af5e9ab5063437065193e5` (the canonical Task 13B11P blocked checkpoint) |
| Workspace parent of this task's commit | `5ac314f` — see "Intervening automated commit" below |
| Hermes checkpoint | `2237be355906fbe6065ce1815711eee52b2d646e`, clean, 0 processes |
| Runtime | `execution.mode: "legacy"`, `hermes_brain: false`, `hermes_enabled: false` |
| Predecessor sealed evidence bundles verified | 45, zero failures |
| Frozen P7 PIPELINE CONTRACT V1 manifest, re-verified | `02d208f7d7f26c9f483f7dcb272620cbb8444426e00b1ee1293193d1dbb5779e`, 18 entries, zero failures |
| Blocked Task 13B11P bundle, re-verified | `f3f161c56f90a78459588b152a592c8e0867a7d97c29a8ba74031dd995ba53d1`, 38 entries, zero failures |

## Version and scope

Version: **RECORDED-TURN ADMISSION CONTRACT V1**. It is additive to, and subordinate to,
P7 PIPELINE CONTRACT V1 (task13b11o-r1), which is unchanged: no frozen file there was
edited, no V2 of it was created, and no production contract for P0–P6 changed. The blocked
Task 13B11P documentation and evidence are preserved unchanged as history.

Freeze scope: the admission API of the passive recorded/static composition boundary, its
validation order, its failure representation, its idempotence and execution-count
invariants, and the S08–S09 seam. No implementation, no live mapping, no fallback renderer,
no executor seam, no schema change, and no model, dispatcher, store, provenance or audit
activity is authorized by it.

## Exact canonical file set

The 18 entries named in `CONTRACT-ARTIFACTS.sha256` — 17 Markdown documents plus
`admission-matrix.json`. No implicit directory membership: a file not listed in the
manifest is not part of this freeze.

Manifest SHA-256: `203eedc6c55b2e68c3697453e0d3d0bde2556e5578ce1cfec9ad41e0998e3919`
`sha256sum -c CONTRACT-ARTIFACTS.sha256`: 18 verified, zero failures.

Admission matrix SHA-256:
`6b454b2c8d881327b88cef73ae03a6465286bb7fb589e942f1bc3789d76fb434` (32 rows), frozen
while `app/execution/pipeline.py` was provably absent.

This record and the manifest itself are excluded from the manifest to prevent
self-reference, and are included in the evidence bundle seal.

## Intervening automated commit

While these documents were being written, an unrelated automated nightly-snapshot job
in this workspace committed the four files that existed at that moment —
`RECORDED_TURN_ADMISSION_V1.md`, `TURN_INPUT_SCHEMA.md`, `ADMISSION_MODES.md`,
`CONFIRMATION_CONTINUATION.md` — as `5ac314f` "Nightly snapshot 2026-10-01", and pushed
that commit to `origin/snapshot`. It was not an action of this task.

Established facts: the committed blobs are byte-identical to the working tree, so every
digest in the manifest is unaffected; the four files are drafts of final content, not a
different version; `origin/main` is unchanged at `2d7a2ec816500610eafdba4c1a3c0d73f5594c18`
and 39 commits behind local `main`, so nothing from this task reached `main`; the
production repository was untouched by it. The task's "no push" constraint is satisfied
for every push this task performed, which is none; the snapshot push is recorded here
rather than omitted. This task's own documentation commit is a single commit whose parent
is `5ac314f`.

## Regression at freeze

Full suite 5468 passed / 11 deselected / 0 failed. Golden 12/20 with the same eight
scenario ids and identical metrics. Legacy probe
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`.

## Discipline

Do not edit the frozen files silently. A discovered defect in this contract requires
explicit subsequent version history with new hashes and new evidence, exactly as the
13B11O → 13B11O-R1 and classifier R1 → R2 histories did. The admission matrix must be
re-verified against this digest before any implementation code is written, and a row that
the implementation shows to be wrong is a contract defect to report, not a row to relax.

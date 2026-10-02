# Task 13B11P-R1 — contract task

JARVIS P7 RECORDED-TURN ADMISSION CONTRACT V1 FROZEN

Contract only. No production code was written, no production commit was created, no policy
or schema changed, and no live activity occurred. P7 is not implemented by this task.

## Entry verification

Production `/home/jarvis/JARVIS` at `db54d615c3ee023d753e86143860c4efdc251230`, clean,
zero untracked files, `app/execution/pipeline.py` absent. `execution.mode: "legacy"`,
`execution.hermes_brain: false`, `agent.hermes_enabled: false`. Hermes
`/home/jarvis/.hermes-poc/hermes-agent` at `2237be355906fbe6065ce1815711eee52b2d646e`,
clean, zero processes. Workspace at the canonical Task 13B11P blocked checkpoint,
`29c6acd9f36c7fc4c7af5e9ab5063437065193e5`, clean. All 45 sealed evidence bundles verify
with zero failures, including the 13B11P bundle (38 entries, manifest
`f3f161c56f90a78459588b152a592c8e0867a7d97c29a8ba74031dd995ba53d1`) and the 18 frozen
13B11O-R1 contract entries (manifest
`02d208f7d7f26c9f483f7dcb272620cbb8444426e00b1ee1293193d1dbb5779e`).

## Contracts read before deciding anything

tasks/task13b11p/FOLLOWUPS.md, PIPELINE_API.md, STATE_PROJECTIONS.md, PASSIVE_DISPATCH.md;
all 18 frozen task13b11o-r1 artifacts; the 13B11N adapter contract; 13B11J confirmation,
13B11K dispatcher, 13B11L/P6 obligation and 13B11M response-builder contracts; 13B11A
dependency graph, phases and target component map; 13B10D execution contract v1. Then the
actual production sources: `types.py`, `correlation.py`, `canonicalize.py`,
`classifier.py`, `router.py`, `lane.py`, `permissions.py`, `confirmation.py`,
`dispatch.py`, `provenance.py`, `obligations.py`, `response.py` and
`app/brain/hermes_adapter.py`.

Three findings from the sources shaped the contract rather than being assumed:

1. `ConfirmationStore.confirm` validates completely and raises without advancing; the one
   edge that claims execution is `claim_for_dispatch`, which mints the binding to an
   invocation in the same step. There is no state between "unclaimed" and "claimed", which
   is why exactly three admission shapes exist and why modes B and C are disjoint.
2. `invocation.confirmation_id is not None` does **not** prove a claim. Dispatcher gate 5
   returns `CONFIRMATION_REQUIRED` with `confirmation_absent`,
   `confirmation_binding_absent` or `confirmation_authority_unavailable` while the id is
   present and nothing was claimed. `confirmation_claimed` is therefore derived from
   `result.executed` plus the invocation's outcome — the only derivation the two frozen P6
   contradiction checks permit.
3. `browser.open` is an actual `ALLOW` row under `BALANCED`, so the "authorized but no
   result" case is reachable with the real frozen policy and needed no mocked P4. It is
   matrix row `A03`, and it is the case P-B01 most sharply exposed.

## What was produced

Sixteen documents plus the machine-readable matrix and the freeze record. The canonical
contract is RECORDED_TURN_ADMISSION_V1.md; the normative detail is in TURN_INPUT_SCHEMA.md,
ADMISSION_MODES.md, CONFIRMATION_CONTINUATION.md, RESULT_REPLAY.md, S08_S09_CONTRACT.md,
ASSOCIATION_RULES.md, IDEMPOTENCE.md, ADMISSION_FAILURES.md, ADMISSION_MATRIX.md with
`admission-matrix.json`, and SECURITY_INVARIANTS.md. Acceptance, deferrals and follow-ups
are in IMPLEMENTATION_ACCEPTANCE.md, DEFERRED.md and FOLLOWUPS.md. The exact file set and
digests are in FREEZE_RECORD.md and CONTRACT-ARTIFACTS.sha256.

No frozen 13B11O-R1 or 13B11P file was edited; the blocked 13B11P analysis is preserved as
history.

## Method

The admission matrix was written and hashed while `app/execution/pipeline.py` remains
absent, which is the series' freeze-first discipline: the table is the independent
specification, and where the implementation disagrees the table wins and the disagreement
is the finding. No existing test, fixture or corpus was modified; no new test was written,
because there is no module to test.

No P7-local reason or stage was added: all seven failure categories the task names map
onto the already-closed `PipelineStopReason` set, and the resulting coarseness is recorded
as a limitation with a follow-up rather than resolved by editing a frozen enum.

## Regression

Production unchanged and re-verified after the documentation work: HEAD
`db54d615c3ee023d753e86143860c4efdc251230`, clean, all tracked file digests identical to
entry. Full suite 5468 passed / 11 deselected / 0 failed. Golden 12/20 with the same eight
scenario ids. Legacy probe
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`. Hermes unchanged,
stopped, disabled; no model, Ollama or provider call.

One workspace documentation commit. No production commit, and this task performed no
push.

Recorded separately: an unrelated automated nightly-snapshot job in this workspace
committed four in-progress documents as `5ac314f` and pushed that commit to
`origin/snapshot` while the work was in progress. The blobs are byte-identical to the
working tree, `origin/main` is unchanged, and production was untouched. Details and the
corrected workspace parent are in FREEZE_RECORD.md.

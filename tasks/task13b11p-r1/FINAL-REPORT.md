# Task 13B11P-R1 final report

**JARVIS P7 RECORDED-TURN ADMISSION CONTRACT V1 FROZEN**

Contract task only. P-B01 is fully resolved. No production code, no production commit, no
policy change, no schema change, no live activity, no push.

## Verdict basis

P-B01 asked for one thing: the complete recorded-turn admission API, especially the S08–S09
confirmation/result replay seam. It is frozen:

- **Turn input** — one immutable P7-local `RecordedTurn`, 21 fields, every field mapped to a
  stage the frozen guard order already names, built only from existing frozen types. No
  callable, store, clock, executor, dispatcher, session object or authority boolean. The
  required/optional/absent table is exact per mode.
- **Three admission shapes** — `INITIAL_TURN`, `CONFIRMATION_CONTINUATION`, `RESULT_REPLAY`,
  **derived** from three presence booleans and never declared, so neither a caller nor a
  model can author the mode. Five of the eight truth-table cells are inadmissible.
- **Confirmation continuation** — `PENDING` only, seven ordered guards B-01…B-07 including
  full twelve-field binding equality against this turn's actual route. No resting
  `CONFIRMED` is resurrected, raw text and id possession grant nothing, and mode B has **no
  edge to S09**; its only successful disposition is the existing P6 `REQUEST_CONFIRMATION`.
- **Result replay** — exact type identity plus eight ordered guards C-01…C-08, including the
  check that the replayed invocation's settled permission outcome and class still agree with
  what `permissions.decide` returns for this turn, so a forged `ALLOW` is refused. The
  dispatcher is skipped and the pipeline resumes at S10. `confirmation_claimed` is derived
  as `result.executed and invocation.permission_outcome is REQUIRE_CONFIRMATION` — the only
  mapping the two frozen P6 contradiction checks permit, and provably not derivable from
  `invocation.confirmation_id`.
- **Mutual exclusivity** — frozen, with the reason the operator decision anticipated:
  production consumes confirmation authority *inside* the dispatcher's atomic claim, so an
  approval is observable only as unclaimed (`PENDING`, mode B) or as already consumed inside
  an invocation/result pair (mode C). Supplying both asserts one approval to be
  simultaneously claimed and unclaimed, and is refused.
- **S08/S09** — input, guards, output and stop conditions documented per mode, with the
  explicit statement of when the dispatcher may be entered: in P7 v1, never. A turn that is
  authorized but has no result stops rather than acquiring an executor.
- **Failures** — the already-closed `PipelineStopReason` set is reused with no additions; all
  seven named categories map onto it. The resulting coarseness is recorded as a limitation
  with a follow-up, not resolved by editing a frozen enum.
- **Idempotence and execution counts** — zero executor calls, dispatcher entries, new
  invocations, new trusted results and new claims in every mode and on every branch, held
  structurally by the admission type rather than by a check.
- **Matrix** — 32 rows frozen with `app/execution/pipeline.py` provably absent, digest
  `6b454b2c8d881327b88cef73ae03a6465286bb7fb589e942f1bc3789d76fb434`, covering all eighteen
  cases the task named.
- **Security** — 20 invariants S-01…S-20, each naming whether it is structural or checked.

## Three source facts that decided the design

1. `ConfirmationStore.confirm` validates fully and raises without advancing; only
   `claim_for_dispatch` claims execution, and it binds the approval to an invocation in the
   same step. There is no state between unclaimed and claimed — hence exactly three shapes.
2. `invocation.confirmation_id is not None` does **not** prove a claim: dispatcher gate 5
   returns `CONFIRMATION_REQUIRED` with the id present and nothing claimed. Deriving
   `confirmation_claimed` from the id would manufacture an approval.
3. `browser.open` is a genuine `ALLOW` row and `tighten` cannot lower an outcome, so under
   production `BALANCED` the "authorized but no result" case is reachable with the real
   frozen policy — no mocked P4, which the frozen pipeline matrix forbids. That is row
   `A03`, and it is the case P-B01 was really about.

## Production non-change

Entry and exit `db54d615c3ee023d753e86143860c4efdc251230`, clean, zero untracked files.
All 337 tracked file digests identical at exit to entry. `app/execution/pipeline.py` still
absent. `execution.mode: "legacy"`, `hermes_brain: false`, `hermes_enabled: false`. Hermes
`2237be355906fbe6065ce1815711eee52b2d646e`, clean, zero processes. No model, Ollama,
provider, registry or tool call; no dispatcher entry, confirmation mutation, provenance
write or audit emission.

## Regression

Full suite 5468 passed / 11 deselected / 0 failed. Golden 12/20 with the same eight ids
(`calendar-move-event-002`, `habit-status-001`, `habit-complete-002`,
`safety-delete-downloads-001`, `safety-shutdown-002`, `safety-derived-injection-004`,
`clarify-open-target-001`, `clarify-delete-target-002`); metrics identical to the 13B11P
baseline. Legacy probe
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`. All 45 predecessor
sealed bundles verify with zero failures, and the 18 frozen 13B11O-R1 contract entries
verify against manifest `02d208f7d7f26c9f483f7dcb272620cbb8444426e00b1ee1293193d1dbb5779e`.

## Honest limits

No pipeline exists, no fixture was scored, and no matrix row was measured — the matrix is a
pre-implementation specification, and no conformance, guard-order, replay or execution-count
*measurement* is claimed. A `TrustedToolResult`'s dispatcher origin cannot be authenticated
from type identity alone (F-P7R1-01). Admission failure reasons are coarse, so test
assertions carry the guard identity rather than a stop field (F-P7R1-03). Replay of a
genuine non-dispatchable-action refusal result is deliberately excluded from v1
(F-P7R1-02). None of these was hidden to make the contract look complete.

No frozen 13B11O-R1 or 13B11P file was edited; the blocked 13B11P analysis is preserved as
history. Vulnerability tooling remains unavailable and nothing was installed.

One further fact, recorded rather than omitted: an unrelated automated nightly-snapshot
job in this workspace committed four in-progress documents as `5ac314f` and pushed that
commit to `origin/snapshot` mid-task. This task performed no push. The committed blobs are
byte-identical to the working tree so no digest is affected, `origin/main` is unchanged at
`2d7a2ec8` and 39 commits behind local `main`, and the production repository was untouched.
FREEZE_RECORD.md carries the detail and the corrected workspace parent.

## Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11p-r1-turn-admission-contract/`, sealed after the
documentation commit; `SHA256SUMS` excludes itself and verifies with zero failures. Exact
counts, the manifest digest and the final chain verification are recorded externally in
`/home/jarvis/.hermes-poc/work/task13b11p-r1-seal-receipt.json` to avoid self-reference.

## Next

STOP. Resume Task 13B11P: P7 PASSIVE PIPELINE IMPLEMENTATION, against the frozen P7
pipeline contract, this admission contract, recorded Hermes outputs and static/test-double
projections only. Do not implement it in this task. Do not enable Hermes, call a live
model, call real tools, wire P7 live, modify the audit schema or push. The remaining P7
server/API/UI and shadow boundary follows the pipeline; P8 and 13C must not start.

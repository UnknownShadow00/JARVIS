# Obligation Contract — Task 13B11L

**Design, not frozen.** What the P6 decision engine is, and is not.

## 1. Scope

Contract §14.1: every **OPERATIONAL** turn has **exactly one** response obligation, derived
deterministically from frozen inputs only. This component decides *what JARVIS is obligated to
report*. It does not decide *how it is worded* — that is the response builder, a separate unit
(`IMPLEMENTATION_PHASES.md` P6 lists `obligations.py` and `response.py` as two modules, and
`TARGET_COMPONENT_MAP.md` §1 gives them separate rows with separate "must never" clauses).

Path: `app/execution/obligations.py`, from `TARGET_COMPONENT_MAP.md` §1
— *"Obligation engine … exactly one obligation per operational turn, frozen priority (§14) …
must never contain per-scenario branches."*

## 2. Reused, never redefined

`ResponseObligation` (11 members), `ObligationDecision`, `OBLIGATION_PRIORITY`,
`OperationalResponseSource`, `ConversationalResponseSource`, `RequestClass`, `Lane`,
`PermissionOutcome`, `ToolResultStatus`, `ReportingIntent`, `PrimaryAction` — all already in
`app/execution/types.py`. No `ResponseDuty`, `ReplyObligation` or `OutcomeMessageType`, and no
second priority tuple.

## 3. The central rule

The **control plane** decides whether JARVIS reports success, failure, a block, a confirmation
requirement, ambiguity, an unsupported capability, missing context or a held value. A model
cannot select an obligation, cannot supply one, and cannot make an unexecuted action successful.
There is no parameter a model output could occupy.

## 4. Conversational turns produce no operational obligation

Contract §14.1 scopes the requirement to operational turns; §4.2 permits model prose on the
conversational lane. So for `Lane.CONVERSATIONAL` the engine returns **no operational
obligation** and the turn's source is `ConversationalResponseSource.MODEL_RAW`, subject to the
existing safety checks. The validated 13B10C5 implementation did the same — it short-circuits
before `derive_obligation()` and records `CONVERSATIONAL_RAW`.

Crucially, the engine must not *re-decide* the lane (task §28, contract §4.1): an operational
turn is never relabelled conversational because no tool ran, because the action failed, or
because a model answer happens to exist.

## 5. Must never

* generate user-facing prose, templates or prompt strings — no `"Done"`, no `"Please confirm"`;
* contain per-scenario branches, benchmark-specific string matching or example-specific
  overrides (§14.3) — the priority walk is a general rule over state;
* read the user's raw request text (§15.3, task §12);
* read a store, a clock, the filesystem, the network or the registry (task §11, §65);
* emit an audit event, write provenance, dispatch, or mutate permission or confirmation state;
* return the value behind an `ANSWER_LEDGER_VALUE` — only that the obligation applies.

## 6. Obligation → source mapping

Taken from the validated 13B10C5 `response-obligation-design.json` `obligation_to_source`, which
maps one-for-one onto the production `OperationalResponseSource` enum. See `SOURCE_SEMANTICS.md`.

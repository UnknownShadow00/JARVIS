# Decision Input — Task 13B11L

**Design, not frozen.** What the obligation engine would consume, mapped to what production
already produces.

Contract §14.1 names the frozen inputs exactly: *"request classification, routing result,
provenance state, trusted tool result, confirmation state, and lane reasons."* Nothing else is
admissible, and all six already exist as passive values.

| Contract input | Production source | Status |
|---|---|---|
| request classification | `classifier.Classification` (`request_class`, `reason`, `rule_id`) | exists |
| routing result | `router.RouteResult` (`primary_action`, `reporting_intent`, `target`, `target_resolved`, `multi_action`, `capability_available`, `reason`) | exists |
| lane reasons | `lane.LaneDecision` (`lane`, `reasons: tuple[LaneReason, ...]`) — `lane.py`'s own docstring says it carries them *"because contract §14.1 names lane reasons as a frozen input to the obligation engine"* | exists |
| confirmation state | the settled `PermissionOutcome` plus whether a valid approval has been claimed | exists (P4/P5), passed as settled values, never as the store |
| trusted tool result | `types.TrustedToolResult` — the only admissible execution truth (§18.1) | exists (P5) |
| provenance state | **a projection, not the ledger** | the one gap — see §3 |

## 1. No store reads

Task §11 and the precedent set by `lane.LaneSignals` — *"Passing the projection rather than the
ledger is deliberate: it keeps this module pure and stops the lane policy acquiring a hidden
dependency on P2 storage."* The obligation engine follows the same rule: no `ProvenanceLedger`,
no `ConfirmationStore`, no registry, no config, no clock.

## 2. Execution truth is typed, never a flag

The input must accept a `TrustedToolResult | None`, never `tool_succeeded: bool`. A boolean is
forgeable by any caller and by any adapter; a `TrustedToolResult` can only have come from the
dispatcher, which is the whole point of §18.1 and of P5's sole-constructor property. `ToolProposal`,
`ModelDraft`, mappings and look-alikes are refused by type.

## 3. The provenance projection — the one thing still to specify

The validated 13B10C5 derivation called `lock._ledger_value(prompt, ledger)` and
`_param_for_prompt(prompt, ledger)` — both of which re-read the **user's raw text** inside the
response layer. That is exactly the "second recogniser" contract §15.3 forbids, and task §12
forbids it here.

So the caller must supply, per turn, a deterministic projection answering only:

* is there a **current** value that answers this question, and is its trust class `VERIFIED`
  (tool-observed) or `SUPPLIED` (user-reported)? — feeds ranks 7 and 9;
* did the user supply an operational fact on **this** turn? — feeds rank 8;
* is a superseded value involved? — §10.1: never presented as current.

The projection carries **availability and trust class only, never the value**: this phase decides
*which* obligation applies, and the later response builder is the only component that touches the
value itself (task §25).

Who computes it is a real open question for the unblocking task. The honest answer is the
provenance layer itself — a `LedgerSnapshot` method that answers "do I hold a current value for
this fact key" — with the fact key coming from the classifier's existing
`candidate_fact_keys()`, which already exists and is already text-derived *upstream*, in P3,
where text derivation belongs.

## 4. Passive and immutable

The input object is a frozen dataclass; the engine mutates nothing, and holding one changes
nothing. `ObligationDecision` (already in `types.py`: `obligation`, `priority`, `reason`) is the
only output.

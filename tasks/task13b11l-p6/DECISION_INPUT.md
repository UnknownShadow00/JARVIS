# Decision Input — Task 13B11L-P6

**FROZEN AND IMPLEMENTED.** `ObligationState`, a frozen dataclass with twelve fields and no
behaviour.

Contract §14.1 names the admissible inputs exactly: *"request classification, routing
result, provenance state, trusted tool result, confirmation state, and lane reasons."*
Nothing else is admissible.

| Contract input | Field(s) | Source |
|---|---|---|
| request classification | `request_class` | `classifier.Classification.request_class` |
| routing result | `primary_action`, `reporting_intent`, `target_resolved`, `multi_action`, `capability_available` | `router.RouteResult` |
| lane reasons | `lane`, `lane_reasons` | `lane.LaneDecision` |
| confirmation state | `permission_outcome`, `confirmation_claimed` | the settled P4 outcome plus whether an approval was claimed |
| trusted tool result | `result: TrustedToolResult \| None` | the P5 dispatcher, the only constructor |
| provenance state | `value: ValueProjection` | a caller-made projection, never the ledger |

## 1. No store reads

No `ProvenanceLedger`, no `LedgerStore`, no `ConfirmationStore`, no registry, no config, no
clock. The precedent is `lane.LaneSignals`: *"Passing the projection rather than the ledger
is deliberate: it keeps this module pure and stops the lane policy acquiring a hidden
dependency on P2 storage."*

## 2. Execution truth is typed, never a flag

`result` is `TrustedToolResult | None`, never `tool_succeeded: bool`. A boolean is forgeable
by any caller and any adapter; a `TrustedToolResult` can only have come from the dispatcher.
`executed` is a **derived property** of the state, read off the result — so a caller cannot
assert execution without a result to assert it from. That is why the frozen matrix's C-09
row ("an executed flag with no result behind it") is not refused at run time but is
*unrepresentable*.

## 3. Confirmation arrives as a projection, not as P4's enum

The first implementation took `confirmation_state: ConfirmationState` and imported
`app/execution/confirmation.py`. Three existing P4 tests failed, correctly:
`confirmation_non_activation_test::test_no_module_under_app_imports_the_confirmation_machine`
and two symbol scans. Phase P5 had gone out of its way to keep that machine importer-free —
`dispatch.py`: *"Reading an attribute rather than importing the module keeps the P4
confirmation machine free of importers."*

The fix was on this side, and the contract supports it. `confirmation.py`'s own docstring:
*"`PENDING` is the confirmation record's own lifecycle state; the **action** state contract
§12.1 names is `ToolResultStatus.CONFIRMATION_REQUIRED`, a separate vocabulary that already
exists in `types.py`."* So the contract's confirmation-state input is the settled
`PermissionOutcome` plus `ToolResultStatus.CONFIRMATION_REQUIRED` plus whether an approval
was claimed — exactly what `tasks/task13b11l/DECISION_INPUT.md` specified a task earlier.
The record's lifecycle stays P4-internal. No existing test was relaxed.

## 4. The provenance projection

`ValueProjection(available, status, trust_class, source, ambiguous)` — five fields, every
one an existing contract enum, and **no value**. It answers only "is there a current value,
and how far may it be trusted", which is what ranks 7, 8 and 9 need. The value itself
belongs to the response builder.

`answers_now` is `available and status is CURRENT and not ambiguous`. A superseded value is
never current (§10.1, INV-019) and ambiguous provenance answers nothing, so neither grounds
rank 7. A `SUPPLIED` value cannot become `VERIFIED` by passing through: the trust class is
carried, not recomputed (§16.1, INV-008).

The blocked task recorded *who computes it* as an open question. It remains open and is
still the caller's problem — P7 pipeline work, not P6. What this phase freezes is that the
projection carries availability and trust, never text and never the value, so no second
recogniser can grow here (§15.3).

## 5. Reporting intent is carried and provably inert

`reporting_intent` is a field because §5.2 makes it part of the routing result, and **no
rule predicate reads it**. That is stronger than omitting it: the matrix varies all six
intents across twelve base states and proves the decision never moves (§7.1, INV-017).

## 6. Passive and immutable

Frozen dataclass, `slots=True`, no mutable field exposed. Holding one changes nothing.
`ObligationDecision` — `obligation`, `priority`, `reason`, already in `types.py` — is the
only output.

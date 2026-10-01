# ADMISSION MODES

Exactly three admission shapes. The mode is **derived** from the presence of fields 15–17
of TURN_INPUT_SCHEMA.md and is never a constructor field, so no caller, provider or model
can author it.

## Derivation

Let `c = turn.confirmation is not None`, `i = turn.invocation is not None`,
`r = turn.result is not None`.

| `c` | `i` | `r` | Derived mode |
|---|---|---|---|
| F | F | F | `INITIAL_TURN` |
| T | F | F | `CONFIRMATION_CONTINUATION` |
| F | T | T | `RESULT_REPLAY` |
| any other combination | | | **no mode** — invalid admission |

The eight-cell truth table has exactly three admissible rows. The five inadmissible rows
are: `c∧r` and `c∧i` (confirmation/result conflict, task §19), `i∧¬r` and `r∧¬i` (partial
replay), and `c∧i∧r`. All five stop identically: `PipelineStop(stage=S01_INPUT,
reason=invalid_input, executed=False, result=None)`.

`AdmissionMode` may be a P7-local enum with those three members, exposed as a read-only
derived property on `RecordedTurn`. It is derived-only by construction: it has no setter,
no constructor field and no mapping from caller data other than the three presence
booleans. Task §7 permits naming the shapes but not letting them be declared; a derived
property satisfies both, and gives the matrix and the tests a name to assert. It carries
no authority and appears in no authority input.

## A. INITIAL_TURN

The ordinary recorded turn. Carries the request, the deterministic context projections,
the adapter recording and — when a supported resolved action is routed — the expected
binding and permission projections. Carries no confirmation authority and no result.

Admissible dispositions: a conversational outcome; any deterministic early P6 terminal
(`REPORT_CAPABILITY_UNAVAILABLE`, `REQUEST_TARGET`, `REPORT_MULTI_ACTION_LIMIT`); any
non-action P6 outcome (`ANSWER_LEDGER_VALUE`, `ACKNOWLEDGE_FACT`,
`REPORT_UNVERIFIED_STATUS`, `MISSING_CONTEXT`,
`ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION`); the permission `DENY` terminal; the first
confirmation ask (`REQUEST_CONFIRMATION`); or any `PipelineStop`.

One disposition is deliberately *not* available: an initial turn whose action reaches an
actual `PermissionOutcome.ALLOW` cannot proceed to an execution, because the recorded-only
core holds no executor. It stops with `PipelineStop(stage=S09_RESULT,
reason=result_invalid)`. This is the single case P-B01 most sharply exposed, and it is
answered by stopping rather than by admitting an executor dependency.

Initial admission explicitly does not accept: a raw `"yes"` or any natural-language
approval (there is no field for it; the request text reaches only the classifier and the
router, never an authority input); a model confirmation or success claim (parsed into
`ModelDraft`/`ToolProposal`, which no gate reads for authority); an arbitrary
result-to-invocation mapping; a caller `confirmed=true`; a caller `executed=true`. None of
these has a field in `RecordedTurn`.

## B. CONFIRMATION_CONTINUATION

Carries exactly one `ConfirmationRecord`, JARVIS-owned, produced by the P4 confirmation
subsystem for this session, and no result. Its full rules are in
CONFIRMATION_CONTINUATION.md. It is an observation of an outstanding approval request, not
an approval; its only successful disposition is the existing P6 `REQUEST_CONFIRMATION`
obligation, and it has **no edge to S09**.

## C. RESULT_REPLAY

Carries exactly one `ToolInvocation` and the one `TrustedToolResult` the P5 dispatcher
produced for it, and no confirmation record. Its full rules are in RESULT_REPLAY.md. It
resumes the pipeline *after* execution: the dispatcher is never entered, no executor is
called, and no second invocation, claim or trusted result is created.

## Mode and lane are independent

Deriving a mode is not deciding a lane. `lane.explain` is still called twice exactly as
the frozen guard order requires. The final call's signals are derived by P7 from admitted
facts, never admitted directly:

| `LaneSignals` field | P7 v1 derivation for the final S04 call |
|---|---|
| `tool_proposal` | `len(proposals) > 0` from the actual S05 parse |
| `tool_result` | `turn.result is not None` |
| `confirmation_required` | the actual S07 outcome is `REQUIRE_CONFIRMATION`, or mode is `CONFIRMATION_CONTINUATION` |
| every other field | taken unchanged from `turn.lane_signals` |

A mode-C turn therefore always reaches `Lane.OPERATIONAL` through the existing policy, not
through a P7 shortcut, and a conversational request class is never a route out of
operational treatment when operational evidence is present.

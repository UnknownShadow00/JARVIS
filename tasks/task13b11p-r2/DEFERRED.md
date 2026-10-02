# DEFERRED

Everything 13B11O-R1 `DEFERRED.md` and 13B11P-R1 `DEFERRED.md` defer stays deferred and is
not re-opened: browser D-01; confirmation numeric TTL and UX; `TIMEOUT` leaving a
confirmation record in the executing state; a `TIMEOUT` provenance source; the redaction
secret-key list; the real registry adapter; live capability projection; live audit and
request wiring; Hermes enablement; model, network and resource configuration; destructive,
financial and messaging policy.

D-P6-01 stays `DENY` -> `REPORT_CAPABILITY_UNAVAILABLE` with `permission_denied` where its
existing rule wins. D-P6-02 stays `TIMEOUT` -> `REPORT_TOOL_ERROR` with
`trusted_tool_timeout`. No new obligation, rank, template, resting approved state, success
inference, timeout settlement or automatic retry.

13B11P-R1's own deferrals are all preserved: F-P7R1-01 (result origin unprovable from type
identity), F-P7R1-02 (replay of a non-dispatchable-action refusal excluded from v1),
F-P7R1-03 (coarse failure reasons), cross-`RecordedTurn` idempotency, already-reported
result detection, and the absence of any ordering constraint between `recorded_at` and
`evaluated_at`.

Classifier version stays `"2"`; the classifier, router, lane, canonicalizer, permission
engine, confirmation machine, dispatcher, obligation engine, response builder, provenance
ledger, audit events, correlation module and Hermes adapter are all unmodified.

## FUTURE-AGENT-BRIDGE (preserved, non-blocking, not implemented)

JARVIS may later communicate bidirectionally with external agent systems. Recorded
requirements, carried forward verbatim in substance and implemented nowhere:

- the external agent remains untrusted at the JARVIS authority boundary;
- JARVIS keeps permission, confirmation and execution ownership;
- the protocol goes through an adapter boundary, like the existing recorded Hermes adapter;
- no direct registry authority;
- external results require deterministic provenance and trust handling;
- local JARVIS must keep functioning when the external service is unavailable.

Nothing in this task advances, designs or authorizes it. Note in passing that the recorded
adapter boundary and the derived-mode admission type are the right shape for it: an external
agent would be another untrusted producer of a `ModelDraft` and `ToolProposal[]`, with no
field through which it could author a mode, a binding, a claim or a result.

## Deferred by this task

| Item | Why |
|---|---|
| The whole P7 passive pipeline implementation | blocked on P-B02; see BLOCKER_ANALYSIS.md |
| The implementation fixture corpus freeze | §44 requires it before code; one input field is unresolved, so freezing now would require re-freezing |
| Matrix measurement, generalization corpus, runtime zero-execution measurement | nothing exists to measure |
| The ~41 sanctioned non-activation allowlist extensions | authorized in kind by frozen 13B11O-R1, but the scope needs explicit operator authorization (decision 2) |
| Changing or disabling the nightly snapshot job | needs operator approval (§47); inspected read-only only |

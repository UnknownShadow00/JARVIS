# Known Limitations — JARVIS Agent Execution Contract v1

**Status:** part of the frozen record (Task 13B10D). These are stated so that no future reader
mistakes the validated architecture for a finished production system.

## 1. The model remains imperfect

Granite 4.1 30B Q3_K_M still fabricates. In Task 13B10C5, 92 of 350 operational drafts were
manually classified unsafe (false state 48, fabricated result with internal leak 14, false
execution 10, internal leak 10, fabricated result 7, false execution with internal leak 3).
Nothing in this contract makes the model trustworthy; it makes the model's untrustworthiness
harmless on operational turns.

## 2. Safety depends on the implementation preserving this contract

The measured guarantees belong to the validated control-plane implementation. A production
implementation that reorders the obligation priority, lets the response layer re-extract values,
allows an operational turn to fall through to model prose, or dispatches outside the permission
layer will not inherit those guarantees, however similar it looks.

## 3. Eleven residual utility failures in C5

* **Five** (`l:L08_L09-t2`): the frozen provenance extractor records no `port` parameter from the
  imperative "Set the service port to 9100", so the later question "What port did I just
  specify?" had no ledger value to answer from and correctly fell to `MISSING_CONTEXT`. Widening
  the extractor is future work and requires its own validation.
* **Six**: conversational-lane explanation turns where the immutable provenance lock blocked the
  model's own prose and substituted the missing-context line.

Neither group invalidates the C5 thresholds — overall utility was 97.2% against a 92% target —
but both are real limitations of the frozen behaviour.

## 4. Confirmation persistence and expiry do not exist

The validated runs created `CONFIRMATION_REQUIRED` state within a turn and proved that nothing
executes without confirmation. They did **not** exercise cross-session persistence of a pending
confirmation, expiry, freshness, or replay of an old approval. §12.3–12.4 of the contract records
these as production requirements, not as validated behaviour.

## 5. The production permission matrix is not implemented

§11 freezes the permission *classes* and the rule that no model may self-authorize. The actual
matrix — which action maps to which class, which classes require confirmation, which are blocked
outright — is not implemented under this contract and must be built and tested before
integration.

## 6. Real production tools were never exercised

Every scored run used five fictional tools (`jarvis_test_open_app`, `jarvis_test_open_url`,
`jarvis_test_deploy`, `jarvis_test_delete_path`, `jarvis_test_get_database_status`) behind an
inert dispatcher. No real application was opened, no deployment ran, nothing was deleted. A
CPython audit hook recorded an empty event array for every dispatch.

## 7. Tool results were synthetic

Trusted tool results were fixtures, not observations of a real system. The *shape* of
trust — bound invocation, tool name, canonical arguments, status, data — was validated; the
reliability of real tool results was not.

## 8. Hermes is still disabled

`hermes_enabled: false` in production JARVIS, unchanged since before this series began. Nothing
in this contract turns it on, and enabling it is explicitly out of scope until the production
entry criteria are met.

## 9. Single model, single scenario family

All C3/C4/C5 numbers come from one model at one quantization, on a scenario set that, while
pre-registered and extended each task (A–F, G, H, I, J, K, L), is finite and authored by the same
process that authored the implementation. The counterfactual review in C5 checks for selection
bugs, but no scenario set proves the absence of unknown failure modes.

## 10. Audit is specified, not built

§19 specifies the required audit events. The validated runs produced an equivalent per-turn
record in the harness, not a production audit subsystem with retention, integrity or access
control.

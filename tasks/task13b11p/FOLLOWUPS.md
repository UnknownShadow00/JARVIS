# Follow-ups
## BLOCKING NOW — P-B01: complete passive pipeline admission API
Question: what is the exact callable signature and required/optional input/variant schema for a complete recorded P7 turn, especially the S08 eligible confirmation handoff and S09 invocation/result/claim evidence?

Current behavior: no pipeline module. The contract freezes constituent boundaries, guard schema, seven-field stop and output alternatives, but the original aggregate input remains explicitly NOT FROZEN. Existing ConfirmationRecord is observation, not approval; P5 owns claims/results. The recorded core does not dispatch, while a later isolated P5 boundary is mentioned without a complete P7 input seam.

Options:
1. Freeze an explicit recorded-only callable over existing typed projections, with an exact required-together/absence/admission table for current and historical results, confirmation evidence, provenance selection and internal audit projection. Generate P4/P5 replay fixtures outside that callable. Recommended: smallest scope consistent with V1's zero-dispatch core.
2. Separately freeze an isolated P5 continuation dependency contract, including executor isolation, claim ownership and replay/state semantics, if whole-turn inert execution is required inside P7.

Security consequence: choosing these implicitly can turn snapshot possession into confirmation authority, lose executed-result evidence at an early stop, or introduce an executable callback into a recorded boundary. No new policy grant is needed, but the interface/trust boundary needs explicit resolution. Function naming and an allowed TurnOutcome alias are ordinary implementation details, not this blocker.

Blocks requested complete Task 13B11P acceptance, not the independently specified proposal equality guard. Do not label a guard-only implementation as the full pipeline. Do not rewrite frozen V1 silently; resolve through explicit versioned contract history.

## BEFORE LIVE WIRING
Existing F-MAP-01 production binding derivation, F-FALLBACK-01 live failure response/audit, F-AUDIT-01 conversational summary correction, F-REPLAY-01 transport-loss semantics, capability/registry/live request/Hermes boundaries remain unchanged. They are not new reasons to reject static comparison.

## LATER HARDENING
Approved vulnerability/type/lint/coverage tooling and the existing resource/digest/redaction follow-ups remain deferred. No installation.

## Next dependency
Resolve P-B01, then resume the same passive pipeline unit. The actual graph next places the remaining P7 server/API/UI and shadow boundary after the pipeline; P8 is not unlocked by a blocked or partial pipeline. Live consumers/shadow, permissions, confirmation policy and Hermes activation still require separate authorization. Stop here.

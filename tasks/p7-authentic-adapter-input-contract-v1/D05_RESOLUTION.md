# D05 semantic closure and later dependencies

| Component | Status | Decision / limit |
|---|---|---|
| CANONICAL ADAPTER | DERIVED FROM EXISTING CONTRACT | app/brain/hermes_adapter.py; AdapterRequest/build_request/parse_recorded_response, no second parser |
| LIVE AUTHENTICITY | FROZEN | Real same-turn generation through authorized transport, faithful canonical normalization and actual parser use; still untrusted |
| TURN ASSOCIATION | FROZEN | Exact existing Context/envelope/RecordedTurn correlation; trusted outer session association, no trace or stamped-ID shortcut |
| REQUEST ASSOCIATION | FROZEN | Exact four-field request/build output bound to corresponding provider operation and parser input; prompt projection must be demonstrable |
| REPLAY STATUS | FROZEN | Original captured/sealed provenance/turn/version, explicit replay; never fresh live |
| SYNTHETIC STATUS | FROZEN | Handbuilt JSON/objects and mocks stay test evidence even after parse/seal/replay |
| ZERO-PROPOSAL RULE | FROZEN | Actual successful authentic canonical parse empty tuple; unavailable/unobserved is not zero |
| PROVIDER-UNAVAILABLE RULE | FROZEN | No valid adapter output; external truthful failure accounting, no substitute/fallback/provider switch |
| MALFORMED RESPONSE RULE | DERIVED FROM EXISTING CONTRACT | Canonical all-or-nothing AdapterError; actual S05 only when reached |
| AUTHENTICITY EVIDENCE | FROZEN | Minimal origin/request/recording/parser/provider/observation associations outside D03/D04; collector/durability still required |
| PROVIDER/MODEL ID REQUIREMENT | FROZEN | JARVIS-controlled actual operation/model identity agrees with caller request; never unverified echo |
| PROVIDER/MODEL SELECTION / NATIVE WIRE MAP | BLOCKED BY D06 | Identity, endpoint/credentials/runtime, complete native response and faithful mapping chosen/reviewed later |
| RETRY DEPENDENCY | BLOCKED BY SCHEDULER | D02/D07 attempt selection, duplicate/cancellation/submission/recoverable accounting; no guessed ordinal |
| OBSERVATION COMPATIBILITY | FROZEN | Preserve all 18 fields and six sink fields; upstream/controller join required for eligibility; sink never authenticates |

No unresolved D05 core semantic/authority decision is required. This is not closure of the live transport implementation, request assembly, classifier/collector schema, scheduler, provider or measured window. No OPERATOR DECISION REQUIRED within D05; D06/D07/D09/D10 remain separately blocked as appropriate. Frozen authority is reused without amending it.

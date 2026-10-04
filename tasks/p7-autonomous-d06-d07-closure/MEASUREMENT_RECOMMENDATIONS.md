# Measurement recommendations — none frozen

Canonical evidence: 116/116 frozen passive cases +53/53 unseen; twenty golden cases with eight known baseline failures; real REST and WS paths have different completion/fallback lifetimes. Historical C5 saw 92/350 unsafe model drafts and host/model lifecycle interference in C4. Those are not a current live traffic-rate or latency baseline. A model-quality mismatch is not itself operational execution or an incorrectly enforced control-plane rule.

| Dimension | Recommendation | Evidence/limitation |
|---|---|---|
| Offline floor | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: rerun all 169 frozen+unseen cases plus the unchanged 20 golden scenarios | These corpus sizes already exist; they are not live sample counts |
| Initial live pilot sample | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: at least 169 eligible logical turns, covering both REST and WS, with explicit action/proposal/permission/failure strata | Mirrors known case breadth only; not a statistical sufficiency claim; strata quotas need controller contract |
| Initial pilot duration | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: at least 24 hours and until coverage is met, whichever is later | Proposed daily lifecycle exposure; no measured request rate exists; does not by itself define a passing window |
| Provider failures | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: report every unavailable/timeout/invalid result; require zero hidden or excluded failures, and defer tolerated failure rate until a supervised pilot | Zero hidden loss is mandatory; no arbitrary availability percentage selected |
| Proposal mismatch | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: descriptive stratified rate in pilot, no numeric pass threshold until authentic baseline exists | Binding safety must hold despite mismatch; historical unsafe-draft rate is not proposal mismatch rate |
| Pipeline stops | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: separate expected deny/confirmation/inert-result stops from unexpected invariant failures; require zero unexpected authority/execution escapes | A global zero-stop limit would reject correct fail-closed cases; no aggregate stop tolerance selected |
| Evidence loss | Existing D04 authority: known loss/uncertainty makes window INCOMPLETE; no passing acceptance from that interval | Submitted=durable is necessary, not proof of missing upstream attempts |
| Latency observation | RECOMMENDATION — OPERATOR APPROVAL REQUIRED: separately collect legacy response and shadow durations/percentiles after clock/controller contract; no numerical latency gate now | D04 UTC persistence chronology is not latency; server awaits/WS fallback need actual measurements |

All proposed pilot numbers remain unapproved. No pilot can be relabeled a formal accepted window before D08/D09 thresholds and controller scope are frozen. Single concurrent shadow generation is already operator-approved, not a recommendation here.

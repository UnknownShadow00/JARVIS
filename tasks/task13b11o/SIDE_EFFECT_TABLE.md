# Side-effect table

No live side effect is authorized by this task. Table describes the candidate passive stage, not work performed here. PP = PASSIVE PROJECTION; FO = FUTURE ONLY. NONE means no access. “Permission” means policy state access, not permission modification.

| Stage | Filesystem | Network | Process | Model | Registry | Permission | Confirmation | Dispatch | Provenance write | Audit write | Response construction |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 caller snapshot | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE |
| S02 classifier | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE |
| S03 router | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE |
| S04 lane | NONE | NONE | NONE | NONE | NONE | NONE | PP | NONE | NONE | NONE | NONE |
| S05 recorded adapter | NONE | NONE | NONE | PP | NONE | NONE | NONE | NONE | NONE | NONE | NONE |
| S06 guard/canonicalizer | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE |
| S07 permission decision | NONE | NONE | NONE | NONE | NONE | READ | NONE | NONE | NONE | NONE | NONE |
| S08 confirmation projection | NONE | NONE | NONE | NONE | NONE | PP | PP | NONE | NONE | NONE | NONE |
| S09 recorded result linkage | NONE | NONE | NONE | NONE | NONE | PP | PP | PP | NONE | NONE | NONE |
| S10 provenance projection | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE | NONE |
| S11 obligation | NONE | NONE | NONE | NONE | NONE | PP | PP | PP | NONE | NONE | NONE |
| S12 builder | NONE | NONE | NONE | NONE | NONE | PP | PP | PP | NONE | NONE | PP |
| Conversational wrapper | NONE | NONE | NONE | PP | NONE | NONE | NONE | NONE | NONE | NONE | PP |
| S13 audit compatibility | NONE | NONE | NONE | NONE | NONE | PP | PP | PP | NONE | NONE | PP |
| Live server/provider/registry/stores | FO | FO | FO | FO | FO | FO | FO | FO | FO | FO | FO |

If the future passive implementation runs the plan-supported inert dispatcher instead of only recorded-result linkage, S09 necessarily performs WRITE to its isolated in-memory idempotency state and P4's isolated confirmation state. S08 creation/registration likewise writes only a dedicated test-owned store. These are NOT pure projections, NOT live mutations and NOT authorized real dispatch. They must be represented explicitly in the eventual frozen scope; no callback is presumed inert merely from its type. P7 itself never owns those state-transition rules.

Review/evidence activity legitimately reads repositories, runs regression processes and writes new documentation/evidence. Those activities are not intrinsic pipeline side effects and do not execute real tools. This table must not be cited as proof that an unimplemented pipeline is pure.

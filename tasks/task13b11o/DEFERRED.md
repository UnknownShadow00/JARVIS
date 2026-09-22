# Deferred items preserved

This task does not resolve or weaken any previous deferred item.

| Item | Preserved behavior / boundary |
|---|---|
| D-P6-01 | DENY → REPORT_CAPABILITY_UNAVAILABLE, permission_denied, subject to existing priority |
| D-P6-02 | TIMEOUT → REPORT_TOOL_ERROR, trusted_tool_timeout |
| Browser D-01 | Current browser.open/browser.search policy stays unchanged; operator decision before altering authority |
| Numeric confirmation TTL / UX | No values or consent experience selected; fixture expiry is caller-supplied |
| P5 timeout lifecycle | Confirmation remains EXECUTING; no recovery/automatic retry |
| Lane audit field | Current schema-v3 field unchanged; no ad-hoc schema extension |
| Redaction secret-key list | No new retention or secret policy; no raw provider reasoning |
| TIMEOUT ProvenanceSource | No new source; no invented success/error fact |
| Historical classifier R1/R2 digest anomaly | File manifests verify; undocumented aggregate formula not guessed |
| Real registry adapter | Later graph dependency and explicit authority; no registry dispatch |
| Live capability projection | D-08 caller/static boundary only; no live discovery |
| Live request wiring / Hermes normalization / shadow | Separate later task; no model inference or server branch |
| Destructive/financial/messaging policy | No policy change or new capability grant |
| Resource bounds / tooling / stale comments | Later hardening; no arbitrary limits, installs or production churn |

Current blockers are not quietly moved to this deferred list: O-B01–O-B04 remain BLOCKING NOW in FOLLOWUPS.md.

# Provider ownership and D06 coexistence

**Not ready for live D06/legacy coexistence.** Candidate schema5's `steps` and `leases` are an isolated extension prototype, not production ModelOwnershipCoordinatorV1. Each step stores attempt, named kind, endpoint, model, profile, request digest and possible-send/terminal/unknown. Lease associates that exact step and endpoint. Global clean() conservatively serializes even distinct endpoints; unique endpoint_exclusion also blocks ACTIVE/REMOTE_UNKNOWN conflicts.

One accepted conversation can own multiple provider transmissions. Existing L1 fixture:12 operations across4 attempts; L2:8 across4. D09 observation submissions/receipts are not all provider calls. Reproduced tests show peak concurrent provider count1; router failure prevents responder/Granite, responder failure prevents Granite, and uncertainty prevents any later model on the endpoint. No automatic retry, fallback, load/unload helper or executor capability exists in this package.

Gate6D restricts begin() to LEGACY_ROUTER, LEGACY_RESPONDER and GRANITE on an unsettled accepted attempt and enforces their order. Exact canonical Granite endpoint/model/profile and limits are now checked before possible-send in the real passive observer bridge. Fixture resources are deliberately documentation-only IP192.0.2.1 and fake profiles; no Granite lease is silently reused for a real gemma/qwen model.

The possible-send row commits before invoking the provider coroutine. It is conservative intent evidence, not packet proof. known_terminal currently trusts an injected ProviderResult; only an associated trusted transport may supply that fact in a release. Cancellation/timeout/late success does not resolve uncertain remote ownership. The stored ACTIVE state after a process exit continues to block clean(), even when the process is gone. Known terminal followed by parse/proposal failure stays known terminal while closing admissions.

Proposed resource extension `G6D-D06-2`:

| Contract element | Required versioned behavior |
|---|---|
| Scope | Fixed approved resource allowlist: legacy router gemma, legacy trivial responder gemma, legacy normal responder qwen, frozen Granite; profiles remain distinct even when model is the same |
| Exclusion identity | Canonical endpoint-wide lifecycle domain, plus model/profile generation identity; canonicalize hostname/IP aliases only from approved topology evidence |
| Durable operations | accepted attempt → named substep → exact resource lease → possible-send → authoritative terminal or unresolved unknown; no helper bypass |
| Legacy D06 compatibility | Validate V2 scope/marker/state unchanged through separate archive reader. No second coordinator root that ignores the first, no broad ownership-check weakening |
| Migration | Separately approved zero-use V2 retirement, quiescent transfer, protected active-root publication and independent old/new exclusion verification |
| External actors | Ollama supervisor/restart, other clients, schedules and privileged lifecycle callers require explicit endpoint reservation; local ledger cannot exclude them |

The fixture schema5 is a versioned prototype for these step/lease associations; Gate6D tests extend its operation whitelist, ordering, unknown exclusion and validation. It lacks a root-protected global D06 resource manifest, actual coordinator adapter, native transport proof and independent actor fence. These remain new implementation and approval requirements. No production D06 storage or ownership state was modified.

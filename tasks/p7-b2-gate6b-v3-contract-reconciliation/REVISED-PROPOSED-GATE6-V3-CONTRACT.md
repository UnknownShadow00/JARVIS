# Proposed Gate6 V3 revision 2 — NOT APPROVED / NOT IMPLEMENTED

This additive revision corrects Gate6A without overwriting it. It preserves Gate1–5 and Gate4 V2 contract c40de55208296b3607c000164238bdf50c8097edb087c2c929cc03fa195e4458 as historical authorities for their exact deployment. Gate5 remains complete for V2 only. V3 revision2 is not an implementation authorization.

**Unresolved semantic field:** bounded legacy response contract. Client output remains legacy-owned; Granite is observational and discarded from client/history. Calling unrestricted legacy handlers and replacing the legacy reply with Granite are both prohibited. Before implementation approval, the operator must approve the separate legacy endpoint/model/router/prompt/memory/budget/ownership/serialization/error contract or explicitly approve a changed deterministic-input experiment. No invented defaults fill this field.

## Frozen Granite / B2 values retained

| Constraint | Existing frozen value | Revision2 treatment |
| --- | --- | --- |
| Accepted capacity / transports | 4 maximum;2 REST +2 WS | Global lineage count, durable ordinals and exact transport association; failures consume capacity |
| Concurrency / queue / intake | 1 generation /0 queue /1 intake | Qualified Granite unchanged; proposed serialization also covers approved legacy substeps, a newly explicit orchestration rule |
| Granite endpoint / alias | http://192.168.0.200:11434 / hermes-candidate-granite41-30b-q3km-64k | Exact, no fallback/model discovery/client override |
| Profile | jarvis.p7.ollama.granite41.b1r2.v1 | Unchanged; never reused to qualify legacy models |
| Context / output / native bytes | 64000 /128tokens /16384bytes | Unchanged for Granite; not falsely applied to old legacy calls |
| Deadline / drain / keep-alive |180s provider /30s local drain /60s keep-alive | Unchanged; local drain is not remote completion |
| Think / stream |false /false | Unchanged Granite; legacy nonstreaming restriction is an explicit proposed delta |
| Sessions |2 /300s idle /1800s max age | Retain Core-owned sessions; one REST and one WS; no restart replay |
| History |8messages /8192UTF-8bytes | User + delivered legacy text only; pre-turn capture preserved |
| Continuation |jarvis-core-b2-pilot-v1 authenticated scope | Preserve reviewed reusable header/control behavior; add runtime/epoch binding through reviewed versioning, not an opening grant |
| Provenance |LIVE, measurement-ineligible | Immutable throughout restart/archive/lineage; no promotion |
| Tools / voice / retries / fallback |None authorized | No operational dispatcher/confirmation/TTS/wake; any proposal stops; no retry/fallback in either approved lane |
| Backup |Startup, each settled attempt, final;COORDINATED_REQUIRED | Versioned manifest binds lineage/control/identities, no next permit before validation |
| D06 |Exact resource, no unknown bypass | Preserve lease truth; separately qualify any legacy resource, no inferred remote completion |

The original frozen storage paths, single-ever-epoch startup, same service identity, in-memory counters and backup ownership rules **cannot all remain unchanged** under the new architecture. Explicit approval deltas: protected release/system unit/new UID and credential loader; fenced D06 path/ownership transfer; retained immutable zero-use predecessor plus exactly one linked successor/new namespace/schema4; versioned archive/backup validators; durable control/permit/ordinal/provider-substep audit; no startup auto-open or terminal recovery; explicit operator user-presence authority; bounded legacy adapter and serial scheduling. Original approved prompts are not silently replaced. Core-local host-loss acceptance must be renewed for the changed layout.

Initial V3 runtime starts CLOSED only. Root-pinned reservation and complete startup checkpoint must match source/config/unit/PID/invocation/epoch and zero accepted state. Explicit signed human OPEN_HOLD grants no work. Each separately approved one-use permit commits consumption and acceptance before any provider work. Every subsequent permit requires exact associated terminal, zero proposal/execution effects, D04/D09/D06 consistency and a coordinated verified checkpoint. Queue/backlog/replay/automatic next-permit callbacks are absent. Manual stop/abort/uncertainty is terminal;30s bounded drain preserves remote uncertainty. Interrupted V3 pilot recovery is not approved by this contract.

V2 retirement requires planned zero-use CLOSED_COMPLETE with truthful OPERATOR_STOP and final archive; any nonzero/unplanned/incomplete/unknown/abort state blocks this narrow successor. Preserve original epoch, original checkpoints and accepted-set truth forever; no reset/relabel/reuse, no duplicate successor/root to evade cap. Initialize new state only through separately approved versioned interfaces after terminal predecessor validation. No live migration or code injection.

Approval sequencing is A–J in V3-DEPLOYMENT-DEPENDENCIES.md. Isolated implementation can be completed and reviewed before stopping V2. Actual UID/privilege/source/credential/migration/startup actions each require explicit approval. New startup and positive-auth/zero-generation evidence precede any pilot opening. Final Gate7 review is mandatory; measurement and formal P7 exit remain unauthorized.

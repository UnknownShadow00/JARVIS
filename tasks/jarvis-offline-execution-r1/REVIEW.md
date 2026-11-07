# Source review of the offline execution sprint

Primary engineer static review plus source-bound runtime tests. No independent
reviewer or live security qualification is claimed for this revision.

| Finding | Implemented closure | Evidence |
|---|---|---|
| Queue had no integrated dispatcher | Explicit built-in-only registry, simulated policy, fenced claim/dispatch, evidence and publication | 60 new pipeline cases; actual app workflow |
| Lost result publication could strand work | Startup publishes existing evidence; no evidence leaves UNKNOWN | Six new SIGKILL boundaries and actual app startup after independent SIGKILL |
| Untrusted result could forge completion | Exact operation/capability/schema/output verification; no public completion route | Five hostile response cases; actual PATCH 405 |
| Public UUID could reserve predictable phase receipt | Public mutation UUID4 namespace; internal occurrence/phase UUID5 namespace | Public create/cancel/schedule reservation attempts return 422 |
| Stale authorization or ownership | Current policy, scope/capability consistency, generation, PID/file/database fencing | Revocation, inconsistent decisions, stale owner, independent owner exclusion |
| Audit or database failure before dispatch | Claim/dispatch and audit receipt commit before computation; storage ambiguity stops worker | Trigger-induced audit failure, lock contention and poisoned-owner checks |
| Sleep and stop did not know about worker | Worker stops before scheduler/storage cleanup; start after scheduler; no stopped admission | Actual app stop/sleep/wake/readiness scenarios |
| Admission could allocate unbounded JSON | Byte/chunk/deadline limits before decoding, strict bounded fields and Unicode checks | Length/chunk/slow-body cases and actual middleware auth-before-limit assertions |
| Polling and task lookup materialized full history | Active outbox polling, direct task lookup, bounded API pages and CLI pagination | Tests forbid fallback to full list materialization |

Local Python and database owners remain trusted. Registry restrictions do not
sandbox malicious same-UID code. SQL/audit/outbox transactions protect the local
contract, not future network effects. No exactly-once external effect is claimed.

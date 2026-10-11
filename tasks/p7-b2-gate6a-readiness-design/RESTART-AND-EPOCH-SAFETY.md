# Epoch preservation, restart and recovery

## V2 facts and compatibility blocker

Current epoch606a991a06b74fd79ed72b308417cc3f is OPEN bookkeeping, input_complete1, accepted0. V2 has no attach/resume interface; startup always tries to create an epoch and rejects any existing row. Driver counters (`_accepted`, transport_counts), intake and continuation sessions are in memory. D09 schema3 does not persist the transport quota needed to reconstruct two REST/two WS. These reset risks are currently prevented by refusal, not solved by an existing recovery feature.

Normal close invokes irreversible stop_admissions, writes the stop reason and closes the epoch. Its truthful status can be CLOSED_COMPLETE even with zero attempts; that says accounting is reconciled, not that the pilot ran. Restart cannot reopen that row. SIGUSR1 is also terminal, never a reusable pause. A force-kill to preserve OPEN, editing row status or dropping controller state would violate the transition contract.

## Proposed V3 lineage, requiring new approval

Preserve the full original namespace, original startup checkpoint and final V2 stop/drain evidence. A **new explicitly authorized deployment/pilot** may have exactly one new schema4 successor in a new versioned namespace, rooted in an immutable closure archive of the original epoch. This is neither recovery nor reopening of the old epoch. It requires explicit approval of a change from V2's global single-epoch startup rule.

The narrow zero-use transition must reject any predecessor acceptance, provider-start/submission/receipt, unresolved ownership, abort/failure/incomplete state, unplanned closure or unverified lineage. The only eligible predecessor closure is the separately authorized planned retirement of the fully reconciled, unexercised deployment, with expected OPERATOR_STOP preserved as terminal. A terminal abort is never eligible. If the operator requires the same runnable epoch ID, this transition is **BLOCKED under V2**; no workaround is recommended.

The lineage ledger must preserve every ancestor accepted ID/high-water mark, source/config and terminal status, enforce global accepted≤4, and permit only one successor. Never hide an earlier attempt in an archive count, reset quotas, create a second successor after a failure/cap/stop, or replace/restore the original namespace. Revalidate predecessor digests against the immutable root-protected archive; unauthorized mutation blocks operation. No new epoch is created in Gate6A.

## V3 recovery proposal

Restart reconstructs accepted IDs, per-transport counts/ordinals, spent grants and terminal facts from durable schema4 and returns CLOSED_RECOVERY_HOLD. It must not grant admission from an old OPEN_COMMITTED record. Load only a separately approved release/config and exact lineage; invalidate old runtime challenges/continuations. Reconstruct no prompt automatically and replay no request.

| Interruption | Required treatment |
| --- | --- |
| Before authorization commit | CLOSED; transaction rollback or explicit ambiguity preserved; no automatic retry |
| After commit, before readiness | Grant spent; CLOSED_RECOVERY_HOLD; audit must not imply a turn was accepted |
| After acceptance, before/after possible dispatch | Keep accepted ID/high-water; unresolved attempt independently blocks opening; inspect authoritative D06 rather than fabricate its state |
| D06 active/unknown or missing/corrupt evidence | Hold; no lease clearing, no inferred completion, no replay |
| Known terminal + joined receipt + verified latest backup, no stop/abort | A **new explicitly authorized recovery action** may be considered against the same V3 epoch and remaining quotas; never the initial zero-only opener |
| Terminal stop/abort, failed backup or closed epoch | Permanently closed; no recovery grant can convert it into a pause |
| Four accepted attempts | Permanently closed to more admissions regardless of restart |

For the first pilot, default to stopping on interruption and independent review. Recovery execution requires a separate approval, fully qualified implementation and revalidated session scope. Lost in-memory history is not reconstructed from guesses or replay; if required continuation semantics cannot be safely re-established, recovery stays blocked. New explicitly authorized sessions, if permitted later, cannot reset accepted/transport quotas or promote eligibility. Late associated evidence may clarify remote uncertainty without reopening terminal authority or rewriting earlier accounting facts.

The disposable model tests a possible V3 recovery state machine, not a deployed recovery path, session persistence implementation or migration. V2 state is never fed to it as a mutable production fixture.

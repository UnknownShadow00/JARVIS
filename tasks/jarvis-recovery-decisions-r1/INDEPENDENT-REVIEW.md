# Independent security and correctness review

Reviewer: `/root/recovery_security_review`, separate reviewer-role agent. This file
was assembled by the primary from the reviewer's returned findings and verdict.
Scope: read-only static review of nine pinned application modules and retained
focused-run metadata. The reviewer did not edit files, run tests, start the app,
access real configuration/credentials, or perform live/privileged qualification.

**Final verdict: PASS. No unresolved HIGH or MEDIUM scoped finding.**

## Resolved findings

1. **HIGH, CLOSED — Restart operator authentication.** Every event requires the
   separate operator HMAC verifier and exact request/scope/command/payload/checkpoint,
   principal, lifetime and admission-time binding. Proposal publication binds the
   entire verified proposal and summary; decisions bind the proposal hash; renewal
   results are checked against the authorized reference.
2. **HIGH, CLOSED — Interrupted initial registry creation.** Dedicated exclusive
   staging, FULL-synchronous schema transaction, exact empty/schema-only recovery,
   fsync and atomic no-replace publication prevent stranded zero final databases.
   Unknown partial content remains quarantined.
3. **MEDIUM, CLOSED — Readiness disclosure.** Readiness returns aggregate state,
   counts and witness/nonactivation flags. Full history, UUIDs, archive paths and
   operator identities require authenticated diagnostics or offline CLI.
4. **MEDIUM, CLOSED — Historical predecessor expiry.** Every decision transition
   computes predecessor state at that event's admission time. A genuine later
   permit cannot approve an expired predecessor that fresh admission would reject.
5. **MEDIUM, CLOSED — Empty-generation witness continuity.** Exactly authenticated
   generation `start - 1` head remains a valid minimum after later generation
   growth, constrained by epoch, rollover hash and complete authenticated history.
6. **MEDIUM, CLOSED — Restart proposal/source binding.** Original request,
   occurrence and task UUIDs plus restore/database/archive/manifest/generation/trust
   bindings survive; branch/restore conflicts and UUID collisions fail closed.
7. **MEDIUM, CLOSED — Offline diagnostic compatibility.** The readonly shim
   explicitly reports registry unconfigured when no registry inputs exist.
8. **LOW, CLOSED — Malformed evidence, caller mutation and lock replacement.**
   Canonical copies, boundary error normalization and active lock fencing close
   the reviewed paths.

The reviewer confirmed that imports, verification, proposals and approvals remain
inert; no recovery path invokes an executor, enables schedules or changes restored
task state. No public recovery mutation or activation endpoint exists. Exact retries
require the original UUID/payload/permit. Distinct intent/SQL/final phases reconcile
without redispatch. The history-snapshot optimization uses one completely verified
immutable result under the shared mutex/flock; fresh renewal retains current-head
verification and there is no persistent unchecked cache.

9. **MEDIUM, CLOSED — Hot-journal recovery prerequisites.** Complete protected
   inventory/chain/permits/checkpoint/state-machine/external-reference validation
   now precedes every recovery writable open. Only the exact sole incomplete
   original admission can recover a real SQLite hot journal. Rollback must remove
   the journal and full SQL/protected replay must pass. Invalid prerequisites leave
   both database and journal unchanged. A proven non-hot zero-header journal is
   retired only by SQLite's original transaction, without manual unlink.
10. **MEDIUM, CLOSED — Admission expiry during expensive verification.** Final
    admission time is selected after full verification; lightweight checks cover
    permits, current witness, proposal context, decision validity and predecessor
    expiry immediately before publishing. Every historical event checks the
    effective witness at its original admission time. Delay-to-expiry tests publish
    no intent.

## Evidence and accepted limits

The primary reported retained focused run `20261106T060908471294Z`, with
72 passed, 0 failed, 0 skipped and 22 independent SIGKILL cases. Those tests were
executed by the primary, not independently by the reviewer. Broader final modes
were still running when the final static verdict was returned; RESULTS.json
records their primary-produced runtime evidence. INITIAL-INDEPENDENT-REVIEW files
preserve the earlier verdict before the hot-journal follow-through work. Final nine source
hashes are in INDEPENDENT-REVIEW.json and must match the retained runtime inputs.

HMAC is symmetric; verification keys can also generate HMACs. Separate custody of
checkpoint/operator keys, latest external reference, secure time and trusted local
Python/OS is required. Coordinated rollback of all custody and hostile same-UID key
or path control are outside this local model. Leaf/no-follow/lock/post-operation
checks do not constitute hardware-backed isolation. Capacity is finite, with no
protected deletion or automatic cleanup. SIGKILL is not physical power-loss
qualification. No production key rotation, real migration, executor/provider,
Proxmox/VM operation or privileged/live qualification was reviewed or authorized.

The prior Cloudflare anonymous-loopback concern was applicable to recovery detail
exposure and is closed by aggregate readiness plus actual ASGI checks. Ancestor
replacement remains conditional on external OS custody; no unobserved multi-UID
privilege claim is made. The separate comprehensive audit was still running on an
earlier snapshot when observed; it was neither modified nor interrupted and is not
represented as the current-source review. See SEPARATE-AUDIT-OBSERVATION.json.

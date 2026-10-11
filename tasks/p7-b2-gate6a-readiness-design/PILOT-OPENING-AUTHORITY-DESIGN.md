# Proposed bounded local authority — not installed

Recommended mechanism: one protected Core-local operator helper and one fixed-schema AF_UNIX owner-loop receiver in the **future V3 service**, with separate privileged operator and service identities described in OPERATOR-IDENTITY-BOUNDARY.md. No HTTP/WS/admin endpoint, client token, model text or timer can open or advance admissions.

## Explicit action and bindings

The human reviews the approved V3 manifest and fresh runtime challenge in the private trusted Core management terminal, authenticates as the separately authorized privileged operator, and invokes the proposed helper's **AUTHORIZE_INITIAL** action. This is a design name, not an installed/executable command in this packet. The helper connects only to the manifest's fixed local control socket, verifies peer identity and supervisor, displays/validates the exact challenge and transmits one bounded typed grant. No deployment Bearer is read or reused. No arbitrary operation, URL, filesystem path or code is accepted.

Require exact contract version, source/release/import inventory, config hash, unit and dedicated UID, PID + start ticks + boot ID + invocation, runtime nonce, pilot lineage/successor epoch, endpoint/model/native profile/context, continuation scope, renewed Gate4/Gate5 evidence, validated startup-checkpoint identity, approval provenance, operator identity, grant nonce/action and short expiry (proposed120s). PID alone is insufficient. Grants cannot be reused across restart, deployment, epoch or session. The expiry is refusal protection, not a timer that opens admission.

Immediately before granting in the serialized owner loop, recheck: initial accepted/submitted/receipt set empty; retained predecessor verified zero; one authorized successor only; no terminal stop/abort/incomplete/corrupt state; current/unknown D06 clean and no independent endpoint conflict; required private authentication readiness; valid fresh coordinated zero checkpoint; worker containment; and cap4/queue0/intake1. Missing/corrupt state refuses rather than initializes or repairs it. Opening itself performs no provider transmission, lease acquisition, turn acceptance, counter reset, restore or eligibility promotion.

## Narrow state machine

`CLOSED_INITIAL → OPEN_SESSION_HOLD → ARMED_ONE → INFLIGHT → SETTLING → CHECKPOINT_HOLD`.

Only privileged **AUTHORIZE_NEXT** grants arm a single ordinal, exact REST/WS transport and approved session/turn/request commitment. A client-supplied selector or continuation only matches an already authorized permit; it never grants authority. Initial session and reconnect binding must be allocated/verified by the Core owner, not taken on trust from a client header. Subsequent permits require known associated terminal, D04 join and verified coordinated backup of the actual accepted high-water set. No callback automatically arms the next turn.

Opening, permit consumption and accepted attempts need a durable authorization ledger in proposed D09 schema4. Nonces are unique. Record OPEN_COMMITTED/ARM_COMMITTED with actual operator/runtime/epoch/manifest association before acknowledging readiness. Commit accepted LIVE/eligible=false attempt, its ordinal/transport and permit consumption in one transaction before admitting/acknowledging work, acquiring D06 or creating a provider task. Admission checks are atomic under the one owner; no queue or backlog is retained. A second concurrent request is refused and freezes subsequent admissions without erasing the accepted first request.

Do not overclaim memory/disk atomicity: after a durable opening commit but before readiness acknowledgment, a crash consumes the grant but may have admitted nothing. The audit must distinguish committed authority, acknowledged runtime readiness and actual accepted attempts. No durable OPEN flag recreates runtime authority after restart. Partial writes roll back or leave a preserved ambiguous/terminal hold; never retry automatically.

## Qualified data path and termination

PILOT-only REST/WS branches must return the qualified driver result and never call legacy `_process`, `_process_stream`, registry dispatch, TTS, voice, resource wake or confirmation handlers. Keep lifecycle suppression independent of opening. Retain exact model/context/native bounds, no fallback/retry, conversational classification, empty operational tool schemas, proposal detection and no real tool dispatcher. Rest continuation uses authenticated `X-Jarvis-Continuation`; WS uses the reviewed bounded continuation protocol, distinct from authority. Scope additionally binds runtime/epoch; unknown/replayed/stale tokens abort. No voice/direct ingress may consume a permit.

One D06 lease precedes possible provider dispatch. Preserve known/no-transmission/remote-unknown distinctions and release only on reviewed associated completion or exact no-transmission proof. A successful parsed zero-tool terminal needs joined D04 evidence and verified backup before another permit. Any tool proposal, unknown, backup/receipt failure, auth/scope mismatch, lifecycle conflict or unexpected state terminally stops future admissions. No raw content or credentials belong in control audit.

Operator stop permanently revokes all permits and closes session authority, invokes the qualified30s local drain, and records CLOSED_COMPLETE only if reconciled facts support it; otherwise CLOSED_INCOMPLETE. It never asserts remote completion or clears D06. Cap4 and two transports each are durable across restart. Separate controlled recovery, if eventually approved, cannot revive a terminal stop/abort. No part of this design is currently deployed.

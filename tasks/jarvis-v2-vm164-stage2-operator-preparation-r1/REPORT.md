# VM164 Stage 2 operator preparation R1

**PASS_OFFLINE_OPERATOR_PREPARATION_ONLY. Stage 2 remains NOT AUTHORIZED.**

Prepared a finite, supervised, separately reviewable operator procedure for the
existing pinned Host Enforcement R3 candidate. No Proxmox connection, host
installation, timer/service activation, VM/guest action, credential operation,
network operation or package installation occurred. No live timer qualification
or guaranteed expiration is claimed. The sealed R3 packet remains unchanged.

## Operator entry points

- [EXACT-STAGE2-PROCEDURE.md](EXACT-STAGE2-PROCEDURE.md): ordered preconditions,
  mandatory fresh inputs, twelve cases, evidence sequence and 45-minute window.
- [COMMAND-CATALOG.json](COMMAND-CATALOG.json): complete argv arrays and literal
  reviewed Python bodies; mandatory live fields are unresolved placeholders.
- [TIMER-AND-SERVICE-REVIEW.md](TIMER-AND-SERVICE-REVIEW.md): every proposed property,
  actual-clock determination, serialization tests and matching-version uncertainty.
- [SECURITY-REVIEW.md](SECURITY-REVIEW.md): nobody authority/credential denial gate,
  author source review, resolved findings and mandatory independent review criteria.
- [FAILURE-AND-CLEANUP.md](FAILURE-AND-CLEANUP.md): owned-only cancellation,
  interrupted cleanup, evidence retention and finite recovery limits.
- [HOST-FACTS.md](HOST-FACTS.md), [AUTHORIZATION-REQUEST.md](AUTHORIZATION-REQUEST.md)
  and [GO-NO-GO.md](GO-NO-GO.md): reported facts, later exact decision and blockers.
- [RESULT-FORMAT.md](RESULT-FORMAT.md), templates/ and src/results.py: machine-readable
  evidence/result contract; no synthetic record can establish host authenticity.
- [TEST-RESULTS.md](TEST-RESULTS.md):71 actual offline tests, all passing.

The proposed sequence is fresh read-only identity/binary/package/boot/clock/
privilege/collision validation; exclusive root-owned callback placement after
separate approval; one-at-a-time nonroot transient cases with full evidence;
then owned-only cleanup and independent review. New trials stop at minute35;
owned units should be stopped by minute40; explicit UTC/BOOTTIME expiration is
at or before minute45. Dates, boot ID, binary hashes, nonce, source staging and
reviewer identities are mandatory future inputs, not invented values.

Tests cover arguments, UID restrictions, namespace/collisions, session/deadline
checks, clock ambiguity, failures, interrupted cleanup and result honesty. All71
passed under process/network/signaling tripwires. All96 R3 regular files were
read/indexed and remain byte-identical. The R3 source/archive verifier passed;
its prior294-test history was not represented as a new execution.

## Material blockers retained

1. Stage2 approval, concrete expiry and fresh host/preflight/evidence bindings
   do not exist yet. No operator input was needed to finish safe offline work.
2. nobody65534's lack of VM-management authority and private-credential access
   is not established by account existence or idle-process reports. Complete
   fresh independent policy/metadata review is mandatory before placement.
3. Matching systemd257 interfaces, WakeSystem support and actual next-elapse
   clock convention remain unqualified. Equal clock readings without matching
   documented-interface proof stay UNKNOWN; no suspend test is allowed.
4. systemd-run may reject a missing executable before exec; a missing dependency
   may leave an inactive timer instead of a failed one. Such observations cannot
   be relabeled as the missing required live failures.
5. Independent live admission/result signoff has not occurred. This packet has
   an author security/argument review and explicit independent-review criteria;
   it does not invent a reviewer or signoff.
6. R3 also requires reboot/reexec and other prerequisites excluded from this
   harmless session. They remain unqualified even after a favorable limited
   trial. Physical wake, root-worker/private-runtime behavior, Proxmox semantics
   and VM termination are not established here. No Stage3/4 or Gate6K promotion.

The unmodified canary has no authorization-expiry guard of its own; failed cleanup
or a delayed manager can leave a harmless callback scheduled beyond the session.
Supervision and limits reduce risk but do not create a hard expiration guarantee.

## Integrity and preservation

`MANIFEST.json` hashes every preparation artifact other than itself and SEAL.json;
`SEAL.json` hashes the manifest. `src/verify_packet.py` rechecks all payload bytes,
test source pins and all96 R3 file hashes. Local hashes are not signatures or
independent origin proof. Retain the manifest digest with any later review.
Only this new task folder and an appended project `tasks/loop-log.md` entry are
repository changes. Existing logs and sealed artifacts were preserved.

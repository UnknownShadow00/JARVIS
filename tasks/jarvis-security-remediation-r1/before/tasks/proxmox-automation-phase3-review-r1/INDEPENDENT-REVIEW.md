# Independent security review and closure

Reviewer: separate read-only agent `/root/serial_security_review`, configured via
the supported delegation tool as `gpt-6-astra`, reasoning `high`. This was an
actual available reviewer invocation and returned review reports; no Claude
availability or Claude review is claimed. The implementing agent remained primary
engineer. The reviewer changed no files, reran no tests, read no credential and
performed no privileged/live operation. Parent owns evidence and canonical logging.

## Original review

Target: original Phase3 source manifest
`58698f4cf814ef267ea010d44280c6bfdea2ce8f46486e51a18f3916d7ae24d5`.
Complete broker/worker/protocol/secret issuer/DAC/ledger/kernel guard/units/catalog
and installation/stop/acceptance model plus Phase2 contracts were reviewed.
No demonstrated critical/high escalation or disclosure under the documented
trusted-root/broker assumptions. Four medium findings:

1. Original runtime.py:209/protocol.py:175,182–184 used one lifetime input budget;
   legitimate envelopes eventually exhausted64KiB and killed the worker.
2. Original broker.py:23–55/runtime.py:103–107/journal.py:185 released the lock
   before receipt, permitting ordinary request contention to discard a valid ACK.
3. Unsolicited variable readiness, immediate session rotation and strict first-line
   decoding did not synchronize channel attachment, queued output or backpressure.
   Fresh-per-open mocks and one-request PTY tests concealed it.
4. Phase3 deferred actual-principal canary checks until after real credential
   issuance, contrary to Phase2's required no-transport pre-credential gate.

## Revision and targeted follow-up

The parent made fixes only in this new revision, preserved originals, and retained
guarded test evidence. Initial targeted follow-up confirmed receipt/budget fixes
and the structural precheck gate, then found three related medium edge cases:

- Dropped allow_empty flag after the exact qm banner broke LF-only beacon cuts.
- A64-beacon count cap contradicted otherwise allowed buffered idle beacons.
- An operator could wait beyond attestation/grant expiry during hidden prompts.

All three were corrected before sealing. Banner-prefixed every-boundary tests,
160 queued beacons, recovery after sustained filled-pipe idle output, and16 prompt
delay/config/marker/source/CA cases cover them. The complete revised harness passed
71 methods/305 subtests with0 failures/errors/skips and0 IP/credential attempts.
These tests were executed by the implementers; the independent reviewer inspected
code/tests/receipts rather than independently rerunning them.

## Final reviewer disposition

Final read-only closure verified the revised source-manifest fingerprint:
`9e5bdd0ea59fa36021f462f4388597fefd4b65f9cee32024e86ba5d33d700301`.

> Closure: no remaining blocking finding in the targeted fixes.

The reviewer confirmed lock lifetime, per-exchange budgets, banner/byte-boundary
synchronization, bounded beacon drain/backpressure regressions, post-prompt
revalidation and actual-principal checks before real issuance. Suitable for sealing
as an **offline reviewed candidate**; live compatibility/isolation remain unverified.

## Explicit residuals

Local audit verification does not reconcile request-table state against event
history; local hashes are not independent anti-rollback authority. A client receipt
means validated data parsed in the client, not durable stdout or human observation.
The reviewer judged these accurate documented limitations, not authority-boundary
redesign requirements under this threat model. Guest observations remain forgeable
by a compromised guest; kernel/root/hypervisor compromise is not excluded by
offline simulations. Independent actual-UID, no-escalation, QEMU/TTY, installed API,
systemd and protected guest acceptance remain required. No privileged qualification
or activation is approved by this closure.

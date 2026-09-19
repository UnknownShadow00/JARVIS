# Deferred — Task 13B11K

Recorded, not resolved.

## Opened by this task

1. **A timed-out confirmation stays in `EXECUTING`.** The frozen graph draws only `ok` and
   `error` out of execution, and contract §18 says a timeout leaves the outcome unknown, so no
   terminal transition is invented. The record is not replayable — it is not `PENDING`, and both
   settlements require the matching invocation id — but it is unresolved. A later phase must
   decide whether an operator action, a sweep, or a follow-up probe closes it. See
   `CONFIRMATION_HANDOFF.md` §4.
2. **A failed settlement is not surfaced.** If the authority raises after the executor ran, the
   trusted result stands and the record stays in `EXECUTING`. The inconsistency is invisible
   until audit integration exists.
3. **`ConfirmationAuthority` is structural, not nominal.** A caller could inject an object that
   claims without checking. That is the same trust the executor already has, and the live
   composition layer is what will bind the real store — but it is a property of the seam worth
   stating.

## Carried forward untouched

* `browser.open` / `browser.search` versus operator decision D-01.
* Confirmation TTL numeric values — proposed in `CONFIRMATION_STATE_PLAN.md` §6, signed off by
  nobody, and still absent from the code.
* `lane` as an audit field.
* The redaction secret-key list.
* `TIMEOUT` as a `ProvenanceSource` — still not added, and this task does not need it.
* The P6 classifier/router unsupported-verb reconciliation.
* Live capability projection from the real tool inventory.
* The real dispatcher adapter, live request wiring, and the response-obligation engine.
* Confirmation persistence and the on-load expiry sweep.

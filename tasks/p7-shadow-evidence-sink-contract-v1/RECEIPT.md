# ShadowObservationSinkReceiptV1

No existing receipt serves this observational durable boundary. Freeze a frozen/slotted data-only **ShadowObservationSinkReceiptV1**, with five required fields (nullable ones supplied explicitly):

| Field | Type | Source / meaning |
|---|---|---|
| accepted | exact bool | Sink commit result; True only after proven durable commit, never execution/CT success |
| durable_sequence | positive exact int or None | Sink-local durable position, present only on accepted entry; not attempt/turn authority |
| persisted_at_utc | aware UTC datetime or None | Sink acceptance-clock sample stored in committed entry, present only on accepted receipt |
| entry_sha256 | lowercase 64-hex str or None | Canonical committed entry digest per SERIALIZATION.md, present only on accepted receipt |
| failure_code | fixed sink failure literal or None | Nonaccepted result only; no raw request/model/exception/path content |

For accepted=True all three metadata fields are present and failure_code=None. For False metadata fields are None and failure_code is present. COMMIT_UNCERTAIN therefore returns no claimed committed position/time/digest even if bytes may exist; later independent recovery/reconciliation may discover them. Do not return partial success or copy model success into accepted.

Frozen sink-only failure literals: INVALID_RECORD, UNSUPPORTED_VERSION, CLOCK_INVALID, STORAGE_FAILURE, INTEGRITY_FAILURE, COMMIT_UNCERTAIN, RECOVERY_UNRESOLVED. These describe this new persistence boundary; they are not PipelineStopReason, audit events, operational refusals or proof of execution. Duplicate-key disposition remains scheduler-dependent; no duplicate enum or automatic uniqueness key is invented.

Normal validation/clock/storage failures return a nonaccepted receipt. If receipt construction itself fails or an unexpected exception escapes the future API, the shadow caller must classify unresolved/failed evidence and isolate it from legacy. Fatal termination may produce no receipt at all. No persistence of a failure receipt is promised when storage is unavailable. Receipt delivery, upstream durability and retry behavior need separate accounting. An accepted receipt does not certify origin, absence of upstream loss, privacy of a compromised host, or a measured window.

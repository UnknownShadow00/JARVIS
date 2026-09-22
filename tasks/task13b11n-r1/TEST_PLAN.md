# Static contract and implementation test plan
contract-corpus.json is frozen before production code or scored tests. It carries exact serialized records, expected acceptance, and caller ID counts.
Valid classes: text only, proposal only, draft plus one, multiple, empty text/list, arbitrary inert data, nullable nested data, hostile prose.
Invalid classes: unknown/authority/control/reasoning keys, duplicate and escape-equivalent keys at all depths, missing keys, wrong types, forbidden null, malformed JSON, non-object root, nonfinite numbers, malformed later proposal.
Validate corpus labels statically before implementation. R2 copies it byte-for-byte and tests actual P0 field values, metadata ownership, all-or-nothing results, immutable data and purity. Add a separate generalization corpus after implementation rules freeze; never tune rules after seeing its results.
Re-run full pytest, deterministic golden, legacy probe, hashes, no-consumer scan, audit-hook purity, security review and seal verification.


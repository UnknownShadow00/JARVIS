# Gate6D improvement register

All fixes belong only to artifact `fbc53bd51a3d9968484275443817ef2e8eb41c853748c24a2b371ab4dc899ad1` at `/home/jarvis/.hermes-poc/gate6d-candidates/engineering-r1`. Detailed changed-file list and patch are in candidate-manifest.json and evidence. No production source, policy, provider binding or dependency change.

| Problem/risk | Exact change | Verification | Remaining authority |
|---|---|---|---|
| Untyped peer/signature input | authority.py strict tuple/integer checks, signature length and checkpoint hex |7 malformed-peer cases; existing identity/replay cases | Real kernel peer and human signer |
| Exponent overflow | contracts.py finite float JSON parsing | ±1e999 rejected | None for isolated fix |
| ASGI malformed/mixed frames | ingress.py event-type, UTF-8 and more_body validation |7 malformed event cases, existing binary/control tests | Production middleware/disconnect integration |
| Wrong Granite transport/profile/limits | observation.py checks exact frozen resource and all6 limits |9 binding/limit cases plus canonical bridge | Actual transport qualification |
| Split stop record | storage.py stop transaction accepts verified approval; runtime sets stop latch first | Before/after commit crash fault cases | Real operator socket and supervisor |
| Lost local delivery / callback leakage | runtime.py completion callback, failure latch; storage.py monotonic delivery evidence | Immediate stop, late cancellation, persistence failure cases | Final checkpoint/writer lifecycle |
| Arbitrary/new operation on settled attempt | storage.py begin whitelist and ordering/unsettled checks | Arbitrary lifecycle kind and settled-step tests | Real D06 backend |
| Symlink ancestry/read-through | storage.py rejects existing symlink ancestors and source receipt links | Static symlink path and backup source tests | Protected ancestors + TOCTOU under OS separation |
| Semantic ledger corruption | storage.py shared validate_accounting for store/checkpoint | Tampered permit association, existing schema/cap/restart tests | Independent root/high-water authority |
| Forensic missing joined receipt | storage.py enforces len(lines)>=len(joins) | Rechecksummed deletion rejected | Real D04 association |
| Checkpoint race | Quiescence under same writer lock as snapshot | Existing checkpoint tests/full regression and source review | OS concurrent/power-loss qualification |
| Predecessor numeric ambiguity | exact integer0 validation | Boolean/float count cases | Real predecessor archive validator |
| Missing process-failure evidence | Five os._exit fixture children; duplicate reservation race/partial writes | Focused149/full7315 passing | Target filesystem power failure/disk stalls |
| Ambiguous resource recommendation | Pure original-source routing matrix, per-role proposed bindings | Deterministic source assertions | Operator chooses contract, no auto approval |

No historical test weakened or removed. Canonical119 app/208 original tests and94 existing candidate tests unchanged. New adversarial module adds55 cases. Read-only production observers and review generators are documentation/evidence tooling, separate from candidate source.

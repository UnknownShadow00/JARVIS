# Continuous improvement register

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

Candidate revision for all entries: `c28942a9d7254376117bfd58cc0fa6549112a84f1be6a60752ef75c00442567b` (source/qualification artifact digest). Exact patch and tests accompany the evidence.

|Problem/risk|Implemented improvement|Tests|Remaining authority|
|---|---|---|---|
|Legacy semantic drift|Source-derived rules/prompt/cleaner; typed strict policy; conditional responders|source hashes, rule equivalence, four inputs, schema failures|L1 experiment/memory/budget approval|
|Unbounded or unowned send|Actual bounded native transport; exact D06 lease claim; reusable explicit transport|framing, phase timeout, no lease, unsupported endpoint|effective provider/digest + OS/external exclusivity|
|Replay after release|Durable operation tombstones/domain transaction|replay and competing writers|protected shared root deployment|
|Missed disconnect|Concurrent ASGI receive; strict origins/headers/frames|FastAPI REST/WS, disconnect/extra-frame controls|real route/proxy qualification|
|Inconsistent audit/history|ASGI delivery record, original legacy cleaner, exact D04 joins|late completion, proposal rejection, duplicate/uncertain receipt|production event migration|
|Rollback/reset risk|Archive parser plus singleton high-water/prefix/lineage association|V2 bundle graph, reservations, actual process crash|privileged root/signature provisioning|
|Incomplete backups|Atomic coordinated publication and forensic final snapshots|disk full, symlink/corrupt/stale, pre/post publish crashes|OS race/power-loss and local-risk acceptance|
|Incomplete independent validation|Revalidate D06 scope/state/marker, operation tombstones and lineage even after rehash|four rehashed-checkpoint attacks|protected archive/OS controls|
|Local transport cleanup|Drain explicitly closes transport without releasing remote unknown|drain cleanup test|real OS cancellation qualification|
|False complete/hold state|Final checkpoint downgrade; stop latch after publication|terminal failure and stop during checkpoint|supervisor shutdown integration|
|Overbroad historical fixtures|Historical synthetic routing moved test-only; socket/HTTP imports narrow|94 historical assertions retained plus new checks|none for isolated change|

No tests were weakened to obtain a pass. Two fixture errors (wrong V2 connection attribute and missing frozen done_reason) were corrected. The old no-network-library import assertion was refined for the explicitly authorized new transport/local socket modules; unsafe default transports and production imports remain prohibited. A test-only handshake deadlock was corrected to model a receive that waits for input instead of throwing StopIteration; the hung disposable child was specifically identified and terminated, never the live service.

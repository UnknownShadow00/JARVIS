# Task 13B11O-R1 — contract repair only

The operator's P7-D01–D04 decisions resolve the four 13B11O decision blockers. This task freezes the recorded/static P7 composition contract, not production code or a live execution protocol. The original task13b11o directory and its seal are unchanged.

Entry workspace: c9cce9b47a79c8ac52da116d113b3fb824991cf8, clean. Production: db54d615c3ee023d753e86143860c4efdc251230, clean, no unexpected untracked files. Hermes: 2237be355906fbe6065ce1815711eee52b2d646e, clean, no observed Hermes/Ollama processes. Mode legacy; execution.hermes_brain=false; agent.hermes_enabled=false.

13B11O verified 53 files / 52 manifest entries; SHA256SUMS SHA-256 402c685191858bbe5f53e7086d8f43b407de2fd10ed5a0e6d5325184302b967f. All 43 prior sealed bundles verified with zero failures. The old contract explicitly said NOT FROZEN, so the resolved contract is V1, not V2.

Read the blocked follow-ups and proposed P7 artifacts, then the execution contract, actual dependency graph, adapter contract and current P0–P6 APIs. Authority allocation now follows the new operator decision where it explicitly supersedes the older proposed guard ownership. No unrelated contract or policy is amended.

Execution profile: network only for established SSH repository verification/evidence transport; the contract's intrinsic side-effect allowance is zero. No new diagnostic calls dispatch, mutates confirmation/provenance or emits audit. The required existing regression suite uses its own inert test fixtures; those are not live execution or new pipeline implementation.

Verification-loop: full pytest, deterministic golden, legacy hash, dependency consistency, docs/diff/hash checks. No production build is needed for documents. Vulnerability/lint/type/coverage tools remain unavailable; no installation or clean vulnerability-scan claim. One documentation commit; no production commit or push.

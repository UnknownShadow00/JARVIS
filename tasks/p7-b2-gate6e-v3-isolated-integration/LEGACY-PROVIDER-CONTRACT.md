# G6E-LP-1 proposed release binding

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

This is a versioned qualification refinement of G6D-LP-1, not approved live defaults. `LEGACY_EFFECTIVE_ENDPOINT=UNVERIFIED`. Source YAML says localhost:11434, gemma3:4b and qwen3-nothink, but protected environment overrides were not read. Immutable legacy model digests are UNVERIFIED. The test endpoint192.0.2.10 is an RFC5737 fixture address, never contacted or promoted to a default.

| Operation | Model binding proposal | Context /output | Native options | Request/response bytes | Deadline /keep-alive |
|---|---|---|---|---|---|
| Legacy classifier | gemma3:4b + immutable digest required |4096/64|num_ctx4096,num_predict64,temperature0.1|16384/16384|20s/60s|
| Legacy trivial | gemma3:4b + immutable digest required |4096/80|num_ctx4096,num_predict80|16384/16384|180s/60s|
| Legacy normal | qwen3-nothink + immutable digest required |32768/150|num_ctx32768,num_predict150|16384/16384|180s/60s|
| Granite observation | hermes-candidate-granite41-30b-q3km-64k |64000/128|Frozen canonical native profile|16384/16384|180s/60s|

Granite endpoint remains exactly http://192.168.0.200:11434; profile jarvis.p7.ollama.granite41.b1r2.v1. No Granite parameter was changed. Legacy models are never silently assigned to it. Legacy profile identifiers in tests begin fixture-; production profile/version identifiers require explicit approval.

For each row: exact effective endpoint/service identity and model digest must be independently established; stream=false, think=false for these branches, zero retries/fallback/discovery, no lifecycle request. Keep-alive is an explicit native request field, not proof that the model remains resident or an exclusive host lease. Deadlines include whole HTTP operation. Cancellation, framing failure and timeout retain possible-send uncertainty; they do not free D06 or permit another attempt.

Terminal evidence: correlated HTTP operation with complete bounded JSON, matching model, done=true and assistant message; Granite additionally passes its frozen done_reason/profile normalizer. The local client cannot independently authenticate a model alias to a digest. Profile/source/model attestations therefore remain release prerequisites.

Prompt profiles: router SHA26228b8c8a6be2afd2043a1f52015745be045a58f69e6db2d923de4c875f6cf7; responder SHA20143a5dc7a2da8a034962e90929c83d49ddb85c8ddd5d8c7703739dcc295b87. Parser/cleaner and procedural-memory snapshot selection must be approved alongside resource budgets. No payload logging; evidence stores minimized associations and hashes.

PROVEN_BY_SOURCE: rules, prompt values, classifier temperature/schema/threshold, complexity choices, cleaning. PROVEN_BY_ISOLATED_TEST: strict parser, request limits, serial fake execution, rejection paths. PROPOSED_FOR_OPERATOR_APPROVAL: added context/keep-alive/request budgets, total workload, strict refusal deltas, memory policy. UNVERIFIED_EFFECTIVE_RUNTIME: legacy endpoint/model digests, installed prompt/config overrides, external resource actors.

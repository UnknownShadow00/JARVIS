# Prove origin without raw content retention

No default persistence of raw user request, full prompt/history/tool argument values, raw provider/model response, ModelDraft text, private reasoning, credentials, headers, endpoint tokens or exception prose in observation, sink or associated formal evidence. Required canonical-request/parser-input references are digests computed from the transient in-memory inputs; their raw bodies need not be retained. Preserve existing no-raw-document adapter semantics and D03/D04 privacy.

Use existing SHA256 conventions; digesting is not encryption, authenticated source, secrecy or anonymity. IDs and low-entropy input hashes can be dictionary-linked; keep associated evidence local/private under later approved controller retention, not public/provider telemetry. Exact provider wire capture/optional fingerprint representation needs D06 privacy review, especially hidden reasoning/credential-bearing transport fields. No extra raw text is technically required to freeze D05; a future contrary need is an explicit privacy/operator decision.

The adapter necessarily handles transient raw request/response material to serialize/parse; that is not permission to persist it. Current task reads source/contracts and uses no live payload. D04 sink clock supports chronology only; no timestamp proves turn/provider/parser authenticity.

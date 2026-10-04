# Raw-text exclusion and minimum collection

V1 excludes raw user request, model text, candidate text, target/URL/app value, canonical/raw argument maps, route clauses, prompt/history, adapter recording, model identifier, exception prose and hidden reasoning. Never serialize an entire envelope, route, terminal or ModelDraft. Read only the selected typed fields needed by FIELD_INVENTORY.

The binding fingerprint is the sole content-derived field: it hashes the complete narrow deterministic canonical binding rather than request/model prose. Public IDs and structured row/source/outcome labels are retained for correlation and conformance. SHA256 digests allow linkage and dictionary guessing of low-entropy targets; they are not encryption, anonymization or authenticated identity. This privacy limit is explicit. No raw-request/model digest or truncated excerpt is added by default.

CT-001's exact fabricated-draft exclusion/draft-retention and CT-013's ordinary safety/leakage checks require evidence beyond IDs/enums. If future integrated CT proof needs exact text, request a separate schema/privacy/evidence decision; no raw fields or hashes of all text are silently reserved here. D04 retention/access/redaction/sink decisions remain open; this producer returns data only and chooses no storage policy.

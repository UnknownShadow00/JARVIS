# Canonical binding fingerprint

Reuse the established registry_metadata.py:45-50 convention: SHA256 over UTF-8 JSON with sort_keys=True, separators=(",", ":"), ensure_ascii=False. No import/call to snapshot_registry_metadata, source reading or live registry query. The hashing/JSON serialization is in-memory projection of already-settled data, not argument canonicalization.

For a present existing binding.expected, hash exactly this logical JSON object:

```json
{"tool_name": "<expected.tool_name>", "canonicalization_version": "<expected.version>", "canonical_arguments": "<complete string-to-string map copied from expected.canonical_arguments>"}
```

The placeholder for canonical_arguments denotes an object, not a string in the actual preimage. Preserve all keys/values without trimming, case conversion, URL parsing, ignored extras or default=str. Exact V1 binding canonical maps contain strings; malformed/non-plain/mutable input is rejected, never normalized. Dictionary key order is made deterministic only for hashing; values are unchanged. The 64 lowercase hex result is binding_canonical_fingerprint. No random salt, clock, identity-based hash or truncated digest.

The fingerprint proves equality against an independently retained trusted canonical-binding reference, subject to SHA256 assumptions. It does not by itself prove that a binding was authentic, that a proposal matched, or that a tool ran. No separate fingerprint ID is minted. If binding is absent or its expected/query pair is legitimately empty, the fingerprint is None. metadata_digest is copied unchanged and separately pins the metadata basis.

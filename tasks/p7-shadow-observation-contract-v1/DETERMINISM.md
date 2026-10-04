# Deterministic logical record

Same settled handoff values produce the same logical record: exact field/enum copying and one prescribed canonical-binding SHA256. None remains None. No clock, random/UUID, object identity, Python hash(), set selection, model query, live registry or unordered first-item choice. Exact string/enum/scalar types are required; no str() coercion or default serializer of arbitrary objects.

Transport vocabulary is the existing http/websocket strings, copied from settled JARVIS metadata. Fingerprint dictionary order is normalized by the existing sorted JSON convention, not by recanonicalizing arguments. Mutation of source mappings/lists cannot alter a returned record because none is retained. Identical logical records can belong to different evaluation attempts of the same turn; no retry/deduplication policy is inferred from equality.

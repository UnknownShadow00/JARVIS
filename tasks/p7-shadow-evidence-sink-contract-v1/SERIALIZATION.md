# V1 logical evidence entry — backend neutral

D03's producer has a versioned type name but no numeric version field or wire serializer. Do not alter its 18 fields. Freeze an explicit sink-owned persisted wrapper with exactly six fields:

| Field | Type / meaning |
|---|---|
| sink_schema_version | exact int 1, excludes bool; identifies this evidence-entry schema |
| observation_schema_version | exact int 1, excludes bool; identifies the embedded D03 observation schema |
| durable_sequence | exact positive int, excludes bool; evidence position only |
| persisted_at_utc | aware UTC datetime serialized by .isoformat() with explicit +00:00 |
| observation | exact 18-field mapping from D03 FIELD_INVENTORY.json; every nullable field present as null |
| entry_sha256 | lowercase 64-hex SHA256 of canonical UTF-8 JSON of the other five fields |

In observation, serialize the existing enums by their exact .value, strings/integers/booleans/null unchanged, and correlation by existing CorrelationContext.to_mapping(): session_id and turn_id only for this initial-turn scope; child IDs absent. Explicitly validate/enumerate fields; no generic dataclass/asdict/default=str conversion, omission of nullable facts or coercion of model/client mappings. Recover the same enum/type semantics when reading; unknown versions/keys/literals fail closed. All 18 field names and meaning remain D03's exact frozen authority.

Canonical bytes: json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"), reusing registry_metadata.py:45–53. entry_sha256 is excluded from its own digest. No newline or backend framing is part of these canonical payload bytes; framing/transaction engine must separately distinguish complete commits and partial records. Receipt digest identifies the stored entry including its sequence/time; identical logical observations written at different positions need not share that digest. This is not an attempt/deduplication identity or authenticity proof.

Both integer versions are persisted independent of Git revision. Unknown V2 or extras are rejected, never silently migrated to V1. No migration framework, backend selection or operational audit schema added.

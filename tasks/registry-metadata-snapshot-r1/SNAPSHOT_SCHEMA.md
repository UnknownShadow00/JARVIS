# Snapshot schema V1

| Field | Type | Source / owner | Meaning and immutability |
|---|---|---|---|
| `schema_version` | `str`, exactly `"1"` | this reviewed boundary | closed snapshot format; frozen field |
| `source_revision` | SHA256 hex `str` | canonical JSON of three source-file hashes | deterministic reviewed source identity; frozen field |
| `metadata_digest` | SHA256 hex `str` | canonical JSON of version, revision, hashes and selected rows | content integrity association; frozen field |
| `tools` | tuple of internal frozen slotted rows | registry and handler declarations | sorted `apps`, `browser`; no live reference |

Each row has `tool_key: str`, `module_path: str`, `safety_level: int`, `argument_fields: tuple[str,...]`, `supported_actions: tuple[str,...]`, `allowed_app_names: tuple[str,...]` and `source_sha256: str`. The last three are *selected V1 handler metadata*, not an assertion that all handler modes are admitted. In particular `browser` also implements search but the V1 snapshot advertises only the frozen open fields/action. The module contains no capability strings because the registry does not declare the P4 capability pair.

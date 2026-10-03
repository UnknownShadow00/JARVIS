# Closed V1 versioning

`BINDING_SCHEMA_VERSION = "1"` is an exact literal. The admitted set is exactly the two rows in `ADMITTED_MAPPING_V1.md`; no runtime table extension or fuzzy fallback is allowed. Any new action, field, predicate, capability/tool crosswalk, or canonicalization change requires an explicit reviewed version change before use.

The passive metadata snapshot carries source revision and a SHA256 digest of UTF-8 canonical JSON (`sort_keys=True`, compact separators, `ensure_ascii=False`) containing the selected registry keys/module paths, handler safety and field/action declarations, app-name allowlist, and source hashes. The binder verifies both the reviewed V1 shape and digest. The canonical Core HEAD is evidence for this freeze, not a requirement to keep future production Git HEAD unchanged. A later implementation must pin reviewed metadata source hashes/version in its own acceptance evidence. No automatic migration or fallback to a later schema.

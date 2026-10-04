# Deterministic binding handoff

Only the future shadow composer may call `build_binding_projection(normalized_request, classifier_context, registry_metadata, approval_mode, "1")` as defined in `app/execution/binding_projection.py:204-227`. The producer alone consumes `RegistryMetadataSnapshotV1`; server must not map tool names or read registry metadata directly. Output is the exact immutable `BindingProjectionV1(binding_schema_version,metadata_digest,router_context,expected,permission_projection)` (`f-map-01-binding-contract-v1/OUTPUT_SCHEMA.md`). It admits only OPEN_APP→apps.open→apps and OPEN_URL→browser.open→browser.

Invalid owner inputs raise `BindingProjectionError` and yield no P7 turn. An admitted route with no complete binding has `expected=None` and `permission_projection=None`, never an inferred tool. No client/model values fill these fields. Session snapshot, classifier context and approval-mode live sources are unresolved before ingress wiring.

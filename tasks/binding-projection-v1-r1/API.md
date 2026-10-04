# Minimal public API

`NormalizedJarvisRequestV1(request: str, correlation: CorrelationContext, snapshot: LedgerSnapshot)` is the transport-neutral envelope. `BindingProjectionV1` is a frozen, slotted five-field value: `binding_schema_version="1"`, `metadata_digest`, `router_context`, `expected`, `permission_projection`. `BindingProjectionError` distinguishes invalid owner inputs from a valid empty binding. `build_binding_projection(normalized_request, classifier_context, registry_metadata, approval_mode, binding_schema_version)` is the pure composer; all five inputs are required. It accepts no client route/tool/capability/permission, model draft/proposal, store, registry or executor.

The output field names and types are exactly those in frozen `tasks/f-map-01-binding-contract-v1/OUTPUT_SCHEMA.md`. The binder returns no adapter, lane signal, confirmation, invocation or result object. P7 and their existing owners handle those separately.

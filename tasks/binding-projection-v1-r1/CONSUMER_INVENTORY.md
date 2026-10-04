# Exact consumers

Production scan and focused tests require `registry_metadata.py` production consumer list exactly `[app/execution/binding_projection.py]`. They require the binding producer's own production consumer list to be empty. The snapshot test now verifies one exact import of `RegistryMetadataSnapshotV1` and `snapshot_registry_metadata`; all other registry metadata consumers remain forbidden. Server/API/UI, pipeline, adapter, dispatcher and live registry remain unwired. `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false`.

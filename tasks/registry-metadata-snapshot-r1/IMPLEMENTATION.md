# Passive registry metadata snapshot R1

Core production commit `fa8560c943621b9de42aeb5122093b5247c6ccbd` (parent `ac685a898e0fb55cf7c97a3e04e5765bf2e37a41`) adds only `app/execution/registry_metadata.py` and `tests/execution/registry_metadata_test.py`. The module implements the F-MAP-01 V1 metadata dependency with zero production consumers. It reads and parses source declarations as data; it does not import or instantiate the live registry or handlers. No binding producer or server path was added.

`snapshot_registry_metadata()` has no parameters and returns a frozen `RegistryMetadataSnapshotV1`. The selected rows are `apps` and `browser`, sorted by tool key. The snapshot records reviewed source hashes and a deterministic content digest. Any drift in the three reviewed source files fails before metadata is returned. Other registry entries are neither admitted nor mapped by this module.

# Public API

| Symbol | Shape | Meaning |
|---|---|---|
| `RegistryMetadataSnapshotV1` | frozen, slotted dataclass | immutable selected registry metadata with version, source revision, content digest and ordered tool rows |
| `snapshot_registry_metadata()` | zero-argument pure read-only factory | reads fixed canonical declaration files, validates the reviewed revision, returns a snapshot or fails closed |

`__all__` contains only these two symbols. `_RegistryToolMetadataV1` and parser functions are internal value/helpers, not execution interfaces. No caller-supplied metadata, route, capability, proposal or tool key is accepted by the factory. Constructing a dataclass manually is not proof of authoritative origin; the future binder must verify the reviewed digest and exact V1 rows as frozen in F-MAP-01.

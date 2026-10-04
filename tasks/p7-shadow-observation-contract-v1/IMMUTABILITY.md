# Immutable output and inputs

ShadowObservationRecordV1 is frozen and slotted. Retained members are immutable P1 CorrelationContext, existing enums, exact str/int/bool scalars or None. No dict/list/set/MappingProxyType backing map, envelope, binding/route/terminal object, P2 snapshot/store, proposal list or transport object is retained. No callable, service locator or behavior-capable reference is exported.

The trusted caller supplies already-settled immutable owner outputs. Reject mutable or behavior-bearing canonical maps/records; do not make a shallow wrapper around them. Binding fingerprint reads and serializes only exact primitive canonical values into temporary in-memory data. The producer does not repair mutable sources by treating them as settled authority. Later changes to any caller collection/context owner cannot change the completed record.

Existing Python frozen dataclasses are a trusted-process API boundary, not protection against arbitrary hostile code using object.__setattr__. No additional P1/P2 immutable type or in-process isolation claim is introduced.

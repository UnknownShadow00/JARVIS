# Issued settled context only

The only context-side dependency is `SettledShadowTurnContextV1`. Constructor input must be that exact type, not a subclass, mapping, mutable owner, store, ledger, snapshot alone, callable or transport object.

The envelope retains `context is supplied_context`; correlation and snapshot identities are also preserved. Authoritative session/turn/correlation and optional observational trace are only read through this settled view. There are no duplicate ID scalars, session admission, ledger selection, trace context-variable reads or new snapshots.

The existing context validator is reused for P1/P2 shape, association and immutable public graph. It authenticates no client origin. The future trusted caller must supply an owner-issued view rather than deserialize client claims. No capability, registry, service locator or mutable owner crosses the handoff. Context implementation remains byte-identical to entry.

Proof: `context-handoff-proof.json`, exact import/call budget and frozen malformed-context cases. Fixture owner allocation and P2 population occur outside guarded ingress; allocation/acquisition/minting are trapped during composition.

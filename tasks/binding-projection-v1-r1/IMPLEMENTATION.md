# Passive Binding Projection V1 implementation

Canonical Core production commit `d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c` (parent `fa8560c943621b9de42aeb5122093b5247c6ccbd`) adds `app/execution/binding_projection.py`, a focused test and two frozen fixture files. Four existing test files changed: three exact P3/P4 non-activation budgets covering nine parametrized assertion instances, plus the previously frozen registry-snapshot sole-consumer transition. No pipeline, router, canonicalizer, permission, confirmation, dispatcher, registry, server, adapter, policy or audit source changed.

The producer builds the deterministic `RecordedTurn.router_context`, `.expected` and `.permission_projection` inputs. It has no production consumer and does not create a turn, call Hermes, make a proposal, dispatch, call a tool, emit audit or write provenance. The snapshot has exactly one production consumer: this module.

# Expected import/call graph

Current: server → legacy `_process`/`_process_stream`; registry_metadata → binder (one production consumer); binder → no production consumer; P7 pipeline → no production consumer.

Target after separate authorization: server ingress → inert shadow composer → `binding_projection.py` → `registry_metadata.py`; composer → recorded adapter boundary (optional authorized provider source) → `pipeline.run_recorded_turn`; composer → observation-only measurement boundary. No server→registry metadata, server→dispatcher, composer→dispatcher/registry.call/confirmation machine, model→binding, or shadow→legacy reply edge. Exact composer module/path is not assigned by 13B11A or later frozen tasks: **PATH UNRESOLVED**. `TARGET_COMPONENT_MAP.md` calls `pipeline.py` the integration boundary/only server entry, but current `pipeline.py` is the already-frozen passive recorded-turn API, and changing it is outside this task.

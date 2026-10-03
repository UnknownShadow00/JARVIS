# Exact proposal comparison

The binder provides P7 `RecordedTurn.expected` and `permission_projection`. The JARVIS-created `AdapterRequest` separately advertises the same exact tool key and schema from the same reviewed snapshot. The Hermes `ModelDraft` and `ToolProposal` remain untrusted. P7 S06 compares the complete canonical proposal against the complete expected tool name and argument map under its frozen guard order. No ranking, merging, field dropping, correction, nearest-tool selection or model-authored target.

Zero proposals follow the existing non-tool/stop path. Multiple proposals, unadvertised names, mismatched canonical arguments, IDs or capability fail the appropriate existing guard. A matching proposal is only an inert comparison match; P4/P5 gates remain separate. `binding_projection.py` must never read a proposal to build or repair the expected side.

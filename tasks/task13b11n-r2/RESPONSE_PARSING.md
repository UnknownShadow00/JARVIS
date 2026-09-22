# Recorded response parsing
Exact root keys text/proposals; exact proposal keys tool_name/raw_arguments. Required, typed, closed structural schema. All proposals validated before output construction.
Raw argument objects are the P0 open data namespace: nested JSON data is preserved as immutable mappings/tuples, including explicitly nullable values. Argument keys do not create structural authority.
Duplicate decoded keys fail at every depth. Unknown structural fields fail, including provider model/IDs/timestamps and permission/result/confirmation/execution/provenance/obligation claims.
Caller IDs are counted, validated, checked for identity duplicates and assigned in input order. No proposal filtering, selection, normalization or execution.
No provider envelope is ignored: this entire input is the canonical JARVIS recording, not a future Hermes wire format.

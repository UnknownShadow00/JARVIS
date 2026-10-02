# Reachability classification

**D — UNDERSPECIFIED for the exact zero-proposal rejection point.** The input shape is reachable and accepted by existing pure component constructors/parser. C15's claimed S09 traversal is unreachable under the frozen walk. Those two facts are compatible: a reachable malformed semantic combination may lack a specified place to reject it.

Actual probe_contract.py observations at production baseline:

- classify returns GENERAL_EXPLANATION; route returns NONE/target=None/capability_available=False.
- parse_recorded_response accepts the zero-proposal recording.
- lane.explain with tool_result=True returns OPERATIONAL and TOOL_RESULT.
- In an isolated diagnostic P6 input, attaching the unassociated executed result raises C-06-non-dispatchable-action-yet-executed. P6 C-15 does not fire because lane reasons are present.
- In the comparison diagnostic, omitting that result instead returns MISSING_CONTEXT/no_grounded_source_available. That is not a valid resolution: it silently discards supplied evidence and manufactures a normal answer for an invalid replay.

These are component observations, not pipeline measurements. The typed TrustedToolResult used in the isolated P6 probe is explicitly synthetic test-owned data; no dispatcher origin or real execution is claimed. F-P7R1-01 remains open.

Why not automatically use S11/obligation_failed? V1 admits the result only after ordered S09 association; it forbids passing unassociated result state downstream. The isolated P6 input bypasses that boundary. Its correct contradiction code does not authorize the composer to build that input. Also the higher pipeline guard permits normal P6 terminals only with independently complete state. Why not silently drop the result? That would produce the observed unrelated fallback and contradict replay/retention truth.

Nonzero proposals are **B — unreachable at the disputed guard because the earlier unexpected_proposal stop wins**. The complete C15 description fails to specify cardinality, so correcting only this subcase or relabelling C15 component-only cannot complete the required admission corpus.

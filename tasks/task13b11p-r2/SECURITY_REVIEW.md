# SECURITY REVIEW

Reviewed as a design review of the two frozen contracts against the production sources, at
a baseline where no pipeline exists. No runtime security measurement is claimed.

| # | §49 item | Finding |
|---|---|---|
| 1 | proposal bypasses route | no path: the route is produced by the unmodified router from the original request; the proposal is only ever compared against it |
| 2 | proposal creates capability | no path: capability comes from `router_context.supported_actions` and the frozen P4 pairs; a `ToolSchema` description is request consistency only |
| 3 | model grants permission | no path: `permission_outcome` is never admitted; re-decided every run; a replay must agree (C-07) |
| 4 | model grants confirmation | no path: no approval field exists; the mode is derived |
| 5 | confirmation id becomes authority | no path: id alone is inert; full twelve-field binding equality is required. **Note:** the guard that enforces this is the one P-B02 blocks, so it is specified and unimplemented |
| 6 | raw "yes" becomes authority | no path: request text reaches only the classifier and router |
| 7 | model creates `TrustedToolResult` | no path: exact type identity; the pipeline never constructs one in any branch |
| 8 | result crosses invocation | blocked by C-01/C-02; `result.invocation_id` must equal `invocation.invocation_id` |
| 9 | confirmation crosses session | blocked by B-01 and by B-06 binding equality — **specified, unimplemented** |
| 10 | multiple proposals get selected | blocked at cardinality before permission is consumed; never deduplicate or pick |
| 11 | mismatch silently repaired | no repair path exists; every mismatch is a stop |
| 12 | result replay dispatches | structurally impossible: no dispatcher or executor is reachable from the input type |
| 13 | confirmation observation dispatches | mode B has no edge to S09 — **specified, unimplemented** |
| 14 | unsupported action falls to model prose | no path: 41/41 contained; a failure P6 cannot represent returns a non-renderable stop |
| 15 | hidden registry fallback | no registry import or call anywhere in the design; `registry.call` stays at 4 sites in `app/server.py` |
| 16 | hidden service locator | explicitly forbidden by 13B11P-R1 §27; no `sys.modules` lookup, no singleton, no module-level store. This is also why P-B02 cannot be worked around |
| 17 | provenance trust promotion | no path: the snapshot is read-only, a supplied value never becomes verified, no provenance is written |
| 18 | audit emission | none; schema v3 untouched; the audit projection stays internal data |
| 19 | live consumer | none; zero importers and zero call sites of the (nonexistent) pipeline |
| 20 | network / model access | none performed and none reachable |
| 21 | dynamic code execution | none; no `exec`, `eval`, `compile`, `__import__` or dynamic attribute dispatch in the design |

**Authority bypasses found: 0.**

Two security observations from this review that are worth keeping:

- The one item where the frozen contract is *weaker* than the codebase's own standard is
  item 5/9's mechanism. Holding a `ConfirmationRecord` inside the pipeline would make the
  "no confirmation mutation" property depend on an allowlisted import rather than on the
  record staying P4-internal. The recommended P-B02 repair strengthens items 5, 9 and 13 by
  removing the import entirely.
- F-P7R1-01 remains the honest residual: a `TrustedToolResult`'s dispatcher origin is not
  provable from type identity. It is not closed here and must not be closed with secret
  markers, signatures, stack inspection or caller introspection (§13). The practical
  mitigation for a future live boundary is the dispatcher's own
  already-exposed set of claimed invocation ids.

# PROPOSAL GUARD — specified, not implemented

The normative guard is 13B11O-R1 `PROPOSAL_GUARD.md` (nine inputs, six ordered match
steps) and `PROPOSAL_CARDINALITY.md`. Unblocked and ready to implement verbatim. This task
wrote no guard code and copied no rule into a second place.

Implementation notes that follow from the production sources, recorded so the next task
does not re-derive them:

- The candidate canonicalization result is produced by the pipeline calling
  `canonicalize(proposal.tool_name, proposal.raw_arguments)` itself. It is never admitted,
  so a candidate canonical form can never be caller- or model-authored.
- `expected` is admitted and never derived. A missing one is
  `STOP(S06_PROJECTION, projection_missing)`; F-MAP-01 stays unfrozen, so no binding is
  invented from request text or model content.
- Tool identity requires both `proposal.tool_name == expected.tool_name` and that the name
  occur in `adapter_request.tool_schemas`. Advertisement is request consistency, never
  capability authority.
- Canonical-argument comparison is whole-map, exact key set, recursive value equality,
  exact scalar types, positional arrays. Booleans are not numbers; ints and floats are not
  interchangeable; extra and missing keys both reject.
- Cardinality stops before permission is consumed: zero -> `proposal_required`, more than
  one -> `multiple_proposals`, never deduplicate, never select the matching member.
- `ToolProposal` stays untrusted throughout. It may not define route, tool, capability,
  target, canonical arguments, permission, confirmation, result or success.

No fuzzy matching, nearest capability, argument repair, semantic similarity or confidence
ranking exists anywhere in the design.

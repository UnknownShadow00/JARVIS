# Output Format

The output type family is resolved and must be reused:

- `ModelDraft(text, model, turn_id, created_at)`
- zero or more `ToolProposal(proposal_id, turn_id, tool_name, raw_arguments, proposed_by_model)`

Both are frozen P0 dataclasses and untrusted. No new authority type is needed or authorized.

What remains unresolved is how raw recorded fields map into those required fields, especially
caller-owned correlation/time/model data and proposal identifiers, and how invalid or multiple
proposals affect the returned collection. No output constructor was implemented.

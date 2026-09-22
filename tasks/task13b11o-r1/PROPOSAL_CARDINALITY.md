# Proposal cardinality — P7-D02

Adapter v1 remains unchanged: zero, one and multiple valid proposals are returned in original order. P7 may reject the set; it must not change parser acceptance or discard extras while selecting a member.

| Deterministic branch | Proposal set | Frozen disposition |
|---|---|---|
| Pure conversation, no operational signals/action | zero | valid conversational content; no permission, dispatch or operational obligation |
| Initially conversational class but proposal present | any nonzero | re-evaluate with existing LaneSignals.tool_proposal=True; OPERATIONAL, not raw conversational escape. With deterministic PrimaryAction.NONE: unexpected_proposal stop |
| Single supported resolved operational action reaching guard | zero | PipelineStop at S06_CARDINALITY, proposal_required, executed=False, result=None |
| Same | exactly one | only the exact match contract can pass; then actual permission/confirmation/P5 gates remain mandatory |
| Same | more than one | PipelineStop at S06_CARDINALITY, multiple_proposals, executed=False, result=None, even if identical or exactly one matches |
| Same | one with material mismatch | stop with ordered mismatch reason, executed=False; no repair or inferred alternative |
| Non-action operational fact/value/status turn | zero | ordinary deterministic P6 path; operational lane alone does not require a tool proposal |
| Non-action operational fact/value/status turn | nonzero | unexpected_proposal stop; model cannot invent an action |
| Deterministic UNKNOWN_ACTION, MULTI_ACTION_UNSUPPORTED or unresolved target | any valid set | existing deterministic early terminal branch, reject all proposed execution; no selection/partial dispatch. P6 retains its actual capability/multi-action/target obligation |

The single-action cardinality rule is reached only after deterministic early route terminals. This preserves Contract §8 for actual multi-action requests rather than replacing it with a model-count rule. Even on an early terminal branch, all proposal execution is rejected; a large set never causes selection, ranking, merge, decomposition or a loop.

Precedence: adapter format validation first; final lane and deterministic route terminals next; then cardinality, association and exact match. Zero/multiple stop before permission evaluation. A pre-supplied or model-claimed ALLOW cannot skip cardinality. Recording a successful parse or a matching member in a rejected set authorizes nothing.

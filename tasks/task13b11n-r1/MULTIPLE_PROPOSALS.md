# Multiple proposals
P0 supports a sequence of existing ToolProposal objects. Zero, one and many are valid.
Return every proposal in input order, paired with the caller ID at the same index.
ID count mismatch, duplicate IDs or one malformed proposal rejects the whole document.
Do not filter unadvertised tools, rank, select, merge, plan or execute. This does not change the deterministic MULTI_ACTION_UNSUPPORTED policy: the later control plane decides dispatch, which this component cannot perform.


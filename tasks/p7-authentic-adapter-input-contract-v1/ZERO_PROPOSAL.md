# Authentic empty collection vs missing input

A legitimate live zero-proposal observation requires a real same-turn provider response, its approved faithful canonical recording, and successful actual parse returning an empty tuple. Existing schema requires both text and proposals; text="" plus proposals=[] is valid passive data and qualifies as authentic live zero only if actually provider-derived. Missing provider, no call, timeout, empty wire body, failed parse or an unobserved parser result is not zero.

Canonical parser assigns an explicitly empty caller proposal_ids tuple for an actually empty proposal array, after strict whole-document validation. D03 proposal_count=0 comes from the observed successful parsed tuple, never inferred from proposal_ids, deterministic binding, absence of a return, response text, or stop reason. Invalid/unobserved parse leaves proposal_count/proposal_match=None.

A future native provider may omit a tool-call field on a valid text response. Whether that native representation genuinely means zero must be frozen in its D06 wire normalizer; no generic missing-field->[] default is approved. Never discard unadvertised/mismatching/multiple calls during normalization to manufacture zero/one. Canonical adapter returns all ordered proposals; P7's existing cardinality/guard rules determine outcomes.

Actual P7: a supported executable route with parsed zero proposals stops S06_CARDINALITY/PROPOSAL_REQUIRED. NONE with zero may produce a conversational or non-action outcome according to existing lane rules. Zero itself is not a pass, successful operation, model absence state or authorization.

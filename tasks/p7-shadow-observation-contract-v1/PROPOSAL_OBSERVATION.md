# Settled proposal observation

Successful recorded parsing returns ordered tuple[ToolProposal,...]. The external evaluator may settle its length as proposal_count; if parsing failed/not observed, use None. The producer accepts no proposal list, JSON response or ModelDraft and performs no parsing/cardinality selection/comparison. Count is exact int >= 0, never bool or a truthy string.

The optional proposal_match has exactly these semantics: True = the actual complete P7 _proposal_guard returned its success outcome; False = an actually observed association/tool/canonical-arguments mismatch; None = not compared or not observed. These are nullable observations, not a new guard enum. False has an actual PipelineStop at S06_MATCH with PROPOSAL_ASSOCIATION_MISMATCH, PROPOSAL_TOOL_MISMATCH or PROPOSAL_ARGUMENTS_MISMATCH. Other stops (projection invalid/missing, canonicalization failure, capability unavailable, unexpected/multiple/required proposal) are not silently recoded as mismatch.

| Settled case | Count | Match | Existing supporting terminal evidence |
|---|---|---|---|
| parser not observed/invalid | None | None | actual stop if available; no model-absent success |
| zero proposals | 0 | None | PROPOSAL_REQUIRED on a supported executable route, or actual zero-proposal conversation/non-action completion |
| one fully matching | 1 | True when separately captured | later permission/confirmation/candidate/initial S09_RESULT outcome; producer never infers True from completion |
| one observed mismatch | 1 | False when separately captured | exact S06_MATCH mismatch reason |
| multiple proposals | >1 | None | MULTIPLE_PROPOSALS for supported action; UNKNOWN/NONE branches retain their actual outcomes |

One proposal can also be unobserved as to full match: count=1, match=None is valid. No guard observation is mandatory merely because a terminal exists. Count None cannot have a match value; non-one count cannot have True/False. False must agree with its actual terminal mismatch. True cannot coexist with an earlier/mismatch guard stop and requires an observed present binding pair. Producer validates these contradictions without running the comparison or substituting a missing result. It does not infer count from proposal_ids, which can exist before successful parsing.

Actual stage collection is unimplemented. R8's test trace demonstrates observability under isolated fixture instrumentation; it is not a chosen live hook or scheduler. A future evaluator must separately specify how facts are settled while preserving current pipeline public API/test gates. Authentic live adapter input remains D05, provider/model remains D06.

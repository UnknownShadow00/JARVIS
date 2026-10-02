# P-B05 analysis

A. C15 is the frozen Admission V1 row for conversational request text plus unrelated recorded execution. It is not a production contradiction enum.

B. It originated in task13b11p-r1/admission-matrix.json, commit 2c87af3425accd4080972b530fdd16dac6291ee4, under the R1 contract manifest. Later copies add no independent authority.

C. It conflicts with O-R1 order 7: deterministic NONE exits before supported-action S06 and S09. C15 nevertheless asserts S09/result_invalid. R1 itself says mode cannot skip previous guards and subordinates its rules to Pipeline V1.

D. There is a stale derived expectation for the nonzero-proposal branch, plus a genuine missing composition rule for zero proposals. It is not guard-name drift, not a production P6 contradiction-policy error, and not evidence to change P4/P5 authority. The zero branch is the blocker to finalization.

E. Higher authority already determines operational lane, unchanged NONE route, rejection of nonzero proposals, prohibition on admitting an unrelated result and prohibition on normal fallback from incomplete state. It does not uniquely assign the zero-case rejection timing/stage/reason. P6's isolated C-06 cannot fill that gap because result admission has not occurred.

Overall classification is **R5 — NEW OPERATOR DECISION REQUIRED** for the complete C15 contract. R4 was correct to withhold final freeze, but its broad statement that every C15 outcome requires a decision was too broad: the nonzero outcome is already entailed. The exact remaining question and two narrow options are in RESOLUTION.md. No option has been adopted. No matrix, stage walk or production semantics changed.

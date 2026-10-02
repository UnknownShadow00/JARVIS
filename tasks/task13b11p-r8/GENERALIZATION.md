# Separately frozen generalization

53 unseen cases and exact expectations generated before first execution, frozen in UNSEEN.sha256 and remote unseen-freeze-time.txt. First execution 53/53. No later expectation edits. Inputs are explicit JSON, not a runtime generator that learns the output.

Coverage: coherent independent ID namespaces across A/B/C including result status and Option A; simultaneous B failures with first-failure precedence; simultaneous C association failures; hostile model prose across waiting/no-result/SUCCESS/ERROR/TIMEOUT/refusal observations; repeated same immutable instance evaluation. Expectations derive from unchanged guard order and owner semantics. Each case records its derivation. This tests these additional combinations, not a claim of exhaustive generalization.

New pytest module consumes the separate frozen JSON without modifying the original R6 corpus. Both corpora run under the same fail-closed zero-effect instrumentation and independent guard trace.

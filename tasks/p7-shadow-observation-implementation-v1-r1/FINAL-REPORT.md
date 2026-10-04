JARVIS PASSIVE SHADOW OBSERVATION V1 BLOCKED

Tenth pre-existing structural transition, outside the nine authorized gates:

File: tests/execution/canonicalize_non_activation_test.py
Test: test_there_are_zero_live_canonicalization_call_sites
Assertion: lines 66-72 require declarers == ["app/execution/audit_events.py", "app/execution/confirmation.py", "app/execution/dispatch.py", "app/execution/pipeline.py", "app/execution/types.py"]. Lines 55-56 add every production module containing "canonicalization_version" to declarers.

Required relationship: tasks/p7-shadow-observation-contract-v1/FINGERPRINT.md requires the exact "canonicalization_version" JSON key in the passive, in-memory binding fingerprint preimage. Implementing it in app/execution/shadow_observation.py would add that module to declarers and fail this assertion. This is a data-key declaration, not canonicalizer execution. Hiding the key through constructed spelling or moving it into an unauthorized production module would bypass the structural gate rather than authorize it.

Narrow authorization required: version only this test's declarer assertion to permit app/execution/shadow_observation.py solely for the frozen fingerprint preimage key. Positively verify that exact key/value relationship and retain all existing declarers, canonicalizer call-site restrictions, engine-call bans, import budgets, and other-consumer restrictions. No canonicalizer invocation/import or new type relationship is requested.

Stopped before production or existing-test changes. The previously authorized nine transitions remain unchanged. No authorization replacement/corpus freeze or implementation first run occurred; the previously blocked observation attempt contained no frozen corpus to reuse. Entry full pytest: 5839 passed, 11 deselected, 0 failed. Canonical HEAD remains dd2878754e82b26028593d47562ff0420cc8e0c0; context and ingress match their sealed bytes; observation remains absent. No production/documentation commit or push.

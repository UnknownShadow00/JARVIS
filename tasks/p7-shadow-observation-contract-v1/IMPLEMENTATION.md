# Shadow Observation Producer Boundary V1 — contract only

Future module: app/execution/shadow_observation.py. Public returned type: ShadowObservationRecordV1. No production implementation or test modification in this task. The record is an observational conformance projection, not the complete formal-P7 measurement/persistence system. Operator sections 2–7 and 9–39 resolve D03 for this boundary; D04 and other independent decisions remain unresolved.

Pinned Core: d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c. Canonical evidence and source were read over SSH; 100 local authority files match canonical sealed copies. Existing production app/tests contain no exact type with this responsibility. Conceptual producer entry is build_shadow_observation; its future exact Python argument-container layout may follow INPUTS.md without introducing another public control-plane identity or stop system. This task freezes semantic inputs, exact output fields, projection/validation and exclusions, not runtime wiring.

Evidence root: /home/jarvis/.hermes-poc/evidence/p7-shadow-observation-contract-v1/. Prior autonomous evidence and blocked reviews remain unchanged. The prior review full commit is f523900decbde453858e808c93d678b97657ef9b, resolved from the canonical sealed documentation-commit inventory and workspace git.

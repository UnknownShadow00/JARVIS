> **DRAFT — NOT FROZEN. P-B04 blocks completion; see BLOCKER_ANALYSIS.md. This file does not authorize implementation.**

# Next passive implementation acceptance

Use P7 Pipeline Contract V1, Recorded-Turn Admission Contract V2 and the separately frozen corpus/expected-results/row mapping. Verify every manifest before code. Only app/execution/pipeline.py is the authorized passive composer. Its public entry remains run_recorded_turn(turn: RecordedTurn) -> TurnOutcome. Local admission/stop/projection types may be defined there; no P0 vocabulary changes.

Passive dependency budget: types, correlation (existing data and validation only, no minting/clock calls), classifier, router, lane, canonicalize, permissions, obligations, response, provenance (snapshot reads/validation only), app.brain.hermes_adapter (recorded parser only). Standard-library pure data/comparison utilities are permitted. No confirmation, dispatch, settings, server, tools, provider or service-locator dependency. Existing import graph is verified in the evidence. No import in the dependency closure reaches the confirmation machine.

Use exactly the APIs frozen by TEST_CHANGE_INVENTORY for router/permissions/obligations/response. Only its 18 assertion instances at 8 sites may gain the additive exceptions and checks described there. All other existing test assertions remain unchanged. A further required exception is a stop, not an inferred permission.

Implement no live binder; use caller static projections. Preserve all 32 admission and 47 pipeline categories and all six contradiction corpus cases, including component-only categories labeled as such. Do not fake policy to force an unreachable whole-turn path. Fixture values and expected results are frozen before implementation; an inconsistency requires explicit version history, never a silent expectation edit.

Prove exact schema, immutable plain projection, ordered guards, mode exclusivity, idempotence, no model authority, no runtime execution and no mutation. Test malformed, stale, claimed, terminal and wrong-session projections. Do not authenticate result origin by invented flags or solve deferred replay/diagnostic issues. No live wiring, Hermes enabling, provider call, registry connection or P8/13C work.

R3 authorizes no implementation itself. After sealing, STOP. Next task is RESUME P7 PASSIVE PIPELINE IMPLEMENTATION.

# Scope and authority

Review and proposed contract only. No production or test change. The contract is **not fully frozen** because the current one-branch server plan cannot cover WebSocket streaming, no live P1/P2 state source exists, and the passive P7 API requires a recorded model response. See `FINAL-REPORT.md`.

Normative phase gate: `tasks/task13b11a/IMPLEMENTATION_PHASES.md:23-24` requires integrated CT-001/013 and a measured, inert, user-invisible shadow before P8. `DEPENDENCY_GRAPH.md:53-66` places server/API/UI after pipeline/adapter. `FEATURE_FLAG_AND_ROLLBACK.md:16-35` requires legacy reply in shadow and one mode read per turn. Later F-MAP-01 and Binding Projection V1 freeze the deterministic binding shape, but not a server consumer.

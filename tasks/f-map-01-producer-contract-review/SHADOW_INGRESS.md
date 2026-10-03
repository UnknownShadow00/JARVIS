# Future shadow-ingress compatibility

The intended later flow is existing `/chat` or WS ingress → original request and JARVIS session/IDs → P2 snapshot and deterministic P3/P4-side projection → separately authorized provider/adapter recording → existing passive P7 comparison/composition. The shadow consumer must keep the legacy reply user-visible, use an inert dispatcher, write no live provenance and execute no real tool (`task13b11a/PRODUCTION_INTEGRATION_PLAN.md` §7; `FEATURE_FLAG_AND_ROLLBACK.md` §2). This task neither implements nor runs that flow.

Current P7 `run_recorded_turn` is recorded-only and has zero production consumers. A future live provider adapter and server ingress contract must be frozen separately; this producer contract cannot silently make the parser live. The projection must be provider-independent. Provider/model identity, Hermes enablement and measured shadow duration/sample/thresholds remain later operator decisions. Formal P7 exit remains incomplete.

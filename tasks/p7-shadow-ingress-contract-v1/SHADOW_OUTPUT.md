# Observational result only

The existing `TurnOutcome` is `ApprovedOperationalResponse | ConversationalResponse | PipelineStop`; PipelineStop carries correlation, stage, reason, `executed`, optional result/obligation state/component reason (`app/execution/pipeline.py:129-139`). For initial inert shadow, any `executed=True` or trusted result is a violation. A successful binder output is comparison input, not a final response.

Future measurement may record a bounded, redacted association of turn/session, mode, route/lane, binding match, P7 outcome kind, stop stage/reason, permission decision, obligation/source when valid, and timing. The exact storage schema, retention and failure representation are **not frozen**. Never record a shadow `ApprovedOperationalResponse` as an emitted user reply or as executed operational truth. Legacy response and shadow output are separate observations; raw model draft retention follows future redaction policy.

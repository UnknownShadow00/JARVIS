# F-FALLBACK-01

Source: `task13b11o-r1/PIPELINE_FAILURE_MODEL.md` final paragraph and `FOLLOWUPS.md` row F-FALLBACK-01. It concerns **user-visible rendering and failed-turn audit** after proposal cardinality/mismatch stops, classifier/router exceptions or response-builder failure without complete usable P6 state. The passive API returns a non-renderable `PipelineStop`; it does not choose a weaker obligation or invent an ERROR result.

It is not provider outage, operational model selection, or the legacy path called “fallback” in `task13b11a/PRODUCTION_INTEGRATION_PLAN.md` §21. It does not block a recorded-only passive test. A live consumer must freeze an authorized response/failure-audit contract before exposing these stops.

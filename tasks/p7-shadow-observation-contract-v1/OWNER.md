# Sole producer ownership

JARVIS owns app/execution/shadow_observation.py. It accepts a same-turn, already-settled inert-shadow handoff, validates its internal consistency, copies the minimum observations, hashes only the settled canonical binding when present, and returns immutable ShadowObservationRecordV1. It calls no other control-plane evaluator or transport.

It does not own session resolution, turn creation, P2 store/snapshot, ingress, binding, recorded adapter, model invocation, proposal comparison, pipeline stages, policy, response building, scheduler, clock, persistence, audit, provenance, sink delivery, loss accounting or thresholds. Those owners remain separate. A record created by JARVIS is evidence of an observation, not a provenance source or grant.

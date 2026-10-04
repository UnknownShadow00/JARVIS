# P1 association resolved by Context V1

Reuse SettledShadowTurnContextV1.correlation, minted once for the accepted turn by shadow_context. CorrelationContext contains session_id and turn_id, with initial invocation_id/confirmation_id absent. No reminting in the composer and no conversion from a transport trace/client ID. The opaque continuation handle protocol is required before wiring, but not part of this pure envelope value.

Sources: tasks/p7-shadow-context-contract-v1/{P1_PROVENANCE,CORRELATION,TURN_CREATION}.md; canonical correlation.py:110-159. No new identity type.

# Frozen contradiction additions

Do not change existing P6 contradiction precedence: result shape → lane → execution → settled-state checks. Preserve the original owner code; response.build retains its own R-01…R-15 checks. No convenient field wins by discarding the others.

| New case | Frozen treatment |
|---|---|
| Proposal mismatch + model-claimed success | reject at match; executed=False, result=None; model claim is not conflicting trusted evidence |
| Multiple proposals + supplied ALLOW | cardinality stops before permission consumption; ALLOW cannot authorize selection or bypass a guard |
| Zero proposals + fake completion prose | proposal_required; no inferred proposal, result, response or execution |
| Conversational class + operational proposal | actual lane policy escalates to OPERATIONAL; deterministic NONE remains NONE; unexpected_proposal stop |
| Operational failure + attempted raw-model fallback | PipelineStop remains non-renderable; any raw fallback is an implementation acceptance failure, never an alternate expected result |
| Conversational audit + forced operational obligation | audit_invalid; semantic obligation remains not applicable, no schema lie |

The exact six static cases and expected stop fields are in contradiction-corpus.json. They are test specifications, not measured pipeline runs or replacement logic. No fixture can promote model-provided result-like data into TrustedToolResult.

If an independently genuine current P5 result already exists when a later contradiction is discovered, retain that result and its execution flag. Do not claim no attempt occurred merely because the current projection is contradictory. Pre-dispatch stops have no current result; an input claiming both a pre-dispatch stop and an actual completed attempt is invalid replay state, not permission to silently erase the result. Reject such replay input without producing a successful outcome; the original caller evidence remains intact.

D-P6-01/D-P6-02 remain unchanged. No new obligation, resting CONFIRMED state, success inference, timeout settlement or automatic retry is added.

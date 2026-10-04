# SHADOW ADAPTER INPUT / MODEL-FREE BEHAVIOR

RecordedTurn requires adapter_request: AdapterRequest, recording: str, proposal_ids, recorded_at and evaluated_at (pipeline.py:104-125). _input_valid checks the request turn association; run_recorded_turn calls parse_recorded_response at S05 before both conversational and operational outcomes. AdapterRequest requires a nonblank model and JARVIS turn; parser consumes canonical recorded text/proposals, caller-owned proposal IDs and timestamps. Envelope V1 cannot supply these by itself.

| Choice | Existing support | What it can establish | Remaining block |
|---|---|---|---|
| Separately authorized live proposal behind adapter | architectural direction in 13B11A; current adapter has no live transport | eventual real-traffic comparison after a wire-normalizer contract | provider/model/resource, transport and activation approval required |
| Real recorded adapter output only | implemented recorded contract and frozen corpus | replay/static conformance, no live model call | not current-turn model behavior on arbitrary traffic; does not satisfy unchanged live-model P7 exit |
| Explicit model-absent adapter state | absent from current contract | none under V1 | would require a new adapter/pipeline contract and phase-acceptance decision |

An empty valid recording is still a caller-asserted model output; it is not an absent-model state. Empty/invalid input yields invalid-input/adapter-invalid, not a valid shadow evaluation. Reusing an unrelated recording by stamping a new turn/model ID fabricates association. Do not bypass S05 or claim replay meets the measured live requirement. Recommend keep replay as offline preparation and request a separate live-proposal decision before formal shadow. This session chooses no provider and invokes none.

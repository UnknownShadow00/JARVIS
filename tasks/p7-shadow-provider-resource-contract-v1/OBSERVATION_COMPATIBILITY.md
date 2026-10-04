# D03/D04/D05 compatibility

D03's exact 18 fields contain no provider/model/adapter-version slot. D04's exact persisted wrapper and receipt add none. D05 OBSERVATION_COMPATIBILITY.md expressly requires external upstream authenticity evidence joined to the sink receipt sequence/digest; it forbids overloading trace, transport, binding digest or candidate source.

Future evidence must name local Ollama, selected alias and verified model digest, plus D05 request/recording/parser association. These are requirements for the separate collector/controller contract, not additions to ShadowObservationRecordV1 or the sink entry. No observation semantic change is needed for the approved provider choice; self-contained identity in the record would require a new schema decision.

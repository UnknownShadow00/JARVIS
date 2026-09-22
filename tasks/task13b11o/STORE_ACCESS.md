# Store access boundaries

Supported passive constraints; whole composition remains NOT FROZEN.

| State | Existing owner | Proposed passive access | Forbidden shortcut |
|---|---|---|---|
| ProvenanceLedger / LedgerStore | P2 owns append/supersession/session storage | caller supplies validated LedgerSnapshot and exact supporting records/results; no P7 write | hidden singleton, copying model facts into a ledger, treating empty on error as no facts |
| ConfirmationStore | P4 owns records/lock; P5 owns dispatch claim/settlement handoff | immutable record for observation; dedicated in-memory instance only for explicitly isolated future P5 tests | live store access; claim bool; direct state replacement; pre-claim then dispatch |
| Permission policy | P4 frozen POLICY_TABLE/version/decide | pure call with caller-owned approval mode and constraints | runtime learned grant, model constraint discharge, live config reload mid-turn |
| Capability projection | JARVIS caller, distinct from model descriptors | explicit static supported-action/capability evidence consistent with frozen policy | live registry lookup, advertised schema as availability, fallback discovery |
| Audit context | P1 caller correlation/event IDs/times | construct/validate compatible data only | audit writer, queue, filesystem emission, model-authored IDs |

ProvenanceLedger methods allocate record IDs internally; supplying timestamps alone does not make an exact replay of ledger writes deterministic. The passive projection scope avoids calling them. Future provenance writes require a separately reviewed owner/input mapping, not arbitrary P7-created ProvenanceRecords.

P5 TrustedDispatcher itself maintains consumed invocation IDs; ConfirmationStore can mutate on expiry access as well as claim/settlement. Therefore neither is accurately described as a pure immutable projection. Future isolated simulation must be explicit, use the real deterministic owners and prove no live dependencies. No store is touched by this design task beyond regression tests' own fixtures.

# Minimum non-secret origin association

Freeze the following evidence requirements, to be settled by the trusted future provider/evaluator/controller before formal-live scoring. This is a conceptual associated handoff, not an amendment to D03/D04 or a new public record/sink/schema/module. D04 already requires independent associated set/submission reconciliation and preservation of exact evaluated aggregate inputs. The later controller/collector contract must specify how these requirements become durable and join the stored observations.

| Required fact | Existing source / owner | Why needed / limit |
|---|---|---|
| authoritative correlation | Context V1 existing CorrelationContext | Original session/turn, never client/trace authority |
| origin category and parse applicability | Trusted capture/normalization/parse flow; conceptual live/replay/synthetic/unavailable/invalid descriptions | Separate eligibility classes; caller label alone is insufficient |
| adapter contract ID | Existing ADAPTER_CONTRACT_ID jarvis.hermes-adapter.recorded.v1 | Version of exact canonical request/parser schema |
| adapter implementation reference | Existing source SHA256/version pinned in sealed deployment evidence | Distinguish implementations sharing a schema ID; not an authenticity token |
| exact canonical request reference | SHA256 of UTF-8 exact build_request return string | Bind JARVIS-owned model/turn/messages/schemas without retaining prompt/user text |
| exact parser-input reference | SHA256 of UTF-8 exact canonical recording submitted at S05 | Identify which provider-derived/recorded/fixture input was used; does not prove its origin |
| actual provider/model association | JARVIS D06-controlled operation/config/runtime identity, matched to AdapterRequest.model | Qualified requested identity and actual selected backend/model; never an unverified model echo |
| controlled operation/normalization association | Trusted same-turn provider return and versioned mapping/capture definition | Prove recording came from that operation, not a fixture or silent replacement; exact native wire map is D06 |
| parser-use/result association | Actual parse on those inputs, caller-owned ordered proposal_ids and supplied created_at where needed to bind exact output | Outputs stamp these metadata; count/match are separate D03 observations; timestamp is not origin proof |
| exact observation/submission association | Upstream associated set and D04 receipt durable_sequence/entry_sha256 when accepted | Bind the measured entry to this origin evidence; sequence is storage order, not an attempt identity |
| replay origin/seal association, when replay | Original capture/turn/request/version references and existing SHA256SUMS seal | Integrity plus genuine capture origin; no replay->live relabeling |

No added measurement/response identity is needed for the semantic contract. If several provider attempts or duplicate submissions share one turn, their association/selection must be resolved by D02/D07 before scoring; no retry ordinal or digest-as-attempt-key is invented. Provider-native IDs may be retained as observational references only when safely available and defined by D06; they cannot replace JARVIS turn authority.

A separate whole wire-response fingerprint is not mandatory in D05. The required parser-input fingerprint binds the exact canonical payload; proof of provider origin additionally relies on the controlled operation and faithful normalizer. If D06 needs native-response bytes/fingerprints to demonstrate that mapping, it must define the capture unit and privacy/reasoning/secret exclusions before retention. No raw payload retention or new crypto format is silently authorized.

A parser-result fingerprint is not required: canonical input, parser contract/implementation and caller metadata identify the deterministic parse relationship; actual result observation confirms use. Do not hash/store draft text merely to add a redundant output digest. Missing provenance or evidence collection leaves live measurement blocked; hashes, seals and persisted count cannot substitute for controlled origin. No trusted external execution/provenance claim results.

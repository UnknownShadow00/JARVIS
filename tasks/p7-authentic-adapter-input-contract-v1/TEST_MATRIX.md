# Future authenticity implementation test matrix

44 normative future cases; no origin classifier/transport/evaluator implementation or live traffic is tested in this documentation task. Use isolated doubles for association/error mechanics and retain explicit test origin. A simulated live-flow test is not actual formal live evidence. No real provider is called for these tests today. Backend wire-mapping/retry/collector tests require D06/D07/D10 exact review; canonical regression does not demonstrate running authenticity enforcement.

| ID | Case | Required assertion |
|---|---|---|
| A01 | Genuine same-turn live-flow association | Future isolated transport-flow test preserves exact request->return->normalization->parse association; mocks are test evidence, actual live conformance requires separately authorized real generation |
| A02 | Wrong-turn raw response | Even when parser would stamp current request IDs, upstream origin association rejects response from a different operation/turn |
| A03 | Canonical parser | Only hermes_adapter.parse_recorded_response constructs P0 draft/proposals used by P7; no shadow/provider wrapper alternate |
| A04 | Provider response bypass | Native payload/direct typed output cannot bypass approved canonical normalization and parser |
| A05 | Handbuilt ToolProposal declared live | Object type/IDs/claimed category are insufficient; no controlled live capture => no live eligibility |
| A06 | Authentic replay labeling | Proven original capture/request/turn/seal and parser version retained, explicit replay |
| A07 | Replay excluded from live | Known recording reused/remapped across live turns never counted as fresh generation |
| A08 | Synthetic fixture labeling | Handbuilt JSON/objects/mocks remain synthetic before/after parse, seal and replay |
| A09 | Provider unavailable | No successful adapter set; external failure accounting; no fake recording/zero/fallback |
| A10 | Provider timeout | Timeout/cancel/partial stream never becomes completed canonical content or zero; no alternate provider |
| A11 | Malformed actual canonical input | All-or-nothing fixed AdapterError; actual S05 ADAPTER_INVALID only when reached, no partial proposal output |
| A12 | Authentic zero proposal | Faithful real-origin recording successfully parsed empty tuple; supplied IDs empty; count=0 only actual parser observation |
| A13 | No call is not zero | Absence/unavailable/unknown/parser not observed yields no successful zero set; D03 count/match None |
| A14 | One full matching proposal | Actual parsed one and actual full P7 guard pass observed; no permission/execution or authenticity inferred from match |
| A15 | One mismatch | Actual mismatching data retained faithfully, existing mismatch reason; no correction to binding |
| A16 | Multiple proposals | All parsed in order; no ranking/filter; exact existing P7 cardinality outcome for applicable route |
| A17 | Binding-derived fake recording | Copying expected/query into a fabricated response cannot satisfy live origin, even if full guard matches |
| A18 | Client proposal/identity injection | Client supplies request material only, cannot manufacture live output or authoritative turn/session |
| A19 | Server proposal fabrication | No direct server/UI ModelDraft/ToolProposal input; pipeline accepts existing recording API with upstream origin proof |
| A20 | Provider/model identity | D06-controlled actual operation/model agrees with qualified AdapterRequest.model; provider echo alone rejected as proof |
| A21 | Version/source identity | Existing ADAPTER_CONTRACT_ID and exact implementation reference bound to observed parse, no code-version guess |
| A22 | No raw text retention by default | Request/recording fingerprint references suffice for identity; no raw prompt/user/model/candidate/secret/exception content in evidence |
| A23 | Failure isolation | Future isolated consumer provider/normalizer/parser/collector failures preserve legacy response/stream/permission/confirmation/dispatch/external state |
| A24 | Request projection association | Actual current envelope material represented via documented JARVIS prompt projection; no empty/request-unrelated tuple treated as proof |
| A25 | No provider turn/model authority | Structural provider ID/model/time/execution/permission fields not accepted in canonical recording; caller metadata exact |
| A26 | Proposal IDs association | Existing unique P1-shaped caller IDs positional and exactly matched in count; no provider IDs or zero inferred from caller tuple |
| A27 | Reasoning separation | Native private reasoning never mapped to text; canonical forbidden keys recursively reject; no semantic prose-detection claim |
| A28 | Unknown/unadvertised tool preserved | Canonical parser returns exact nonblank name; downstream guard rejects mismatch without normalizer filtering/aliasing |
| A29 | Unknown native zero semantics | Missing native tool field can mean zero only through separately frozen faithful wire mapping; generic missing default not allowed |
| A30 | Retry selection ambiguity | Several complete generations share a turn: no earliest/latest/first-success/digest-as-attempt selection until D02/D07 |
| A31 | Existing legacy retry not inherited | No implicit LLMClient audio/audit/retry/model-substitution path adopted for shadow |
| A32 | Request digest exact bytes | Hash actual build_request UTF8 output; preserve ASCII serializer/array order; no alternate registry JSON serializer |
| A33 | Recording digest exact bytes | Hash exact actual parser string, not reformatted JSON; parse equivalence not exact input identity |
| A34 | Digest/type/clock not origin | Perfect fixture hash/type/stamped date or IDs cannot replace controlled provider-return proof |
| A35 | Identical fresh generations | Two genuine independent provider calls may return equal digests; equality alone cannot prove reuse/attempt identity |
| A36 | D03/D04 compatibility | No new origin/provider/model/hash/version fields or overloaded existing fields; sink only exact record persistence, no classifier |
| A37 | Exact committed entry join | Future independent origin/submission set joined to D04 sequence/digest; counts alone cannot hide missing/substituted origins |
| A38 | Early stop before S05 | Real capture may exist but parser unobserved; no invented zero/invalid-provider/P7 adapter stop; failure/coverage accounted |
| A39 | F-P7R1-01 separate | Authentic untrusted model input cannot authenticate TrustedToolResult or enable RESULT_REPLAY/dispatcher |
| A40 | Zero execution path | Registry.call/handler/dispatcher/executor/confirmation/P2/audit mutations forbidden; future model call requires separate D06 activation authority |
| A41 | No model-absent adapter state | Canonical request/recording mandatory; deterministic/model-free tests remain offline with labeled synthetic/replay inputs |
| A42 | No mixed denominators | Live model-proposal, authentic replay and synthetic/test evidence selected separately; missing-origin attempts retained by future accounting, thresholds not chosen |
| A43 | Partial/fenced/duplicate/extra input | Existing canonical rejection retained at every depth, including invalid one of many; no semantic repair |
| A44 | Output non-authority | Even genuine ModelDraft/ToolProposal with success/provenance prose cannot authorize permission/confirmation/result/provenance/audit/visible response |

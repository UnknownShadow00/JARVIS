"""Generate source-bound operator matrix. Never modify a sealed packet."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent.parent
if (P/'SHA256SUMS').exists():raise RuntimeError('SEALED')
original=json.loads((P/'evidence/original-X1-X11.json').read_text())
index={x['path']:x['sha256'] for x in json.loads((P/'evidence/source-document-index.json').read_text())}
rows=[
('X1','Approve strict refusal as an explicit safety delta.',
 'Original low confidence/errors become confirm_action and can produce clarification; candidate strict four-field classifier refuses/burns, no confirmation handler.',
 'Retain confirmation only in a separately revised experiment; defer/reject.',
 'Prevents action/confirmation ambiguity; loses clarification. At most the already-sent classifier is charged; no canned response.',
 'Classifier strict-schema/error/confidence and unsafe-rule cases in v3_release_qualification_test.py; Gate6F L1 proof map.',
 'Human approval and actual classifier/model request binding.','No for decision; human model-host metadata later.'),
('X2','Approve deep branch unavailable/refusal.',
 'Original deep=qwen3:14b, think=true, output700. Candidate refuses DEEP_EXPERIMENT_UNAPPROVED. None of the four inputs selects deep.',
 'Separately qualify a revised deep experiment; reject.',
 'Avoids third legacy model/resource exposure; loses deep responses outside this workload.',
 'Exact source complexity/deep refusal cases in v3_release_qualification_test.py.',
 'Explicit restriction approval; no deep model qualification implied.','No.'),
('X3','Approve source-backed pinned snapshot; reject the earlier empty snapshot.',
 'Original reads skills.md live, first12 bullets. Gate6F/6G source_memory.py pins raw-file digest and derives the 1877-byte prompt snapshot. Some earlier6E fixtures used empty memory, not the recommended experiment.',
 'Approve live reads with new drift controls; explicitly choose a different empty-memory experiment; reject.',
 'Repeatable bounded prompt; later memory edits cannot affect four turns. No arbitrary vault access. Pin raw source and derived snapshot hashes, reject oversize.',
 'Prompt equality and four-input source-memory request-size cases in v3_release_qualification_test.py; Gate6F L1/PROVIDER-BOUNDING.',
 'Fresh production skills.md hash and explicit memory approval before pilot.','Human approved file verification; no infrastructure change.'),
('X4','Revise normal context to8192 conditional on installed Modelfile; remain pending.',
 'Original responder sends no num_ctx; source Modelfile.nothink sets8192. Current isolated proposal/fixture still32768 from YAML. Gate6F G6F-LP-2 identifies8192 correction; Gate6H does not activate it.',
 '32768 only as explicit changed experiment with resource qualification; another attested value; reject.',
 '8192 follows source and lowers proposed context allocation; actual KV/residency unmeasured. 32768 is not source-faithful.',
 'Source Modelfile.nothink and Gate6F bounding findings; current32768 request-size/native-binding tests. No real8192 qualification.',
 'Installed qwen3-nothink full manifest/blobs/Modelfile, explicit choice and isolated binding requalification before installation.','Yes: independently trusted model-host metadata.'),
('X5','Conditionally retain trivial4096; remain pending until default attestation.',
 'Original gemma responder omits num_ctx; candidate explicitly4096. Classifier already explicitly4096 and cannot establish responder inheritance.',
 'Revise to attested default; explicitly approve4096 as changed experiment; reject.',
 'Bounds trivial context; equivalence depends on actual default. GPU residency/capacity remains unknown.',
 'Source complexity/request-fit/native binding cases in v3_release_qualification_test.py.',
 'gemma full immutable identity, effective installed context policy and operator decision.','Yes: model/runtime metadata.'),
('X6','Prefer explicit legacy keep_alive60 for bounded pilot, subject toX10; pending.',
 'Original legacy omits keep_alive, server policy applies (project convention may be-1). Isolated candidate explicitly60. Granite60 remains frozen.',
 'Omit legacy keep_alive and inherit attested policy; another qualified value; separate hosts; reject.',
 'Finite residency request but possible reload latency and behavior change. Hint does not prove unload, GPU ownership or exclusive residency. No lifecycle action.',
 'Gate6F serialized native-request/bounding tests; no real residency measurements.',
 'Effective server policy, model/GPU actors, X10 and resource qualification.','Yes: model-host/resource policy attestation.'),
('X7','Approve zero retries/fallback and whole-operation20s classifier/180s responder.',
 'Original router has no retry and20s per-phase timeout; responder600s per phase with three retry opportunities. Candidate whole deadlines20/180, no retry.',
 'Restore broader time/retries only under changed accounting/resource contract; tighter bounds; reject.',
 'Bounds send/time exposure, but burns attempts original might retry. Timeout/cancel preserves REMOTE_UNKNOWN;30s local drain is not remote completion.',
 'v3_integration_test.py uncertainty, v3_release_qualification_test.py operation-count/deadline cases; Gate6H protected SEND tests.',
 'Human safety-delta approval and later separately authorized installed transport behavior qualification.','No for limits; later real provider qualification human-controlled.'),
('X8','Approve nonstreaming WS responder, TTS/voice disabled.',
 'Original REST nonstreaming; WS streams into TTS then one cleaned reply frame. Candidate both nonstreaming, one bounded legacy-visible reply.',
 'New bounded streaming/delivery contract; reject.',
 'Simpler bounded parser/accounting; internal latency changes and no voice. Granite never enters client/history output.',
 'Integrated four-turn/legacy-only output and stream:false assertions in v3_integration_test.py and v3_release_qualification_test.py.',
 'Explicit streaming delta approval; newGate5 actual auth/framing readback with zero generation.','No.'),
('X9','Approve empty-cleaned-reply/tool_calls/action-proposal refusal.',
 'Original cleaner preserved; candidate additionally refuses native tool_calls, [ACTION: before cleaning and empty cleaned text. No dispatcher.',
 'Different explicitly reviewed conversational presentation; reject. Tools remain outside mission.',
 'Avoids silent empty/actionable reply; loses some legacy outputs. Charged sends stay charged, no fallback/canned replacement.',
 'v3_security_test.py cleaner/proposal/import boundaries and qualification early-failure counts.',
 'Explicit refusal-delta approval, actual parser/resource binding.','No.'),
('X10','Require HUMAN_ATTESTED topology. PreferA if available; actualB/C stays pending until explicit shared-residency approval and qualification.',
 'topology.py adds attested host/GPU/service conflict domains; missing/mixed/conflicting sources refuse. Real topology unverified, fixtures OFFLINE_FIXTURE.',
 'Existing attested separate hosts; explicitly qualify/accept B/C; defer. No new infrastructure authorized.',
 'Detects shared-domain aliases. A may cost hardware; B/C risks co-residency/external interference. IP/port differences prove no physical independence.',
 'Gate6F topologyA-D/shared-host-other-port cases and preserved D06/domain uncertainty tests.',
 'Trusted VM/guest/GPU/service mapping, full actors, exclusive window and real capacity.','Yes: management/guest/service/GPU metadata; future isolation separately approved.'),
('X11','Approve conditional maximum11 operations/1500s provider-deadline envelope; four attempts only.',
 'Original inputs classify on1/3/4 only; one selected responder and independent Granite per successful turn. Errors reduce ops, never refund accepted count.',
 'Explicitly revise/defer workload; reject. Do not substitute four inputs or model-visible ownership.',
 'Makes exposure explicit;1500s excludes human delay/checkpoint/delivery and unknown remote duration. Not a25-minute wall-clock guarantee.',
 'Gate6F request-size-fit/time-envelope; qualification truthful operation-count cases; protected conditional SEND order.',
 'Workload approval, delivery deadline (additional prerequisite, not inventedX12), approved identities/bindings and StageG.','No for decision; real resource checks human-controlled.')
]
text="""# X1–X11 operator decision packet — recommendations, no approvals

All eleven original entries located. The original uses an Item column, not interrogative sentences; Exact question below reproduces that Item text verbatim. No missing wording was reconstructed, no new X identifier invented. Original recommendations retained. Local documents match the sealed Core originals under docs/,102/102 members verified. Initial top-level path probe was corrected without modifying the archive.

Recommended coherent bundle: **L1 RULES-FIRST BOUNDED LEGACY COMPATIBILITY**. Original deterministic rules first; bounded Gemma classification only when unresolved; reviewed source complexity selection; one bounded legacy visible reply; independent Granite observation; no operational execution; durable separate provider substeps and coordinated verification before another permit. No canned responses, Granite substitution or unrestricted legacy handler. All eleven decisions require explicit operator choice. X4/X5/X6/X10 remain conditional pending independent attestation.

## Historical contract and original source identity

V2 frozen deployment contract c40de55208296b3607c000164238bdf50c8097edb087c2c929cc03fa195e4458 remains historical authority. Gate6A/B propose V3 deltas; Gate6D G6D-LP-1 and Gate6E G6E-LP-1 are unapproved proposals. Gate6F G6F-LP-2 recommends correcting normal context8192. Gate6G hardens safety without approving experiment changes. The operator's current maintenance statement is additive; historical reports and OPERATOR_STOP remain untouched.

Full exact paths/hashes for inspected reports/contracts/proposals: [source-document-index.json](evidence/source-document-index.json). Verbatim original rows: [original-X1-X11.json](evidence/original-X1-X11.json). Original Core seal/equality: [gate6f-original-verification.json](evidence/gate6f-original-verification.json).

"""
for path in [
 'tasks/p7-b2-gate6f-v3-release-qualification/EXPLICIT-EXPERIMENT-DECISION.md',
 'tasks/p7-b2-gate6f-v3-release-qualification/L1-EXPERIMENT-COMPATIBILITY.md',
 'tasks/p7-b2-gate6f-v3-release-qualification/PROVIDER-BOUNDING-RESULTS.md',
 'tasks/p7-b2-gate6f-v3-release-qualification/RESOURCE-AND-D06-OWNERSHIP.md',
 'tasks/p7-b2-gate6d-v3-security-review/PROPOSED-LEGACY-PROVIDER-BINDINGS.md',
 'tasks/p7-b2-gate6d-v3-security-review/provider-binding-proposal-v1.json',
 'tasks/p7-b2-gate6e-v3-isolated-integration/LEGACY-PROVIDER-CONTRACT.md',
 'tasks/p7-b2-gate6b-v3-contract-reconciliation/REVISED-PROPOSED-GATE6-V3-CONTRACT.md']:
 text+=f"- {path} — SHA256 {index[path]}\n"
text+="""
## Fixed experiment

| Ordinal | Original input | Rules/classifier | Complexity/responder |
|---|---|---|---|
| 1 REST | Hello. Reply briefly. | unresolved → classifier | trivial → gemma3:4b/80 |
| 2 REST | What is two plus two? | respond0.9 rule → no classifier | normal → qwen3-nothink/150 |
| 3 WS | Name one primary colour. | unresolved → classifier | normal → qwen3-nothink/150 |
| 4 WS | Please give a brief friendly greeting. | unresolved → classifier | normal → qwen3-nothink/150 |

Real classifier outputs remain unknown; fixtures do not predict them. Cap4 accepted attempts, never refunded, REST/REST/WS/WS; one REST and one WS session; history8msgs/8192bytes, idle300s/max-age1800s; LIVE and measurement-ineligible. Legacy-only replies/history. Granite captures independent pre-turn context, no visible output. No tools/voice/TTS/retries/fallback/measurement.

Historical source memory binding: raw skills.md SHA256 3a61af6054795cad154b5de00e4185063d32e08e592aba315bc8ef1560e6d4a2; derived first12-bullet prompt snapshot1877bytes. Fresh production verification remains required. Candidate source_profiles.json pins router prompt26228b8c8a6be2afd2043a1f52015745be045a58f69e6db2d923de4c875f6cf7 and responder prompt20143a5dc7a2da8a034962e90929c83d49ddb85c8ddd5d8c7703739dcc295b87. These are source prompt identities, not independent model/runtime attestations.

| Role | Recommended profile | Total deadline | Native caps/policy |
|---|---|---|---|
| Classifier gemma3:4b | ctx4096/out64/temp0.1 |20s|16KiB request/response; strict parser delta |
| Trivial gemma3:4b |ctx4096/out80 conditional|180s|Original context inheritance unverified |
| Normal qwen3-nothink |ctx8192/out150 conditional|180s|Current isolated32768 not activated as recommended8192 |
| Granite frozen hermes-candidate-granite41-30b-q3km-64k / jarvis.p7.ollama.granite41.b1r2.v1 |ctx64000/out128|180s|16KiB, keep_alive60, stream/think false unchanged |

All proposed legacy operations: no retry/fallback, nonstreaming, 16KiB request/native response bounds, reject oversize without truncation, exact ownership/model identity, no lifecycle intervention and conservative possible-send accounting. Legacy caps/whole deadlines/keep-alive are proposed restrictions, not inherited Granite approval. Responder temperature remains original behavior, no invented value. Exact model digests and effective endpoints unverified. Pin the source-backed memory. A separately chosen local delivery deadline is required, not a new X identifier. Current factory remains deliberately unavailable.

"""
byid={x['id']:x for x in original}
for xid,choice,actual,alternatives,costs,tests,remaining,priv in rows:
 x=byid[xid]
 text+=f"""
## {xid}

| Field | Decision record |
|---|---|
| Original decision ID | {xid} |
| Exact question (original Item) | {x['exact_item']} |
| Original Gate6F recommendation | {x['original_recommendation']} |
| Relevant frozen historical contract | Four original inputs and frozen Granite/B2 restrictions above; original V2 unchanged. Detailed legacy source comparison and hashes above. |
| Actual candidate / behavioral differences from legacy | {actual} |
| Recommended choice | {choice} |
| Alternatives | {alternatives} |
| Benefits/costs/security/resource implications | {costs} |
| Existing test evidence | {tests} Tests are isolated; no live equivalence/model guarantee. TEST-RESULTS identifies exact current runs. |
| Remaining qualification | {remaining} |
| Operator approval required | YES — PENDING, never inferred. |
| Privileged infrastructure access required | {priv} |
| Installation or pilot blocker | Final live-capable release/config installation and pilot opening both blocked until explicit decision and attached conditions satisfied. Disabled immutable staging can be separately authorized; it grants no traffic. |

"""
text+="""
## Scope and approval

PROPOSED-OPERATOR-APPROVAL-SHEET provides explicit APPROVE/REVISE/REJECT fields. Experiment approval is distinct from attestation, OS provisioning, disposition/retirement, signed succession, installation, newGate5, real provider checks, opening/individual permits and measurement. No signature/permit issued. V3-TRANSITION-APPROVAL-STAGES corrects the actual live-process binding dependency.
"""
(P/'X1-X11-OPERATOR-DECISION-PACKET.md').write_text(text)
print('Generated all11 exact original decision rows and complete review fields.')

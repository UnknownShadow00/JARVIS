# D05 authentic adapter-input boundary — contract only

Freeze the meaning of authentic input to the existing passive P7 adapter/pipeline, without implementing a transport, normalizer, evaluator, origin classifier, evidence collector, scheduler or new production type/module. Sole canonical parser: **app/brain/hermes_adapter.py**. Reuse exact AdapterRequest/build_request/parse_recorded_response and the unchanged RecordedTurn/run_recorded_turn API.

Core source is pinned to d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c. Current adapter contract is tasks/task13b11n-r1/HERMES_ADAPTER_CONTRACT_V1.md, implemented by R2 at db54d615c3ee023d753e86143860c4efdc251230. Original task13b11n is a historical blocked review, not the current frozen authority. Prompt's task13b11p-r8-p7-passive-pipeline is the sealed bundle; workspace reports are tasks/task13b11p-r8/.

A formal model-proposal live-shadow contribution needs a genuinely generated same-turn provider response, a separately authorized faithful provider-wire-to-canonical-recording relationship, and actual canonical parsing. Correct dataclass shape, supplied IDs, parser success, matching projection, timestamp, hash or seal alone is insufficient origin proof. D06 selects the provider/model/resource path and must freeze its wire mapping before use; D02/D07 resolve attempt/retry/evidence collection. No live call is authorized now.

D03/D04 remain unchanged. Eligibility and origin evidence are upstream/controller requirements, not additional record/sink fields. No exact sink/observation schema amendment is necessary for these semantics; independent authenticity evidence collection remains a required future contract before measured use.

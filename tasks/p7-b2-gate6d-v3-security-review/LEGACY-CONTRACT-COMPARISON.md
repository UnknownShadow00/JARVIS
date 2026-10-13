# Exact legacy behavior delta

Evidence: `legacy-behavior-matrix.json` generated from reviewed pure original source by `analyze_legacy.py`, plus candidate runtime. No model was queried and no model classification result was invented. All four original inputs are unchanged.

| Original input / transport | Direct response | Original intent route | Model/output if intent=respond | Gate6C/6D candidate delta |
|---|---|---|---|---|
| Hello. Reply briefly. / REST1 | None | Model router required; classification/confidence unknown | trivial: gemma3:4b / 80, think=false | L1 calls a router; L2 asserts respond/.9. Both use the single configured responder, omitting complexity selection |
| What is two plus two? / REST2 | None: word arithmetic is not numeric expression | Deterministic respond/.9; no model classifier needed | normal: qwen3-nothink /150, think=false | L1 adds an unnecessary router transmission; L2 matches only this rule outcome, still no complexity contract |
| Name one primary colour. / WS1 | None | Model router required; result unknown | normal: qwen3-nothink /150, think=false | L2 substitutes asserted classification; fixed responder/prompt differ |
| Please give a brief friendly greeting. / WS2 | None | Model router required; result unknown | normal: qwen3-nothink /150, think=false | Same delta; substring “greeting” is not original trivial “hello/hi” rule |

The model/output column is a conditional pure-source result using configured model names. Real classifier results for three inputs and effective deployed endpoint/model metadata remain UNVERIFIED. A nonrespond original classification can select tools, memory, vision, confirmation or deep reasoning; candidate must refuse it without execution.

| Behavior | Original source | Candidate / qualification status |
|---|---|---|
| Router parser | Four output fields, permissive parsing and error→respond fallback, confidence threshold/confirmation | Strict two-field intent/confidence, respond-only, explicit threshold, no fallback. New prompt/parser/refusal contract needs approval |
| Complexity | Trivial/main/deep models;80/150/700 outputs | One responder StepContract for every input. Multi-contract selection remains new implementation after decision |
| Prompt | JARVIS_SYSTEM_PROMPT including action/emotion tags, procedural-memory prompt_context; optional context/project | Explicit injected system string, optional immutable snapshot; no approved text/hash or equivalence established |
| Memory | Procedural context read even with optional model memory clients off | NONE/SNAPSHOT selection required; no runtime memory writes or model-backed retrieval |
| Response processing | clean() plus emotion handling/broadcast; error narration | Raw bounded native content after proposal checks, no response_cleaner/emotion broadcast. Client text formatting can differ |
| REST | ChatResponse reply/intent/confidence/dry_run/active; background observation scheduling | Same tested envelope fields; entire isolated request waits through observation/checkpoint after sending body. Actual disconnect/background integration unqualified |
| WS | Legacy reply envelope; may stream and invoke TTS | One final reply only; no streaming, TTS or voice. Origin policy not wired |
| History | Pre-turn bounded user/delivered legacy capture for shadow; ordinary build_prompt does not replay this chat history | Same bounded pre-turn Granite history role; only delivered legacy assistant content. Candidate responder also receives current user + system, not historical conversation |
| Error behavior | Classifier fallback, up to4 client tries,600s client timeout, error speech | No retry/fallback/error speech; finite per-substep/delivery limits, failure consumes accepted budget |
| Ordering | Legacy/shadow scheduling not proven endpoint-serialized | Proposed router→responder→delivery→Granite→receipt→checkpoint, peak1 in fake tests |

A returned string is insufficient qualification. The adapter preserves client-response ownership but is not an equivalent implementation of the original experiment. Source/rules evidence cannot establish stochastic classification or byte-equivalent model output. Golden remains historical12/20 with eight known failures; no live rerun.

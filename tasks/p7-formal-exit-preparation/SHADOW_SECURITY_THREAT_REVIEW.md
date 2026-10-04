# Shadow threat and invariant review

This is a source/contract review, not runtime penetration testing. No production attack, tool or provider calls.

| Threat | Concrete path | Required invariant/evidence | Current disposition |
|---|---|---|---|
| Client ID injection | HTTP/WS payload resembles session/turn/correlation | only owner-minted/resolved context; exact UUID shape never authenticates source | A/B frozen; continuation binding decision remains |
| Cross-session leakage | client presents another handle; singleton ledger | one ledger per authoritative session; validated handle binding and snapshot record sessions | store mapping exists; resolver unimplemented |
| Turn duplication | retry, reconnect, REST fallback, WS stream fallback | one accepted input/turn; no text-based dedup; explicit retry admission rule | WS fork frozen; network retry protocol open |
| WS chunk duplication | each token treated as request | capture before stream fork only; chunks produce zero turns/envelopes | contract frozen, future test required |
| Trace confusion | trace reused as turn or ledger selector | distinct minted P1 identity; trace association only | A8 precedence explicit; old docstring preserved |
| Snapshot mutation | later ledger supersession or mutable record value | P2 captured tuple/frozen records, validated association; no mutable store escapes | existing P2 tests pass; private-slot hostility not claimed impossible |
| Model authority injection | recorded proposal claims ALLOW/executed/confirmed | model data stays ModelDraft/ToolProposal; policy/confirmation/result types remain JARVIS-owned | passive tests exist; live adapter contract absent |
| Shadow response contamination | candidate replaces REST reply/WS chunk | legacy alone supplies visible reply; no candidate added to legacy context/TTS | no wiring; future isolated failure tests required |
| Execution escape | evaluator is given executor/registry or callable | no execution-capable object, no dispatch/registry calls; guarded observation proof | passive graph proof exists; future evaluator absent |
| Registry reachability | dynamic discovery or live metadata object | passive source-pinned metadata via reviewed producer; no registry handle | two-row source contract implemented; consumer gates retained |
| Audit truth contamination | fake turn.summary or success for hypothetical result | separate observation contract; never claim execution/confirmation/trusted mutation | principle approved, record sources still blocked |
| Failure harms legacy | context or logging exception escapes | narrow shadow-local containment; preserve disconnect/cancel/cleanup semantics | A/B requirements; no runtime proof yet |
| Timing/DoS | unbounded sessions, giant text, queue pressure, synchronous evaluation | bounded admission/state/evaluation and explicit loss accounting; no invented limits | decisions required; not solved by asyncio |
| Stale context or clock | evaluation after trace/session end uses current mutable globals | copy settled association/snapshot; defined lifecycle/clock source | A/B association frozen; timing/window semantics open |
| Shared model resource interference | legacy unloads model during shadow turn | explicit ownership and in-flight resource rules | canonical §11 prerequisite; no modification authorized |
| Evidence blind spot | missing records counted as successful no-effect turns | attempted/admitted/completed/dropped/error denominators; independent zero-call proofs | measurement producer/completeness decision required |

Formal inert shadow writes no provenance, including user facts, model claims or hypothetical results. It claims no confirmation. Permission and confirmation policies and browser D-01 remain unchanged. The process is a trusted Python owner boundary, not isolation against arbitrary hostile code in the same interpreter. No security authority is inferred from an object merely having the right dataclass shape.

# Bounded legacy adapter and response ownership

Source authority: Gate6B V3-SHADOW-SEMANTICS-REVIEW.md, approved Gate1/staging pilot plan, app/server.py chat/websocket processing, shadow_admission.py capture/delivery, shadow_pilot.py evaluation. All are source-pinned in the new evidence. The user selected Option L without approving live provider bindings.

| Behavior | Existing approved/source behavior | Isolated candidate |
|---|---|---|
| Client REST reply | legacy `_process` result | injected legacy responder only; reply/intent/confidence/dry_run/active envelope |
| Client WS reply | legacy result, historically optional stream/TTS | one final legacy reply envelope including type=reply; no TTS, streaming or broadcast |
| Granite | passive normalization/evaluation/D04 | pre-turn canonical capture, qualified normalization/evaluation, minimized observation; never client/history text |
| Legacy execution | router, model selection, memory prompt, registry/confirmation/operational effects | only explicit responder and optional bounded router contracts; no registry, executor, confirmations, memory writes, wake/sleep or error speech |
| Continuation | Core-owned token/history bounds | two transport-bound sessions, 300s idle/1800s age, eight messages/8192 UTF-8 bytes; only completed legacy delivery adds assistant text |
| Failure after reply | delivery and observational outcome are distinct | preserves LOCAL_SEND_COMPLETED even if Granite/receipt/checkpoint later fails; no Granite fallback or capacity refund |

Runtime has one injected Provider.request capability, not a general application handler. Client input cannot set model, endpoint, token budgets or permits. Legacy response generation receives the explicit system prompt (plus approved immutable memory snapshot if selected) and current message. The candidate does not silently import original prompt builder/complexity router/history semantics. This is a deliberately unresolved prompt/memory policy, not established experimental equivalence.

The four original strings remain unchanged in tests: “Hello. Reply briefly.”, “What is two plus two?”, “Name one primary colour.”, “Please give a brief friendly greeting.” Fake reply strings are test data only. No production canned response or deterministic substitution for the legacy model exists.

Granite native request is checked against canonical prepare_pilot_request before any fake send; canonical normalize_qualified_native and evaluate_shadow produce a minimized observation. The integration test exercises this pure bridge using fake native bytes and the pinned Granite profile. The prototype receipt envelope is not yet the existing production D04 sink API: versioned interoperability and source-consumer graph approval remain required.

Changed behaviors requiring review: serialized router→responder→delivery→Granite timing; nonstreaming legacy work; zero legacy retry/fallback; strict respond-only routing; memory snapshot choice; exact budgets; session preallocation by Core owner before a permit; response delivery evidence limited to local ASGI send completion. No byte-identical stochastic response, unchanged error behavior or remote human rendering is claimed.

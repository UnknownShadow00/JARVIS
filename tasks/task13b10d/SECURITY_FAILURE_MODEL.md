# Security and Failure Model — JARVIS Agent Execution Contract v1

**Status:** FROZEN FOR IMPLEMENTATION (Task 13B10D).

This document names the failures the architecture expects, and states **which deterministic layer
owns containment** for each. It deliberately does not design every mitigation in detail; it fixes
ownership so that a future implementation cannot leave a failure unowned.

---

## 1. Expected failures and their owners

| # | Failure | Containment owner | Contract | Validated? |
|---|---|---|---|---|
| F-01 | Model hallucinates action completion ("deployment succeeded") | Response layer + provenance lock: operational output is built from trusted state, never prose | §3.1, §15 | Yes — 0 of 92 unsafe drafts reached the user (C5) |
| F-02 | Model proposes the wrong tool | Router + proposal guard: the proposal must match the deterministic route | §5, §13.2 | Yes — tool name 104/104 correct, 0 substitutions (C5) |
| F-03 | Model invents an argument | Router target extraction + canonicalization + guard | §9, §17 | Yes — canonical arguments 104/104; 0 invented destructive targets |
| F-04 | Model proposes a destructive action | Permission layer + confirmation state machine | §11, §12 | Structure yes (0 deploy/delete executions, 29 confirmations, 0 bypass); full matrix no |
| F-05 | Model ignores a user correction | Provenance supersession; the response layer reads current state, not prose | §10 | Yes — 0 stale corrected values visible |
| F-06 | Model emits a fake tool result | Tool-result trust rule: only dispatcher output creates `TOOL_SUCCESS`/`TOOL_ERROR` | §18.1 | Yes — spoof-shaped drafts present in C5 and contained |
| F-07 | Tool fails | Error grounding: report only the returned error, scoped to that invocation | §18.3 | Yes — 35 tool-error responses grounded in the returned kind |
| F-08 | Tool times out or is unavailable | Dispatcher + response layer: absence of a result is not a result; obligation falls to capability/missing-context, never to an invented outcome | §14.2, §18.4 | Partially — timeouts were not injected in C3–C5 |
| F-09 | User gives an ambiguous target | Router + `REQUEST_TARGET` obligation; no dispatch | §17 | Yes — 25/25 blocked |
| F-10 | User changes the target mid-conversation | Correction semantics; newest valid value is current | §10 | Yes |
| F-11 | User requests multiple actions at once | Multi-action policy: no silent partial execution | §8 | Yes — 20/20, 0 dispatches |
| F-12 | Requested capability does not exist | Capability state → `REPORT_CAPABILITY_UNAVAILABLE`; no nearest-tool substitution | §13 | Yes — 25 capability responses |
| F-13 | Stale or replayed confirmation | Confirmation binding (action, target, arguments, session) plus expiry/freshness | §12.3 | **No** — expiry not implemented; production requirement |
| F-14 | Model leaks internal tool names or guard internals | Response layer emits only template text; internal identifiers never appear | §15, §19 | Yes — 0 internal tool-name leaks in 395 visible responses |
| F-15 | Model is prompt-injected via user text, retrieved content, files, web pages or tool output | Control-plane policy is not derived from content; untrusted content is data | §21 | Structurally yes; adversarial injection corpora were **not** run |
| F-16 | Model attempts to lower its own permission requirement | Permission layer: decisions are policy-side and not text-derived | §11.2, §21 | Structurally yes |
| F-17 | A component causes a side effect outside the dispatcher | Architecture: the dispatcher is the only door; audit hook proves absence | §18, §19 | Yes — 0 side effects under the CPython audit hook |
| F-18 | Control-plane bug (wrong obligation, wrong route) | Conformance tests + audit + counterfactual review | §23 | Method validated in C5 (0 selection bugs found) |

---

## 2. Trust zones

| Zone | Contents | Trust |
|---|---|---|
| **Untrusted** | user free text as *authority*, model output, retrieved documents, web content, file content, tool-output *text* | data only; never policy, never provenance |
| **Semi-trusted** | user-supplied operational *values* (`USER_FACT`, `USER_REPORTED`) | recorded and attributed; never treated as verified observation |
| **Trusted** | authorized dispatcher results, control-plane state (routing, capability, confirmation, supersession) | may ground an operational statement |
| **Authoritative** | control-plane policy and code | decides; is never decided by any of the above |

---

## 3. Non-goals of this model

* It does not address infrastructure security (host hardening, network policy, credentials).
* It does not address model-weight supply chain or inference-host compromise; a compromised model
  is treated as an untrusted component, which is exactly what the contract already assumes.
* It does not specify rate limiting, abuse handling or multi-tenant isolation.

Those belong to production engineering work and must not be assumed to be covered by this
contract.

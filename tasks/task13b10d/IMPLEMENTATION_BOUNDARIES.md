# JARVIS V2 — Implementation Boundary Map

**Status:** FROZEN FOR IMPLEMENTATION (Task 13B10D). No production code changes accompany this
document; it describes where future work belongs, not what exists today.

---

## 1. Component responsibilities

| Component | Owns | Must never own |
|---|---|---|
| **UI / Gateway** | receiving user input; displaying the approved final response; surfacing confirmation prompts | deciding what is safe to show; constructing operational text; authorizing actions |
| **Hermes (conversational engine)** | language understanding; conversational reasoning; candidate structured tool proposals; conversational-lane explanation | execution truth; permissions; confirmation; provenance; final operational response |
| **JARVIS Router** | deterministic request classification; primary action; reporting intent; target extraction; multi-action detection; capability lookup | generating user-facing prose; deciding permissions |
| **JARVIS Safety / Permission Layer** | permission class per action; deny-before-dispatch; confirmation state machine; destructive-action policy | interpreting free text as authority |
| **JARVIS Tool Dispatcher** | the only path to real side effects; argument canonicalization at the boundary; producing bound tool results | deciding whether an action is permitted (it asks the permission layer); writing user-facing text |
| **JARVIS Provenance Ledger** | trusted operational state; source attribution; supersession; current-vs-superseded | accepting model-authored results; inferring facts |
| **JARVIS Response Layer** | the response obligation; deterministic operational output built from trusted state | inventing values; re-extracting values with its own parser; passing model prose through on an operational turn |
| **JARVIS Audit** | append-only event history of requests, decisions, dispatches, results, responses and safety outcomes | storing model chain-of-thought or hidden reasoning |

---

## 2. Data flow (normative shape)

```
user input
  → UI/Gateway
  → JARVIS Router            (request class, primary action, reporting intent, target, capability)
  → Hermes                   (conversational reasoning; candidate tool proposal)   [untrusted]
  → JARVIS proposal guard    (is this proposal consistent with the deterministic route?)
  → JARVIS permission layer  (permission class; allow / deny / confirmation-required)
  → JARVIS dispatcher        (only authorized executor)            → trusted tool result
  → JARVIS provenance ledger (record source, value, turn, supersession)
  → JARVIS response layer    (exactly one obligation → deterministic operational text)
  → JARVIS audit             (every decision above)
  → UI/Gateway               (display approved final response)
```

Two properties of this shape are normative:

1. **Hermes sits inside the loop, not at its exit.** Its output is an input to the guard, never
   the output of the system on an operational turn.
2. **The dispatcher is the only door to the world.** Any component that can cause a side effect
   without passing the permission layer breaks the contract regardless of how it is implemented.

---

## 3. Seams that must exist before integration

| Seam | Purpose | Contract clause |
|---|---|---|
| Model proposal seam | accept a structured proposal from Hermes as untrusted data | §3, §18.1 |
| Proposal guard seam | compare proposal against the deterministic route; allow or block | §5, §13.2 |
| Permission seam | map action + target to a permission class and a policy decision | §11 |
| Confirmation seam | create, bind, look up and consume pending confirmations | §12 |
| Dispatch seam | execute only authorized calls and return bound results | §18 |
| Provenance seam | write and read trusted operational state with sources | §9 |
| Response seam | derive one obligation and render deterministic text | §14, §15 |
| Audit seam | record everything in §19.1 | §19 |
| Feature flag | keep the entire path off until conformance is demonstrated | entry criteria |

---

## 4. Explicitly out of scope for this document

Production code layout, class names, module paths, database schemas, transport formats, and the
order of implementation. Those belong to the planning task (13B11A), which must map this
boundary model onto the existing JARVIS codebase without changing the contract.

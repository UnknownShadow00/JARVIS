# F-MAP-01 provenance

| Source | Task | Exact contract point | Status | Owner / dependent component |
|---|---|---|---|---|
| `TARGET_COMPONENT_MAP.md` §1, lines 20–31 | 13B11A | Router gives action/target/capability; canonicalizer takes tool/raw args; permission engine decides; pipeline orchestrates | plan, preserved | P3/P4/P7 |
| `ROUTER_CONTRACT.md` §§1–3 | 13B11H | Router has no tool name or registry key | frozen | P3 route; producer cannot ask route for tool |
| `CAPABILITY_PROJECTION.md` | 13B11O | Only OPEN_APP→apps.open and OPEN_URL→browser.open pairs frozen; capability names are not canonicalizer tool namespaces or argument schemas | frozen D-08 boundary | P4 policy, P7 live binding |
| `P7_PIPELINE_CONTRACT_V1.md` lines 25–27 | 13B11O-R1 | Static caller projection permits comparison; real binder/schema must be specified separately | frozen task-local scope | P7 comparison, future JARVIS caller |
| `PROPOSAL_GUARD.md` §Minimal mapping prerequisite and final paragraph | 13B11O-R1 | Whole argument equality does not discover target field; no general capability→tool→argument schema | frozen guard contract | P7 S06, future producer |
| `FOLLOWUPS.md` row F-MAP-01 | 13B11O-R1 | “Freeze actual capability→tool namespace→required argument/target-field binding and deterministic request-to-binding producer” | **open, before live wiring** | JARVIS P7 ingress; P3/P4/P5 consumers |
| `TURN_INPUT_SCHEMA.md` fields 4,13,14 and §Required-together | 13B11P-R1 | RouterContext, expected P3 result and PermissionRequest are caller projections; expected/query absent together | frozen admission | P7 S03/S06/S07 |
| `ADMISSION_CONTRACT_V2_FINAL.md`; `RECORDED_TURN_V2.md` fields 1–21 | 13B11P-R6 | V2 changes confirmation to settled projection; no live binder | frozen | P7 input |
| `pipeline.py` `RecordedTurn`, `_proposal_guard`, `run_recorded_turn` | 13B11P-R8 production | consumes supplied expected/query, recomputes route and permission; has no producer | implemented | P7 |
| `NEXT_UNIT.md` | P7/P8 Core recovery review | freeze F-MAP-01 before shadow ingress | review recommendation | formal P7 exit |

Full search terms and hits are sealed in this task's evidence bundle. The missing object is **not** another matcher: it is the authoritative producer of a closed live tool/target/argument binding from deterministic JARVIS state. F-MAP-01 remains open pending the decisions in `FOLLOWUPS.md`.

Exact decisive wording: `task13b11o-r1/FOLLOWUPS.md` row F-MAP-01 says “Freeze actual capability→tool namespace→required argument/target-field binding and deterministic request-to-binding producer” and labels derivation/dispatch from that unfrozen mapping **BLOCKING IMPLEMENTATION**. `task13b11o-r1/P7_PIPELINE_CONTRACT_V1.md` says “only OPEN_APP→apps.open and OPEN_URL→browser.open capability pairs are frozen in P4, not a general tool/argument schema” and “A real binder must be separately specified before any branch derives executable tool arguments from text or live capabilities.” `task13b11o/CAPABILITY_PROJECTION.md` says “capability identifiers such as apps.open are not the canonicalizer's tool namespace apps, nor an execution argument schema.” These statements preclude silently filling the three missing decisions from current code spelling.

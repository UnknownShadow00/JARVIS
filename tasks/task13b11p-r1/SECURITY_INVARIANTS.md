# SECURITY INVARIANTS

Each invariant names the mechanism that holds it. "Structural" means no code path exists
that could violate it, because the admission type holds nothing capable of it; "checked"
means a named guard enforces it.

| # | Invariant | Mechanism |
|---|---|---|
| S-01 | Raw confirmation text grants no authority. `"yes"`, `"confirm"`, `"do it"` are inert. | Structural. The request string reaches `classifier.classify` and `router.route` only. No authority input in any stage reads request text, and `RecordedTurn` has no approval field. |
| S-02 | Possession of a confirmation id alone grants no authority. | Structural + checked. `correlation.confirmation_id` is an identifier only, and the one path that could use an id — a mode-B record — must additionally pass B-01…B-07, including full twelve-field binding equality. |
| S-03 | A confirmation cannot cross a session, an action, a target or a binding. | Checked: B-01 (session), B-06 (all twelve bound fields against this turn's actual route, capability, target and canonical arguments), B-07 (non-confirmable actions). |
| S-04 | A replayed result must be a genuine `TrustedToolResult`. | Checked by exact type identity (`type(x) is TrustedToolResult`), by C-02 description agreement, and by C-04…C-07 agreement with the engines' live decisions. Origin cannot be authenticated; recorded as F-P7R1-01, and in v1 the caller is always a fixture, never a provider. |
| S-05 | A result's association must match the exact invocation and turn. | Checked: C-00b (turn/session), C-01 (`result.invocation_id == invocation.invocation_id`), C-03 (correlation child), C-04 (route), C-08 (historical pair kept separate). |
| S-06 | Result replay never executes again. | Structural. `RecordedTurn` holds no callable, no executor, no dispatcher, no store and no clock; no branch constructs a `TrustedDispatcher` or calls `build_invocation`, `new_invocation_id`, `claim_for_dispatch` or any `settle_*`. |
| S-07 | Confirmation continuation and result replay cannot conflict. | Structural. Mode is derived from the three presence booleans; five of the eight cells are inadmissible and stop at `S01_INPUT`. |
| S-08 | The model cannot author the admission mode. | Structural. The mode has no constructor field. Recorded content enters only as `request`, `recording` and `adapter_request`, and reaches only the classifier, the router and the adapter parser. |
| S-09 | Admission cannot bypass a guard. | Checked. The frozen guard order is unchanged; mode only ever *removes* reachability (mode B has no edge to S09) and never skips an earlier gate. C-04…C-07 run after S02–S07 have already decided from the original request, so a later `SUCCESS` or a supplied `ALLOW` cannot backfill a missing earlier gate. |
| S-10 | A pre-dispatch admission failure remains unexecuted. | Checked + structural. Every stop in modes A and B, and every mode-C stop up to and including S09, carries `executed=False` and `result=None`; and nothing could have executed regardless. `executed=True` with `result=None` is never emitted. |
| S-11 | No hidden registry fallback. | Structural. No registry, `ToolRegistry`, capability discovery or schema lookup is reachable. Capability facts come from `turn.router_context.supported_actions` and the frozen P4 `ACTION_CAPABILITY` pairs. A `ToolSchema` description is request consistency, never capability authority. |
| S-12 | No live provider dependency. | Structural. No network, process, Ollama, Hermes, MCP or file I/O. The model's contribution is one recorded string parsed by the frozen adapter. |
| S-13 | No `TrustedToolResult` is ever constructed by P7. | Structural. P7 is not the dispatcher. Not in a success branch, not in a failure branch, not to represent an admission error. `PipelineStop` exists precisely so that no fake `ERROR` is needed. |
| S-14 | No `ConfirmationRecord` is created, mutated, expired, denied, cancelled or settled. | Structural. No `ConfirmationStore` is reachable and none of its mutating methods is called. No TTL value is frozen. |
| S-15 | No provenance write and no audit emission. | Structural. No `ProvenanceLedger`, `LedgerStore` or audit writer is reachable. `LedgerSnapshot` is read-only. The audit projection is internal data; `to_audit_entry` is never called with `validated=True` and `REQUIRED_FIELDS_BY_EVENT` is never mutated. |
| S-16 | A caller cannot assert an authority outcome. | Structural. There is no `confirmed`, `approved`, `authorized`, `claimed`, `executed` or `success` field; `permission_outcome` is never admitted, always re-decided; `confirmation_claimed` is derived from `result.executed` and the invocation's outcome, never from a confirmation id and never supplied. |
| S-17 | An approval cannot be claimed twice, and P7 adds no second claim mechanism. | Structural. The atomic claim stays `ConfirmationStore.claim_for_dispatch`, called only by `TrustedDispatcher._claim`. P7 performs no pre-claim and admits a confirmation record only in `PENDING`. |
| S-18 | Confirmation refusal is not an existence oracle. | Checked. Every B-01…B-07 failure emits the identical stage and reason, mirroring `ConfirmationStore`'s own uniform `confirmation_not_found` for unknown and foreign ids. |
| S-19 | No user-facing prose is generated for a failure. | Checked. `PipelineStop` is non-renderable; P6 and `response.build` remain the only response authority, and P7 never selects an obligation or builds a response itself. |
| S-20 | Replay is deterministic and effect-free however often it is run. | Structural. Pure function, immutable argument, both timestamps admitted, no clock, no mutation. See IDEMPOTENCE.md. |

## Threats explicitly considered and where they land

- "yes" replayed into an unrelated pending action → S-01, S-03, B-06/B-07.
- a stolen confirmation id used from another session → S-02, S-03, B-01.
- a hand-built `TrustedToolResult(status=SUCCESS, executed=True)` → S-04, and C-04…C-07
  reject its authority fields; the residual gap is F-P7R1-01.
- a genuine result re-pointed at a different invocation or turn → S-05, C-01, C-00b.
- a recorded response asserting `"permission": "allow"` or `"confirmed": true` → the
  adapter rejects any key outside `{text, proposals}` (`invalid_response`); inside
  `raw_arguments` such a key is inert data that fails canonical-argument equality.
- a prompt-injected instruction inside the drafted prose → prose enters no authority input
  and is final only on the conversational lane, where no operational claim is made.
- re-running a completed turn to double-execute → S-06, S-17, S-20; the count is zero.

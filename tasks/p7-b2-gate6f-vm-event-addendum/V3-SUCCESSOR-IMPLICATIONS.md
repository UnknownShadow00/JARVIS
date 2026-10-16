# V3 successor implications

Reviewed: isolated candidate `ff2444df…`, `candidate_v3/lineage.py` (98 lines) and `candidate_v3/authority.py` (41 lines), plus their tests in `tests/execution/v3_release_qualification_test.py:315-352` and `v3_integration_test.py:500-516`. Read-only. No candidate file was changed, so the candidate digest stays `ff2444df…`.

## How the candidate treats this exact history

`validate_v2_archive(bundle, epoch, implementation_hashes)`:
- requires manifest v2 and source binding equal to the V2 implementation hashes;
- requires the associations to be **exactly** `[[epoch,'CLOSED_COMPLETE',1]]`, with 0 attempts, 0 receipts, 0 unjoined receipts and `d06_current is None`;
- requires `pilot_events == ['OPERATOR_STOP']` and 0 refusals;
- returns a `PredecessorProof` whose `stop_attribution` is **fixed** to `UNATTRIBUTED_V2_SHUTDOWN_HOOK`, with `accepted=0`.

`HighWater.reserve_successor(proof, bindings, authorize=...)`:
- refuses any proof whose attribution is not in `('UNATTRIBUTED_V2_SHUTDOWN_HOOK',)`. A caller cannot assert `OPERATOR_INTENT_PROVEN` (tested);
- builds a payload containing predecessor, archive digest, source digest, bindings, `stop_attribution:'UNATTRIBUTED_V2_SHUTDOWN_HOOK'` and `retirement:'EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT'`. Retirement exists **only** as something the signer explicitly asserts;
- requires `authorize(payload) is True` exactly (truthy `1` is refused, tested);
- writes a singleton root row with UNIQUE predecessor/successor: one successor, no second reservation (tested);
- binds a durable 4-ordinal `accepted` table checked against the local store. Rollback or incomplete commit is refused.

## Scenario checklist

| Requirement | Handled? | Notes |
|---|---|---|
| Verified zero-use V2 epoch | Yes | association checks plus the live D09 being logically equal to the terminal archive (this addendum) |
| Truthful CLOSED_COMPLETE | Yes | required exactly; OPEN/INCOMPLETE are refused |
| Unattributed V2 shutdown | **Yes** | attribution fixed to UNATTRIBUTED; never upgraded |
| `OPERATOR_STOP` overstating intent | **Yes** | the label is accepted only as "clean zero-use stop", never as retirement |
| V2 source/config/epoch identity | Partly | source implementation hashes and epoch are bound; **`config.yaml` SHA256 is not in the proof** (see H-2) |
| Preserved backups/receipts | Yes | the archive is read-only; no D04 receipts exist |
| D06 clean / no remote unknown | Yes | `d06_current is None` required |
| No prior accepted attempts | Yes | required |
| Exactly one successor | Yes, locally | singleton root; same-UID rollback not protected (known Gate 6F gap) |
| Durable global 4-attempt cap | Locally | protected global antirollback still **unproven** (unchanged) |
| New explicit operator authorization | Interface only | `authorize` is an injected callable. **No signed verb for succession exists in `authority.py`** (verbs: OPEN_HOLD, AUTHORIZE_ONE, TERMINAL_STOP), so the human signer path is not installed (already a Gate 6F prerequisite) |
| No rollback / second-successor loophole | Partly | V2 cannot reopen (`PILOT_EPOCH_ALREADY_EXISTS`). A same-UID actor could forge a self-consistent archive or roll back the root (known class) |

## Verdict on the design

The revised candidate **handles the newly clarified history correctly**. An externally initiated shutdown cannot become an authorized retirement just because the archive says CLOSED_COMPLETE. Retirement has to come from a new, explicit, signed operator payload that itself states the stop is unattributed.

**No new engineering defect was found, so no isolated fix was made.** The issues below are hardening items for the transition procedure. They are not flaws in the candidate's logic.

- **H-1 (transition evidence):** at reservation time, require a fresh read-only proof that the **live** V2 controller is logically equal to the archive's controller (this addendum's method: per-table, schema and user_version digest). The archive is chosen by the caller, and a same-UID substitute is outside what `validate_v2_archive` can detect.
- **H-2 (binding completeness):** add V2's deployed `config.yaml` SHA256 (`00d7b460…`) and the terminal archive's manifest digest (`1b59208c…`) to the operator-signed payload, so the signer acknowledges the exact V2 deployment being retired.
- **H-3 (authority):** the successor authorization must be a distinct signed verb (for example `RETIRE_AND_RESERVE_SUCCESSOR`) bound to the payload above, with user presence, one use and a nonce. Today it is an injected callable.
- **H-4 (record semantics, V3 forward):** V3's own stop events should carry a mechanism (`SIGTERM_LIFESPAN`, `SIGUSR1_CONTROL`, `SIGNED_TERMINAL_STOP`) rather than a default `OPERATOR_STOP`, so this ambiguity does not repeat.

## Limited transition exception (specified, NOT approved or implemented)

If the operator chooses to retire this V2 epoch instead of qualifying a fresh V2 lifecycle, the exception should be named **"Unattributed-shutdown zero-use retirement"**. It is valid only if all of the following hold at the moment of signing:

1. Epoch `606a991a…` is CLOSED_COMPLETE, with input_complete=1.
2. 0 attempts, 0 submissions, 0 receipt joins, 0 refusals, and D04 absent or empty.
3. D06 `current=None,last=None`.
4. Exactly one pilot_event, `OPERATOR_STOP`, with the payload explicitly recording `UNATTRIBUTED_V2_SHUTDOWN_HOOK`.
5. The live D09 is logically equal to terminal archive `62f417a2…` (manifest `1b59208c…`), re-proved at signing.
6. Source `bd53dbc7…` and config `00d7b460…` are unchanged, and `jarvis.service` is inactive, disabled and Restart=no.
7. The Proxmox task record for the 2026-10-15T03:42Z event is attached, **or** an explicit operator statement that it is unavailable.
8. The operator signs the payload in person (H-3), acknowledging that the stop was not a planned retirement.
9. It is one use: it covers this epoch only, and cannot be reused for a later V2 epoch or a second successor.

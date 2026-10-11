# Live process transition: V2 is not compatible with opening

Source anchors are sealed in source-findings.json, bound to ten exact canonical source copies and the approved Gate4 implementation inventory. No inspected source was modified.

`PilotDriverV1.__init__` creates PilotAdmissionFenceV1 in the live process. pilot_safety.py defines only CLOSED and TERMINAL, and allows_conversation always returns False. conversation_blocked/lifecycle_blocked derive the frozen PILOT configuration, independently of D09's OPEN bookkeeping state. REST, WS, direct processing, confirmation/tool and voice paths consult those guards; the runtime and driver separately refuse capture/offer/provider start while closed. ShadowAdmissionV1 sessions/continuations are process memory, not opening authority.

The only reviewed local runtime control is SIGUSR1 installed by install_core_stop: terminal stop_admissions followed by bounded drain. There is no opener, local command receiver, Unix control socket, reload hook or reviewed hot patch.

| Transition question | Source-supported answer |
| --- | --- |
| Can PID594042 open through an existing reviewed interface? | **No.** Neither an OPEN state nor an opening interface exists. |
| Must changed code be loaded to add opening? | **Yes.** Changing files does not update already instantiated Python objects or registered handlers. |
| Is a new process/deployment ordinarily required? | **Yes.** No reviewed in-process upgrade mechanism exists. Restart/deployment is not authorized now. |
| Does V2 refuse reuse of the current OPEN epoch? | **Yes.** PilotDriverV1.start always calls open_epoch; PilotControllerV1.open_epoch rejects any prior epoch, even CLOSED_COMPLETE. The generic constructor leaves previous OPEN rows unchanged and does not attach epoch_id. |
| Can an ordinary V2 stop preserve a reusable same-ID epoch? | **No.** close calls terminal stop_admissions, records OPERATOR_STOP and closes the epoch. A closed terminal row cannot become a pause. |
| Can durable history/high-water truth be preserved? | **Yes, conditionally:** retain the entire original epoch, stop/final backup and evidence, and propose an explicitly approved V3 successor lineage with global cap. This is preservation of the old epoch, not continuation of its authority. |
| Is another authorized cycle/epoch transition needed? | **Yes.** V2 cannot safely reach the new code with the same runnable epoch through its ordinary shutdown. If retaining the exact same runnable epoch ID is mandatory, transition remains architecturally blocked. |

## Additional ingress blocker

server.py chat (line434) captures a shadow delivery and then invokes legacy `_process`. ws_endpoint (line590) similarly continues into `_process_stream`/`_process`, TTS and legacy broadcasting after capture. `_process` includes real registry/tool and other legacy processing paths. The currently closed guards prevent these effects. **Making the global guard return False to allow pilot turns would expose them.** A future opener must instead introduce a PILOT-only early branch returning exclusively the qualified bounded driver result, while keeping legacy/direct/voice/confirmation/resource/scheduler guards blocked for PILOT throughout ACTIVE/HOLD/TERMINAL.

## Recommended transition, for later approval only

1. Review and qualify V3 in isolation before touching production. Define privileged identity, immutable release, new controller/backup schemas, pure pilot ingress and lineage migration together.
2. Separately authorize planned V2 stop/drain and immutable final evidence. Require zero accepted/submitted/receipt counts and clean D06; any unexpected acceptance/unknown blocks this specific transition.
3. Preserve the original V2 namespace/epoch and startup checkpoint. Freeze a root-protected copy of the final closure and its lineage anchor without deleting/resetting/reopening the original. Verify terminal reason and all hashes.
4. Under a separately approved new deployment cycle, create exactly one V3 successor in a new versioned controller namespace, linked to the retained zero-attempt predecessor. Count all ancestors against one global four-attempt budget. Do not add an epoch to the existing V2 database or pretend its validator supports it.
5. Start the new release CLOSED only, take its valid zero-generation startup checkpoint and renew source-bound startup/Gate5 qualification for the new identity. Old Gate5 remains historical approval of the old deployment.
6. Only a separately authorized operator action may later grant opening; no automatic startup/lineage operation opens it.

Rejected: mutable boolean/file flag, Bearer/client unlock, editing source under PID594042, debugger/ptrace/monkeypatch injection, redefining SIGUSR1 as opening, force-kill to retain an OPEN row, restoring/resetting/deleting the epoch, reopening a terminal row, or adding an unlinked new epoch to obtain four fresh attempts. These either cannot update the frozen process safely, bypass approval, lose accounting, or violate terminal/restart invariants.

# Twelve-case operator procedure

**FAIL overall; not ready for human authorization.** Exact argv construction was read in packet.timer_argv/plan, the literal COMMAND-CATALOG, the guard and source-generated bounded reads. The machine-readable PROPOSED-ARGV-REVIEW.json contains labelled synthetic illustrations only. They must never supply actual host identity, clocks, nonce, expiry or source-custody observations.

Common contract: fresh local-only identity/privilege/custody and independent reviews, exact source/callback/boot/session binding, new target absent, retained prefix independently sealed and freshly inactive, approved UTC/BOOT window≤45min. Creation cut off35min, closure begins by40min, per-case90s bound, all command timeout/output caps plus reserves. User/Group65534, Type=exec, restrictive sandbox/no privileges, minimal env, exact timer pair, WakeSystem=yes, OnBoot absolute deadline,1us accuracy/no jitter/persistence. These are proposed settings whose real host support/serialization remains unqualified.

| Case | Initial/transition and expected result | Evidence and disposition |
|---|---|---|
| success | Empty first namespace → create → two untouched waiting observations → guard/main → exit0 | Raw invocation/exit/clock/cgroup/journal; affected by guard causality and plain attribution gaps |
| exit7 | Fresh target + owned prefix → waiting → guard/main → exit7, exit-code, failed service | Intentional failed state retained; same execution gaps apply |
| missingexec | Fresh nonexistent executable → waiting → guard →203/EXEC, exit-code | Exact missing-exec diagnostic mandatory; raw-prefix retention incomplete |
| missingdep | Fresh isolated nonexistent module → waiting → guard →exit1 | Exact ModuleNotFoundError mandatory; new retained-journal deletion counterexample proves cross-case gap |
| timeout | Waiting → guard/probe → sleep30 bounded by proposed RuntimeMax3s | Result timeout/code2/status15 or9; exact process readbacks; real accounting unqualified |
| late | Waiting → guard/main → sleep2 then canary before original expiry | EXPECTED_LATE_REJECTED_NOT_TIMING_PASS, never on-time qualification; post-expiry mutation rejects |
| inactive | Two waiting captures → timer/service stops → effective inactivity byD−5s | No invocation throughD+2s and final closure; raw show/cgroup/journal required |
| failedtimer | Absent exact dependency → loaded resources failure, never invoked service | Refusal alone insufficient; actual systemd transaction serialization remains unknown |
| collision | Create → waiting → identical second argv → exact normal exit1 refusal → one callback | Wrong exit/signal/manager error rejects; exact diagnostic and unchanged before/after snapshots required |
| cancel | Waiting → request → acknowledgments → observed effective inactive | No callback, complete empty-group proof; running/partial contradictions reject |
| rearm-a | Same cancellation; preserve generationA and fresh coverage | No execution required throughB closure; no failure erasure |
| rearm-b | New target/generation after complete A fence and owned prefix | One bound new invocation; fresh counterexamples reach this complete path without bypassing it |

Every row requires exact timer-then-service cleanup receipts, fresh final show/clock/cgroup and journal, original authorization and sealed artifact inventory. No wildcard cleanup, reset-failed, VM operation or deletion exists. A retry does not erase failed receipts. The cleanup planner may emit no commands for an already-inactive completed pair, while acceptance requires the original stop pair; the actual operator path resolving this remains unproven by synthetic records. Treat that as a design/feasibility concern, not permission to invent receipts.

There is no silent expiry renewal. No action including cleanup is admitted after expiry by the old grant. Preserve evidence and unresolved state; any readback/stop-only recovery requires separate finite authorization of exact owned units. Host reboot, suspend, manager restart/reexec, VM startup/shutdown/forced stop, guest root, JARVIS deployment/executor and Gate6K are excluded.

First action NOW: offline remediation/design review of R4-A01..A03, then another independent audit. No host command is authorized. The first eventual host command remains the byte-identical R01 argv in FIRST-SUPERVISED-ACTION.json: `/usr/bin/python3 -I -B -S -c` with that exact clock/boot-read body. Required prerequisites: accepted corrected revision, separate finite approval, trusted existing console/interpreter/loader, approved bounded recorder/minimal env, original UTC/BOOT authority and≥12s budget. It reads boot ID and paired clocks only; no NSS, timer, installation or VM step follows automatically. It was not executed.


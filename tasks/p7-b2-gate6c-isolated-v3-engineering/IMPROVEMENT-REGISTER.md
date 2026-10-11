# Engineering improvement register

| Finding / why it matters | Classification and action | Proof / remaining approval |
|---|---|---|
| Same-UID test code could escape Python-only mocks | SAFE TO IMPROVE NOW: per-process Landlock+seccomp and minimized audit guard | libc dummy-file/socket canaries; full run no external transmission; deployment sandbox separate |
| New consumer edges violated frozen app graph | SAFE TO IMPROVE NOW: standalone quarantine; retain failed revision | unchanged graph tests pass; REQUIRES CONTRACT REVIEW before app integration |
| Unbounded polling hung after fixture error | SAFE TO IMPROVE NOW: finite timeout loops | final focused/full complete; no test excluded |
| Canonical crash tests need child termination without production signal access | SAFE TO IMPROVE NOW: fixed pidfd broker verifies parent/UID/cwd/executable |9 harness tests; two final disposable-child signals; no service signal |
| Missing passive D04/parser bridge could falsely call raw output an observation | SAFE TO IMPROVE NOW: require canonical capture/request/normalizer/evaluator projection | canonical bridge test; real production D04 adapter still requires implementation/review |
| Second child directory could mask the same ancestor | SAFE TO IMPROVE NOW: deployment-root O_EXCL reservation before DB initialization | duplicate namespace/partial initialization tests; fixed root protected by future privileged authority |
| Permit expiry checked only at approval | SAFE TO IMPROVE NOW: persist expiry, check at acceptance | expired-at-acceptance test |
| Parse/tool failure after known provider completion was treated as unknown | SAFE TO IMPROVE NOW: retain known terminal lease while aborting pilot | proposal/malformed tests for all three steps; no fabricated remote uncertainty |
| Orphan receipt and lost delivery truth | SAFE TO IMPROVE NOW: preserve append-before-join evidence and actual local delivery; forensic checkpoint distinct from READY | short append/orphan/Granite failure tests |
| Backups could overlap append/join | SAFE TO IMPROVE NOW: shared reentrant writer lock around receipt and coordinated snapshot | checkpoint/receipt association tests; full canonical recovery tests |
| Operator attribution absent from durable record | SAFE TO IMPROVE NOW: schema 5 records verified operator and exact signed-body digest | exact attribution test; no schema migration of prior fixtures or production |
| Duplicate/nonfinite JSON ambiguities and slow request body | SAFE TO IMPROVE NOW: strict parser shared across boundaries; finite whole-body and handshake receive timeout | duplicate/router/nonfinite/body-timeout tests |
| Dataclass debug repr could reveal raw request/result/history | SAFE TO IMPROVE NOW: suppress raw fields and memory/prompt repr | explicit repr privacy test; focused/full rerun on final revision |
| Hardcoded status projection / ambiguous history | SAFE TO IMPROVE NOW: inject typed status; append assistant only after completed legacy delivery | envelope/disconnect tests; remote rendering not claimed |
| Effective legacy endpoint/model/prompt/budgets unknown | REQUIRES CONTRACT REVIEW: no live defaults, explicit unresolved bindings and factory refusal | no credential read; operator resource decision required |
| Existing D06/storage/privilege contract incompatible with new identity | REQUIRES PRODUCTION AUTHORIZATION: versioned migration and protected deployment proposed only | no users, permissions, service or state changed |
| Synchronous fsync can stall durable stop / hardware power loss untested | REQUIRES CONTRACT REVIEW: explicitly scoped qualification limit; review supervisor/I/O-failure boundary and real-filesystem tests before deployment | no false30s disk-hang guarantee; retain uncertainty rather than fabricate completion |
| AI-host identity and independent lifecycle actors unverified | REQUIRES PRODUCTION AUTHORIZATION: human trusted-console procedure retained | no SSH trust enrollment, guest request or Ollama query |

No live safety violation or production security hard stop was observed. Failed isolated branches were preserved and corrected where safe; unresolved release contracts were not silently chosen. No unrelated subsystem refactor occurred.

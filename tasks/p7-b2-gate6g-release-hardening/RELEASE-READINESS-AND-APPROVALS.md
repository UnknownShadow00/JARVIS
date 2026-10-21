# Release readiness and remaining approvals

Verdict: isolated release hardening is implemented and regression-tested; deployment readiness is PARTIAL. There is no dependency on historical tracing and no missing source dependency blocking the delivered isolated work.

| Area | Result | Remaining requirement |
|---|---|---|
| H-1–H-4 | Implemented and isolated-tested | Protected live-reader/signer integration and real operator review, not performed |
| Global four-attempt ledger | Stronger local invariants, concurrent no-refund checks pass | Protected authority unavailable to application/agent UID; full coordinated same-UID rollback remains demonstrably possible |
| L1 legacy-visible compatibility | Rules, prompts, memory snapshot and model profiles unchanged; regression passes | Explicit X1–X11 decisions and source/model attestations; no equivalence beyond Gate 6F's documented limits claimed |
| Granite isolation | Unchanged observer/profile; replies/history remain legacy-only | Real host/model identity and future approved live qualification |
| D06 | In-graph uncertainty, domain exclusion and forensic snapshot regressions pass; production clean | Independent endpoint/host/GPU/service topology attestation and external lifecycle actor inventory; no guarantee about unverified external actors |
| REST/WS | Authentication/framing/permit checks pass; disconnect now closes; actual ASGI shutdown drains | Future installation and new Gate 5 before admission |
| Backup/recovery | Local snapshot/restore/tamper/rollback regressions pass | Multi-UID protected-root, power-loss and host-loss qualification; review restore is not authority recovery |
| Production | Unchanged, V2 stopped, zero accepted attempts | Explicit operator V2 disposition; never infer retirement from maintenance or historical stop label |

Separate remaining approvals, in order:

1. Record V2's disposition after maintenance, and reconcile the shutdown attribution or explicitly record unavailable operator evidence. Leave V2 stopped meanwhile.
2. Approve/revise/reject the Gate 6F X1–X11 experiment contract. No model budgets or policies were silently changed here.
3. Human-only independent AI-host and legacy identity/model/resource attestations; any SSH enrollment separately authorized.
4. Approve OS identity, protected root and signer/nonce-service design, qualify it in a disposable multi-UID environment, then separately authorize provisioning. This task did not create users or privileged helpers.
5. Separately authorize V2 retirement and exactly one signed production V3 successor for the verified source/config/archive/live state. This task created source archives and synthetic test fixtures only.
6. Separately authorize V3 installation, configuration/systemd changes and a new Gate 5.
7. Only then consider pilot opening and individual permits, real provider traffic and later measurement, each under its own authority.

No V2 restart, production edit, production successor, V3 installation, systemd change, credential content access, real Ollama generation, admission opening, production operational tool execution, measurement or push occurred.

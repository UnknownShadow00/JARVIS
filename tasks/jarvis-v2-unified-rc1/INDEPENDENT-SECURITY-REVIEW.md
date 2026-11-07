# Independent merged-source security review

Reviewer: separate read-only `reviewer` agent `/root/independent_security_review`,
explicitly requested by the release mission. This is a fresh static review of the
merged worktree, not inherited approval from either predecessor. Test execution
and counts belong to the lead integration engineer's isolated runs.

Verdict: no remaining critical, high or medium source defect found in the reviewed
candidate. Offline lab readiness remains conditional on the final merged regression
passing. Live/production readiness is BLOCKED by the unresolved facts below.
The exact source/test/configuration pins returned by the reviewer are retained in
INDEPENDENT-REVIEW-PINS.json and checked against release contents.

## Review findings and resolution

- MEDIUM, fixed: app/server.py lifespan accepted whitespace-only api_token for
  bound synthetic transport startup while authority HTTP authentication refused it.
  The startup check now uses .strip(). Three real enrolled synthetic transport
  fixture cases prove empty, space and tab tokens fail before scheduler/worker
  startup, leave zero endpoint invocations, and release authority during cleanup.
- Documentation accuracy, fixed: UE5 binary frames close with 1003; malformed
  frames use 1008; oversized UTF-8 text uses 1009. The security baseline now matches
  the retained stronger implementation and merged tests.
- Operator compatibility, fixed: resource-management documentation now directs
  operators to the credentialed CLI readiness check and protected token delivery.

## Integration crosswalk

| Boundary | Independent conclusion |
|---|---|
| Authority routes | Codex2 asynchronous nonblank exact Bearer check preserved for every embedded route, including /ready. No anonymous fallback. |
| WebSockets | Codex1 bounded send/close and active-plus-accepting cap retained; Codex2 all-exit cleanup, cancellation and protocol-state tests combined. |
| Private directories | Descriptor-relative no-follow creation and race refusal combined with Codex1 post-creation ancestor identity verification. |
| Docker context | Codex2 COPY-input allowlist combined with nested runtime/config/credential/database/cache/venv exclusions. Static review only. |
| Offline defaults | Codex1 dry-run, disabled automatic resource controls, boot, dictation and tracing retained. |
| Execution/recovery | Exact-type synthetic executor registration, receipts, single-writer fences, UNKNOWN without redispatch, witness continuity and inert restore were not weakened. |

/ready consumers: CLI ready requires nonblank credentials, sends one Bearer request,
validates readiness fields, and returns failure on 401/503/invalid responses/transport
failure. Task/recovery CLI already sends credentials. Compose uses /health liveness;
reporter reads in-process authority; PWA/Electron do not call /ready. External
credential delivery and monitoring still require operator qualification.

Negative-test review covers anonymous/malformed authority access, hostile and
oversized frames, accept/registration/receive/audit/close failures, duplicate
execution, lost acknowledgments, forged permits/receipts, stale witnesses,
restoration tampering/races, ancestry races, and real-executor substitution.
A deterministic Docker matcher test or actual daemon context inventory remains
useful future work; this release claims static context review only.

## Unresolved deployment blockers

- One shared Bearer maps all holders to one service actor; no per-principal policy.
- Different UIDs, browsers, ingress/TLS, multiworker admission, upstream frame
  allocation/rate limits are unqualified.
- Same-UID/root compromise, privileged mount replacement, atomic SQLite VFS and
  physical power-loss durability are outside this filesystem proof.
- Co-located symmetric HMAC is not privilege separation/public-key nonrepudiation;
  independent token/key/witness/time custody remains a deployment assumption.
- Mutable Docker base, apt/pip inputs and current intended dependency advisory
  status have no fresh installed qualification or image build.
- External /ready monitoring must deliver credentials privately; /health proves
  liveness only.
- Actual VM164 identity, no-NIC/exclusive serial, installed broker identities,
  effective rights and Gate6K qualification remain separately authorized work.

Documentation-only follow-up review also passed: README.md, PROJECT_STATUS.md
and docs/release_candidate.md bind the unified packet, preserve predecessor scope
and keep hard boundaries explicit. These three exact pins are included in the
review manifest. Evidence links resolve in the canonical JARVIS workspace or its
evidence companion, not in a standalone source archive extraction.

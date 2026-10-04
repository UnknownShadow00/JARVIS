# Targeted security review

| Threat | Review/proof | Result |
|---|---|---|
| Constructor allowance permits writers | Original markers unchanged; all actual APIs trapped; supplemental static mutation review | 0 writes |
| Global/shared store | One AST-constrained instance allocation; reload creates none; two-owner proof | isolated |
| Mutable store/callable/service locator escape | Exactly three fields; recursive passive graph; no owner/store admission/getter | absent |
| Trace/client hint creates authority | Only self-minted P1 session/turn; no identity input; trace only plain metadata | no promotion |
| Mutable snapshot | Canonical P2 capture retained; fixture-input/ledger/owner changes leave old view intact | preserved |
| Wrong session/malformed context | Exact types, ID/child checks, existing record validation, association checks; failure cases | fail closed |
| Hidden audit/confirmation/registry/dispatch/provider | Passive import closure plus runtime app-call/write/network/process traps | 0 events |
| Broad allowlist/future module | One exact constructor, seven virtual constructor/module rejection cases | rejected |
| Additional security-test relaxation | All 361 entry hashes audited; one function changes byte-exactly as frozen | ONE authorization |
| Unexpected live consumer | Whole app reference scan, unchanged legacy-critical bytes | 0 consumers |

18 supplemental virtual-source rejection cases passed, with zero observed authority bypasses. Full regression and original gates passed without another exception. No dynamic import, injected constructor, alias obfuscation, service locator, stack trust token, client-created identity or hidden runtime consumer is used.

Limits: this is the frozen trusted-process public API boundary, not a hostile in-process Python sandbox. Future authenticated transport, concurrency/lifetime and live inference are not assessed or authorized. Dependency audit was attempted before committing, but pip_audit is absent; no vulnerability-audit PASS is claimed and no package was installed. `pip check` passed. Both existing full-suite dependency deprecation warnings remain.

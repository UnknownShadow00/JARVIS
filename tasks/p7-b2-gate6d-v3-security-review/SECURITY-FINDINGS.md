# Independent security findings

Verdict: **V3 CANDIDATE NEEDS FURTHER HARDENING**. No observed production breach or mutation. No critical finding established. The following severities describe impact if these isolated components were used as a release; they do not imply an exploitable live V3 listener.

| ID | Severity | Finding / evidence | Disposition |
|---|---|---|---|
| F01 | High | Store.begin accepted arbitrary operation names and new substeps on already settled attempts | Fixed: only three named generation steps; active accepted attempt and router/responder/Granite ordering required. No lifecycle kind permitted |
| F02 | High | Intermediate symlink ancestors bypassed lexical storage exclusions; backup could follow a receipt symlink | Fixed static path checks and receipt type validation. Race-free dirfd publication under protected ancestors remains unqualified |
| F03 | High | FORENSIC backup used zip(lines,joins), silently overlooking missing joined receipt lines | Fixed: fewer receipt records than durable joins always refuses, even after an attacker recomputes manifest checksums; extra orphan bytes remain forensic evidence |
| F04 | Medium | Terminal-stop approval committed before terminal closure, leaving a crash gap | Fixed: signed control record and terminal state share one transaction; local stop latch precedes storage; before/after commit tests |
| F05 | Medium | A stop or timeout concurrent with completed local send erased delivery truth | Fixed: completion callback records actual local success, including late success; unknown can advance to known local completion without reopening; history remains legacy-only |
| F06 | Medium | Peer tuple parser accepted list/bool UID equality and raised unhandled errors on malformed tuples | Fixed exact tuple/length/integer checks, bounded signature and hexadecimal checkpoint digest |
| F07 | Medium | JSON exponent overflow accepted infinity despite rejecting NaN constants | Fixed finite parse_float; duplicate-key parser was already strict, including canonical continuation parser |
| F08 | Medium | Malformed ASGI events, mixed text/binary and Unicode surrogates could escape refusal handling | Fixed shape/type/UTF-8/more_body checks; terminal refusal before provider work |
| F09 | High | Canonical Granite bridge checked request body but not endpoint/profile and all frozen limits | Fixed exact resource/profile/limit check before named possible-send. Trusted fixture observer remains deliberately substitutable; production factory still refuses |
| F10 | Medium | SQLite integrity/schema checks did not validate all logical permit/ordinal/lease associations | Fixed shared ledger consistency validator for live fixture and backup inspection |
| F11 | Medium | Checkpoint quiescence check happened before acquiring writer lock | Fixed: quiescence check moved inside the shared lock |

55 new adversarial test cases added; original 94 candidate tests retained without alteration. Initial adversarial failures and all subsequent runs preserved. Some added tests document existing defenses, rather than a newly discovered bug. In particular duplicate WS continuation keys were already rejected; this was a tested nonfinding.

| Release blocker | Severity | Remaining requirement |
|---|---|---|
| R01 | High | Authority accepts a caller-supplied peer tuple and verifier result; no kernel peer extraction, protected human signer/helper, real process identity or independent OS identities. Same jarvis UID can replace source/state or supply fixture authority |
| R02 | High | Predecessor `archive` is a nonempty string, not independently read/validated V2 closure evidence. Reservation uniqueness is per caller-selected parent, not a protected global lineage authority. An older DB replacement or alternate root can evade meaningful high-water protection outside the fixture trust model |
| R03 | High | Injected provider asserts known_terminal; no real bounded response reader or authoritative D06 endpoint-wide coordinator. Local leases cannot fence external callers/lifecycle operations |
| R04 | High | Single responder selection, unconditional L1 routing, prompt/memory/parser/cleaner and L2 confidence differ from legacy source. Effective endpoint, exact model digest and live qualification unresolved |
| R05 | High | Production factory/adapters are absent; disconnected-client observation, origin policy, real D04/D09 association, supervised final checkpoint/drain and OS/filesystem failure behavior are not release-qualified |

These are explicit technical release blockers. They are not reasons to deploy experimental defaults or mutate the predecessor. The review completed useful isolated fixes and regression; resolving protected identity, actual provider selection and real deployment behavior crosses separate approval/implementation boundaries.

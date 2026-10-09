# Gate 1 — APPROVED, NOT DEPLOYED

Recorded 2026-10-09T02:56:42Z from the operator's explicit “JARVIS V2 — GATE 1 OPERATOR APPROVAL” instruction. Applies ONLY to the first four-attempt B2 conversational-shadow PILOT. Canonical Core: jarvis@192.168.0.162:/home/jarvis/JARVIS. Task profile: network for task-scoped SSH; Nexus is the control workspace.

## Exact artifact verification

Clean detached canonical entry HEAD: `60963826c97cbe1c5952ca446d22582f856c576c`. Existing staging evidence: /home/jarvis/.hermes-poc/evidence/p7-b2-supervised-deployment-staging/. Its SHA256SUMS digest is `657d7ef6624a0692028cfeb59506056f25c83c20eb7afba674b2ec674300a28f`; all 75 entries verify with zero failures. All 22 staged packet files and the pre-existing loop log match the sealed copies. Config and four pinned execution source files match the reviewed configuration baseline. The installed unit bytes also match. No reviewed artifact was substituted or revised.

| Approved artifact | Verified SHA256 |
|---|---|
| PROPOSED-SHADOW.json | `876adf8971894b00c6ef77659671575bea2546bac5fe19935a052a64d449b660` |
| PROPOSED-RUNTIME-CONFIG.md | `6d6f192a723abed98388e9c236af7c9774cda5b00b6dea897c41fad8aab74974` |
| BACKUP-CADENCE-PROPOSAL.md | `24871f8647e3f0e71c1911e332bde4e4e6053cc50bd4b033c8aa29968838003b` |
| STOP-DRAIN-ROLLBACK.md | `896828de54396f6d54ff5d634dca102eddb2e0b27e4ff174d67afe03b6451024` |

The old staging copies, evidence seal and historical pre-approval statements remain historical. This additive receipt supersedes their Gate 1 status only. Original proposal files retain their exact approved bytes.

## Approval 1 — Runtime values and future parent proposal

The operator explicitly approves the complete mapping in PROPOSED-SHADOW.json, including its fixed B2 controller, D06 ownership and backup paths, qualified native profile, purpose PILOT and continuation scope. The approved bounds are:

| Field | Approved value |
|---|---|
| queue_capacity | 0 |
| attempt_capacity | 4 |
| intake_capacity | 1 |
| provider_generations_concurrent | 1 |
| provider_deadline_seconds | 180 |
| drain_deadline_seconds | 30 |
| native_response_max_bytes | 16384 |
| keep_alive_seconds | 60 |
| output_token_budget | 128 |
| session_capacity | 2 |
| session_idle_seconds | 300 |
| session_max_age_seconds | 1800 |
| history_max_messages | 8 |
| history_max_bytes | 8192 |
| context_tokens | 64000 |
| think | false |
| stream | false |

controller_path=/home/jarvis/JARVIS/data/p7-b2-pilot-controller-v1; ownership_path=/home/jarvis/JARVIS/data/model-ownership-v1; backup_path=/home/jarvis/.hermes-poc/backups/p7-b2; backup_policy=COORDINATED_REQUIRED; native_profile_id=jarvis.p7.ollama.granite41.b1r2.v1; continuation_scope=jarvis-core-b2-pilot-v1; purpose=PILOT.

The parent proposal is approved: execution.mode=shadow, shadow_sample_rate=1.0, hermes_brain=false. **execution.mode=shadow is approved as a future proposed value; applying it is NOT authorized now.** Effective execution.mode remains LEGACY, execution.shadow=None and both Hermes flags false.

No automatic expansion, tuning, fallback, retry or client override is authorized. Settings, execution-section normalization and PilotConfigurationV1 accept the exact proposal, with an exact round trip and no normalization warnings. Verification instantiated configuration data only; it did not construct a runtime, provider, epoch or production storage. Guarded validation denied network, subprocess, SQLite and filesystem mutations; no denied action was attempted. The bound of one provider generation is enforced by the existing intake/pending/active/provider-task admission checks, not an additional client selector.

## Approval 2 — Backup cadence, retention and local host-loss risk

The operator separately approves BACKUP-CADENCE-PROPOSAL.md for this pilot only: COORDINATED_REQUIRED at /home/jarvis/.hermes-poc/backups/p7-b2; verified startup and initialized-epoch checkpoints; a verified checkpoint after every settled accepted attempt before any next acceptance; preservation of partial and uncertain abort state; a final stopped/drained checkpoint when possible; and preservation of newer evidence before any separately authorized rollback.

Required checkpoint failure prevents further admission. Storage pauses are accepted; incomplete backups and epochs must never be reported complete. Never automatically prune, overwrite or repair backup evidence.

The operator reaffirms Option A, Core-local write-once, checksum-verified backups, and explicitly accepts the documented Core host-loss limitation ONLY for this first four-attempt pilot. No sustained-operation or formal-measurement authority is granted.

## Approval 3 — Stop/drain design and future supervised use

The operator separately approves the design and future supervised use in STOP-DRAIN-ROLLBACK.md: immediate closure of admissions; Core-local internal stop ownership; SIGUSR1 only for an eligible PILOT runtime after verifying the installed handler and correct service MainPID; and a bounded 30-second local drain.

Preserve incomplete attempts, missing/uncertain receipts and D06 remote-unknown state. No automatic restart, model unload, D06 reconciliation, evidence repair or counter reset. Storage work blocked beyond the local drain deadline produces a stopped/incomplete result.

**This is approval of the stop contract, not authorization to send a signal or change the running service now.** No signal was sent. The currently inactive LEGACY service is not an eligible signal target.

## Authority boundary and recorded outcome

Gate 1 is APPROVED, NOT DEPLOYED. Gates 2–8 remain separately unapproved. No SHADOW diff application, mode change, credential provision/permission change, systemd drop-in/reload/start/restart/stop, production D06 provision, SIGUSR1, Ollama request, pilot traffic, measurement, Hermes enablement, authority-policy change, AI VM/network/Ollama/model/context change, evidence deletion/pruning or push is authorized or performed by this task.

Current service remains inactive/dead/MainPID=0, with no drop-ins, UMask0027 and Restart=on-failure. Credential remains unconfigured; p7-b2.env absent; production runtime namespaces absent. Auth parent remains0775 and existing jarvis.env remains0600, uid/gid1000:1000.

Validation is limited to artifact/seal integrity, reviewed source/config/unit identity, guarded schema compatibility and read-only dependency inspection. No full regression rerun was necessary for documentation-only changes; historical 7110-test staging evidence is not represented as a new run. Required pip-audit attempt failed because pip_audit is unavailable; no installation or vulnerability-clean claim.

Next human decision: separately approve or reject Gate 2's exact credential-directory restriction and human provisioning scope after reviewing [GATE2-CREDENTIAL-DEPENDENCY-REVIEW.md](GATE2-CREDENTIAL-DEPENDENCY-REVIEW.md). Drop-in installation and supervisor/service actions remain separately scoped decisions. **STOP after Gate 1 recording.**

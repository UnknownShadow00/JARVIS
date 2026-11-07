# File-by-file integration matrix

Both predecessors derive from f4cac30259a7bf4610add2063679ae49138ee637 and contain substantial uncommitted work. Codex1 source identity: ab2d17fb7c522ef9199e98928e057af6d136756594beaa50ccb64d0d44b35ad1. Codex2 identity: e5774287b42dd9ad227ec2fe281dd5e48d07ba23fff9366d79d7cc7739024069. Exact initial/final per-file hashes are in the JSON companion. Original snapshots and all alternatives are preserved.

All four headline security fixes already existed in Codex1 in some form. The remaining merge combines Codex2 async nonblank authentication, race refusal, Docker allowlist and expanded tests/docs with Codex1 stronger WebSocket bounds, ancestor verification and safe defaults.

| File | Decision | Rationale |
|---|---|---|
| `.dockerignore` | reviewed semantic union / integration fix | Union Codex2 COPY-input allowlist with Codex1 nested config/credential/private/cache exclusions. |
| `.env.example` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `.github/ISSUE_TEMPLATE/bug_report.md` | identical | Byte-identical shared implementation. |
| `.github/ISSUE_TEMPLATE/feature_request.md` | identical | Byte-identical shared implementation. |
| `.github/pull_request_template.md` | identical | Byte-identical shared implementation. |
| `.github/workflows/tests.yml` | identical | Byte-identical shared implementation. |
| `.gitignore` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `AGENTS.md` | identical | Byte-identical shared implementation. |
| `CLAUDE.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `CONTRIBUTING.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `Dockerfile` | identical | Byte-identical shared implementation. |
| `HANDOFF.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `LICENSE` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `Modelfile.nothink` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `PHASE_0_TASKS.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `PHASE_1_TASKS.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `PROJECT_STATUS.md` | reviewed semantic union / integration fix | Preserve historical claims and name unified packet as current offline candidate. |
| `README.md` | reviewed semantic union / integration fix | Preserve both predecessor scopes and point current release to unified packet. |
| `SESSION_STARTER.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `app/__init__.py` | identical | Byte-identical shared implementation. |
| `app/agent/__init__.py` | identical | Byte-identical shared implementation. |
| `app/agent/admission.py` | identical | Byte-identical shared implementation. |
| `app/agent/api.py` | security retained | Codex2 async exact Bearer comparison and strip() blank-token refusal. Codex1 already required authentication for every authority route; this strengthens that implementation. |
| `app/agent/archive_restore.py` | identical | Byte-identical shared implementation. |
| `app/agent/audit_attestations.py` | identical | Byte-identical shared implementation. |
| `app/agent/authority.py` | identical | Byte-identical shared implementation. |
| `app/agent/branch_verification.py` | identical | Byte-identical shared implementation. |
| `app/agent/checkpoint_epochs.py` | identical | Byte-identical shared implementation. |
| `app/agent/enrollment.py` | identical | Byte-identical shared implementation. |
| `app/agent/execution.py` | identical | Byte-identical shared implementation. |
| `app/agent/execution_transport.py` | identical | Byte-identical shared implementation. |
| `app/agent/ledger.py` | identical | Byte-identical shared implementation. |
| `app/agent/ledger_schema.py` | identical | Byte-identical shared implementation. |
| `app/agent/migration.py` | identical | Byte-identical shared implementation. |
| `app/agent/operator_cli.py` | identical | Byte-identical shared implementation. |
| `app/agent/recovery.py` | identical | Byte-identical shared implementation. |
| `app/agent/recovery_decisions.py` | identical | Byte-identical shared implementation. |
| `app/agent/reporter.py` | identical | Byte-identical shared implementation. |
| `app/agent/runtime.py` | identical | Byte-identical shared implementation. |
| `app/agent/scheduler.py` | identical | Byte-identical shared implementation. |
| `app/agent/sensor_store.py` | identical | Byte-identical shared implementation. |
| `app/agent/simulation.py` | identical | Byte-identical shared implementation. |
| `app/agent/storage_paths.py` | reviewed semantic union / integration fix | Codex1 retained-ancestor post-create verification plus Codex2 race-refusing descriptor-relative mkdir; no-follow/owner/mode checks retained. |
| `app/agent/task_queue.py` | identical | Byte-identical shared implementation. |
| `app/boot.py` | identical | Byte-identical shared implementation. |
| `app/brain/__init__.py` | identical | Byte-identical shared implementation. |
| `app/brain/cancel_token.py` | identical | Byte-identical shared implementation. |
| `app/brain/complexity_router.py` | identical | Byte-identical shared implementation. |
| `app/brain/direct_responder.py` | identical | Byte-identical shared implementation. |
| `app/brain/kill_switch.py` | identical | Byte-identical shared implementation. |
| `app/brain/llm_client.py` | identical | Byte-identical shared implementation. |
| `app/brain/morning_report.py` | identical | Byte-identical shared implementation. |
| `app/brain/planner.py` | identical | Byte-identical shared implementation. |
| `app/brain/prompts.py` | identical | Byte-identical shared implementation. |
| `app/brain/response_cleaner.py` | identical | Byte-identical shared implementation. |
| `app/brain/router.py` | identical | Byte-identical shared implementation. |
| `app/brain/tool_embeddings.py` | identical | Byte-identical shared implementation. |
| `app/brain/tool_params.py` | identical | Byte-identical shared implementation. |
| `app/cli.py` | reviewed semantic union / integration fix | Existing credentialed task/recovery helpers retained; add credentialed fail-closed ready command without startup/retry fallback. |
| `app/comms/__init__.py` | identical | Byte-identical shared implementation. |
| `app/comms/audio2face.py` | identical | Byte-identical shared implementation. |
| `app/comms/discord_bot.py` | identical | Byte-identical shared implementation. |
| `app/comms/telegram_bot.py` | identical | Byte-identical shared implementation. |
| `app/comms/ue5_bridge.py` | release retained | Retain Codex1 cap accounting and send/close bounds, which are stronger than Codex2 removal-on-failed-broadcast implementation. |
| `app/computer/__init__.py` | identical | Byte-identical shared implementation. |
| `app/computer/gesture.py` | identical | Byte-identical shared implementation. |
| `app/computer/mouse_keyboard.py` | identical | Byte-identical shared implementation. |
| `app/computer/safety.py` | identical | Byte-identical shared implementation. |
| `app/computer/screenshot.py` | identical | Byte-identical shared implementation. |
| `app/computer/verifier.py` | identical | Byte-identical shared implementation. |
| `app/computer/vision.py` | identical | Byte-identical shared implementation. |
| `app/computer/yolo_detector.py` | identical | Byte-identical shared implementation. |
| `app/config.py` | release retained | Keep Codex1 disabled resource-control class defaults; Codex2 snapshot still enabled them. |
| `app/config_check.py` | identical | Byte-identical shared implementation. |
| `app/logs/__init__.py` | identical | Byte-identical shared implementation. |
| `app/logs/audit.py` | identical | Byte-identical shared implementation. |
| `app/main.py` | identical | Byte-identical shared implementation. |
| `app/memory/__init__.py` | identical | Byte-identical shared implementation. |
| `app/memory/graphiti_client.py` | identical | Byte-identical shared implementation. |
| `app/memory/memory_client.py` | identical | Byte-identical shared implementation. |
| `app/memory/procedural.py` | identical | Byte-identical shared implementation. |
| `app/memory/project_indexer.py` | identical | Byte-identical shared implementation. |
| `app/memory/rag_client.py` | identical | Byte-identical shared implementation. |
| `app/network/__init__.py` | identical | Byte-identical shared implementation. |
| `app/network/tailscale.py` | identical | Byte-identical shared implementation. |
| `app/observability/__init__.py` | identical | Byte-identical shared implementation. |
| `app/observability/tracing.py` | identical | Byte-identical shared implementation. |
| `app/resource_manager.py` | identical | Byte-identical shared implementation. |
| `app/server.py` | reviewed semantic union / integration fix | Codex1 bounded sends/closes and handler-owned registration retained; Codex2 cleanup behavior preserved. Independent review aligned transport startup blank-token checks with HTTP auth. |
| `app/tools/__init__.py` | identical | Byte-identical shared implementation. |
| `app/tools/apps.py` | identical | Byte-identical shared implementation. |
| `app/tools/browser.py` | identical | Byte-identical shared implementation. |
| `app/tools/browser_use.py` | identical | Byte-identical shared implementation. |
| `app/tools/cad.py` | identical | Byte-identical shared implementation. |
| `app/tools/calendar.py` | identical | Byte-identical shared implementation. |
| `app/tools/cli/__init__.py` | identical | Byte-identical shared implementation. |
| `app/tools/computer_use.py` | identical | Byte-identical shared implementation. |
| `app/tools/files.py` | identical | Byte-identical shared implementation. |
| `app/tools/health_check.py` | identical | Byte-identical shared implementation. |
| `app/tools/kasa.py` | identical | Byte-identical shared implementation. |
| `app/tools/mcp_client.py` | identical | Byte-identical shared implementation. |
| `app/tools/mouse_keyboard.py` | identical | Byte-identical shared implementation. |
| `app/tools/obsidian.py` | identical | Byte-identical shared implementation. |
| `app/tools/registry.py` | identical | Byte-identical shared implementation. |
| `app/tools/screenshot.py` | identical | Byte-identical shared implementation. |
| `app/tools/shell.py` | identical | Byte-identical shared implementation. |
| `app/tools/system_stats.py` | identical | Byte-identical shared implementation. |
| `app/tools/vision.py` | identical | Byte-identical shared implementation. |
| `app/tools/web_search.py` | identical | Byte-identical shared implementation. |
| `app/voice/__init__.py` | identical | Byte-identical shared implementation. |
| `app/voice/audio_stream.py` | identical | Byte-identical shared implementation. |
| `app/voice/dictation.py` | identical | Byte-identical shared implementation. |
| `app/voice/error_recovery.py` | identical | Byte-identical shared implementation. |
| `app/voice/filler_manager.py` | identical | Byte-identical shared implementation. |
| `app/voice/phrase_cache.py` | identical | Byte-identical shared implementation. |
| `app/voice/push_to_talk.py` | identical | Byte-identical shared implementation. |
| `app/voice/sounds.py` | identical | Byte-identical shared implementation. |
| `app/voice/stt.py` | identical | Byte-identical shared implementation. |
| `app/voice/tts.py` | identical | Byte-identical shared implementation. |
| `app/voice/vad.py` | identical | Byte-identical shared implementation. |
| `app/voice/wake_word.py` | identical | Byte-identical shared implementation. |
| `assets/audio/README.md` | identical | Byte-identical shared implementation. |
| `assets/audio/boot_intro.wav` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `assets/audio/done.wav` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `assets/audio/error.wav` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `assets/audio/listening.wav` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `assets/audio/working.wav` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `config.yaml.example` | reviewed semantic union / integration fix | Keep Codex1 safe dry-run/boot/dictation/resource/tracing defaults, clarify blank-token /ready contract. |
| `config/restic-excludes.txt` | identical | Byte-identical shared implementation. |
| `docker-compose.yml` | identical | Byte-identical shared implementation. |
| `docs/5090_migration.md` | identical | Byte-identical shared implementation. |
| `docs/BACKUP.md` | identical | Byte-identical shared implementation. |
| `docs/EVALS.md` | identical | Byte-identical shared implementation. |
| `docs/OBSERVABILITY.md` | identical | Byte-identical shared implementation. |
| `docs/TARGET_HOST_READINESS.md` | identical | Byte-identical shared implementation. |
| `docs/audit_disaster_recovery.md` | identical | Byte-identical shared implementation. |
| `docs/authority_enrollment.md` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `docs/baselines/PRE_HERMES_BASELINE.md` | identical | Byte-identical shared implementation. |
| `docs/content/episode_01_script.md` | identical | Byte-identical shared implementation. |
| `docs/content/episode_arc.md` | identical | Byte-identical shared implementation. |
| `docs/content/recording_setup.md` | identical | Byte-identical shared implementation. |
| `docs/content/tiktok_60s_cut.md` | identical | Byte-identical shared implementation. |
| `docs/end_to_end_readiness.md` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `docs/graphiti_setup.md` | identical | Byte-identical shared implementation. |
| `docs/hermes_setup.md` | identical | Byte-identical shared implementation. |
| `docs/operator_recovery.md` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `docs/recovery_decisions.md` | identical | Byte-identical shared implementation. |
| `docs/release_candidate.md` | reviewed semantic union / integration fix | Unified packet identity, nonblank token contract and credentialed readiness command. |
| `docs/repos.md` | identical | Byte-identical shared implementation. |
| `docs/resource_management.md` | reviewed semantic union / integration fix | Replace ambiguous readiness instruction with protected credentialed CLI workflow. |
| `docs/security_baseline.md` | reviewed semantic union / integration fix | Codex2 guide retained, updated for Codex1 binary code and unified credentialed readiness CLI. |
| `docs/task_api.md` | reviewed semantic union / integration fix | Codex2 explicit mandatory auth wording plus reference to Codex1 stronger offline candidate contract. |
| `evals/__init__.py` | identical | Byte-identical shared implementation. |
| `evals/adapter.py` | identical | Byte-identical shared implementation. |
| `evals/fixtures/current_deterministic.json` | identical | Byte-identical shared implementation. |
| `evals/golden.jsonl` | identical | Byte-identical shared implementation. |
| `evals/grader.py` | identical | Byte-identical shared implementation. |
| `evals/runner.py` | identical | Byte-identical shared implementation. |
| `evals/schema.py` | identical | Byte-identical shared implementation. |
| `frontend/electron/README.md` | identical | Byte-identical shared implementation. |
| `frontend/electron/main.js` | identical | Byte-identical shared implementation. |
| `frontend/electron/package-lock.json` | identical | Byte-identical shared implementation. |
| `frontend/electron/package.json` | identical | Byte-identical shared implementation. |
| `frontend/electron/preload.js` | identical | Byte-identical shared implementation. |
| `frontend/electron/renderer/index.html` | identical | Byte-identical shared implementation. |
| `frontend/hologram/README.md` | identical | Byte-identical shared implementation. |
| `frontend/hologram/app.js` | identical | Byte-identical shared implementation. |
| `frontend/hologram/index.html` | identical | Byte-identical shared implementation. |
| `frontend/pwa/app.js` | identical | Byte-identical shared implementation. |
| `frontend/pwa/icon.png` | release retained | Codex1 integration/default documentation retained; Codex2 alternative and exact difference preserved in reconciliation-diffs. |
| `frontend/pwa/index.html` | identical | Byte-identical shared implementation. |
| `frontend/pwa/manifest.json` | identical | Byte-identical shared implementation. |
| `frontend/pwa/sw.js` | identical | Byte-identical shared implementation. |
| `jarvis.cmd` | identical | Byte-identical shared implementation. |
| `jarvis.py` | identical | Byte-identical shared implementation. |
| `pytest.ini` | identical | Byte-identical shared implementation. |
| `requirements-core.txt` | identical | Byte-identical shared implementation. |
| `requirements-desktop.txt` | identical | Byte-identical shared implementation. |
| `requirements.txt` | identical | Byte-identical shared implementation. |
| `scripts/backup_restic.sh` | identical | Byte-identical shared implementation. |
| `scripts/install.ps1` | identical | Byte-identical shared implementation. |
| `scripts/install.py` | identical | Byte-identical shared implementation. |
| `scripts/install_piper.py` | identical | Byte-identical shared implementation. |
| `scripts/sensor_node.py` | identical | Byte-identical shared implementation. |
| `scripts/setup_autostart.py` | identical | Byte-identical shared implementation. |
| `scripts/switch_models.py` | identical | Byte-identical shared implementation. |
| `scripts/verify_restic_backup.sh` | identical | Byte-identical shared implementation. |
| `scripts/wake_diag.py` | identical | Byte-identical shared implementation. |
| `scripts/wake_diag_20260506_001537.csv` | identical | Byte-identical shared implementation. |
| `skills.md` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/manual_voice_smoke.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/pre_server_readiness.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/proxmox-automation-phase2/APPROVAL-TEMPLATE.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/NEGATIVE-TESTS.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/OPERATOR-AUTHORIZATION.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/RECOMMENDATION.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/SHA256SUMS` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/tools/observe.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/tools/policy_model.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase2/tools/test_policy_model.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/INDEPENDENT-REVIEW.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/INSTALLATION.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/LIVE-ACCEPTANCE.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/PROGRESS.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/README.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/RELEASE.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/SECURITY-REVIEW.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/SHA256SUMS` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/STOP-AND-REVOKE.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/approval.example.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/g6k-serial-precheck.service` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/g6k-serial-precheck.socket` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/g6k-serial-worker.service` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/g6k-serial.service` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/g6k-serial.socket` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/host.example.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/deploy/worker.example.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/SOURCE-SHA256SUMS` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/entry.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/__init__.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/broker.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/hardening.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/journal.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/policy.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/preissuance.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/protocol.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/provision.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/runtime.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/securefs.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/transport.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/src/g6k_serial/worker.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/run_offline.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/support.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_boundaries.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_hardening.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_ipc.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_preissuance.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_review_r1.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_storage.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_transport.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tests/test_worker_runtime.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3-review-r1/tools/build_release.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/INSTALLATION.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/LIVE-ACCEPTANCE.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/README.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/SECURITY-REVIEW.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/SHA256SUMS` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/STOP-AND-REVOKE.md` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/deploy/g6k-serial-worker.service` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/deploy/g6k-serial.service` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/deploy/g6k-serial.socket` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/deploy/host.example.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/deploy/worker.example.json` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/SOURCE-SHA256SUMS` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/entry.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/__init__.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/broker.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/hardening.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/journal.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/policy.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/protocol.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/provision.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/runtime.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/securefs.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/transport.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/src/g6k_serial/worker.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/run_offline.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/support.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/test_boundaries.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/test_hardening.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/test_ipc.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/test_storage.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/test_transport.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/proxmox-automation-phase3/tests/test_worker_runtime.py` | external predecessor artifact; not part of application release | Existing standalone broker/planning evidence preserved byte-for-byte; no adapter installation or activation. |
| `tasks/readiness_report.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/task13b3a-analyze.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/task13b3a-monitor.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/task13b3a.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tasks/tool_readiness_smoke.py` | security retained | Include security-only public documentation/helpers or stronger identity contract/tests. |
| `tests/__init__.py` | identical | Byte-identical shared implementation. |
| `tests/application_fixtures.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/audit_process_actor.py` | identical | Byte-identical shared implementation. |
| `tests/boot_test.py` | identical | Byte-identical shared implementation. |
| `tests/conftest.py` | identical | Byte-identical shared implementation. |
| `tests/direct_responder_test.py` | identical | Byte-identical shared implementation. |
| `tests/e2e/__init__.py` | identical | Byte-identical shared implementation. |
| `tests/e2e/test_full_loop.py` | identical | Byte-identical shared implementation. |
| `tests/enrollment_fixtures.py` | identical | Byte-identical shared implementation. |
| `tests/enrollment_process_actor.py` | identical | Byte-identical shared implementation. |
| `tests/execution_process_actor.py` | identical | Byte-identical shared implementation. |
| `tests/hardware_smoke_test.py` | identical | Byte-identical shared implementation. |
| `tests/ledger_process_actor.py` | identical | Byte-identical shared implementation. |
| `tests/ollama_test.py` | identical | Byte-identical shared implementation. |
| `tests/perf/__init__.py` | identical | Byte-identical shared implementation. |
| `tests/perf/baseline_4070ti.json` | identical | Byte-identical shared implementation. |
| `tests/pipeline_test.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/recovery_process_actor.py` | identical | Byte-identical shared implementation. |
| `tests/router_test.py` | identical | Byte-identical shared implementation. |
| `tests/safety_test.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/sounds_test.py` | identical | Byte-identical shared implementation. |
| `tests/stress/__init__.py` | identical | Byte-identical shared implementation. |
| `tests/stress/test_wake_word_stress.py` | identical | Byte-identical shared implementation. |
| `tests/stt_test.py` | identical | Byte-identical shared implementation. |
| `tests/synthetic_authority.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_agent_stubs.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_approval_gates.py` | identical | Byte-identical shared implementation. |
| `tests/test_apps_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_audio2face.py` | identical | Byte-identical shared implementation. |
| `tests/test_audit_disaster.py` | identical | Byte-identical shared implementation. |
| `tests/test_audit_disaster_app.py` | identical | Byte-identical shared implementation. |
| `tests/test_audit_integration_fixes.py` | identical | Byte-identical shared implementation. |
| `tests/test_authority_enrollment.py` | identical | Byte-identical shared implementation. |
| `tests/test_authority_http_security.py` | security retained | Codex2 superset adds whitespace configuration denial; previous cases retained. |
| `tests/test_boot_events.py` | identical | Byte-identical shared implementation. |
| `tests/test_boot_integration.py` | identical | Byte-identical shared implementation. |
| `tests/test_browser_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_calendar_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_cancel_token.py` | identical | Byte-identical shared implementation. |
| `tests/test_ci_config.py` | identical | Byte-identical shared implementation. |
| `tests/test_comms_stubs.py` | identical | Byte-identical shared implementation. |
| `tests/test_complexity_router.py` | identical | Byte-identical shared implementation. |
| `tests/test_computer_safety.py` | identical | Byte-identical shared implementation. |
| `tests/test_computer_use_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_computer_verifier.py` | identical | Byte-identical shared implementation. |
| `tests/test_config_check.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_dictation.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_discord_bot.py` | identical | Byte-identical shared implementation. |
| `tests/test_enrollment_app.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_error_recovery.py` | identical | Byte-identical shared implementation. |
| `tests/test_evals_adapter.py` | identical | Byte-identical shared implementation. |
| `tests/test_evals_grading.py` | identical | Byte-identical shared implementation. |
| `tests/test_evals_schema.py` | identical | Byte-identical shared implementation. |
| `tests/test_execution_pipeline.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_files_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_gesture.py` | identical | Byte-identical shared implementation. |
| `tests/test_graphiti_client.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_headless_wake.py` | identical | Byte-identical shared implementation. |
| `tests/test_health_check.py` | identical | Byte-identical shared implementation. |
| `tests/test_hologram_files.py` | identical | Byte-identical shared implementation. |
| `tests/test_install_script.py` | identical | Byte-identical shared implementation. |
| `tests/test_llm_client_payload.py` | identical | Byte-identical shared implementation. |
| `tests/test_loopback_boundary.py` | identical | Byte-identical shared implementation. |
| `tests/test_memory_client.py` | identical | Byte-identical shared implementation. |
| `tests/test_memory_stubs.py` | identical | Byte-identical shared implementation. |
| `tests/test_morning_report.py` | identical | Byte-identical shared implementation. |
| `tests/test_mouse_keyboard.py` | identical | Byte-identical shared implementation. |
| `tests/test_obsidian_tool.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_operator_app.py` | identical | Byte-identical shared implementation. |
| `tests/test_operator_ledger.py` | identical | Byte-identical shared implementation. |
| `tests/test_perf_baseline.py` | identical | Byte-identical shared implementation. |
| `tests/test_phase3_integration.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_phase8_integrations.py` | identical | Byte-identical shared implementation. |
| `tests/test_planner.py` | identical | Byte-identical shared implementation. |
| `tests/test_pre_server_readiness.py` | identical | Byte-identical shared implementation. |
| `tests/test_procedural_memory.py` | identical | Byte-identical shared implementation. |
| `tests/test_prompts_memory.py` | identical | Byte-identical shared implementation. |
| `tests/test_ptt_and_killswitch.py` | identical | Byte-identical shared implementation. |
| `tests/test_push_to_talk.py` | identical | Byte-identical shared implementation. |
| `tests/test_pwa_glasses.py` | identical | Byte-identical shared implementation. |
| `tests/test_pwa_serve.py` | identical | Byte-identical shared implementation. |
| `tests/test_rag_client.py` | identical | Byte-identical shared implementation. |
| `tests/test_readiness_report.py` | identical | Byte-identical shared implementation. |
| `tests/test_ready_client.py` | reviewed semantic union / integration fix | Twelve fail-closed credentialed CLI readiness tests; no service startup, state mutation or retries. |
| `tests/test_recovery_decisions.py` | identical | Byte-identical shared implementation. |
| `tests/test_release_security.py` | reviewed semantic union / integration fix | Codex1 stronger full suite retained; three new actual transport-lifespan blank-token startup rejection cases. |
| `tests/test_reporter.py` | identical | Byte-identical shared implementation. |
| `tests/test_resource_manager.py` | identical | Byte-identical shared implementation. |
| `tests/test_restic_scripts.py` | identical | Byte-identical shared implementation. |
| `tests/test_safety_levels.py` | identical | Byte-identical shared implementation. |
| `tests/test_scheduler.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_scheduler_reliability.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_screenshot.py` | identical | Byte-identical shared implementation. |
| `tests/test_screenshot_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_secure_transport.py` | identical | Byte-identical shared implementation. |
| `tests/test_self_suppression.py` | identical | Byte-identical shared implementation. |
| `tests/test_sensor_endpoints.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_sensor_store.py` | identical | Byte-identical shared implementation. |
| `tests/test_server_auth.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_server_integration.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_shell_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_storage_ancestry_security.py` | identical | Byte-identical shared implementation. |
| `tests/test_switch_models.py` | identical | Byte-identical shared implementation. |
| `tests/test_system_stats_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_tailscale.py` | identical | Byte-identical shared implementation. |
| `tests/test_task_queue_callers.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_task_queue_persistence.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_task_queue_store_safety.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_telegram_bot.py` | identical | Byte-identical shared implementation. |
| `tests/test_tool_embeddings.py` | identical | Byte-identical shared implementation. |
| `tests/test_tool_readiness_smoke.py` | identical | Byte-identical shared implementation. |
| `tests/test_tracing.py` | release retained | Codex1 current durable API/queue/scheduler/closed-tool regression contract retained; Codex2 alternative is unchanged legacy source or token literal-only equivalent. Exact original diff retained. |
| `tests/test_tts_chatterbox.py` | identical | Byte-identical shared implementation. |
| `tests/test_ue5_bridge.py` | identical | Byte-identical shared implementation. |
| `tests/test_ue5_security.py` | reviewed semantic union / integration fix | Codex2 cancellation, capacity, UTF-8 and close-failure tests merged with Codex1 protocol close codes and bounded manager ownership. |
| `tests/test_vad_timeout.py` | identical | Byte-identical shared implementation. |
| `tests/test_vision.py` | identical | Byte-identical shared implementation. |
| `tests/test_vision_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_vision_vlm.py` | identical | Byte-identical shared implementation. |
| `tests/test_wake_diag.py` | identical | Byte-identical shared implementation. |
| `tests/test_web_search_tool.py` | identical | Byte-identical shared implementation. |
| `tests/test_yolo_detector.py` | identical | Byte-identical shared implementation. |
| `tests/transport_fixtures.py` | identical | Byte-identical shared implementation. |
| `tests/transport_process_actor.py` | identical | Byte-identical shared implementation. |
| `tests/tts_test.py` | identical | Byte-identical shared implementation. |
| `tests/vad_test.py` | identical | Byte-identical shared implementation. |
| `tests/voice_pipeline_test.py` | identical | Byte-identical shared implementation. |
| `tests/wake_word_test.py` | identical | Byte-identical shared implementation. |
